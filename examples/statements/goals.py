"""Backend-neutral theorem requests derived from expanded constructions.

Goals contain only neutral Kaleion terms.  Their request fingerprint includes
the parent statement and exact hypotheses, domain, and proposition while
excluding display names and result backends.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re

from .terms import Term, term


GOAL_SCHEMA = "kaleion-goal/1"
_INTEGER = re.compile(r"-?(0|[1-9][0-9]*)")
_FINGERPRINT = re.compile(r"[0-9a-f]{64}")
_DECIMAL_DIGITS = 1235
_BINARY = {"add", "sub", "mul", "floordiv", "mod", "gcd",
           "eq", "ne", "lt", "le", "gt", "ge", "and", "or"}
_UNARY = {"neg", "abs", "indicator", "not"}


def decode_term(data):
    """Validate and reconstruct the version-1 neutral term wire format."""
    if not isinstance(data, dict) or set(data) != {"op", "sort", "args"}:
        raise ValueError("A theorem term needs exactly op, sort, and args")
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
        raise ValueError(f"Theorem requests do not support term operation {op!r}")
    if len(args) != expected or not all(isinstance(value, dict) for value in args):
        raise ValueError(f"{op} needs {expected} term argument(s)")
    decoded = tuple(decode_term(value) for value in args)
    rebuilt = term(op, *decoded)
    if rebuilt.sort != sort:
        raise ValueError(f"Declared sort for {op} does not match its operands")
    return rebuilt


@dataclass(frozen=True)
class Goal:
    """One universally quantified implication, independent of any backend."""

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
        if (self.statement_fingerprint is not None
                and (not isinstance(self.statement_fingerprint, str)
                     or not _FINGERPRINT.fullmatch(self.statement_fingerprint))):
            raise ValueError("A parent statement fingerprint must be a SHA-256 hexadecimal string")
        if not isinstance(self.source, str) or not 0 < len(self.source) <= 160:
            raise ValueError("A goal source needs a bounded label")
        seen = set()
        for variable, extent in self.domain:
            if variable.op != "bound" or variable.sort != "integer" or extent.sort != "integer":
                raise ValueError("Goal domains need integer bound variables and extents")
            if variable.args[0] in seen:
                raise ValueError("Goal domain variables must be distinct")
            seen.add(variable.args[0])

    def request_data(self):
        """Exact request identity, deliberately excluding presentation labels."""
        return {
            "schema": GOAL_SCHEMA,
            "statement_fingerprint": self.statement_fingerprint,
            "hypotheses": [value.data() for value in self.hypotheses],
            "domain": [[variable.data(), extent.data()]
                       for variable, extent in self.domain],
            "proposition": self.proposition.data(),
        }

    @property
    def fingerprint(self):
        encoded = json.dumps(self.request_data(), sort_keys=True,
                             separators=(",", ":"), ensure_ascii=False)
        return sha256(encoded.encode("utf-8")).hexdigest()

    def data(self):
        """Versioned JSON-safe theorem request; not a proof or persisted verdict."""
        return {
            **self.request_data(),
            "goal_fingerprint": self.fingerprint,
            "name": self.name,
            "source": self.source,
        }


def _domain(data):
    if not isinstance(data, list) or len(data) > 16:
        raise ValueError("A statement domain needs at most sixteen dimensions")
    dimensions = []
    for pair in data:
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError("A statement domain needs variable/extent pairs")
        dimensions.append((decode_term(pair[0]), decode_term(pair[1])))
    return tuple(dimensions)


def decode_goal(data):
    """Validate a version-1 theorem request and its semantic fingerprint."""
    required = {"schema", "statement_fingerprint", "hypotheses", "domain",
                "proposition", "goal_fingerprint", "name", "source"}
    if not isinstance(data, dict) or set(data) != required:
        raise ValueError("A theorem request needs exactly the version-1 goal fields")
    if data["schema"] != GOAL_SCHEMA:
        raise ValueError("Unsupported theorem-request schema")
    if not isinstance(data["hypotheses"], list) or len(data["hypotheses"]) > 64:
        raise ValueError("A theorem request needs bounded hypotheses")
    if not isinstance(data["proposition"], dict):
        raise ValueError("A theorem request needs one proposition")
    goal = Goal(
        data["name"],
        decode_term(data["proposition"]),
        tuple(decode_term(value) for value in data["hypotheses"]),
        _domain(data["domain"]),
        data["statement_fingerprint"],
        data["source"],
    )
    if (not isinstance(data["goal_fingerprint"], str)
            or not _FINGERPRINT.fullmatch(data["goal_fingerprint"])
            or data["goal_fingerprint"] != goal.fingerprint):
        raise ValueError("Theorem-request fingerprint does not match its semantics")
    return goal


def goals_from_statement(report):
    """Decompose one expanded comparison into visible backend-sized goals."""
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
