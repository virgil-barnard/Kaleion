"""Small CPU tensor kernel boundary. Integer buffers contain Python integers.

Exact object tensors intentionally prioritize semantics over acceleration.
Float64 is used only when a rule explicitly requests real arithmetic/geometry.
"""

from __future__ import annotations

import operator
import math
import numpy as np


def readonly(value, dtype=None):
    out = np.array(value, dtype=dtype, copy=True)
    out.flags.writeable = False
    return out


def exact(value, *, bits=4096):
    out = np.asarray(value, dtype=object)
    for v in out.flat:
        if not isinstance(v, (int, np.integer)) or isinstance(v, (bool, np.bool_)):
            raise ValueError(
                "Integer contents require exact integers; use // for integer quotient"
            )
        if int(v).bit_length() > bits:
            raise ValueError("Integer exceeds the configured bit budget")
    return np.array(out, dtype=object, copy=True)


def size(value, label, maximum, minimum=0):
    a = np.asarray(value)
    if a.ndim != 0:
        raise ValueError(f"{label} must be scalar")
    v = a.item()
    if (
        not isinstance(v, (int, np.integer))
        or isinstance(v, (bool, np.bool_))
        or not minimum <= v <= maximum
    ):
        raise ValueError(f"{label} must be an integer in [{minimum}, {maximum}]")
    return int(v)


def broadcast(value, length, *, boolean=False):
    arr = np.asarray(value)
    if arr.ndim == 0:
        arr = np.full(length, arr.item(), dtype=arr.dtype)
    if arr.shape != (length,):
        raise ValueError(
            f"Expected one value per occurrence ({length},), got {arr.shape}"
        )
    if boolean and arr.dtype != bool:
        if not all(isinstance(v, (bool, np.bool_)) for v in arr.flat):
            raise ValueError("An incidence rule must return Booleans, not numbers")
        arr = arr.astype(bool)
    return arr


def coordinates(columns, length):
    if not 1 <= len(columns) <= 3:
        raise ValueError("A placement needs one, two, or three coordinate expressions")
    out = np.stack([broadcast(c, length) for c in columns], axis=-1).astype(float)
    if not np.isfinite(out).all():
        raise ValueError("Placement must be finite")
    return out


def take(buffer, addresses):
    addr = np.asarray(addresses)
    if addr.dtype.kind not in "iu" or addr.ndim != 1:
        raise ValueError("Gather addresses must be a 1D integer tensor")
    if np.any(addr < 0) or np.any(addr >= len(buffer)):
        raise IndexError("Gather address outside the source; wrapping is explicit")
    return np.take(buffer, addr.astype(np.int64), axis=0)


def segment_sum(values, segments, count):
    out = np.zeros(count, dtype=object)
    np.add.at(out, segments, values)
    return out


def factorize(keys):
    """Stable first-appearance order; bindings use keys, never this storage order."""
    unique, lookup, inverse = [], {}, []
    for key in keys:
        if key not in lookup:
            lookup[key] = len(unique)
            unique.append(key)
        inverse.append(lookup[key])
    return tuple(unique), np.asarray(inverse, dtype=np.int64)


def key_rows(columns, length):
    cols = [broadcast(c, length) for c in columns]
    rows = []
    for row in zip(*cols):
        key = tuple(v.item() if isinstance(v, np.generic) else v for v in row)
        if any(
            isinstance(v, (list, tuple, dict))
            or isinstance(v, float)
            and not np.isfinite(v)
            for v in key
        ):
            raise ValueError("Keys must be finite scalar values")
        rows.append(key)
    return tuple(rows)


def align(source_keys, target_keys):
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


_BINARY = {
    "add": operator.add,
    "sub": operator.sub,
    "mul": operator.mul,
    "div": operator.truediv,
    "floordiv": operator.floordiv,
    "mod": operator.mod,
    "pow": operator.pow,
    "eq": operator.eq,
    "ne": operator.ne,
    "lt": operator.lt,
    "le": operator.le,
    "gt": operator.gt,
    "ge": operator.ge,
}


def operation(op, args):
    arrays = [np.asarray(a) for a in args]
    if op in ("and", "or", "not"):
        if any(
            a.dtype != bool and not all(isinstance(x, (bool, np.bool_)) for x in a.flat)
            for a in arrays
        ):
            raise ValueError("Logical operators require Boolean expressions")
        return {"and": np.logical_and, "or": np.logical_or, "not": np.logical_not}[op](
            *arrays
        )
    if op in ("div", "floordiv", "mod") and np.any(arrays[1] == 0):
        raise ZeroDivisionError("Division or remainder by zero")
    if op == "mod" and (
        np.any(arrays[1] <= 0)
        or any(not isinstance(v, (int, np.integer)) for v in arrays[1].flat)
    ):
        raise ValueError(
            "mod uses a positive integer modulus and least nonnegative residues"
        )
    if op == "pow":
        if any(
            not isinstance(v, (int, np.integer)) or abs(v) > 4096
            for v in arrays[1].flat
        ):
            raise ValueError(
                "Power exponent must be an integer with magnitude at most 4096"
            )
        if any(
            isinstance(v, (int, np.integer)) and int(v).bit_length() > 4096
            for v in arrays[0].flat
        ):
            raise ValueError("Power base exceeds bit budget")
        bases, exponents = np.broadcast_arrays(*arrays)
        if any(
            isinstance(b, (int, np.integer))
            and e > 0
            and max(0, abs(int(b)).bit_length() - 1) * int(e) > 4096
            for b, e in zip(bases.flat, exponents.flat)
        ):
            raise ValueError("Power exceeds integer work budget")
    with np.errstate(all="raise"):
        if op in _BINARY:
            out = _BINARY[op](*arrays)
        elif op == "neg":
            out = -arrays[0]
        elif op == "abs":
            out = np.abs(arrays[0])
        elif op in ("sin", "cos", "sqrt"):
            out = getattr(np, op)(arrays[0].astype(float))
        elif op in ("floor", "ceil"):
            out = np.frompyfunc(getattr(math, op), 1, 1)(arrays[0])
        elif op == "where":
            cond = arrays[0]
            if cond.dtype != bool:
                raise ValueError("choose() requires a Boolean condition")
            out = np.where(*arrays)
        elif op == "vector":
            out = np.stack(np.broadcast_arrays(*arrays), axis=-1)
        else:
            raise ValueError(f"Unsupported expression operation {op}")
    out = np.asarray(out)
    if out.dtype.kind == "f" and not np.isfinite(out).all():
        raise ValueError("Nonfinite expression result")
    if out.dtype == object:
        for v in out.flat:
            if isinstance(v, int) and v.bit_length() > 4096:
                raise ValueError("Integer exceeds bit budget")
            if isinstance(v, float) and not np.isfinite(v):
                raise ValueError("Nonfinite expression result")
    return out
