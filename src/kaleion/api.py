"""Declarative public objects. Methods create definitions; evaluation is explicit."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from .ir import Expr, Node, F, expression, vector, incidence_universe


def _node(value):
    return value.node if isinstance(value, Object) else value


def _key_expr(value):
    if isinstance(value, str):
        return F[value]
    if isinstance(value, (list, tuple)):
        return vector(*(_key_expr(v) for v in value))
    return expression(value)


def _named_groups(by):
    groups = () if by is None else (by,) if isinstance(by, (str, Expr)) else tuple(by)
    named = []
    for n, group in enumerate(groups):
        e = _key_expr(group)
        name = e.args[0] if e.op == "field" else f"group_{n}"
        if name in {"value", "index", "x", "y", "z"}:
            name = f"group_{n}"
        named.append((name, e))
    if len({name for name, _ in named}) != len(named):
        raise ValueError("Group names must be distinct")
    return tuple(named)


def _coordinates(positional, named):
    if not named:
        return positional
    if positional:
        raise TypeError("Use positional coordinates or named x, y, z coordinates")
    names = "xyz"[:len(named)]
    if not 1 <= len(named) <= 3 or set(named) != set(names):
        raise ValueError("Named coordinates must be x, x/y, or x/y/z")
    return tuple(named[k] for k in names)


@dataclass(frozen=True, eq=False)
class Object:
    node: Node

    def evaluate(self, **parameters):
        from .evaluate import Evaluator

        return Evaluator(parameters).get(self.node)

    def with_params(self, **bindings):
        """Bind a local parameter case to this whole definition; evaluate later."""
        return wrap(
            Node(
                "case",
                self.node.kind,
                (self.node,),
                {"bindings": {k: expression(v) for k, v in bindings.items()}},
            )
        )

    def __or__(self, operation):
        if not isinstance(operation, Transform):
            return NotImplemented
        return operation(self)

    def __bool__(self):
        raise TypeError(
            "A construction has no truth value; evaluate or compare explicitly"
        )

    def __eq__(self, other):
        raise TypeError(
            "Compare explicit fields and keys; use same_definition() for definition identity"
        )

    def same_definition(self, other):
        return isinstance(other, Object) and self.node.id == other.node.id

    __hash__ = None


@dataclass(frozen=True, eq=False)
class Collection(Object):
    @staticmethod
    def sequence(length, *, start=1, step=1, name="Sequence"):
        return Collection(
            Node(
                "sequence",
                "collection",
                (),
                {
                    "length": expression(length),
                    "start": expression(start),
                    "step": expression(step),
                    "name": name,
                    "origin": uuid4().hex,
                },
            )
        )

    @staticmethod
    def literal(values, *, keys=None, fields=None, name="Integers"):
        return Collection(
            Node(
                "literal",
                "collection",
                (),
                {
                    "values": tuple(values),
                    "keys": None if keys is None else tuple(keys),
                    "fields": fields or {},
                    "name": name,
                    "origin": uuid4().hex,
                },
            )
        )

    @staticmethod
    def grid(*shape, axes=None, values=None, name="Integer grid"):
        axes = tuple(axes or "ijk"[: len(shape)])
        if (
            len(axes) != len(shape)
            or len(set(axes)) != len(axes)
            or not 1 <= len(shape) <= 3
        ):
            raise ValueError("Choose one to three distinct logical axes")
        if set(axes) & {"value", "index", "key", "x", "y", "z"}:
            raise ValueError(
                "Logical axes cannot shadow built-in value, index, key, or coordinate fields"
            )
        return Collection(
            Node(
                "grid",
                "collection",
                (),
                {
                    "shape": tuple(map(expression, shape)),
                    "axes": axes,
                    "values": F.index + 1 if values is None else expression(values),
                    "name": name,
                    "origin": uuid4().hex,
                },
            )
        )

    @staticmethod
    def tuples(*shape, axes=None, name="Tuples"):
        """A finite indexed domain without numeric contents.

        Indices, identity, relations and counts work without values. Assign
        integer contents explicitly with with_values(); F.value is unavailable
        until then. Grid's existing default filling remains unchanged.
        """
        grid = Collection.grid(*shape, axes=axes, name=name)
        attributes = {k: v for k, v in grid.node.attributes.items() if k != "values"}
        return Collection(Node("tuples", "collection", (), attributes))

    @staticmethod
    def young(partition, *, values=None, name="Young diagram filling"):
        return Collection(
            Node(
                "young",
                "collection",
                (),
                {
                    "partition": tuple(partition),
                    "values": F.index + 1 if values is None else expression(values),
                    "name": name,
                    "origin": uuid4().hex,
                },
            )
        )

    def arrange(self, *coordinates, **named):
        """Declare placement with positional coordinates or explicit x/y/z names."""
        coordinates = _coordinates(coordinates, named)
        return Arrangement(
            Node(
                "place",
                "arrangement",
                (self.node,),
                {"coordinates": tuple(map(expression, coordinates))},
            )
        )

    def with_values(self, rule):
        return wrap(
            Node("values", self.node.kind, (self.node,), {"rule": expression(rule)})
        )

    def annotate(self, **fields):
        if set(fields) & {"value", "index", "x", "y", "z"}:
            raise ValueError("Use with_values/place for reserved attributes")
        return wrap(
            Node(
                "annotate",
                self.node.kind,
                (self.node,),
                {"fields": {k: expression(v) for k, v in fields.items()}},
            )
        )

    def where(self, rule):
        return Lens(expression(rule))(self)

    def bind(self, *, on, key=F.key, read=F.value):
        """Keyed gather from this source into the eventual target's context."""
        return Expr(
            "aligned", (self.node, _key_expr(on), _key_expr(key), expression(read))
        )

    def scalar(self):
        """Explicitly require exactly one integer; useful for constructor arguments."""
        return Expr("scalar", (self.node,))

    def reduce(self, reducer="sum", *, by=None, value=F.value):
        return self.where(True).reduce(reducer, by=by, value=value)

    def sum(self, *, by=None, value=F.value):
        return self.reduce("sum", by=by, value=value)

    def count(self, *, by=None):
        return self.reduce("count", by=by)

    def group_by(self, *keys):
        """Declare retained groups; ordering and measurements are separate choices."""
        from .grouping import Grouping

        return Grouping(self, _named_groups(keys))

    def require(self, condition, *, message="Required incidence check failed"):
        """Pass these items through only when every declared check is true."""
        if not isinstance(condition, Incidence):
            raise TypeError("require() needs an incidence of checks")
        if not isinstance(message, str):
            raise TypeError("A requirement message must be text")
        return wrap(Node("require", self.node.kind, (self.node, condition.node),
                         {"message": message}))

    def gather(self, indices, *, axis=None):
        """Return a collection; placement is deliberately specified afterwards."""
        return Collection(
            Node(
                "gather",
                "collection",
                (self.node,),
                {
                    "indices": (
                        _node(indices)
                        if isinstance(indices, Object)
                        else expression(indices)
                    ),
                    "axis": axis,
                },
            )
        )

    def permute(self, indices, *, axis=None):
        return Collection(
            Node(
                "gather",
                "collection",
                (self.node,),
                {
                    "indices": (
                        _node(indices)
                        if isinstance(indices, Object)
                        else expression(indices)
                    ),
                    "axis": axis,
                    "bijective": True,
                },
            )
        )

    def order_by(self, field=F.value):
        return wrap(
            Node("order", self.node.kind, (self.node,), {"field": expression(field)})
        )

    def tile(self, times, *, axis=None):
        return Collection(
            Node(
                "tile",
                "collection",
                (self.node,),
                {"times": expression(times), "axis": axis},
            )
        )

    def concat(self, other, *, axis=None):
        return Collection(
            Node("concat", "collection", (self.node, other.node), {"axis": axis})
        )

    def pad(self, before=0, after=0, *, value=0, attribute_fill=None):
        """Pad the explicit flattened sequence; extra attribute fill is explicit."""
        return Collection(
            Node(
                "pad",
                "collection",
                (self.node,),
                {
                    "before": expression(before),
                    "after": expression(after),
                    "value": expression(value),
                    "attribute_fill": attribute_fill or {},
                },
            )
        )

    def lookup(self, table, *, address=F.value):
        """Integer positional addresses into a declared substitution table."""
        if not isinstance(table, Collection):
            table = Collection.literal(table, name="Substitution table")
        return self.with_values(Expr("lookup", (table.node, expression(address))))


@dataclass(frozen=True, eq=False)
class Arrangement(Collection):
    @staticmethod
    def points(values, positions, *, keys=None, fields=None, name="Point arrangement"):
        items = Collection.literal(values, keys=keys, fields=fields, name=name)
        return Arrangement(
            Node("positions", "arrangement", (items.node,), {"positions": positions})
        )

    @staticmethod
    def spiral(count, *, initial=1, values=None, name="Rectangular spiral"):
        return Arrangement(
            Node(
                "spiral",
                "arrangement",
                (),
                {
                    "count": expression(count),
                    "initial": expression(initial),
                    "values": F.index + 1 if values is None else expression(values),
                    "name": name,
                    "origin": uuid4().hex,
                },
            )
        )

    @property
    def items(self):
        return Collection(Node("items", "collection", (self.node,), {}))

    def place(self, *coordinates, **named):
        return self.arrange(*coordinates, **named)

    def move(self, displacement):
        return Arrangement(
            Node(
                "move",
                "arrangement",
                (self.node,),
                {"displacement": expression(displacement)},
            )
        )

    def roll(self, *, axis, shift):
        """Cyclically reassign contents to fixed logical slots and positions."""
        return Arrangement(
            Node(
                "roll",
                "arrangement",
                (self.node,),
                {"axis": axis, "shift": expression(shift)},
            )
        )


@dataclass(frozen=True, eq=False)
class Lens:
    rule: Expr

    def __post_init__(self):
        object.__setattr__(self, "rule", expression(self.rule))

    def __call__(self, target):
        return Incidence(
            Node("incidence", "incidence", (target.node,), {"rule": self.rule})
        )

    def __and__(self, other):
        return Lens(self.rule & other.rule)

    def __or__(self, other):
        return Lens(self.rule | other.rule)

    def __invert__(self):
        return Lens(~self.rule)

    def window(self, lower, upper):
        if len(lower) != len(upper) or not 1 <= len(lower) <= 3:
            raise ValueError("Window dimensions must agree")
        rule = self.rule
        for name, lo, hi in zip("xyz", lower, upper):
            rule = rule & (F[name] >= lo) & (F[name] < hi)
        return Lens(rule)


@dataclass(frozen=True, eq=False)
class Incidence(Object):
    """A Boolean relation applied to one declared collection or arrangement."""

    @property
    def universe(self):
        """The collection or arrangement being inspected, including local cases."""
        return wrap(incidence_universe(self.node))

    def _combine(self, other, op):
        if not isinstance(other, Incidence):
            return NotImplemented
        universe = self.universe
        if not universe.same_definition(other.universe):
            raise ValueError(
                "Incidences need the same declared universe, including parameter scope"
            )
        if self.node.op == other.node.op == "incidence":
            # Keep existing definitions compact and their saved identities stable.
            a, b = self.node.attributes["rule"], other.node.attributes["rule"]
            return Lens(a & b if op == "and" else a | b)(universe)
        return Incidence(
            Node("incidence_boolean", "incidence", (self.node, other.node), {"operator": op})
        )

    def __and__(self, other):
        return self._combine(other, "and")

    def __or__(self, other):
        if isinstance(other, Transform):
            return other(self)
        return self._combine(other, "or")

    def __invert__(self):
        if self.node.op == "incidence":
            return Lens(~self.node.attributes["rule"])(self.universe)
        return Incidence(
            Node("incidence_boolean", "incidence", (self.node,), {"operator": "not"})
        )

    def select(self):
        """Retain matched occurrences and their placement, when present."""
        return wrap(Node("select", self.universe.node.kind, (self.node,), {}))

    def reduce(self, reducer="count", *, by=None, value=F.value):
        if reducer not in ("count", "sum", "any"):
            raise ValueError("Reducer must be count, sum, or any")
        named = _named_groups(by)
        return Collection(
            Node(
                "reduce",
                "collection",
                (self.node,),
                {
                    "reducer": reducer,
                    "groups": tuple(named),
                    "value": expression(value),
                },
            )
        )

    def count(self, *, by=None):
        """Count matches per retained key, or over the whole universe."""
        return self.reduce("count", by=by)

    def sum(self, *, by=None, value=F.value):
        """Sum exact integer weights over matches, retaining the chosen keys."""
        return self.reduce("sum", by=by, value=value)

    def any(self, *, by=None):
        return self.reduce("any", by=by)

    def group_by(self, *keys):
        """Retain keys of the pre-mask universe, including its zero groups."""
        from .grouping import Grouping

        return Grouping(self, _named_groups(keys))


@dataclass(frozen=True)
class Transform:
    steps: tuple[tuple[str, tuple], ...]

    def __call__(self, target):
        result = target
        for name, args in self.steps:
            result = getattr(result, name)(*args)
        return result

    def __rshift__(self, other):
        if not isinstance(other, Transform):
            return NotImplemented
        return Transform(self.steps + other.steps)


def Move(displacement):
    return Transform((("move", (expression(displacement),)),))


def Values(rule):
    return Transform((("with_values", (expression(rule),)),))


def Place(*coordinates):
    return Transform((("place", tuple(map(expression, coordinates))),))


def wrap(node):
    return {
        "collection": Collection,
        "arrangement": Arrangement,
        "incidence": Incidence,
    }[node.kind](node)
