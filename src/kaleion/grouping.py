"""Small authoring records for groups, member order, and coverage.

These records build definitions only. They do not evaluate, draw, or own history.
Existing reductions and bindings do the work, with an ordered-rank operation for
compact predecessor measurements and a requirement operation for checked reuse.
"""

from dataclasses import dataclass, replace

from .api import Collection, Incidence, _key_expr, _named_groups
from .ir import F, Node, choose, expression, vector


@dataclass(frozen=True, eq=False)
class Grouping:
    source: Collection | Incidence
    groups: tuple
    order: tuple = ()

    def __post_init__(self):
        if not isinstance(self.source, (Collection, Incidence)):
            raise TypeError("Group a collection, arrangement, or incidence")
        groups = tuple((name, _key_expr(e)) for name, e in self.groups)
        if tuple(name for name, _ in groups) != tuple(
            name for name, _ in _named_groups(tuple(e for _, e in groups))
        ):
            raise ValueError("Group field names must follow their declared expressions")
        object.__setattr__(self, "groups", groups)
        object.__setattr__(self, "order", tuple(_key_expr(e) for e in self.order))

    def __bool__(self):
        raise TypeError("A grouping has no truth value; construct and evaluate a measurement")

    @property
    def key(self):
        """Retained key expression in a grouped measurement's context."""
        return vector(*(F[name] for name, _ in self.groups)) if len(self.groups) > 1 else F.key

    def count(self):
        return self.source.count(by=tuple(e for _, e in self.groups))

    def sum(self, *, value=F.value):
        return self.source.sum(by=tuple(e for _, e in self.groups), value=value)

    def order_by(self, *fields):
        """Declare a lexicographic order within each group; ties need another field."""
        if not fields:
            raise ValueError("Declare at least one member-order expression")
        return replace(self, order=tuple(_key_expr(f) for f in fields))

    def ranks(self, *, key=F.key):
        """Count strict predecessors, keyed by one unique key per selected item.

        Ranks start at zero. Group/order ties and duplicate output keys fail;
        storage order never supplies an undeclared tiebreaker.
        """
        if not self.order:
            raise ValueError("Declare member order with order_by() before ranks()")
        source = self.source.select() if isinstance(self.source, Incidence) else self.source
        keys = _named_groups(key)
        if not keys:
            raise ValueError("Rank measurements need an explicit item key")
        return Collection(Node("rank", "collection", (source.node,), {
            "groups": self.groups, "order": self.order, "keys": keys,
        }))

    def coverage(self):
        """Measure matches over the source's declared pre-mask group domain."""
        return Coverage(self, self.count())


@dataclass(frozen=True, eq=False)
class Coverage:
    grouping: Grouping
    full_counts: Collection
    key_rule: object = None

    def __post_init__(self):
        if not isinstance(self.grouping, Grouping) or not isinstance(self.full_counts, Collection):
            raise TypeError("Coverage needs a grouping and its count definition")
        if not self.full_counts.same_definition(self.grouping.count()):
            raise ValueError("Coverage counts must come from the declared grouping")
        if self.key_rule is not None:
            object.__setattr__(self, "key_rule", expression(self.key_rule))

    def __bool__(self):
        raise TypeError("Coverage has no truth value; evaluate counts or exactly() checks")

    @property
    def counts(self):
        return (self.full_counts if self.key_rule is None
                else self.full_counts.where(self.key_rule).select())

    @property
    def missing(self):
        """Retained groups with no matching occurrence."""
        return self.counts.where(F.value == 0)

    @property
    def overlaps(self):
        """Retained groups with more than one matching occurrence."""
        return self.counts.where(F.value > 1)

    def exactly(self, expected=1):
        """An incidence of checks, evaluated in the retained-group context."""
        return self.counts.where(F.value == expression(expected))

    def on_keys(self, rule):
        """Explicitly restrict this report using the grouped-count context."""
        rule = expression(rule)
        return replace(self, key_rule=rule if self.key_rule is None else self.key_rule & rule)

    def unique(self, *, value=F.value):
        """Read the sole contributor's integer value after requiring coverage one.

        Duplicate matching occurrences fail even if their values are equal.
        The result retains the weighted reduction's contributor evidence.
        """
        values = self.grouping.sum(value=value)
        if self.key_rule is not None:
            scope = self.full_counts.with_values(choose(self.key_rule, 1, 0))
            key = self.grouping.key
            values = values.where(scope.bind(on=key, key=key) == 1).select()
        return values.require(self.exactly(1), message="Unique assignment requires coverage exactly one")
