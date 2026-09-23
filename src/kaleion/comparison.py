"""Exact integer-key lookup and finite comparison over captured snapshots.

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
    left_value_field: str = "value"
    right_value_field: str = "value"

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
            "left_value_field": self.left_value_field,
            "right_value_field": self.right_value_field,
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


def _context(snapshot):
    if not isinstance(snapshot, Snapshot):
        raise TypeError("Supply a captured Snapshot, not a definition or incidence")
    # Existing notebook keys read stored attributes, even on manually assembled
    # snapshots whose x/y attribute names overlap placement bindings. Geometry
    # never supplies a key. Intrinsic index/key/value fields extend that contract.
    context = {name: column for name, column in snapshot.context().items()
               if name in {"index", "key", "value"}}
    context.update(snapshot.fields)
    context["value"] = snapshot.values
    return context


def keyed_indices(snapshot, *, keys):
    """Map unique exact integer keys to captured occurrence indices.

    Key names are a nonempty ordered sequence. Duplicate keys fail even when
    values agree. Missing fields fail on empty captures too. Placement is ignored;
    the domain's occurrence values do not participate in key validation.
    """
    context = _context(snapshot)
    keys = _field_names(keys)
    for name in keys:
        if name not in context:
            raise ValueError(f"Missing key field {name!r}")
    data = {}
    for index, row in enumerate(zip(*(context[name] for name in keys))):
        for name, component in zip(keys, row):
            if isinstance(component, bool) or not isinstance(component, Integral):
                raise TypeError(f"Key field {name!r} requires exact integers, got {component!r}")
        key = tuple(int(component) for component in row)
        if key in data:
            raise ValueError(f"Duplicate key {key!r}; occurrences cannot be silently combined")
        data[key] = index
    return data


def keyed_items(snapshot, *, keys, value="value"):
    """Map unique integer keys to (occurrence index, selected integer value)."""
    context = _context(snapshot)
    indices = keyed_indices(snapshot, keys=keys)
    if not isinstance(value, str) or value not in context:
        raise ValueError(f"Missing value field {value!r}")
    data = {}
    for key, index in indices.items():
        item = context[value][index]
        if isinstance(item, bool) or not isinstance(item, Integral):
            raise TypeError(f"Value field {value!r} requires exact integers, got {item!r}")
        data[key] = (index, int(item))
    return data


def keyed_values(snapshot, *, keys, value="value"):
    """Return detached exact values under unique integer keys, ignoring placement."""
    return {key: item for key, (_, item) in keyed_items(snapshot, keys=keys, value=value).items()}


def compare_keyed_values(left, right, *, left_keys, right_keys=None, domain=None,
                         left_value="value", right_value="value"):
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
    left_values = keyed_values(left, keys=left_fields, value=left_value)
    right_values = keyed_values(right, keys=right_fields, value=right_value)
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
                           differences, left_value, right_value)
