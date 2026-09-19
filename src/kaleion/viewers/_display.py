"""Shared presentation policy, independent of Plotly, Pillow, and evaluation."""

from dataclasses import dataclass
from html import escape

import numpy as np

from ..model import IncidenceSnapshot, Snapshot
from ..motion import Frame

BACKGROUND = "#101827"
FOREGROUND = "#e6edf7"
GRID = "#293449"
NEUTRAL = "#48cdb4"
MATCH = "#f5bd59"
MISS = "#61718a"
CHANGING = "#bd9aff"


@dataclass(frozen=True)
class DisplayData:
    positions: np.ndarray
    labels: tuple[str, ...]
    hover: tuple[str, ...]
    colors: tuple[str, ...]
    opacity: np.ndarray
    status: str = "ready"


def _label(value):
    return "∅" if value is None else str(value)


def _pair(before, after, fraction):
    if fraction == 0:
        return _label(before)
    if fraction == 1 or before == after:
        return _label(after)
    return f"{_label(before)} → {_label(after)}"


def _color(before, after, fraction):
    if 0 < fraction < 1 and before != after:
        return CHANGING
    selected = before if fraction == 0 else after
    return NEUTRAL if selected is None else MATCH if selected else MISS


def prepare(value):
    """Retain exact labels and Boolean endpoints; positions alone are floats."""
    if isinstance(value, Frame):
        positions = value.positions
        labels = tuple(_pair(a, b, value.fraction) for a, b in value.label_pairs)
        before = value.matched_before or (None,) * len(labels)
        after = value.matched_after or (None,) * len(labels)
        colors = tuple(_color(a, b, value.fraction) for a, b in zip(before, after))
        hover = tuple(
            f"Value: {escape(label)}<br>Before: {escape(_label(a))}"
            f"<br>After: {escape(_label(b))}<br>Original path: {value.fraction:.3f}"
            f"<br>Incidence: {_pair(m0, m1, value.fraction)}"
            f"<br>Status: {escape(value.status)}"
            for label, (a, b), m0, m1 in zip(labels, value.label_pairs, before, after)
        )
        opacity = value.opacity
        status = value.status
    else:
        incidence = value if isinstance(value, IncidenceSnapshot) else None
        snap = incidence.source if incidence is not None else value
        if not isinstance(snap, Snapshot):
            raise TypeError("View an evaluated Snapshot, IncidenceSnapshot, or Frame")
        if snap.positions is None:
            raise ValueError("This collection has no placement; call .arrange(...) first")
        positions = snap.positions
        labels = tuple(map(str, snap.values))
        mask = incidence.mask if incidence is not None else (None,) * len(snap)
        colors = tuple(NEUTRAL if m is None else MATCH if m else MISS for m in mask)
        hover = tuple(
            f"Value: {escape(label)}"
            + "".join(f"<br>{escape(k)}: {escape(str(v[i]))}" for k, v in snap.fields.items())
            + f"<br>Occurrence: {escape(snap.ids[i])}"
            + (f"<br>Matches: {bool(mask[i])}" if incidence is not None else "")
            for i, label in enumerate(labels)
        )
        opacity = np.ones(len(snap))
        status = "ready"
    # A 1D arrangement is displayed on y=0, without changing its snapshot.
    if positions.shape[1] == 1:
        positions = np.column_stack((positions[:, 0], np.zeros(len(positions))))
    return DisplayData(positions, labels, hover, colors, opacity, status)


def series(samples, labels=None):
    data = tuple(prepare(sample) for sample in samples)
    if not data:
        raise ValueError("Provide at least one evaluated sample")
    if len({d.positions.shape[1] for d in data}) != 1:
        raise ValueError("All samples need the same displayed dimension; place them explicitly")
    labels = tuple(map(str, range(len(data)))) if labels is None else tuple(map(str, labels))
    if len(labels) != len(data):
        raise ValueError("Provide one label for each sample")
    return data, labels


def bounds(data):
    """One fixed extent for the entire playback, including intermediate arcs."""
    points = np.concatenate([d.positions for d in data])
    if not len(points):
        return [(-1.0, 1.0)] * points.shape[1]
    lo, hi = points.min(axis=0), points.max(axis=0)
    pad = np.maximum((hi - lo) * 0.08, 0.65)
    return [(float(a), float(b)) for a, b in zip(lo - pad, hi + pad)]


def rgba(color, alpha):
    rgb = tuple(int(color[i : i + 2], 16) for i in (1, 3, 5))
    return f"rgba({rgb[0]},{rgb[1]},{rgb[2]},{float(alpha):.4f})"
