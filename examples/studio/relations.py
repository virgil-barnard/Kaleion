"""Copy a scalar predicate with explicit field bindings, without evaluating it.

A reusable rule is read from a captured incidence, never inferred from its mask.
Local parameters become captured constants in the copy. Definition-valued reads
need a richer binding contract and deliberately remain outside this adapter.
"""

from dataclasses import dataclass
from collections.abc import Mapping
import math

from kaleion import F, Lens
from kaleion.ir import Expr, expression
from kaleion.model import IncidenceSnapshot


BINARY = {"add": "+", "sub": "−", "mul": "×", "div": "/", "floordiv": "div",
          "mod": "mod", "pow": "^", "eq": "=", "ne": "≠", "lt": "<",
          "le": "≤", "gt": ">", "ge": "≥", "and": "and", "or": "or"}
UNARY = {"neg": "−", "abs": "abs", "not": "not"}


@dataclass
class PortableRule:
    rule: Expr
    fields: list
    parameters: dict
    formula: str


def portable_rule(state, name):
    if name not in state.results or not isinstance(state.results[name], IncidenceSnapshot):
        raise ValueError("Choose a successfully captured relation lens")
    node, trace = state.roots[name].node, state.provenance.get("trace", {})
    for _ in range(24):
        if node.op != "case":
            break
        trace = trace.get(node.id, {}).get("subtrace", {})
        node = node.inputs[0]
    if node.op != "incidence":
        raise ValueError("This construction has no single reusable predicate; inspect its inputs")
    record = trace.get(node.id, {})
    if record.get("status") != "ready":
        raise ValueError("The rule's captured parameter scope is unavailable")
    fields, parameters, budget = [], {}, [512]

    def visit(value, depth=0):
        budget[0] -= 1
        if depth > 24 or budget[0] < 0 or not isinstance(value, Expr):
            raise ValueError("This rule exceeds the bounded scalar predicate editor")
        op, args = value.op, value.args
        if op == "literal" and len(args) == 1:
            v = args[0]
            if type(v) not in (int, float, bool) or (type(v) is float and not math.isfinite(v)):
                raise ValueError("Only scalar numeric and Boolean literals can be reused here")
            return value, str(v)
        if op == "field" and len(args) == 1:
            if args[0] not in fields:
                fields.append(args[0])
            return value, args[0]
        if op == "param" and len(args) == 1:
            bindings = record.get("parameters")
            v = bindings.get(args[0]) if isinstance(bindings, Mapping) else None
            if type(v) is not int:
                raise ValueError("A rule parameter lacks a captured integer binding")
            parameters[args[0]] = str(v)
            return expression(v), str(v)
        if (op in BINARY and len(args) == 2) or (op in UNARY and len(args) == 1):
            parts = [visit(v, depth + 1) for v in args]
            formula = (f"({parts[0][1]} {BINARY[op]} {parts[1][1]})" if op in BINARY
                       else f"{UNARY[op]}({parts[0][1]})")
            return Expr(op, tuple(p[0] for p in parts)), formula
        raise ValueError("This rule uses reads or structured inputs that need explicit dependency bindings; inspect its construction")

    rule, formula = visit(node.attributes["rule"])
    return PortableRule(rule, fields, parameters, formula)


def describe_rule(state, name):
    try:
        rule = portable_rule(state, name)
        return dict(available=True, fields=rule.fields, parameters=rule.parameters,
                    formula=rule.formula, capture=state.results[name].node)
    except ValueError as error:
        return dict(available=False, reason=str(error))


def reuse_rule(state, name, target, mapping, capture):
    rule = portable_rule(state, name)
    if capture != state.results[name].node:
        raise ValueError("This rule belongs to an earlier capture; choose it again")
    result = state.results.get(target)
    if result is None or isinstance(result, IncidenceSnapshot):
        raise ValueError("Apply a lens to a ready collection or arrangement")
    target_fields = set(result.context())
    if (not isinstance(mapping, dict) or set(mapping) != set(rule.fields)
            or any(not isinstance(v, str) or v not in target_fields for v in mapping.values())):
        raise ValueError("Map every rule input to a field on the destination")

    def bind(value):
        if value.op == "field":
            return F[mapping[value.args[0]]]
        return Expr(value.op, tuple(bind(a) if isinstance(a, Expr) else a for a in value.args))

    return Lens(bind(rule.rule))(state.roots[target])


def reduction_fields(state, name):
    """Logical axes, or explicit retained keys of a measurement, in declared order."""
    result = state.results.get(name)
    if result is None:
        return []
    source = result.source if isinstance(result, IncidenceSnapshot) else result
    if source.axes:
        return list(source.axes)
    node = state.roots[name].node
    for _ in range(24):
        if node.op not in {"place", "move", "positions", "annotate", "values", "case", "incidence"}:
            break
        node = node.inputs[0]
    if node.op == "reduce":
        return [name for name, _ in node.attributes["groups"] if name in source.context()]
    return []


def reduce_axes(state, name, axes, reducer, weight):
    result = state.results.get(name)
    if result is None:
        raise ValueError("Choose a ready object to total")
    fields = reduction_fields(state, name)
    if (not isinstance(axes, list) or any(not isinstance(a, str) for a in axes)
            or len(set(axes)) != len(axes) or not set(axes) <= set(fields)
            or (fields and not axes)):
        raise ValueError("Choose one or more distinct logical axes to total along")
    retained = [a for a in fields if a not in axes]
    groups = state.roots[name].group_by(*(F[a] for a in retained))
    if reducer == "count":
        measured = groups.count()
    elif reducer == "sum":
        measured = groups.sum(value=weight)
    else:
        raise ValueError("Choose Count matches or Sum weights")
    # Retained fields are keys, not newly invented logical axes. A named placement
    # makes their exact measurements visible and remains ordinary saved mathematics.
    source = result.source if isinstance(result, IncidenceSnapshot) else result
    context = source.context()
    numeric = all(all(type(v) in (int, float, bool) for v in context[a].tolist()) for a in retained)
    return measured.arrange(*(F[a] for a in retained)) if 1 <= len(retained) <= 3 and numeric else measured
