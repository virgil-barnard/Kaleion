"""Finite group selection over captured data, independent of views and execution."""

from dataclasses import dataclass
from math import prod

from kaleion import F, Incidence
from kaleion.indexing import group_keys, retained_axes_shape
from kaleion.ir import expression
from kaleion.model import IncidenceSnapshot, Snapshot


@dataclass(frozen=True)
class CapturedGroups:
    capture: str
    source: Snapshot
    by: tuple
    keys: tuple
    members: tuple
    matches: tuple
    domain: str

    def lens(self, definition, group):
        """Lower a chosen captured key to a predicate, retaining the universe."""
        if type(group) is not int or not 0 <= group < len(self.keys):
            raise ValueError("Choose a group in the captured grouping")
        rule = expression(True)
        for field, value in zip(self.by, self.keys[group]):
            rule = rule & (F[field] == value)
        if isinstance(definition, Incidence):
            return definition & definition.universe.where(rule)
        return definition.where(rule)


def captured_groups(result, by):
    """Group before the incidence mask; enumerate membership without graph work.

    Result order follows the core domain policy, not a mathematical member order.
    A group reference is the capture, chosen fields, and a position in this query;
    it is not a persistent key across edits or an independently declared domain.
    """
    if (not isinstance(by, (list, tuple)) or any(not isinstance(k, str) for k in by)
            or len(set(by)) != len(by)):
        raise ValueError("Choose distinct grouping fields in declared order")
    incidence = isinstance(result, IncidenceSnapshot)
    source = result.source if incidence else result
    context = source.context()
    shape = retained_axes_shape(source.axes, source.shape, by)
    if shape is not None and prod(shape) > 2000:
        raise ValueError("Captured group browsing exceeds the 2000-group study budget")
    keys, inverse = group_keys([context[k] for k in by], len(source), retained_shape=shape)
    if len(keys) > 2000:
        raise ValueError("Captured group browsing exceeds the 2000-group study budget")
    members, matches = [[] for _ in keys], [[] for _ in keys]
    for i, group in enumerate(inverse):
        members[group].append(i)
        if not incidence or bool(result.mask[i]):
            matches[group].append(i)
    return CapturedGroups(result.node, source, tuple(by), keys,
                          tuple(tuple(g) for g in members), tuple(tuple(g) for g in matches),
                          "whole domain" if not by else "declared axes" if shape is not None else "observed keys")
