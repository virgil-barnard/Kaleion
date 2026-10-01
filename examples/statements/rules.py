"""Backend-neutral named rules for experimental proof assistance.

Rule recognition is deliberately separate from solver translation.  A rule step
records the exact neutral premises, introduced witnesses, consequence, and a
short explanation.  Backends may translate a recognized step, while a future UI
or checked prover can consume the same plan without importing Z3.
"""

from __future__ import annotations

from dataclasses import dataclass

from .terms import Term, literal, render, term


@dataclass(frozen=True)
class RuleStep:
    """One explicitly named mathematical addition to a backend attempt."""

    rule: str
    title: str
    premises: tuple[Term, ...]
    conclusion: Term
    bindings: tuple[tuple[str, Term], ...] = ()
    witnesses: tuple[str, ...] = ()
    uses: tuple[str, ...] = ()
    explanation: str = ""

    def __post_init__(self):
        if (not isinstance(self.rule, str) or "/" not in self.rule
                or not 0 < len(self.rule) <= 80):
            raise ValueError("A named rule step needs a bounded versioned identifier")
        if not isinstance(self.title, str) or not 0 < len(self.title) <= 160:
            raise ValueError("A named rule step needs a bounded title")
        if self.conclusion.sort != "boolean" or any(p.sort != "boolean" for p in self.premises):
            raise ValueError("Rule premises and conclusion must be predicates")
        names = [name for name, _ in self.bindings]
        if (len(names) != len(set(names)) or any(
                not isinstance(name, str) or not 0 < len(name) <= 80 for name in names)):
            raise ValueError("Rule binding names must be distinct bounded strings")
        if (len(self.witnesses) != len(set(self.witnesses)) or any(
                not isinstance(name, str) or not 0 < len(name) <= 80
                for name in self.witnesses)):
            raise ValueError("Rule witness names must be distinct bounded strings")
        if any(not isinstance(value, Term) for _, value in self.bindings):
            raise ValueError("Rule bindings must contain neutral terms")
        if any(not isinstance(name, str) or not 0 < len(name) <= 80 for name in self.uses):
            raise ValueError("Rule dependencies must be bounded identifiers")
        if not isinstance(self.explanation, str) or len(self.explanation) > 800:
            raise ValueError("A rule explanation must be bounded text")

    @property
    def statement(self):
        body = render(self.conclusion)
        if self.witnesses:
            return f"Choose {' and '.join(self.witnesses)} in ℤ such that {body}."
        return body

    def data(self):
        """Return a stable JSON-safe explanation, not a proof certificate."""
        return {
            "rule": self.rule,
            "title": self.title,
            "premises": [value.data() for value in self.premises],
            "bindings": {name: value.data() for name, value in self.bindings},
            "witnesses": list(self.witnesses),
            "conclusion": self.conclusion.data(),
            "statement": self.statement,
            "uses": list(self.uses),
            "explanation": self.explanation,
        }


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


def _one_less_parameter(value):
    if value.op != "sub":
        return None
    parameter, one = value.args
    if (parameter.op == "parameter" and one.op == "literal"
            and one.sort == "integer" and one.args == (1,)):
        return parameter
    return None


def named_rule_plan(hypotheses, domain):
    """Recognize the narrowly supported arithmetic steps for one goal.

    The plan is pure neutral data.  It does not decide a goal, invoke a backend,
    or claim that the rule implementation has been checked by an external kernel.
    """
    hypotheses = tuple(hypotheses)
    domain = tuple(domain)
    if len(hypotheses) > 64 or len(domain) > 16:
        raise ValueError("Named rule input exceeds its hypothesis or domain budget")
    if any(not isinstance(value, Term) or value.sort != "boolean" for value in hypotheses):
        raise ValueError("Named rules need Boolean hypotheses")
    coordinates = {}
    for variable, extent in domain:
        if variable.op != "bound" or variable.sort != "integer" or extent.sort != "integer":
            raise ValueError("Named rules need integer bound domains")
        parameter = _one_less_parameter(extent)
        if parameter is not None and parameter.args[0] not in coordinates:
            coordinates[parameter.args[0]] = variable

    one = literal(1)
    steps = []
    seen = set()
    for hypothesis in hypotheses:
        operands = _coprime_operands(hypothesis)
        if operands is None:
            continue
        left, right = operands
        signature = ("bezout-coprime/1", left, right)
        if signature not in seen:
            u, v = Term("bound", ("u",)), Term("bound", ("v",))
            bezout = term(
                "eq",
                term("add", term("mul", left, u), term("mul", right, v)),
                one,
            )
            steps.append(RuleStep(
                "bezout-coprime/1",
                "Expose coprimality through Bezout witnesses",
                (hypothesis,),
                bezout,
                (("left", left), ("right", right)),
                ("u", "v"),
                (),
                "For integers, gcd(left, right) = 1 exactly when integer Bezout "
                "coefficients make left*u + right*v = 1.",
            ))
            seen.add(signature)

        if (any(value.op != "parameter" for value in operands) or left == right):
            continue
        left_coordinate = coordinates.get(right.args[0])
        right_coordinate = coordinates.get(left.args[0])
        if left_coordinate is None or right_coordinate is None:
            continue
        signature = ("coprime-interior/1", left, right,
                     left_coordinate, right_coordinate)
        if signature in seen:
            continue
        left_multiple = term("mul", left, term("add", left_coordinate, one))
        right_multiple = term("mul", right, term("add", right_coordinate, one))
        consequence = term("ne", left_multiple, right_multiple)
        steps.append(RuleStep(
            "coprime-interior/1",
            "Exclude a tie inside the coprime rectangle",
            (hypothesis,),
            consequence,
            (("left", left), ("right", right),
             ("left_coordinate", left_coordinate),
             ("right_coordinate", right_coordinate)),
            (),
            ("bezout-coprime/1",),
            "A tie and the Bezout identity would make right divide "
            "left_coordinate + 1, contradicting its strict interior bound.",
        ))
        seen.add(signature)
    return tuple(steps)
