"""Evaluated data and lineage. Snapshots are independent of expression execution."""

from __future__ import annotations

from dataclasses import dataclass, field, fields as record_fields
from types import MappingProxyType
from typing import Mapping
import numpy as np

from .ir import freeze
from .tensor import readonly, exact
from .measurements import contributors


def _updated(source, changes):
    """Private record update: only a validated source can authorize buffer reuse."""
    names = tuple(f.name for f in record_fields(source))
    unknown = changes.keys() - set(names)
    if unknown:
        raise TypeError(f"Unknown snapshot fields: {', '.join(sorted(unknown))}")
    result = object.__new__(type(source))
    for name in names:
        object.__setattr__(result, name, changes.get(name, getattr(source, name)))
    result._seal(reuse=source)
    return result


def _field_buffer(value):
    given = np.asarray(value)
    out = np.array(given, dtype=object if given.dtype.kind in "iu" else None, copy=True)
    if out.dtype.kind not in "biufUO":
        raise ValueError("Attributes require immutable scalar values")
    if out.dtype.hasobject:
        scalars = (str, int, float, bool, np.integer, np.floating, np.bool_, type(None))
        for i, v in enumerate(out.flat):
            if not isinstance(v, scalars):
                raise ValueError("Attributes require immutable scalar values")
            if isinstance(v, (float, np.floating)) and not np.isfinite(v):
                raise ValueError("Attributes require finite scalar values")
            if isinstance(v, np.generic):
                out.flat[i] = v.item()
    elif out.dtype.kind == "f" and not np.isfinite(out).all():
        raise ValueError("Attributes require finite scalar values")
    out.flags.writeable = False
    return out


def _metadata(value, previous=None):
    if previous is not None and value is previous:
        return previous
    if not isinstance(value, Mapping):
        raise ValueError("Snapshot metadata must be a mapping")
    # Previously sealed members are immutable; a caller's mapping proxy alone
    # is not an ownership guarantee. Freeze every new or changed member.
    previous = {} if previous is None else previous
    return MappingProxyType({
        str(k): previous[str(k)] if str(k) in previous and v is previous[str(k)] else freeze(v)
        for k, v in value.items()
    })


@dataclass(frozen=True, slots=True)
class Ref:
    node: str
    occurrence: str

    def __post_init__(self):
        if not isinstance(self.node, str) or not isinstance(self.occurrence, str):
            raise ValueError("Lineage references require node and occurrence strings")


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
        self._seal()

    def _with_changes(self, **changes):
        """Reuse unchanged owned buffers; copy and validate every changed input."""
        return _updated(self, changes)

    def _seal(self, reuse=None):
        def unchanged(name):
            return reuse is not None and getattr(self, name) is getattr(reuse, name)

        if not isinstance(self.node, str):
            raise ValueError("Snapshot node identity must be a string")
        values = self.values
        if not unchanged("values") or values.flags.writeable:
            values = exact(values)  # exact() returns a fresh, validated allocation.
            values.flags.writeable = False
        if values.ndim != 1:
            raise ValueError("Contents are a flat tensor of scalar integers")
        n = len(values)
        for name in ("ids", "sources", "axes"):
            if not unchanged(name):
                strings = tuple(getattr(self, name))
                if any(not isinstance(v, str) for v in strings):
                    raise ValueError(f"{name} must contain strings")
                if name in ("ids", "axes") and len(set(strings)) != len(strings):
                    raise ValueError(f"{name} must be unique")
                object.__setattr__(self, name, strings)
        if len(self.ids) != n or len(self.sources) != n:
            raise ValueError("Occurrences need unique IDs and source identities")
        object.__setattr__(self, "values", values)
        fields = self.fields
        if not unchanged("fields") or any(v.flags.writeable for v in fields.values()):
            previous = {} if reuse is None else reuse.fields
            fields = MappingProxyType({
                k: v if k in previous and v is previous[k] and not v.flags.writeable
                else _field_buffer(v)
                for k, v in fields.items()
            })
        if any(not isinstance(k, str) for k in fields):
            raise ValueError("Attribute names must be strings")
        if any(v.shape != (n,) for v in fields.values()):
            raise ValueError("Attributes need one scalar per occurrence")
        object.__setattr__(self, "fields", fields)
        if self.positions is not None:
            shared = unchanged("positions") and not self.positions.flags.writeable
            p = self.positions if shared else readonly(self.positions, float)
            if (
                p.ndim != 2
                or p.shape[0] != n
                or not 1 <= p.shape[1] <= 3
                or not shared and not np.isfinite(p).all()
            ):
                raise ValueError("Invalid placement tensor")
            object.__setattr__(self, "positions", p)
        if self.shape is not None and not unchanged("shape"):
            shape = tuple(self.shape)
            if any(not isinstance(v, (int, np.integer)) or isinstance(v, (bool, np.bool_))
                   or v < 0 for v in shape):
                raise ValueError("Logical shape needs nonnegative integer dimensions")
            object.__setattr__(self, "shape", tuple(map(int, shape)))
        if self.shape is not None and (
            len(self.shape) != len(self.axes) or np.prod(self.shape, dtype=object) != n
        ):
            raise ValueError("Logical tensor shape does not match its items")
        if not unchanged("parents"):
            parents = tuple(tuple(group) for group in self.parents) or ((),) * n
            if any(not isinstance(ref, Ref) for group in parents for ref in group):
                raise ValueError("Parents must be occurrence references")
            object.__setattr__(self, "parents", parents)
        if not unchanged("motion_parents"):
            parents = tuple(self.motion_parents) or (None,) * n
            if any(ref is not None and not isinstance(ref, Ref) for ref in parents):
                raise ValueError("Motion parents must be occurrence references or None")
            object.__setattr__(self, "motion_parents", parents)
        if len(self.parents) != n or len(self.motion_parents) != n:
            raise ValueError("Lineage shape mismatch")
        previous = None if reuse is None else reuse.metadata
        object.__setattr__(self, "metadata", _metadata(self.metadata, previous))

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
        return contributors(self.metadata, key)


@dataclass(frozen=True, eq=False, slots=True)
class IncidenceSnapshot:
    node: str
    source: Snapshot
    mask: np.ndarray
    rule: str

    def __post_init__(self):
        self._seal()

    def _with_changes(self, **changes):
        return _updated(self, changes)

    def _seal(self, reuse=None):
        if not isinstance(self.node, str) or not isinstance(self.rule, str):
            raise ValueError("Incidence identity and displayed rule must be strings")
        if not isinstance(self.source, Snapshot):
            raise ValueError("An incidence needs a captured collection or arrangement")
        shared = reuse is not None and self.mask is reuse.mask and not self.mask.flags.writeable
        mask = self.mask if shared else readonly(self.mask, bool)
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
