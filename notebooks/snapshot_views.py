"""Notebook-compatible names for captured integer-key queries; no Plotly."""

from kaleion.comparison import (
    KeyedComparison, KeyedDifference, compare_keyed_values, keyed_values,
)


def rectangular_values(snapshot, *, x, y):
    """Return (xs, ys, rows), with rows[y_index][x_index] and ascending axes.

    x and y name distinct integer key fields, not placement coordinates. Require
    exactly one occurrence per pair in the product of the observed axis labels.
    An absent cell is not a zero measurement. Labels need not be consecutive;
    entirely absent axis labels cannot be inferred. Empty input returns three
    empty lists, without guessing axis extents from shape or other metadata.
    """
    data = keyed_values(snapshot, keys=(x, y))
    xs = sorted({key[0] for key in data})
    ys = sorted({key[1] for key in data})
    if len(data) != len(xs) * len(ys):
        missing = next((a, b) for b in ys for a in xs if (a, b) not in data)
        raise ValueError(f"Incomplete rectangular domain: missing key {missing!r}; absent is not zero")
    return xs, ys, [[data[a, b] for a in xs] for b in ys]
