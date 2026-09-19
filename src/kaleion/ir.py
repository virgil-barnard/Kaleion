"""Immutable expressions and operation definitions; no evaluator or UI here."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import math
from types import MappingProxyType
from typing import Any, Mapping


def freeze(value):
    if isinstance(value, Mapping):
        return MappingProxyType({str(k): freeze(v) for k, v in value.items()})
    if isinstance(value, (list, tuple, range)):
        return tuple(freeze(v) for v in value)
    if hasattr(value, "tolist"):
        return freeze(value.tolist())
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Definitions cannot contain NaN or infinity")
    if isinstance(value, (Expr, Node, str, int, float, bool, type(None))):
        return value
    raise TypeError(f"Unsupported definition value: {type(value).__name__}")


def encode(value):
    if isinstance(value, Node):
        return {"$node": value.id}
    if isinstance(value, Expr):
        return {"$expr": value.op, "args": [encode(v) for v in value.args]}
    if isinstance(value, Mapping):
        return {k: encode(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [encode(v) for v in value]
    return value


def dependencies(value):
    if isinstance(value, Node):
        yield value
    elif isinstance(value, Expr):
        yield from dependencies(value.args)
    elif isinstance(value, Mapping):
        for child in value.values():
            yield from dependencies(child)
    elif isinstance(value, tuple):
        for child in value:
            yield from dependencies(child)


@dataclass(frozen=True, eq=False, slots=True)
class Expr:
    op: str
    args: tuple[Any, ...]

    def __post_init__(self):
        object.__setattr__(self, "args", freeze(self.args))

    def _binary(self, op, other):
        return Expr(op, (self, expression(other)))

    def _reverse(self, op, other):
        return Expr(op, (expression(other), self))

    def __add__(self, other):
        return self._binary("add", other)

    def __radd__(self, other):
        return self._reverse("add", other)

    def __sub__(self, other):
        return self._binary("sub", other)

    def __rsub__(self, other):
        return self._reverse("sub", other)

    def __mul__(self, other):
        return self._binary("mul", other)

    def __rmul__(self, other):
        return self._reverse("mul", other)

    def __truediv__(self, other):
        return self._binary("div", other)

    def __rtruediv__(self, other):
        return self._reverse("div", other)

    def __floordiv__(self, other):
        return self._binary("floordiv", other)

    def __rfloordiv__(self, other):
        return self._reverse("floordiv", other)

    def __mod__(self, other):
        return self._binary("mod", other)

    def __rmod__(self, other):
        return self._reverse("mod", other)

    def __pow__(self, other):
        return self._binary("pow", other)

    def __rpow__(self, other):
        return self._reverse("pow", other)

    def __neg__(self):
        return Expr("neg", (self,))

    def __abs__(self):
        return Expr("abs", (self,))

    def __eq__(self, other):
        return self._binary("eq", other)

    def __ne__(self, other):
        return self._binary("ne", other)

    def __lt__(self, other):
        return self._binary("lt", other)

    def __le__(self, other):
        return self._binary("le", other)

    def __gt__(self, other):
        return self._binary("gt", other)

    def __ge__(self, other):
        return self._binary("ge", other)

    def __and__(self, other):
        return self._binary("and", other)

    def __rand__(self, other):
        return self._reverse("and", other)

    def __or__(self, other):
        return self._binary("or", other)

    def __ror__(self, other):
        return self._reverse("or", other)

    def __invert__(self):
        return Expr("not", (self,))

    def __bool__(self):
        raise TypeError(
            "A symbolic rule has no Python truth value. Use parenthesized &, |, ~; evaluate explicitly."
        )

    __hash__ = None

    def __str__(self):
        if self.op in ("field", "param"):
            return str(self.args[0])
        if self.op == "literal":
            return repr(self.args[0])
        signs = {
            "add": "+",
            "sub": "-",
            "mul": "*",
            "div": "/",
            "floordiv": "//",
            "mod": "%",
            "pow": "**",
            "eq": "==",
            "ne": "!=",
            "lt": "<",
            "le": "<=",
            "gt": ">",
            "ge": ">=",
            "and": "&",
            "or": "|",
        }
        if self.op in signs:
            return f"({self.args[0]} {signs[self.op]} {self.args[1]})"
        if self.op == "aligned":
            return f"align({self.args[0].id}, on={self.args[1]}, key={self.args[2]}, read={self.args[3]})"
        return self.op + "(" + ", ".join(map(str, self.args)) + ")"


def expression(value):
    return value if isinstance(value, Expr) else Expr("literal", (freeze(value),))


def param(name: str):
    if not name or not name.isidentifier():
        raise ValueError("Parameter names must be identifiers")
    return Expr("param", (name,))


class _Fields:
    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        return Expr("field", (name,))

    def __getitem__(self, name):
        return Expr("field", (name,))


F = _Fields()


def vector(*parts):
    return Expr("vector", tuple(expression(p) for p in parts))


def choose(condition, yes, no):
    return Expr("where", tuple(map(expression, (condition, yes, no))))


def sin(value):
    return Expr("sin", (expression(value),))


def cos(value):
    return Expr("cos", (expression(value),))


def sqrt(value):
    return Expr("sqrt", (expression(value),))


def floor(value):
    return Expr("floor", (expression(value),))


def ceil(value):
    return Expr("ceil", (expression(value),))


@dataclass(frozen=True, eq=False, slots=True)
class Node:
    op: str
    kind: str
    inputs: tuple[Node, ...]
    attributes: Mapping[str, Any]
    id: str = ""

    def __post_init__(self):
        if self.kind not in ("collection", "arrangement", "incidence"):
            raise ValueError("Unknown output kind")
        object.__setattr__(self, "inputs", tuple(self.inputs))
        object.__setattr__(self, "attributes", freeze(self.attributes))
        body = self.definition()
        digest = sha256(
            json.dumps(
                body, sort_keys=True, separators=(",", ":"), allow_nan=False
            ).encode()
        ).hexdigest()[:24]
        object.__setattr__(self, "id", "n_" + digest)

    def definition(self):
        return {
            "op": self.op,
            "version": 1,
            "kind": self.kind,
            "inputs": [n.id for n in self.inputs],
            "attributes": encode(self.attributes),
        }

    def parents(self):
        seen = set()
        for n in (*self.inputs, *dependencies(self.attributes)):
            if n.id not in seen:
                seen.add(n.id)
                yield n


def incidence_universe(node: Node) -> Node:
    """The declared source with its parameter cases, without moving predicates.

    Scope order is part of definition identity. This does not infer whether two
    different parameter expressions happen to produce equal finite domains.
    """
    if node.kind != "incidence":
        raise TypeError("Expected an incidence definition")
    if node.op == "incidence":
        source = node.inputs[0]
        if source.kind not in ("collection", "arrangement"):
            raise TypeError("An incidence needs a collection or arrangement universe")
        return source
    if node.op == "case":
        source = incidence_universe(node.inputs[0])
        return Node("case", source.kind, (source,), node.attributes)
    if node.op == "incidence_boolean":
        return incidence_universe(node.inputs[0])
    raise ValueError(f"Unknown incidence operation {node.op}")


def graph(roots: Mapping[str, Node]):
    records = {}
    visiting = set()

    def visit(node):
        if node.id in visiting:
            raise ValueError("Dependency cycle")
        if node.id in records:
            return
        visiting.add(node.id)
        for parent in node.parents():
            visit(parent)
        visiting.remove(node.id)
        records[node.id] = node.definition()

    for root in roots.values():
        visit(root)
    return {"schema": 1, "roots": {k: n.id for k, n in roots.items()}, "nodes": records}


def load_graph(document, *, max_nodes=2000):
    if document.get("schema") != 1:
        raise ValueError("Unsupported graph schema")
    records = document["nodes"]
    if len(records) > max_nodes:
        raise ValueError("Graph exceeds node budget")
    built, visiting = {}, set()

    def decode(value, depth=0):
        if depth > 100:
            raise ValueError("Definition nesting exceeds budget")
        if isinstance(value, dict):
            if "$node" in value:
                return build(value["$node"])
            if "$expr" in value:
                return Expr(
                    value["$expr"], tuple(decode(v, depth + 1) for v in value["args"])
                )
            return {k: decode(v, depth + 1) for k, v in value.items()}
        if isinstance(value, list):
            return tuple(decode(v, depth + 1) for v in value)
        return freeze(value)

    def build(key):
        if key in built:
            return built[key]
        if key in visiting or len(visiting) > 100:
            raise ValueError("Dependency cycle or excessive graph depth")
        visiting.add(key)
        r = records[key]
        if r.get("version") != 1:
            raise ValueError("Unsupported operation version")
        node = Node(
            r["op"],
            r["kind"],
            tuple(build(k) for k in r["inputs"]),
            decode(r["attributes"]),
        )
        if node.id != key:
            raise ValueError("Operation identity does not match its definition")
        visiting.remove(key)
        built[key] = node
        return node

    return {name: build(key) for name, key in document["roots"].items()}
