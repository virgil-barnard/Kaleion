"""Optional solver assistance for neutral Kaleion statement terms.

This module owns one backend translation and its result taxonomy. It does not
execute construction graphs, mutate a workspace, or assign kernel-checked proof
status. Z3 is imported only when :class:`Z3Assistant` is constructed, so the
statement and studio modules remain usable without the ``proof`` extra.
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib

# Keep these neutral names importable from this former home for existing callers;
# solver-specific behavior begins with Attempt and Z3Assistant below.
from .goals import (Goal, coprime_interior_goal, decode_term,
                    goals_from_statement, indicator_order_goal)
from .rules import RuleStep, named_rule_plan
from .terms import evaluate


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
    rule_steps: tuple[RuleStep, ...] = ()
    goal_fingerprint: str | None = None

    def data(self):
        value = {
            "status": self.status,
            "goal": self.goal,
            "backend": self.backend,
            "statement_fingerprint": self.statement_fingerprint,
            "goal_fingerprint": self.goal_fingerprint,
            "assignments": [{"kind": kind, "name": name, "value": value}
                            for kind, name, value in self.assignments],
        }
        if self.reason is not None:
            value["reason"] = self.reason
        if self.independently_reproduced is not None:
            value["independently_reproduced"] = self.independently_reproduced
        if self.rules:
            value["rules"] = list(self.rules)
        if self.rule_steps:
            value["rule_steps"] = [step.data() for step in self.rule_steps]
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

    def _lower_bezout(self, step, symbols, auxiliaries):
        bindings = dict(step.bindings)
        left, right = (self._lower(bindings[name], symbols)
                       for name in ("left", "right"))
        index = len(auxiliaries) // 2
        u = self.z3.Int(f"aux:bezout:{index}:u")
        v = self.z3.Int(f"aux:bezout:{index}:v")
        auxiliaries.extend((u, v))
        # Bezout's identity is equivalent to gcd(x, y) = 1 over the integers.
        # The fresh coefficients are solver witnesses, not Kaleion parameters,
        # and therefore never appear in a returned mathematical assignment.
        return left * u + right * v == 1

    def check(self, goal, *, timeout_ms=1000):
        """Look for a counterexample, then replay any model with neutral semantics."""
        if not isinstance(goal, Goal):
            raise TypeError("Z3 assistance needs an explicit Goal")

        def attempt(status, **values):
            return Attempt(status=status, goal=goal.name, backend=self.backend,
                           statement_fingerprint=goal.statement_fingerprint,
                           goal_fingerprint=goal.fingerprint, **values)
        symbols = {}
        auxiliaries = []
        rule_steps = named_rule_plan(goal.hypotheses, goal.domain)
        bezout_by_premise = {
            step.premises[0]: step for step in rule_steps
            if step.rule == "bezout-coprime/1"
        }
        try:
            hypotheses = [
                self._lower_bezout(bezout_by_premise[value], symbols, auxiliaries)
                if value in bezout_by_premise else self._lower(value, symbols)
                for value in goal.hypotheses
            ]
            for variable, extent in goal.domain:
                coordinate = self._lower(variable, symbols)
                size = self._lower(extent, symbols)
                hypotheses.append(self.z3.And(coordinate >= 0, coordinate < size))
            proposition = self._lower(goal.proposition, symbols)
            derived = [self._lower(step.conclusion, symbols) for step in rule_steps
                       if step.rule == "coprime-interior/1"]
        except _Unsupported as error:
            applied_rules = tuple(sorted({step.rule for step in rule_steps}))
            return attempt("unsupported", reason=str(error), rules=applied_rules,
                           rule_steps=rule_steps)

        applied_rules = tuple(sorted({step.rule for step in rule_steps}))

        consistency = self._solver(timeout_ms)
        consistency.add(*hypotheses)
        state = consistency.check()
        if state == self.z3.unknown:
            return attempt("unknown",
                           reason=f"Assumption check: {consistency.reason_unknown()}",
                           rules=applied_rules, rule_steps=rule_steps)
        if state == self.z3.unsat:
            return attempt("inconsistent_assumptions",
                           reason="No assignment satisfies the displayed hypotheses and goal domain",
                           rules=applied_rules, rule_steps=rule_steps)

        solver = self._solver(timeout_ms)
        solver.add(*hypotheses, *derived, self.z3.Not(proposition))
        state = solver.check()
        if state == self.z3.unknown:
            return attempt("unknown", reason=solver.reason_unknown(),
                           rules=applied_rules, rule_steps=rule_steps)
        if state == self.z3.unsat:
            reason = "Negated goal is unsatisfiable in the supported Z3 integer fragment"
            if applied_rules:
                reason += " after applying the recorded named rules"
            return attempt("solver_valid", reason=reason, rules=applied_rules,
                           rule_steps=rule_steps)

        model = solver.model()
        assignments = []
        parameters, coordinates = {}, {}
        for (kind, name), symbol in sorted(symbols.items()):
            interpreted = model.eval(symbol, model_completion=True)
            if not self.z3.is_int_value(interpreted):
                return attempt("invalid_counterexample",
                               reason=f"Model value for {kind} {name!r} is not an exact integer",
                               rules=applied_rules, rule_steps=rule_steps)
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
        return attempt(status, assignments=tuple(assignments), reason=reason,
                       independently_reproduced=reproduced, rules=applied_rules,
                       rule_steps=rule_steps)
