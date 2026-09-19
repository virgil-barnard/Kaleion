"""Checked addresses and stable key domains, independent of item identity.

These functions decide how keys and rectangular coordinates map to flat addresses.
Named operations still decide whether occurrences, placement, and evidence survive.
"""

from math import prod
import numpy as np

from . import tensor as T


def key_rows(columns, length):
    cols = [T.broadcast(c, length) for c in columns]
    rows = []
    for row in zip(*cols):
        key = tuple(v.item() if isinstance(v, np.generic) else v for v in row)
        if any(
            isinstance(v, (list, tuple, dict))
            or isinstance(v, float) and not np.isfinite(v)
            for v in key
        ):
            raise ValueError("Keys must be finite scalar values")
        rows.append(key)
    return tuple(rows)


def row_keys(value, length):
    """Interpret a scalar field or an N-by-d vector field as occurrence keys."""
    a = np.asarray(value)
    if a.ndim <= 1:
        return key_rows([a], length)
    if a.ndim != 2 or a.shape[0] != length:
        raise ValueError("A composite key needs one tuple per occurrence")
    return key_rows([a[:, i] for i in range(a.shape[1])], length)


def factorize(keys):
    """Assign groups in first-appearance order; this is not binding order."""
    unique, lookup, inverse = [], {}, []
    for key in keys:
        if key not in lookup:
            lookup[key] = len(unique)
            unique.append(key)
        inverse.append(lookup[key])
    return tuple(unique), np.asarray(inverse, dtype=np.int64)


def align(source_keys, target_keys):
    """Match each requested key to one source address, with no implicit fill."""
    table = {}
    for i, key in enumerate(source_keys):
        if key in table:
            raise ValueError(
                f"Ambiguous driver key {key}; reduce or disambiguate explicitly"
            )
        table[key] = i
    missing = [key for key in target_keys if key not in table]
    if missing:
        raise KeyError(f"Missing driver key {missing[0]}; no implicit fill")
    return np.asarray([table[key] for key in target_keys], dtype=np.int64)


def group_keys(columns, length, *, retained_shape=None):
    """Return the full key domain and one group address per source occurrence."""
    if not columns:
        return ((),), np.zeros(length, dtype=np.int64)
    rows = key_rows(columns, length)
    if retained_shape is None:
        return factorize(rows)
    keys = tuple(tuple(int(v) for v in row) for row in np.ndindex(retained_shape))
    return keys, align(keys, rows)


def axis_dimension(axes, shape, axis):
    if shape is None or axis not in axes:
        raise ValueError(f"{axis!r} is not a declared rectangular index axis")
    return axes.index(axis)


def grid_fields(shape, axes, *, max_items):
    if prod(shape) > max_items:
        raise ValueError("Shape exceeds item budget")
    indices = np.indices(shape, dtype=np.int64).reshape(len(shape), -1)
    return {name: indices[i].astype(object) for i, name in enumerate(axes)}


def checked_indices(given, bound, *, bijective=False):
    indices = T.exact(given)
    if indices.ndim != 1:
        raise ValueError("Gather indices must be a 1D sequence")
    if any(i < 0 or i >= bound for i in indices):
        raise IndexError("Gather address outside declared axis")
    indices = np.asarray(indices, dtype=np.int64)
    if bijective and (len(indices) != bound or len(set(indices.tolist())) != bound):
        raise ValueError("A permutation requires a bijection")
    return indices


def gather_axis(shape, indices, dimension, *, max_items):
    """Lift an axis address sequence to flat addresses and a destination shape."""
    destination = list(shape)
    destination[dimension] = len(indices)
    destination = tuple(destination)
    if prod(destination) > max_items:
        raise ValueError("Gather exceeds item budget")
    addresses = np.take(np.arange(prod(shape)).reshape(shape), indices, axis=dimension)
    return addresses.ravel(), destination


def roll_axis(shape, shifts, dimension):
    """One cyclic shift per fiber, expressed as a flat source address map."""
    if prod(shape) == 0:
        return np.empty(0, dtype=np.int64)
    shaped = shifts.reshape(shape)
    first = np.take(shaped, 0, axis=dimension)
    if not np.all(shaped == np.expand_dims(first, dimension)):
        raise ValueError("Roll shift must be constant along each shifted fiber")
    extent = shape[dimension]
    stride = prod(shape[dimension + 1:])
    flat = np.arange(prod(shape), dtype=np.int64)
    coordinate = (flat // stride) % extent
    # Reduce exact (possibly huge) shifts before entering fixed-width arithmetic.
    bounded_shift = np.asarray(shifts % extent, dtype=np.int64)
    moved = (coordinate - bounded_shift) % extent
    return flat + (moved - coordinate) * stride


def concat_axis(left_shape, right_shape, dimension):
    if len(left_shape) != len(right_shape) or any(
        a != b for i, (a, b) in enumerate(zip(left_shape, right_shape)) if i != dimension
    ):
        raise ValueError("Non-concatenated axes must agree")
    shape = tuple(a + b if i == dimension else a
                  for i, (a, b) in enumerate(zip(left_shape, right_shape)))
    left_count, right_count = prod(left_shape), prod(right_shape)
    addresses = np.concatenate((
        np.arange(left_count).reshape(left_shape),
        np.arange(left_count, left_count + right_count).reshape(right_shape),
    ), axis=dimension)
    return addresses.ravel(), shape
