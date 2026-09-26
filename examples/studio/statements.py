"""Comparison-to-statement adapter: author intent, domains, and obligations.

No solver is invoked and no numerical construction is executed. Saved options
are requests, never trusted statements or proof verdicts. Re-expansion uses the
captured definition graph and the versioned translator below.
"""

from hashlib import sha256
import json

from .formulas import formula
from ..statements import Expansion, Unsupported
from ..statements.expansion import Condition
from ..statements.terms import ONE, literal, term, render, domain_text, evaluate


TRANSLATOR = "kaleion-integer-projection/1"
SIGNS = {"+": "add", "-": "sub", "*": "mul", "//": "floordiv", "%": "mod",
         "=": "eq", "≠": "ne", "<": "lt", "≤": "le", ">": "gt", "≥": "ge",
         "and": "and", "or": "or"}


def options_for(options, parameters):
    if not isinstance(options, dict) or set(options) != {"vary", "assumptions", "coprime"}:
        raise ValueError("Give varied parameters, an assumption formula, and coprime pairs")
    vary, assumptions, coprime = (options[k] for k in ("vary", "assumptions", "coprime"))
    if (not isinstance(vary, list) or len(vary) > 16
            or not all(isinstance(v, str) for v in vary)
            or len(set(vary)) != len(vary) or not set(vary) <= parameters.keys()):
        raise ValueError("Vary only distinct declared parameters")
    if not isinstance(assumptions, str) or len(assumptions) > 256:
        raise ValueError("Write at most 256 characters of parameter assumptions")
    if (not isinstance(coprime, list) or len(coprime) > 8
            or any(not isinstance(pair, list) or len(pair) != 2
                   or not all(isinstance(v, str) and v in parameters for v in pair)
                   or pair[0] == pair[1] for pair in coprime)):
        raise ValueError("Coprime assumptions need two different declared parameter names")
    return {"vary": list(vary), "assumptions": assumptions.strip(), "coprime": [list(p) for p in coprime]}


def assumptions_for(options, environment):
    conditions = []
    def lower(spec):
        if "integer" in spec:
            return literal(int(spec["integer"]))
        if "parameter" in spec:
            return environment[spec["parameter"]]
        args = tuple(lower(v) for v in spec["args"])
        op = SIGNS[spec["op"]]
        if op in ("floordiv", "mod"):
            conditions.append(Condition((), term("gt" if op == "mod" else "ne", args[1], literal(0)),
                                        "Assumption expression is defined", "author-assumption"))
        return term(op, *args)
    predicates = []
    if options["assumptions"]:
        predicates.append(lower(formula(options["assumptions"], environment, relation=True)))
    for a, b in options["coprime"]:
        predicates.append(term("eq", term("gcd", environment[a], environment[b]), ONE))
    return predicates, conditions


def captured_truth(predicate, parameters):
    try:
        result = evaluate(predicate, parameters)
        if type(result) is not bool:
            raise ValueError("An assumption must be a predicate")
        return {"satisfied": result}
    except (ValueError, KeyError, ZeroDivisionError, OverflowError) as error:
        return {"satisfied": None, "unavailable": str(error)}


def captured_condition(condition, parameters):
    """Check a quantified side condition at this case, with a finite budget."""
    budget = [100_000]
    def check(dimensions, bindings):
        if not dimensions:
            return evaluate(condition.predicate, parameters, bindings, budget=budget)
        (variable, extent), *tail = dimensions
        size = evaluate(extent, parameters, bindings, budget=budget)
        if size < 0 or size > budget[0]:
            raise ValueError("Invalid or over-budget condition domain")
        return all(check(tail, {**bindings, variable.args[0]: i}) for i in range(size))
    try:
        return {"satisfied": check(condition.dimensions, {})}
    except (ValueError, KeyError, ZeroDivisionError, OverflowError) as error:
        return {"satisfied": None, "unavailable": str(error)}


def comparison_statement(roots, parameters, spec, options):
    """Expand the requested fields, keeping coverage as part of the conclusion.

    Varying applies to explicitly named global parameters only. Local case
    bindings and unrelated equal literals retain their recorded meanings.
    """
    options = options_for(options, parameters)
    expansion = Expansion(parameters, options["vary"])
    assumptions, assumption_conditions = assumptions_for(options, expansion.environment)
    report = {
        "translator": TRANSLATOR, "status": "conjecture", "proof": "not-attempted",
        "options": options,
        "variables": [{"name": k, "domain": "integers"} for k in options["vary"]],
        "fixed": {k: str(parameters[k]) for k in sorted(parameters) if k not in options["vary"]},
        "hypotheses": [{"text": render(p), "predicate": p.data(), **captured_truth(p, parameters)} for p in assumptions],
        "projection": "Exact integer fields and occurrence domains; geometry, motion, and host item budgets are excluded",
        "goal": "For every varied integer parameter satisfying the author hypotheses, establish construction obligations, exact key coverage, and field equality",
        "sources": {role: {"name": spec[key], "node": roots[spec[key]].node.id}
                    for role, key in (("left", "name"), ("right", "right"), ("expected", "expected"))},
        "hypotheses_defined": all(captured_condition(c, parameters)["satisfied"] is True for c in assumption_conditions),
    }
    try:
        left_domain, left = expansion.keyed(roots[spec["name"]], spec["left_by"], spec["left_value"])
        right_domain, right = expansion.keyed(roots[spec["right"]], spec["right_by"], spec["right_value"])
        expected_domain, _ = expansion.keyed(roots[spec["expected"]], spec["expected_by"])
        if len(left_domain) != len(right_domain) or len(left_domain) != len(expected_domain):
            raise ValueError("Comparison key arities must agree")
        domains = {"left": left_domain, "right": right_domain, "expected": expected_domain}
        report["conclusion"] = {
            "domains": {k: [[v.data(), n.data()] for v, n in d] for k, d in domains.items()},
            "left": left.data(), "right": right.data(),
            "key_names": {"left": spec["left_by"], "right": spec["right_by"], "expected": spec["expected_by"]},
            "coverage": "left = right = expected",
        }
        header = ("Vary: " + ", ".join(options["vary"]) + " ∈ ℤ\n" if options["vary"] else "Fixed integer case\n")
        if report["fixed"]:
            header += "Fixed: " + ", ".join(f"{k} = {v}" for k, v in report["fixed"].items()) + "\n"
        header += "Assume: " + ("; ".join(render(p) for p in assumptions) or "no additional hypotheses") + "\n\n"
        report["text"] = (header + "D = " + domain_text(expected_domain)
                          + "\ndom(L) = " + ("D" if left_domain == expected_domain else domain_text(left_domain))
                          + "\ndom(R) = " + ("D" if right_domain == expected_domain else domain_text(right_domain))
                          + "\n\nRequire dom(L) = dom(R) = D"
                          + f"\n∀ k ∈ D,\n  {render(left)}\n  = {render(right)}")
    except Unsupported as error:
        report.update(status="unsupported", blocker=error.data())
    report["obligations"] = [{**c.data(), "captured": captured_condition(c, parameters)}
                             for c in (*assumption_conditions, *expansion.conditions)]
    report["projections"] = expansion.projections
    # Includes exact source definitions/scopes and translator semantics, not a
    # finite verdict. This is an identity for a future proof request, not proof.
    identity = {"translator": TRANSLATOR, "options": options, "parameters": {k: str(v) for k, v in parameters.items()},
                "spec": spec, "roots": {role: roots[spec[key]].node.id
                                        for role, key in (("left", "name"), ("right", "right"), ("expected", "expected"))},
                "hypotheses": [p.data() for p in assumptions], "conclusion": report.get("conclusion"),
                "obligations": [{k: c[k] for k in ("domain", "predicate", "node")} for c in report["obligations"]],
                "unsupported_node": report.get("blocker", {}).get("node")}
    report["fingerprint"] = sha256(json.dumps(identity, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    report["source_nodes"] = list(expansion.nodes)
    return report
