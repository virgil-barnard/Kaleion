"""Readable declarations and scoped input navigation, without evaluation.

Addresses are paths from an applied root, not names guessed from captured values.
A case's definition input enters its saved subtrace; its binding expressions stay
in the surrounding scope. Missing traces never fall back to a global namesake.
"""

from collections.abc import Mapping
import json

from kaleion.ir import Expr, Node, dependencies, encode
from .views import exact_wire


TITLES = {
    "sequence": "Sequence", "literal": "Integers", "grid": "Grid", "tuples": "Tuples · no values",
    "young": "Young diagram", "spiral": "Rectangular spiral",
    "place": "Arrange", "positions": "Explicit positions", "move": "Move",
    "annotate": "Define fields", "values": "Change values", "incidence": "Relation lens",
    "incidence_boolean": "Combine incidences", "select": "Keep matches",
    "reduce": "Measure", "rank": "Rank", "prefix_sum": "Prefix sum",
    "case": "Local parameter case", "gather": "Gather", "order": "Order",
    "roll": "Roll", "tile": "Tile", "concat": "Concatenate", "pad": "Pad",
    "items": "Underlying collection", "require": "Require a condition",
}
NOTES = {
    "grid": "Axes are ordered logical slots. A Product recipe is stored as Grid, Count and declared reads; expand the inputs to see those operations.",
    "place": "Coordinates change placement. Values and occurrence identity remain separate; existing consumers retain their own input definitions.",
    "move": "Displacement changes placement, not labels or logical addresses.",
    "incidence": "The rule marks occurrences within the declared universe; nonmatches remain part of that universe.",
    "incidence_boolean": "Combine membership in the same declared universe, including parameter scope.",
    "select": "Matches become a new finite universe. Later groups may differ from the original incidence's zero groups.",
    "reduce": "Group measurements retain zero groups from the declared domain. They do not invent missing keys.",
    "rank": "One result per item: count strict predecessors within its group. The current item is excluded; order ties and duplicate item keys fail.",
    "prefix_sum": "One result per item: sum earlier weights within its group. The current item is excluded. Zero and negative weights still contribute; ties and duplicate item keys fail.",
    "case": "Bindings apply to the whole wrapped definition. The definition input uses this local case; binding expressions use the surrounding case.",
    "roll": "Contents move cyclically through fixed logical slots and positions.",
    "gather": "Each declared source address creates a new occurrence with a captured source link. Logical axis fields become destination slots; placement is declared separately.",
    "tile": "Repeat source occurrences along a logical axis or flattened sequence. Copies have distinct identities and retain their original source links.",
    "concat": "Join explicit domains with compatible fields. No padding values or copies are inferred; each result occurrence retains its supplying source.",
}
SIGNS = dict(add="+", sub="−", mul="×", div="/", floordiv="//", mod="%",
             pow="**", eq="=", ne="≠", lt="<", le="≤", gt=">", ge="≥",
             **{"and": "and", "or": "or"})


def _edges(node):
    """Stable direct edge order; do not collapse an input and a scoped read."""
    roles = {"incidence": ("Universe",), "select": ("Incidence",),
             "case": ("Definition in local case",), "require": ("Source", "Condition"),
             "concat": ("First source", "Second source"),
             "incidence_boolean": ("First incidence", "Second incidence")}
    result = [(f"input:{i}", roles.get(node.op, ())[i] if i < len(roles.get(node.op, ()))
               else "Source" if i == 0 else f"Input {i + 1}", child, "input")
              for i, child in enumerate(node.inputs)]
    seen = set()
    for child in dependencies(node.attributes):
        if child.id not in seen:
            seen.add(child.id)
            result.append((f"read:{len(seen) - 1}", "Expression input", child, "read"))
    return result


def _step(node, trace, scopes, edge):
    key, _, child, _ = edge
    if node.op == "case" and key == "input:0":
        record = trace.get(node.id, {})
        return child, record.get("subtrace", {}), (*scopes, node)
    return child, trace, scopes


def _names(state, node, scopes):
    # Even identical integer bindings do not erase a declared local-case boundary.
    return [] if scopes else [name for name, root in state.roots.items() if root.node.id == node.id]


def _label(state, node, scopes):
    names = _names(state, node, scopes)
    if names:
        return " / ".join(names)
    name = node.attributes.get("name")
    title = TITLES.get(node.op, node.op)
    return f"{title} · {name}" if isinstance(name, str) and name and name != title else title


def _brief(state, node, trace, scopes, target):
    record = trace.get(node.id, {})
    capture = record.get("evaluation")
    available = capture in state.evaluated or any(s.node == capture for s in state.results.values())
    names = _names(state, node, scopes)
    return dict(target=target, definition=node.id, operation=node.op, kind=node.kind,
                label=target["root"] if not target["path"] else _label(state, node, scopes), names=names,
                context="Local case input" if scopes else "Current named object" if names else "Earlier or unnamed input",
                status=record.get("status", "unavailable"),
                capture=capture if available else None, extent=record.get("extent"),
                error=record.get("error"))


def describe_construction(state, root, path=()):
    """Describe one definition and direct inputs in an applied captured state.

    Root descriptions can travel with state(). Expanding an input only reads this
    query. It never executes a graph, interprets an expression, or edits history.
    Canonical JSON is text so large integers are not parsed by JavaScript.
    """
    if not isinstance(root, str) or root not in state.roots:
        raise ValueError("Choose a current root to inspect its construction")
    if (not isinstance(path, (list, tuple)) or len(path) > 100
            or any(not isinstance(part, str) for part in path)):
        raise ValueError("Use a bounded construction input path")
    node, trace, scopes = state.roots[root].node, state.provenance.get("trace", {}), ()
    for part in path:
        edge = next((edge for edge in _edges(node) if edge[0] == part), None)
        if edge is None:
            raise ValueError("This input is absent from the selected definition")
        node, trace, scopes = _step(node, trace, scopes, edge)
    target = dict(root=root, path=list(path))
    result = _brief(state, node, trace, scopes, target)
    edges = _edges(node)
    inputs = []
    for edge in edges:
        child, child_trace, child_scopes = _step(node, trace, scopes, edge)
        inputs.append({**_brief(state, child, child_trace, child_scopes,
                               dict(root=root, path=[*path, edge[0]])),
                       "role": edge[1], "route": edge[3]})
    reads, shortened = [], False
    # Formatting is bounded independently of evaluation. The canonical view and
    # ordinary Save retain unfamiliar syntax; formatting never simplifies it.
    remaining = 1200

    def source(child):
        return next(entry for entry in inputs if entry["route"] == "read"
                    and entry["definition"] == child.id)

    def fmt(value, site="", depth=0):
        nonlocal remaining, shortened
        remaining -= 1
        if depth > 24 or remaining < 0:
            shortened = True
            return "…"
        def part(v):
            return fmt(v, site, depth + 1)
        if isinstance(value, Node):
            return source(value)["label"]
        if isinstance(value, Expr):
            op, args = value.op, value.args
            if op == "field" and len(args) == 1:
                return str(args[0])
            if op == "param" and len(args) == 1:
                return "$" + str(args[0])
            if op == "literal" and len(args) == 1:
                return part(args[0])
            if op in SIGNS and len(args) == 2:
                return f"({part(args[0])} {SIGNS[op]} {part(args[1])})"
            if op == "vector":
                return "(" + ", ".join(part(v) for v in args) + ")"
            if op in ("aligned", "scalar", "lookup") and args and isinstance(args[0], Node):
                src = source(args[0])
                read = dict(site=site, mode=op, source=src["label"], target=src["target"])
                if op == "aligned" and len(args) == 4:
                    read.update(on=part(args[1]), key=part(args[2]), value=part(args[3]))
                    rendered = f"read({src['label']}, on={read['on']}, key={read['key']}, value={read['value']})"
                else:
                    rendered = op + "(" + ", ".join(part(v) for v in args) + ")"
                reads.append(read)
                return rendered
            return op + "(" + ", ".join(part(v) for v in args) + ")"
        if isinstance(value, Mapping):
            return "{" + ", ".join(f"{k}: {part(v)}" for k, v in list(value.items())[:16]) + (", …" if len(value) > 16 else "") + "}"
        if isinstance(value, (tuple, list)):
            return "[" + ", ".join(part(v) for v in value[:16]) + (f", … ({len(value)} entries)" if len(value) > 16 else "") + "]"
        return json.dumps(value, ensure_ascii=False, allow_nan=False)

    arguments = []
    def arg(label, value):
        arguments.append(dict(label=label, text=fmt(value, label)))

    def named_keys(label, values):
        if not isinstance(values, tuple) or any(not isinstance(v, tuple) or len(v) != 2 for v in values):
            arg(label, values)
        else:
            arguments.append(dict(label=label, text=", ".join(f"{name} ← {fmt(value, label)}" for name, value in values)))

    a, op = node.attributes, node.op
    if op == "place" and isinstance(a.get("coordinates"), tuple):
        for axis, value in zip("xyz", a["coordinates"]):
            arg(f"{axis} coordinate", value)
    elif op in ("annotate", "case") and isinstance(a.get("fields" if op == "annotate" else "bindings"), Mapping):
        for name, value in a["fields" if op == "annotate" else "bindings"].items():
            arg(f"{'Field' if op == 'annotate' else 'Bind parameter'} {name}", value)
    elif op in ("reduce", "rank", "prefix_sum") and "groups" in a and (op == "reduce" or {"keys", "order"} <= a.keys()):
        arguments.append(dict(label="Reducer", text=str(a.get("reducer", op)).replace("_", " ")))
        named_keys("Group keys (in order)", a["groups"])
        if not a["groups"]:
            arguments[-1]["text"] = "Whole domain · no group keys"
        if op != "reduce":
            arg("Strict member order", a["order"])
            named_keys("Unique item keys", a["keys"])
        if (op == "prefix_sum" or a.get("reducer") == "sum") and "value" in a:
            arg("Contribution weight", a["value"])
    else:
        labels = {"rule": "Membership rule" if op == "incidence" else "Value expression",
                  "shape": "Lengths (axis order)", "axes": "Logical axes (in order)",
                  "values": "Values", "length": "Finite length", "start": "Start", "step": "Step"}
        for key, value in a.items():
            if key not in ("origin", "name"):
                arg(labels.get(key, key.replace("_", " ").capitalize()), value)
    for entry in inputs:
        sites = list(dict.fromkeys(read["site"] for read in reads if read["target"] == entry["target"]))
        if sites:
            entry["role"] = "Read for " + ", ".join(sites)

    record = trace.get(node.id, {})
    canonical = json.dumps(node.definition(), ensure_ascii=False, indent=2, allow_nan=False)
    notes = [NOTES[op]] if op in NOTES else []
    if op not in TITLES:
        notes.append("This constructor has no specialized studio editor. Its actual operation, attributes and inputs remain available here.")
    if shortened:
        notes.append("Long expressions are shortened with …; inspect the canonical declaration for their syntax.")
    if record.get("status") == "ready" and result["capture"] is None:
        notes.append("The trace records success but its result is unavailable; inspection will not recreate it.")
    parameters = record.get("parameters", None if scopes else state.parameters)
    result.update(title=TITLES.get(op, op), arguments=arguments, inputs=inputs, reads=reads,
                  parameters=None if parameters is None else exact_wire(dict(parameters)),
                  local_depth=len(scopes), notes=notes,
                  scope_bindings=[json.dumps(encode(case.attributes.get("bindings", {})),
                                             ensure_ascii=False) for case in scopes],
                  canonical=canonical[:24000], canonical_truncated=len(canonical) > 24000)
    return result
