"""Read-only integer-key adapters shared by lessons 04–05.

These functions read captured snapshots, never definitions or animation frames.
They neither evaluate a construction nor choose a plotting technology. Returned
containers are detached display/inspection data, not new measured arrangements.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from numbers import Integral

from kaleion.model import Snapshot


@dataclass(frozen=True, slots=True)
class KeyedDifference:
    """One exact left-minus-right comparison on a key present on both sides."""

    key: tuple[int, ...]
    left: int
    right: int
    residual: int

    def to_dict(self):
        return {"key": list(self.key), "left": self.left, "right": self.right,
                "residual": self.residual}


@dataclass(frozen=True, slots=True)
class KeyedComparison:
    """Finite keyed-value equality report; detached from captured evidence."""

    left_fields: tuple[str, ...]
    right_fields: tuple[str, ...]
    domain: tuple[tuple[int, ...], ...]
    explicit_domain: bool
    missing_left: tuple[tuple[int, ...], ...]
    missing_right: tuple[tuple[int, ...], ...]
    unexpected_left: tuple[tuple[int, ...], ...]
    unexpected_right: tuple[tuple[int, ...], ...]
    differences: tuple[KeyedDifference, ...]

    @property
    def nonzero(self):
        return tuple(item for item in self.differences if item.residual != 0)

    @property
    def same_domain(self):
        return not (self.missing_left or self.missing_right or
                    self.unexpected_left or self.unexpected_right)

    @property
    def values_equal_on_common(self):
        return not self.nonzero

    @property
    def holds(self):
        return self.same_domain and self.values_equal_on_common

    def to_dict(self):
        def keys(items):
            return [list(key) for key in items]

        return {
            "kind": "keyed_values",
            "residual": "left - right",
            "left_fields": list(self.left_fields),
            "right_fields": list(self.right_fields),
            "domain": keys(self.domain),
            "explicit_domain": self.explicit_domain,
            "missing_left": keys(self.missing_left),
            "missing_right": keys(self.missing_right),
            "unexpected_left": keys(self.unexpected_left),
            "unexpected_right": keys(self.unexpected_right),
            "differences": [item.to_dict() for item in self.differences],
            "nonzero": [item.to_dict() for item in self.nonzero],
            "same_domain": self.same_domain,
            "values_equal_on_common": self.values_equal_on_common,
            "holds": self.holds,
        }


def _field_names(keys):
    if isinstance(keys, str) or not isinstance(keys, Sequence):
        raise TypeError("keys must be an ordered sequence of field names, not a string or set")
    keys = tuple(keys)
    if not keys or any(not isinstance(name, str) or not name for name in keys):
        raise ValueError("Declare at least one nonempty key-field name")
    if len(set(keys)) != len(keys):
        raise ValueError("Key-field names must be distinct")
    return keys


def _key_tuple(item, width):
    if width == 1 and isinstance(item, Integral) and not isinstance(item, bool):
        item = (item,)
    if isinstance(item, (str, bytes)) or not isinstance(item, Sequence) or len(item) != width:
        raise ValueError(f"Each domain key must have exactly {width} integer component(s)")
    if any(isinstance(value, bool) or not isinstance(value, Integral) for value in item):
        raise TypeError(f"Domain keys require exact integers, got {item!r}")
    return tuple(int(value) for value in item)


def keyed_values(snapshot, *, keys):
    """Return {key_tuple: integer_value}, in snapshot occurrence order.

    Declare a nonempty sequence of distinct field names. Keys must be exact
    integers, not booleans, floats, or strings; duplicate tuples are errors even
    when their values agree. A one-field key remains a one-tuple. Missing fields
    fail even on an empty snapshot. Placement and rectangular shape are ignored.
    """
    if not isinstance(snapshot, Snapshot):
        raise TypeError("Supply a captured Snapshot, not a definition or incidence")
    keys = _field_names(keys)
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


def compare_keyed_values(left, right, *, left_keys, right_keys=None, domain=None):
    """Compare exact values after aligning two snapshots by declared integer keys.

    With no domain, compare over the ordered union of observed keys: left order,
    then new right keys. Supplying a domain makes its order and extent authoritative,
    so keys outside it are unexpected and keys absent on either side stay missing.
    Differences exist only where both sides have a value and always mean left-right.
    This report reads snapshots; it is not a new arrangement or proof object.
    """
    left_fields = _field_names(left_keys)
    right_fields = left_fields if right_keys is None else _field_names(right_keys)
    if len(left_fields) != len(right_fields):
        raise ValueError("Left and right keys need the same number of components")
    left_values = keyed_values(left, keys=left_fields)
    right_values = keyed_values(right, keys=right_fields)
    explicit = domain is not None
    if explicit:
        if isinstance(domain, (str, bytes)) or not isinstance(domain, Sequence):
            raise TypeError("domain must be an ordered sequence of finite integer keys")
        declared = tuple(_key_tuple(item, len(left_fields)) for item in domain)
        if len(set(declared)) != len(declared):
            raise ValueError("Comparison domain keys must be unique")
    else:
        declared = tuple(left_values) + tuple(key for key in right_values if key not in left_values)
    declared_set = set(declared)
    missing_left = tuple(key for key in declared if key not in left_values)
    missing_right = tuple(key for key in declared if key not in right_values)
    unexpected_left = tuple(key for key in left_values if key not in declared_set) if explicit else ()
    unexpected_right = tuple(key for key in right_values if key not in declared_set) if explicit else ()
    differences = tuple(KeyedDifference(key, left_values[key], right_values[key],
                                        left_values[key] - right_values[key])
                        for key in declared if key in left_values and key in right_values)
    return KeyedComparison(left_fields, right_fields, declared, explicit,
                           missing_left, missing_right, unexpected_left, unexpected_right,
                           differences)
