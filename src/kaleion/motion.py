"""Presentation paths between captured results. Frames are not arrangements."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping
import numpy as np

from .ir import Expr, expression, param, F
from .model import IncidenceSnapshot
from .expressions import evaluate_expression
from .tensor import readonly, coordinates


@dataclass(frozen=True)
class Motion:
    """A path reads sx/sy/sz, tx/ty/tz and parameter time in [0,1]."""

    path: tuple[Expr, ...] | None = None

    def __post_init__(self):
        if self.path is not None:
            object.__setattr__(self, "path", tuple(map(expression, self.path)))

    @classmethod
    def arc(cls, *, height=1.0, axis=1, dimension=2):
        if not 1 <= dimension <= 3 or not 0 <= axis < dimension:
            raise ValueError("Arc dimension/axis mismatch")
        t = param("time")
        parts = [(1 - t) * F["s" + c] + t * F["t" + c] for c in "xyz"[:dimension]]
        parts[axis] = parts[axis] + 4 * t * (1 - t) * height
        return cls(tuple(parts))

    @classmethod
    def custom(cls, *path):
        return cls(tuple(map(expression, path)))

    def positions(self, start, end, t):
        if self.path is None:
            return (1 - t) * start + t * end
        if len(self.path) != start.shape[1]:
            raise ValueError("Motion dimension mismatch")
        context = {
            **{"s" + c: start[:, i] for i, c in enumerate("xyz"[: start.shape[1]])},
            **{"t" + c: end[:, i] for i, c in enumerate("xyz"[: end.shape[1]])},
            "index": np.arange(len(start), dtype=object),
        }

        def unavailable(_):
            raise ValueError(
                "A motion path uses captured coordinates; external drivers belong in the construction"
            )

        columns = [
            evaluate_expression(
                p, context, {"time": float(t)}, unavailable, length=len(start)
            )
            for p in self.path
        ]
        return coordinates(columns, len(start))


@dataclass(frozen=True, eq=False)
class Frame:
    positions: np.ndarray
    opacity: np.ndarray
    before_ids: tuple[str | None, ...]
    after_ids: tuple[str | None, ...]
    values_before: tuple[int | None, ...]
    values_after: tuple[int | None, ...]
    fraction: float
    status: str = "ready"
    matched_before: tuple[bool | None, ...] = ()
    matched_after: tuple[bool | None, ...] = ()

    def __post_init__(self):
        object.__setattr__(self, "positions", readonly(self.positions, float))
        object.__setattr__(self, "opacity", readonly(self.opacity, float))

    @property
    def label_pairs(self):
        """Discrete labels, never a claim of fractional integer contents."""
        return tuple(zip(self.values_before, self.values_after))


def _items(value):
    return value.source if isinstance(value, IncidenceSnapshot) else value


def _membership(result, ids):
    if not isinstance(result, IncidenceSnapshot):
        return (None,) * len(ids)
    mask = dict(zip(result.source.ids, map(bool, result.mask)))
    return tuple(mask.get(oid) for oid in ids)


@dataclass(frozen=True, eq=False)
class _Tracks:
    """Captured correspondence; only the path's progress changes during playback."""

    start: np.ndarray
    end: np.ndarray
    before_ids: tuple
    after_ids: tuple
    values_before: tuple
    values_after: tuple
    opacity_before: np.ndarray
    opacity_after: np.ndarray
    status: str
    matched_before: tuple
    matched_after: tuple

    def __post_init__(self):
        for name in ("start", "end", "opacity_before", "opacity_after"):
            object.__setattr__(self, name, readonly(getattr(self, name), float))

    def frame(self, motion, fraction):
        return Frame(
            motion.positions(self.start, self.end, fraction),
            (1 - fraction) * self.opacity_before + fraction * self.opacity_after,
            self.before_ids,
            self.after_ids,
            self.values_before,
            self.values_after,
            fraction,
            self.status,
            self.matched_before,
            self.matched_after,
        )


@dataclass(frozen=True, eq=False)
class Transition:
    """Captured endpoints and paths, with correspondence prepared once per root."""

    before: object
    after: object
    motions: Mapping[str, Motion]
    backwards: bool = False
    _tracks_cache: dict = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self):
        object.__setattr__(self, "motions", MappingProxyType(dict(self.motions)))

    def reverse(self):
        reversed_path = Transition(self.before, self.after, self.motions, not self.backwards)
        object.__setattr__(reversed_path, "_tracks_cache", self._tracks_cache)
        return reversed_path

    @property
    def start(self):
        return self.after if self.backwards else self.before

    @property
    def end(self):
        return self.before if self.backwards else self.after

    def _tracks(self, name):
        if name not in self._tracks_cache:
            self._tracks_cache[name] = self._prepare_tracks(name)
        return self._tracks_cache[name]

    def _prepare_tracks(self, name):
        def capture(start, end, bi, ai, bv, av, alpha0, alpha1, status):
            return _Tracks(
                start, end, bi, ai, bv, av, alpha0, alpha1, status,
                _membership(self.before.results.get(name), bi),
                _membership(self.after.results.get(name), ai),
            )

        old = _items(self.before.results.get(name))
        new = _items(self.after.results.get(name))
        failed = name in self.after.errors or name in self.before.errors
        if failed:
            kept = old if old is not None else new
            if kept is None or kept.positions is None:
                return None
            return capture(
                kept.positions,
                kept.positions,
                tuple(kept.ids),
                tuple(kept.ids),
                tuple(kept.values),
                tuple(kept.values),
                np.ones(len(kept)),
                np.ones(len(kept)),
                "failed operation; retained geometry",
            )
        if old is not None and old.positions is None:
            old = None
        if new is not None and new.positions is None:
            new = None
        if old is None and new is None:
            return None
        dimension = (new if new is not None else old).positions.shape[1]
        if old is not None and new is not None and old.positions.shape[1] != dimension:
            raise ValueError(
                "A motion between spatial dimensions needs an explicit projection/embedding first"
            )
        lookup = {} if old is None else {oid: i for i, oid in enumerate(old.ids)}
        captured = {**self.before.evaluated, **self.after.evaluated}
        indexes, resolved = {}, {}

        def ancestor(ref):
            trail, seen, result = [], set(), None
            while old is not None and ref is not None:
                if ref.node == old.node and ref.occurrence in lookup:
                    result = lookup[ref.occurrence]
                    break
                if ref in resolved:
                    result = resolved[ref]
                    break
                if ref in seen:
                    break
                seen.add(ref)
                trail.append(ref)
                snap = _items(captured.get(ref.node))
                if snap is None:
                    break
                if ref.node not in indexes:
                    indexes[ref.node] = {oid: i for i, oid in enumerate(snap.ids)}
                idx = indexes[ref.node].get(ref.occurrence)
                if idx is None:
                    break
                ref = snap.motion_parents[idx]
            for ref in trail:
                resolved[ref] = result
            return result

        starts, ends, bi, ai, bv, av, alpha0, alpha1, used = (
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            set(),
        )
        if new is not None:
            for j, oid in enumerate(new.ids):
                i = lookup.get(oid)
                if i is None:
                    i = ancestor(new.motion_parents[j])
                ends.append(new.positions[j])
                ai.append(oid)
                av.append(new.values[j])
                alpha1.append(1.0)
                if i is None:
                    starts.append(new.positions[j])
                    bi.append(None)
                    bv.append(None)
                    alpha0.append(0.0)
                else:
                    starts.append(old.positions[i])
                    bi.append(old.ids[i])
                    bv.append(old.values[i])
                    alpha0.append(1.0)
                    used.add(i)
        if old is not None:
            for i, oid in enumerate(old.ids):
                if i in used:
                    continue
                starts.append(old.positions[i])
                ends.append(old.positions[i])
                bi.append(oid)
                ai.append(None)
                bv.append(old.values[i])
                av.append(None)
                alpha0.append(1.0)
                alpha1.append(0.0)
        return capture(
            np.asarray(starts, float).reshape(-1, dimension),
            np.asarray(ends, float).reshape(-1, dimension),
            tuple(bi),
            tuple(ai),
            tuple(bv),
            tuple(av),
            np.asarray(alpha0),
            np.asarray(alpha1),
            "ready",
        )

    def validate(self):
        for name in set(self.before.results) | set(self.after.results):
            tracks = self._tracks(name)
            if tracks is None:
                continue
            start, end = tracks.start, tracks.end
            motion = self.motions.get(name, Motion())
            if not np.allclose(
                motion.positions(start, end, 0), start, atol=1e-12, rtol=0
            ) or not np.allclose(
                motion.positions(start, end, 1), end, atol=1e-12, rtol=0
            ):
                raise ValueError(
                    "Motion path must start and end at the captured positions"
                )

    def frame(self, name, t):
        if not np.isfinite(t) or not 0 <= t <= 1:
            raise ValueError("Motion progress must be in [0,1]")
        q = 1 - float(t) if self.backwards else float(t)
        tracks = self._tracks(name)
        if tracks is None:
            return None
        motion = self.motions.get(name, Motion())
        # For a duplicated gather, q=0 may contain coincident tracks. They are
        # display correspondences, not additional mathematical occurrences.
        return tracks.frame(motion, q)
