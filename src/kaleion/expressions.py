"""Interpret fields with explicit context, parameters, and a source resolver.

This module owns no graph scheduling or cache. Construction evaluation supplies a
resolver for drivers; captured motion supplies one that rejects external sources.
"""

import numpy as np

from .ir import Expr
from .model import Snapshot
from . import tensor as T
from .indexing import row_keys, align


def _literal(value):
    out = np.asarray(value)
    # All integer arithmetic starts with Python integers, before a ufunc runs.
    return np.asarray(value, dtype=object) if out.dtype.kind in "iu" else out


def evaluate_expression(rule, context, params, resolve, *, length=0, depth=0):
    """Evaluate one expression; errors and eager branch evaluation stay explicit."""
    if depth > 100:
        raise ValueError("Expression depth exceeds budget")
    if not isinstance(rule, Expr):
        return _literal(rule)
    op, args = rule.op, rule.args
    if op == "literal":
        return _literal(args[0])
    if op == "field":
        if args[0] not in context:
            raise KeyError(f"Unbound field {args[0]}")
        return np.asarray(context[args[0]])
    if op == "param":
        if args[0] not in params:
            raise KeyError(f"Unbound parameter {args[0]}")
        return _literal(params[args[0]])

    def ev(expr, ctx=context, n=length):
        return evaluate_expression(expr, ctx, params, resolve, length=n, depth=depth + 1)

    if op in ("scalar", "lookup", "aligned"):
        source = resolve(args[0])
        if not isinstance(source, Snapshot):
            raise ValueError("A driver must supply a collection or arrangement")
        if op in ("scalar", "lookup") and source.values is None:
            raise ValueError("This domain has tuples only; assign integer values before reading contents")
        if op == "scalar":
            if len(source) != 1:
                raise ValueError("scalar() requires exactly one item")
            return _literal(source.values[0])
        if op == "lookup":
            address = T.broadcast(ev(args[1]), length)
            addr = T.exact(address)
            if any(v < 0 or v >= len(source) for v in addr):
                raise IndexError("Substitution address outside table")
            return T.take(source.values, np.asarray(addr, dtype=np.int64))
        on, key, read = args[1:]
        source_ctx = source.context()
        source_keys = row_keys(ev(key, source_ctx, len(source)), len(source))
        target_keys = row_keys(ev(on), length)
        addresses = align(source_keys, target_keys)
        values = ev(read, source_ctx, len(source))
        if values.ndim == 0:
            values = T.broadcast(values, len(source))
        if len(values) != len(source):
            raise ValueError("Driver read shape mismatch")
        return T.take(values, addresses)
    return T.operation(op, [ev(a) for a in args])
