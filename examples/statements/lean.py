"""Deterministic Lean 4 proposition requests, without proof claims.

This module only translates the supported neutral Kaleion term fragment into a
closed Lean ``Prop`` definition.  It never emits a theorem, axiom, ``sorry``, or
``admit``.  A separate checked backend must prove the generated proposition and
return the exact statement and goal fingerprints.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import re

from .goals import Goal, decode_goal
from .terms import Term


LEAN_REQUEST_SCHEMA = "kaleion-lean-request/1"
LEAN_TRANSLATOR = "kaleion-to-lean4/1"
LEAN_NAMESPACE = "KaleionProofs"
_FINGERPRINT = re.compile(r"[0-9a-f]{64}")
_BINARY = {
    "add": "+", "sub": "-", "mul": "*", "eq": "=", "ne": "≠",
    "lt": "<", "le": "≤", "gt": ">", "ge": "≥", "and": "∧", "or": "∨",
}
_UNSUPPORTED = {"floordiv", "mod", "sum", "table", "abs"}


class UnsupportedLeanTerm(ValueError):
    """The request needs a Lean semantic choice this translator does not own."""


def _walk(value):
    if isinstance(value, Term):
        yield value
        for argument in value.args:
            yield from _walk(argument)
    elif isinstance(value, tuple):
        for item in value:
            yield from _walk(item)


def _symbols(goal):
    terms = [*goal.hypotheses, *(extent for _, extent in goal.domain), goal.proposition]
    parameter_names = sorted({
        node.args[0] for value in terms for node in _walk(value)
        if node.op == "parameter"
    })
    coordinate_names = [variable.args[0] for variable, _ in goal.domain]
    declared = set(coordinate_names)
    free_bounds = sorted({
        node.args[0] for value in terms for node in _walk(value)
        if node.op == "bound" and node.args[0] not in declared
    })
    if free_bounds:
        raise UnsupportedLeanTerm(
            "Lean requests need every bound symbol in the explicit goal domain: "
            + ", ".join(free_bounds)
        )
    parameters = tuple((name, f"p{index}") for index, name in enumerate(parameter_names))
    coordinates = tuple((name, f"x{index}") for index, name in enumerate(coordinate_names))
    return parameters, coordinates


def _render(value, parameters, coordinates):
    op, args = value.op, value.args
    if op in _UNSUPPORTED:
        raise UnsupportedLeanTerm(
            f"Lean translator {LEAN_TRANSLATOR} does not define {op!r} semantics"
        )
    if op == "literal":
        if value.sort == "boolean":
            return "True" if args[0] else "False"
        return f"({args[0]} : ℤ)"
    if op == "parameter":
        return parameters[args[0]]
    if op == "bound":
        try:
            return coordinates[args[0]]
        except KeyError as error:
            raise UnsupportedLeanTerm(
                f"Lean request contains undeclared bound symbol {args[0]!r}"
            ) from error
    if op in _BINARY:
        left = _render(args[0], parameters, coordinates)
        right = _render(args[1], parameters, coordinates)
        return f"({left} {_BINARY[op]} {right})"
    if op == "neg":
        return f"(-{_render(args[0], parameters, coordinates)})"
    if op == "not":
        return f"(¬ {_render(args[0], parameters, coordinates)})"
    if op == "indicator":
        predicate = _render(args[0], parameters, coordinates)
        return f"(if {predicate} then (1 : ℤ) else (0 : ℤ))"
    if op == "gcd":
        left = _render(args[0], parameters, coordinates)
        right = _render(args[1], parameters, coordinates)
        return f"((Int.gcd {left} {right} : Nat) : ℤ)"
    raise UnsupportedLeanTerm(
        f"Lean translator {LEAN_TRANSLATOR} does not support operation {op!r}"
    )


def _closed_proposition(goal, parameters, coordinates):
    parameter_names = dict(parameters)
    coordinate_names = dict(coordinates)
    binders = [lean for _, lean in (*parameters, *coordinates)]
    clauses = [
        _render(value, parameter_names, coordinate_names)
        for value in goal.hypotheses
    ]
    clauses.extend(
        f"((0 : ℤ) ≤ {coordinate_names[variable.args[0]]} ∧ "
        f"{coordinate_names[variable.args[0]]} < "
        f"{_render(extent, parameter_names, coordinate_names)})"
        for variable, extent in goal.domain
    )
    body = _render(goal.proposition, parameter_names, coordinate_names)
    for clause in reversed(clauses):
        body = f"({clause} → {body})"
    if binders:
        body = f"∀ ({' '.join(binders)} : ℤ), {body}"
    return body


@dataclass(frozen=True)
class LeanRequest:
    """One reproducible proposition source awaiting an external Lean proof."""

    goal: Goal
    definition: str
    source: str
    parameters: tuple[tuple[str, str], ...]
    coordinates: tuple[tuple[str, str], ...]

    @property
    def source_sha256(self):
        return sha256(self.source.encode("utf-8")).hexdigest()

    def data(self):
        return {
            "schema": LEAN_REQUEST_SCHEMA,
            "translator": LEAN_TRANSLATOR,
            "statement_fingerprint": self.goal.statement_fingerprint,
            "goal_fingerprint": self.goal.fingerprint,
            "goal": self.goal.data(),
            "definition": self.definition,
            "source_sha256": self.source_sha256,
            "parameters": [
                {"kaleion": kaleion, "lean": lean}
                for kaleion, lean in self.parameters
            ],
            "coordinates": [
                {"kaleion": kaleion, "lean": lean}
                for kaleion, lean in self.coordinates
            ],
            "source": self.source,
        }


def lean_request(goal):
    """Translate one exact goal into an axiom-free closed proposition source."""
    if not isinstance(goal, Goal):
        raise TypeError("Lean translation needs an explicit Goal")
    # Exercise the same strict wire boundary an external checker will receive;
    # hand-built malformed Terms must not bypass theorem-request validation.
    goal = decode_goal(goal.data())
    parameters, coordinates = _symbols(goal)
    proposition = _closed_proposition(goal, parameters, coordinates)
    local_definition = f"kaleionGoal_{goal.fingerprint}"
    definition = f"{LEAN_NAMESPACE}.{local_definition}"
    statement = goal.statement_fingerprint or "none"
    source = (
        "module\n\n"
        "import Mathlib\n\n"
        "set_option autoImplicit false\n\n"
        f"namespace {LEAN_NAMESPACE}\n\n"
        f"/- Kaleion statement: {statement}\n"
        f"   Kaleion goal: {goal.fingerprint}\n"
        "   This definition states a proposition; it is not a proof. -/\n"
        f"public def {local_definition} : Prop :=\n"
        f"  {proposition}\n\n"
        f"end {LEAN_NAMESPACE}\n"
    )
    return LeanRequest(goal, definition, source, parameters, coordinates)


def decode_lean_request(data):
    """Strictly validate a request by regenerating all derived Lean content."""
    required = {
        "schema", "translator", "statement_fingerprint", "goal_fingerprint",
        "goal", "definition", "source_sha256", "parameters", "coordinates",
        "source",
    }
    if not isinstance(data, dict) or set(data) != required:
        raise ValueError("A Lean request needs exactly the version-1 fields")
    if data["schema"] != LEAN_REQUEST_SCHEMA or data["translator"] != LEAN_TRANSLATOR:
        raise ValueError("Unsupported Lean request schema or translator")
    if (not isinstance(data["goal_fingerprint"], str)
            or not _FINGERPRINT.fullmatch(data["goal_fingerprint"])):
        raise ValueError("A Lean request needs an exact goal fingerprint")
    expected = lean_request(decode_goal(data["goal"]))
    if data != expected.data():
        raise ValueError("Lean request does not match its exact regenerated source")
    return expected
