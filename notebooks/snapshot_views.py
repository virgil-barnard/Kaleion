"""Read-only integer-key adapters shared by lessons 04–05.

These functions read captured snapshots, never definitions or animation frames.
They neither evaluate a construction nor choose a plotting technology. Returned
containers are detached display/inspection data, not new measured arrangements.
"""

from collections.abc import Sequence
from numbers import Integral

from kaleion.model import Snapshot


def keyed_values(snapshot, *, keys):
    """Return {key_tuple: integer_value}, in snapshot occurrence order.

    Declare a nonempty sequence of distinct field names. Keys must be exact
    integers, not booleans, floats, or strings; duplicate tuples are errors even
    when their values agree. A one-field key remains a one-tuple. Missing fields
    fail even on an empty snapshot. Placement and rectangular shape are ignored.
    """
    if not isinstance(snapshot, Snapshot):
        raise TypeError("Supply a captured Snapshot, not a definition or incidence")
    if isinstance(keys, str) or not isinstance(keys, Sequence):
        raise TypeError("keys must be an ordered sequence of field names, not a string or set")
    keys = tuple(keys)
    if not keys or any(not isinstance(name, str) or not name for name in keys):
        raise ValueError("Declare at least one nonempty key-field name")
    if len(set(keys)) != len(keys):
        raise ValueError("Key-field names must be distinct")
    for name in keys:
        if name not in snapshot.fields:
            raise ValueError(f"Missing key field {name!r}")
    data = {}
    for row, value in zip(zip(*(snapshot.fields[name] for name in keys)), snapshot.values):
        for name, component in zip(keys, row):
            if isinstance(component, bool) or not isinstance(component, Integral):
                raise TypeError(f"Key field {name!r} requires exact integers, got {component!r}")
        key = tuple(int(component) for component in row)
        if key in data:
            raise ValueError(f"Duplicate key {key!r}; occurrences cannot be silently combined")
        data[key] = int(value)
    return data


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
