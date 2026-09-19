"""Evaluated data and lineage. Snapshots are independent of expression execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping
import numpy as np

from .ir import freeze
from .tensor import readonly, exact


@dataclass(frozen=True, slots=True)
class Ref:
    node: str
    occurrence: str


@dataclass(frozen=True, eq=False, slots=True)
class Snapshot:
    node: str
    values: np.ndarray
    ids: tuple[str, ...]
    sources: tuple[str, ...]
    fields: Mapping[str, np.ndarray] = field(default_factory=dict)
    positions: np.ndarray | None = None
    axes: tuple[str, ...] = ()
    shape: tuple[int, ...] | None = None
    parents: tuple[tuple[Ref, ...], ...] = ()
    motion_parents: tuple[Ref | None, ...] = ()
    metadata: Mapping = field(default_factory=dict)

    def __post_init__(self):
        values = exact(self.values)
        if values.ndim != 1:
            raise ValueError("Contents are a flat tensor of scalar integers")
        n = len(values)
        if len(self.ids) != n or len(set(self.ids)) != n or len(self.sources) != n:
            raise ValueError("Occurrences need unique IDs and source identities")
        object.__setattr__(self, "values", readonly(values, object))
        fields = {k: readonly(v) for k, v in self.fields.items()}
        if any(v.shape != (n,) for v in fields.values()):
            raise ValueError("Attributes need one scalar per occurrence")
        object.__setattr__(self, "fields", MappingProxyType(fields))
        if self.positions is not None:
            p = readonly(self.positions, float)
            if (
                p.ndim != 2
                or p.shape[0] != n
                or not 1 <= p.shape[1] <= 3
                or not np.isfinite(p).all()
            ):
                raise ValueError("Invalid placement tensor")
            object.__setattr__(self, "positions", p)
        if self.shape is not None and (
            len(self.shape) != len(self.axes) or np.prod(self.shape, dtype=object) != n
        ):
            raise ValueError("Logical tensor shape does not match its items")
        object.__setattr__(self, "parents", self.parents or tuple(() for _ in range(n)))
        object.__setattr__(
            self, "motion_parents", self.motion_parents or tuple(None for _ in range(n))
        )
        if len(self.parents) != n or len(self.motion_parents) != n:
            raise ValueError("Lineage shape mismatch")
        object.__setattr__(self, "metadata", freeze(self.metadata))

    def __len__(self):
        return len(self.values)

    def context(self):
        ctx = dict(self.fields)
        ctx.update(value=self.values, index=np.arange(len(self), dtype=object))
        if self.positions is not None:
            ctx.update(
                {
                    name: self.positions[:, i]
                    for i, name in enumerate("xyz"[: self.positions.shape[1]])
                }
            )
        return ctx

    def contributor_ids(self, key):
        if "contributor_ids" not in self.metadata:
            raise ValueError(
                "Inspect a reduction or its unchanged placement; value transformations have their own input provenance"
            )
        keys = self.metadata.get("keys", ())
        key = key if isinstance(key, tuple) else (key,)
        if key not in keys:
            raise KeyError(key)
        if keys.count(key) != 1:
            raise ValueError(
                "This key has repeated occurrences; inspect the source reduction"
            )
        return self.metadata["contributor_ids"][keys.index(key)]


@dataclass(frozen=True, eq=False, slots=True)
class IncidenceSnapshot:
    node: str
    source: Snapshot
    mask: np.ndarray
    rule: str

    def __post_init__(self):
        mask = readonly(self.mask, bool)
        if mask.shape != (len(self.source),):
            raise ValueError("Incidence shape mismatch")
        object.__setattr__(self, "mask", mask)

    @property
    def cardinality(self):
        return int(self.mask.sum())


def snapshot_dict(value):
    if isinstance(value, IncidenceSnapshot):
        return {
            "type": "incidence",
            "node": value.node,
            "source": snapshot_dict(value.source),
            "mask": value.mask.tolist(),
            "rule": value.rule,
        }
    return {
        "type": "items",
        "node": value.node,
        "values": value.values.tolist(),
        "ids": list(value.ids),
        "sources": list(value.sources),
        "fields": {k: v.tolist() for k, v in value.fields.items()},
        "positions": None if value.positions is None else value.positions.tolist(),
        "axes": list(value.axes),
        "shape": value.shape,
        "parents": [[[r.node, r.occurrence] for r in refs] for refs in value.parents],
        "motion_parents": [
            None if r is None else [r.node, r.occurrence] for r in value.motion_parents
        ],
        "metadata": plain(value.metadata),
    }


def plain(value):
    if isinstance(value, Mapping):
        return {k: plain(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [plain(v) for v in value]
    return value


def snapshot_from_dict(d):
    if d["type"] == "incidence":
        return IncidenceSnapshot(
            d["node"], snapshot_from_dict(d["source"]), d["mask"], d["rule"]
        )
    positions = d["positions"]
    # JSON cannot preserve a zero-row tensor's second dimension on its own.
    if positions == []:
        positions = np.empty((0, d["metadata"].get("dimension", 1)))
    return Snapshot(
        d["node"],
        d["values"],
        tuple(d["ids"]),
        tuple(d["sources"]),
        d["fields"],
        positions,
        tuple(d["axes"]),
        None if d["shape"] is None else tuple(d["shape"]),
        tuple(tuple(Ref(*r) for r in row) for row in d["parents"]),
        tuple(None if r is None else Ref(*r) for r in d["motion_parents"]),
        d["metadata"],
    )
