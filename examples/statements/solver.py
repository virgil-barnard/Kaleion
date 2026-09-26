"""Optional solver assistance for neutral Kaleion statement terms.

This module owns one backend translation and its result taxonomy. It does not
execute construction graphs, mutate a workspace, or assign kernel-checked proof
status. Z3 is imported only when :class:`Z3Assistant` is constructed, so the
statement and studio modules remain usable without the ``proof`` extra.
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib
import re

from .terms import Term, evaluate, term


_INTEGER = re.compile(r"-?(0|[1-9][0-9]*)")
_FINGERPRINT = re.compile(r"[0-9a-f]{64}")
_DECIMAL_DIGITS = 1235
_BINARY = {"add", "sub", "mul", "floordiv", "mod", "gcd",
           "eq", "ne", "lt", "le", "gt", "ge", "and", "or"}
_UNARY = {"neg", "abs", "indicator", "not"}


def decode_term(data):
    """Validate and reconstruct the version-1 neutral term wire format."""
    if not isinstance(data, dict) or set(data) != {"op", "sort", "args"}:
        raise ValueError("A solver term needs exactly op, sort, and args")
    op, sort, args = data["op"], data["sort"], data["args"]
    if sort not in ("integer", "boolean") or not isinstance(op, str) or not isinstance(args, list):
        raise ValueError("Invalid term operation, sort, or arguments")
    if op == "literal":
        if len(args) != 1:
            raise ValueError("A literal needs one value")
        if sort == "boolean":
            if type(args[0]) is not bool:
                raise ValueError("A Boolean literal needs true or false")
            value = args[0]
        else:
            if (not isinstance(args[0], str) or len(args[0]) > _DECIMAL_DIGITS
                    or not _INTEGER.fullmatch(args[0])):
                raise ValueError("An integer literal needs a bounded decimal string")
            value = int(args[0])
        return Term(op, (value,), sort)
    if op in ("parameter", "bound"):
        if sort != "integer" or len(args) != 1 or not isinstance(args[0], str) or not 0 < len(args[0]) <= 80:
            raise ValueError("A symbol needs one bounded name and integer sort")
        return Term(op, (args[0],), sort)
    if op == "sum":
        if sort != "integer" or len(args) != 3 or not all(isinstance(value, dict) for value in args):
            raise ValueError("A bounded sum needs a variable, extent, and integer body")
        variable, extent, body = (decode_term(value) for value in args)
        if variable.op != "bound" or extent.sort != "integer" or body.sort != "integer":
            raise ValueError("Invalid bounded sum sorts")
        return Term(op, (variable, extent, body), sort)
    if op == "table":
        if (sort != "integer" or len(args) != 2 or not isinstance(args[0], list)
                or not isinstance(args[1], dict) or len(args[0]) > 20_000
                or any(not isinstance(value, str) or len(value) > _DECIMAL_DIGITS
                       or not _INTEGER.fullmatch(value)
                       for value in args[0])):
            raise ValueError("A table term needs bounded exact integer entries and an address")
        index = decode_term(args[1])
        if index.sort != "integer":
            raise ValueError("A table address must be integer")
        return Term(op, (tuple(map(int, args[0])), index), sort)
    expected = 2 if op in _BINARY else 1 if op in _UNARY else None
    if expected is None:
        # Keep the rejection at the backend boundary explicit. A statement may
        # still contain a sound neutral term that this first adapter cannot use.
        raise ValueError(f"Z3 assistance does not support term operation {op!r}")
    if len(args) != expected or not all(isinstance(value, dict) for value in args):
        raise ValueError(f"{op} needs {expected} term argument(s)")
    decoded = tuple(decode_term(value) for value in args)
    rebuilt = term(op, *decoded)
    if rebuilt.sort != sort:
        raise ValueError(f"Declared sort for {op} does not match its operands")
    return rebuilt


@dataclass(frozen=True)
class Goal:
    """One universally quantified implication checked by counterexample search."""

    name: str
    proposition: Term
    hypotheses: tuple[Term, ...] = ()
    domain: tuple[tuple[Term, Term], ...] = ()
    statement_fingerprint: str | None = None
    source: str = "derived"

    def __post_init__(self):
        if not isinstance(self.name, str) or not 0 < len(self.name) <= 160:
            raise ValueError("A proof-assistance goal needs a bounded name")
        if self.proposition.sort != "boolean" or any(value.sort != "boolean" for value in self.hypotheses):
            raise ValueError("A goal and all hypotheses must be Boolean")
        if len(self.hypotheses) > 64 or len(self.domain) > 16:
            raise ValueError("Goal exceeds the hypothesis or domain budget")
        seen = set()
        for variable, extent in self.domain:
            if variable.op != "bound" or variable.sort != "integer" or extent.sort != "integer":
                raise ValueError("Goal domains need integer bound variables and extents")
            if variable.args[0] in seen:
                raise ValueError("Goal domain variables must be distinct")
            seen.add(variable.args[0])


@dataclass(frozen=True)
class Attempt:
    """A backend result; ``solver_valid`` is deliberately not ``checked_proof``."""

    status: str
    goal: str
    backend: str
    statement_fingerprint: str | None = None
    assignments: tuple[tuple[str, str, str], ...] = ()
    reason: str | None = None
    independently_reproduced: bool | None = None
    rules: tuple[str, ...] = ()

    def data(self):
        value = {
            "status": self.status,
            "goal": self.goal,
            "backend": self.backend,
            "statement_fingerprint": self.statement_fingerprint,
            "assignments": [{"kind": kind, "name": name, "value": value}
                            for kind, name, value in self.assignments],
        }
        if self.reason is not None:
            value["reason"] = self.reason
        if self.independently_reproduced is not None:
            value["independently_reproduced"] = self.independently_reproduced
        if self.rules:
            value["rules"] = list(self.rules)
        return value


class _Unsupported(ValueError):
    pass


class Z3Assistant:
    """Quantifier-free integer counterexample search using the optional Z3Py API."""

    def __init__(self):
        try:
            self.z3 = importlib.import_module("z3")
        except ImportError as error:
            raise RuntimeError("Install the optional proof tools with python3 -m pip install -e '.[proof]'") from error
        self.backend = f"z3/{self.z3.get_version_string()}"

    def _lower(self, value, symbols):
        z3, op, args = self.z3, value.op, value.args
        if op == "literal":
            return z3.BoolVal(args[0]) if value.sort == "boolean" else z3.IntVal(args[0])
        if op in ("parameter", "bound"):
            key = (op, args[0])
            if key not in symbols:
                prefix = "p" if op == "parameter" else "k"
                symbols[key] = z3.Int(f"{prefix}:{args[0]}")
            return symbols[key]
        # Reject operations before descending into their non-Term payloads
        # (notably lookup-table entries). Each will need a dedicated semantic
        # contract before a backend may translate it.
        if op in {"floordiv", "mod", "gcd", "sum", "table"}:
            raise _Unsupported(f"Z3 assistance does not support term operation {op!r}")
        lowered = [self._lower(arg, symbols) for arg in args]
        operations = {
            "add": lambda: lowered[0] + lowered[1],
            "sub": lambda: lowered[0] - lowered[1],
            "mul": lambda: lowered[0] * lowered[1],
            "neg": lambda: -lowered[0],
            "abs": lambda: z3.If(lowered[0] >= 0, lowered[0], -lowered[0]),
            "eq": lambda: lowered[0] == lowered[1],
            "ne": lambda: lowered[0] != lowered[1],
            "lt": lambda: lowered[0] < lowered[1],
            "le": lambda: lowered[0] <= lowered[1],
            "gt": lambda: lowered[0] > lowered[1],
            "ge": lambda: lowered[0] >= lowered[1],
            "and": lambda: z3.And(*lowered),
            "or": lambda: z3.Or(*lowered),
            "not": lambda: z3.Not(lowered[0]),
            "indicator": lambda: z3.If(lowered[0], z3.IntVal(1), z3.IntVal(0)),
        }
        if op in operations:
            return operations[op]()
        # Floor division, positive modulus, finite sums, tables, and gcd need
        # dedicated semantic lemmas. Z3's totalized/signed operations must not
        # silently replace Kaleion's partial Python-integer contract.
        raise _Unsupported(f"Z3 assistance does not support term operation {op!r}")

    def _solver(self, timeout_ms):
        if type(timeout_ms) is not int or not 1 <= timeout_ms <= 60_000:
            raise ValueError("Solver timeout must be an integer from 1 to 60000 milliseconds")
        solver = self.z3.Solver()
        solver.set(timeout=timeout_ms)
        return solver

    @staticmethod
    def _coprime_operands(value):
        """Recognize only the neutral predicate ``gcd(x, y) = 1``."""
        if value.op != "eq":
            return None
        left, right = value.args
        for candidate, one in ((left, right), (right, left)):
            if (candidate.op == "gcd" and one.op == "literal"
                    and one.sort == "integer" and one.args == (1,)):
                return candidate.args
        return None

    def _lower_hypothesis(self, value, symbols, auxiliaries, rules):
        operands = self._coprime_operands(value)
        if operands is None:
            return self._lower(value, symbols)
        left, right = (self._lower(operand, symbols) for operand in operands)
        index = len(auxiliaries) // 2
        u = self.z3.Int(f"aux:bezout:{index}:u")
        v = self.z3.Int(f"aux:bezout:{index}:v")
        auxiliaries.extend((u, v))
        rules.add("bezout-coprime/1")
        # Bezout's identity is equivalent to gcd(x, y) = 1 over the integers.
        # The fresh coefficients are solver witnesses, not Kaleion parameters,
        # and therefore never appear in a returned mathematical assignment.
        return left * u + right * v == 1

    @staticmethod
    def _one_less_parameter(value):
        if value.op != "sub":
            return None
        parameter, one = value.args
        if (parameter.op == "parameter" and one.op == "literal"
                and one.sort == "integer" and one.args == (1,)):
            return parameter
        return None

    def _domain_lemmas(self, goal, symbols, rules):
        """Return named arithmetic consequences for an exact rectangle domain."""
        coordinates = {}
        for variable, extent in goal.domain:
            parameter = self._one_less_parameter(extent)
            if parameter is not None and parameter.args[0] not in coordinates:
                coordinates[parameter.args[0]] = variable
        lemmas = []
        one = Term("literal", (1,))
        for hypothesis in goal.hypotheses:
            operands = self._coprime_operands(hypothesis)
            if (operands is None or any(value.op != "parameter" for value in operands)
                    or operands[0] == operands[1]):
                continue
            left, right = operands
            # The coordinate paired with a parameter is bounded by the other
            # parameter: 0 <= i < b-1 and 0 <= j < a-1. Coprimality therefore
            # excludes a(i+1) = b(j+1). This named lemma avoids asking an SMT
            # heuristic to rediscover the divisibility proof on every goal.
            left_coordinate = coordinates.get(right.args[0])
            right_coordinate = coordinates.get(left.args[0])
            if left_coordinate is None or right_coordinate is None:
                continue
            left_multiple = term("mul", left, term("add", left_coordinate, one))
            right_multiple = term("mul", right, term("add", right_coordinate, one))
            lemmas.append(self._lower(term("ne", left_multiple, right_multiple), symbols))
            rules.add("coprime-interior/1")
        return lemmas

    def check(self, goal, *, timeout_ms=1000):
        """Look for a counterexample, then replay any model with neutral semantics."""
        if not isinstance(goal, Goal):
            raise TypeError("Z3 assistance needs an explicit Goal")
        symbols = {}
        auxiliaries = []
        rules = set()
        try:
            hypotheses = [self._lower_hypothesis(value, symbols, auxiliaries, rules)
                          for value in goal.hypotheses]
            for variable, extent in goal.domain:
                coordinate = self._lower(variable, symbols)
                size = self._lower(extent, symbols)
                hypotheses.append(self.z3.And(coordinate >= 0, coordinate < size))
            proposition = self._lower(goal.proposition, symbols)
            derived = self._domain_lemmas(goal, symbols, rules)
        except _Unsupported as error:
            return Attempt("unsupported", goal.name, self.backend, goal.statement_fingerprint,
                           reason=str(error), rules=tuple(sorted(rules)))

        applied_rules = tuple(sorted(rules))

        consistency = self._solver(timeout_ms)
        consistency.add(*hypotheses)
        state = consistency.check()
        if state == self.z3.unknown:
            return Attempt("unknown", goal.name, self.backend, goal.statement_fingerprint,
                           reason=f"Assumption check: {consistency.reason_unknown()}",
                           rules=applied_rules)
        if state == self.z3.unsat:
            return Attempt("inconsistent_assumptions", goal.name, self.backend,
                           goal.statement_fingerprint,
                           reason="No assignment satisfies the displayed hypotheses and goal domain",
                           rules=applied_rules)

        solver = self._solver(timeout_ms)
        solver.add(*hypotheses, *derived, self.z3.Not(proposition))
        state = solver.check()
        if state == self.z3.unknown:
            return Attempt("unknown", goal.name, self.backend, goal.statement_fingerprint,
                           reason=solver.reason_unknown(), rules=applied_rules)
        if state == self.z3.unsat:
            reason = "Negated goal is unsatisfiable in the supported Z3 integer fragment"
            if applied_rules:
                reason += " after applying the recorded named rules"
            return Attempt("solver_valid", goal.name, self.backend, goal.statement_fingerprint,
                           reason=reason,
                           rules=applied_rules)

        model = solver.model()
        assignments = []
        parameters, coordinates = {}, {}
        for (kind, name), symbol in sorted(symbols.items()):
            interpreted = model.eval(symbol, model_completion=True)
            if not self.z3.is_int_value(interpreted):
                return Attempt("invalid_counterexample", goal.name, self.backend,
                               goal.statement_fingerprint,
                               reason=f"Model value for {kind} {name!r} is not an exact integer",
                               rules=applied_rules)
            value = interpreted.as_long()
            assignments.append((kind, name, str(value)))
            (parameters if kind == "parameter" else coordinates)[name] = value
        reproduced = False
        reason = None
        try:
            assumptions_hold = all(evaluate(value, parameters, coordinates)
                                   for value in goal.hypotheses)
            domain_holds = all(0 <= coordinates[variable.args[0]]
                               < evaluate(extent, parameters, coordinates)
                               for variable, extent in goal.domain)
            reproduced = assumptions_hold and domain_holds and not evaluate(
                goal.proposition, parameters, coordinates)
        except (KeyError, ValueError, ZeroDivisionError, OverflowError) as error:
            reason = f"Neutral replay failed: {error}"
        status = "counterexample" if reproduced else "invalid_counterexample"
        if reason is None:
            reason = ("Exact model independently violates the goal"
                      if reproduced else "Backend model did not violate the neutral Kaleion goal")
        return Attempt(status, goal.name, self.backend, goal.statement_fingerprint,
                       tuple(assignments), reason, reproduced, applied_rules)


def _domain(data):
    if not isinstance(data, list) or len(data) > 16:
        raise ValueError("A statement domain needs at most sixteen dimensions")
    dimensions = []
    for pair in data:
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError("A statement domain needs variable/extent pairs")
        dimensions.append((decode_term(pair[0]), decode_term(pair[1])))
    return tuple(dimensions)


def goals_from_statement(report):
    """Decompose one expanded comparison into visible solver-sized goals.

    Construction obligations are conclusions, never added as hypotheses. Domain
    equality and pointwise equality are separate so missing coverage cannot hide
    behind a value proof. Every goal retains the statement fingerprint.
    """
    if not isinstance(report, dict) or report.get("status") != "conjecture":
        raise ValueError("Proof assistance needs a supported expanded conjecture")
    if report.get("translator") != "kaleion-integer-projection/1":
        raise ValueError("Proof assistance needs an explicitly supported translator version")
    fingerprint = report.get("fingerprint")
    if not isinstance(fingerprint, str) or not _FINGERPRINT.fullmatch(fingerprint):
        raise ValueError("Proof assistance needs the exact statement fingerprint")
    declarations = report.get("hypotheses")
    if (not isinstance(declarations, list) or len(declarations) > 64
            or any(not isinstance(value, dict) or "predicate" not in value
                   for value in declarations)):
        raise ValueError("Expanded statement has malformed hypotheses")
    hypotheses = tuple(decode_term(value["predicate"]) for value in declarations)
    conclusion = report.get("conclusion")
    if (not isinstance(conclusion, dict)
            or not all(name in conclusion for name in ("domains", "left", "right"))
            or not isinstance(conclusion["domains"], dict)
            or not all(name in conclusion["domains"] for name in ("left", "right", "expected"))):
        raise ValueError("Expanded statement has no conclusion")
    domains = {name: _domain(value) for name, value in conclusion["domains"].items()}
    expected = domains["expected"]
    goals = []
    for side in ("left", "right"):
        actual = domains[side]
        if len(actual) != len(expected):
            proposition = Term("literal", (False,), "boolean")
        else:
            equalities = [term("eq", actual_extent, expected_extent)
                          for (_, actual_extent), (_, expected_extent) in zip(actual, expected)]
            proposition = Term("literal", (True,), "boolean")
            for equality in equalities:
                proposition = term("and", proposition, equality)
        goals.append(Goal(f"{side} key domain equals expected domain", proposition,
                          hypotheses, (), fingerprint, "coverage"))
    equality = term("eq", decode_term(conclusion["left"]), decode_term(conclusion["right"]))
    goals.append(Goal("compared integer fields are equal", equality, hypotheses,
                      expected, fingerprint, "comparison"))
    obligations = report.get("obligations")
    if not isinstance(obligations, list) or len(obligations) > 256:
        raise ValueError("Expanded statement has malformed construction obligations")
    for index, obligation in enumerate(obligations):
        if not isinstance(obligation, dict) or not isinstance(obligation.get("reason"), str):
            raise ValueError("Malformed construction obligation")
        goals.append(Goal(f"obligation {index + 1}: {obligation['reason']}",
                          decode_term(obligation["predicate"]), hypotheses,
                          _domain(obligation["domain"]), fingerprint, "obligation"))
    return tuple(goals)


def indicator_order_goal():
    """The backend-independent order lemma used by quotient ownership fields."""
    x, y = Term("parameter", ("x",)), Term("parameter", ("y",))
    left = term("add", term("indicator", term("le", x, y)),
                term("indicator", term("le", y, x)))
    right = term("add", Term("literal", (1,)), term("indicator", term("eq", x, y)))
    return Goal("two weak order indicators count equality twice", term("eq", left, right),
                source="shared integer-order lemma")


def coprime_interior_goal():
    """Coprime rectangle coordinates cannot meet on the interior diagonal."""
    a = Term("parameter", ("a",))
    b = Term("parameter", ("b",))
    i = Term("bound", ("i",))
    j = Term("bound", ("j",))
    one = Term("literal", (1,))
    hypotheses = (
        term("gt", a, one),
        term("gt", b, one),
        term("eq", term("gcd", a, b), one),
    )
    left = term("mul", a, term("add", i, one))
    right = term("mul", b, term("add", j, one))
    domain = ((i, term("sub", b, one)), (j, term("sub", a, one)))
    return Goal("coprime positive rectangle has no interior tie",
                term("ne", left, right), hypotheses, domain,
                source="shared coprime-interior lemma")
