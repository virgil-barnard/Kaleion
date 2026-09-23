"""A read-only summary of named definition inputs, not a live wiring graph.

Stop at the nearest named definition. Never identify a local-case input with
its unscoped namesake, or an earlier driver with a root that now has its name.
Unshown boundaries remain explicit; occurrence evidence belongs to Inspection.
"""

from collections.abc import Mapping

from kaleion.ir import Expr, Node


def definition_connections(roots):
    names = {}
    for name, obj in roots.items():
        names.setdefault(obj.node.id, []).append(name)
    edges, hidden = [], []
    for target, obj in roots.items():
        seen, found, boundaries = set(), set(), set()

        def visit(node, route="input", *, first=False):
            marker = (node.id, route)
            if marker in seen:
                return
            seen.add(marker)
            if not first and node.id in names:
                for source in names[node.id]:
                    if source != target:
                        found.add((source, route))
                return
            if node.op == "case":
                boundaries.add((node.id, "local parameter case"))
                return
            if route == "read" and not first:
                boundaries.add((node.id, "earlier or unnamed read"))
                return
            if not tuple(node.parents()) and not first:
                boundaries.add((node.id, "unnamed source"))
            for parent in node.inputs:
                visit(parent, route)
            attributes(node.attributes)

        def attributes(value):
            if isinstance(value, Node):
                visit(value, "read")
            elif isinstance(value, Expr):
                attributes(value.args)
            elif isinstance(value, Mapping):
                for item in value.values():
                    attributes(item)
            elif isinstance(value, (tuple, list)):
                for item in value:
                    attributes(item)

        visit(obj.node, first=True)
        edges.extend(dict(source=source, target=target, kind=route)
                     for source, route in sorted(found))
        hidden.extend(dict(target=target, definition=node, reason=reason)
                      for node, reason in sorted(boundaries))
    return dict(edges=edges, boundaries=hidden)
