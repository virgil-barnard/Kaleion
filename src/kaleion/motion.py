"""Presentation paths between captured results. Frames are not arrangements."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .ir import Expr, expression, param, F
from .model import Snapshot, IncidenceSnapshot, Ref
from .evaluate import evaluate_expression
from .tensor import readonly, coordinates


@dataclass(frozen=True)
class Motion:
    """A path reads sx/sy/sz, tx/ty/tz and parameter time in [0,1]."""

    path: tuple[Expr, ...] | None = None

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


@dataclass(frozen=True, eq=False)
class Transition:
    before: object
    after: object
    motions: dict
    backwards: bool = False

    def reverse(self):
        return Transition(self.before, self.after, self.motions, not self.backwards)

    @property
    def start(self):
        return self.after if self.backwards else self.before

    @property
    def end(self):
        return self.before if self.backwards else self.after

    def _tracks(self, name):
        old = _items(self.before.results.get(name))
        new = _items(self.after.results.get(name))
        failed = name in self.after.errors or name in self.before.errors
        if failed:
            kept = old if old is not None else new
            if kept is None or kept.positions is None:
                return None
            return (
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

        def ancestor(ref, seen):
            if old is None or ref is None:
                return None
            if ref.node == old.node and ref.occurrence in lookup:
                return lookup[ref.occurrence]
            token = (ref.node, ref.occurrence)
            if token in seen:
                return None
            seen.add(token)
            snap = _items(captured.get(ref.node))
            if snap is None or ref.occurrence not in snap.ids:
                return None
            idx = snap.ids.index(ref.occurrence)
            return ancestor(snap.motion_parents[idx], seen)

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
                    i = ancestor(new.motion_parents[j], set())
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
        return (
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
            start, end, *_ = tracks
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
        start, end, bi, ai, bv, av, a0, a1, status = tracks
        motion = self.motions.get(name, Motion())
        positions = motion.positions(start, end, q)

        def membership(state, ids):
            result = state.results.get(name)
            if not isinstance(result, IncidenceSnapshot):
                return tuple(None for _ in ids)
            mask = dict(zip(result.source.ids, map(bool, result.mask)))
            return tuple(mask.get(oid) for oid in ids)

        # For a duplicated gather, q=0 may contain coincident tracks. They are
        # display correspondences, not additional mathematical occurrences.
        return Frame(
            positions,
            (1 - q) * a0 + q * a1,
            bi,
            ai,
            bv,
            av,
            q,
            status,
            membership(self.before, bi),
            membership(self.after, ai),
        )
