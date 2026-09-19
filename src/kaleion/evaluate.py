"""Bounded reference evaluator. Dependency resolution is independent of display."""

from __future__ import annotations

from hashlib import sha256
import json
from math import prod
import numpy as np

from .ir import Node, incidence_universe
from .expressions import evaluate_expression
from .model import Snapshot, IncidenceSnapshot, Ref
from . import tensor as T
from . import indexing
from . import measurements


class EvaluationError(ValueError):
    pass


_PRIMITIVES = {
    "sequence": ("arange", "broadcast", "multiply", "add"),
    "literal": ("constant",),
    "grid": ("cartesian_indices", "elementwise"),
    "young": ("ragged_indices", "elementwise"),
    "spiral": ("bounded_scan", "concatenate", "elementwise"),
    "place": ("elementwise", "stack"),
    "positions": ("constant",),
    "move": ("keyed_gather_or_broadcast", "add"),
    "values": ("elementwise", "keyed_gather_or_lookup"),
    "annotate": ("elementwise",),
    "items": ("view",),
    "incidence": ("elementwise_predicate",),
    "incidence_boolean": ("scoped_predicates", "elementwise_boolean"),
    "select": ("nonzero", "gather"),
    "reduce": ("factorize_keys", "segment_sum", "nonzero"),
    "gather": ("address_map", "gather"),
    "roll": ("subtract", "mod", "gather"),
    "order": ("stable_argsort", "gather"),
    "tile": ("tile_addresses", "gather"),
    "concat": ("concatenate", "address_map"),
    "pad": ("constant", "concatenate"),
    "case": ("bind_parameters", "evaluate_construction"),
    "rank": ("factorize_keys", "lexicographic_sort", "prefix_ranges"),
    "require": ("all_checks", "view"),
}


class Evaluator:
    def __init__(self, parameters=None, *, max_items=10_000, max_nodes=2000):
        if (
            not isinstance(max_items, int)
            or not 1 <= max_items <= 1_000_000
            or not isinstance(max_nodes, int)
            or not 1 <= max_nodes <= 10_000
        ):
            raise ValueError("Invalid finite evaluator budget")
        self.parameters = dict(parameters or {})
        for name, value in self.parameters.items():
            if (
                not isinstance(name, str)
                or not isinstance(value, (int, float, bool))
                or isinstance(value, float)
                and not np.isfinite(value)
            ):
                raise ValueError("Parameters must be named finite scalars")
        self.max_items, self.max_nodes = max_items, max_nodes
        self.cache, self.errors, self.records, self._active = {}, {}, {}, set()
        self.evaluated = {}
        self.case_id = sha256(
            json.dumps(self.parameters, sort_keys=True, allow_nan=False).encode()
        ).hexdigest()[:16]

    def expr(self, rule, data=None, context=None):
        ctx = data.context() if data is not None else context or {}
        return evaluate_expression(
            rule,
            ctx,
            self.parameters,
            self.get,
            length=len(data) if data is not None else len(ctx.get("index", ())),
        )

    def get(self, node):
        if node.id in self.cache:
            return self.cache[node.id]
        if node.id in self.errors:
            raise EvaluationError(self.errors[node.id])
        if node.id in self._active:
            raise EvaluationError("Dependency cycle")
        if len(self.records) >= self.max_nodes or len(self._active) >= 100:
            raise EvaluationError("Evaluation exceeds node/depth budget")
        self._active.add(node.id)
        self.records[node.id] = {
            "operation": node.op,
            "primitive_families": _PRIMITIVES.get(node.op, ()),
            "parameters": dict(self.parameters),
        }
        try:
            result = self._execute(node)
            n = (
                len(result.source)
                if isinstance(result, IncidenceSnapshot)
                else len(result)
            )
            if n > self.max_items:
                raise ValueError("Result exceeds item budget")
            result = result._with_changes(node=node.id + "@" + self.case_id)
            self.cache[node.id] = result
            self.evaluated[result.node] = result
            self.records[node.id].update(
                status="ready",
                evaluation=result.node,
                extent=n,
                coverage="complete finite requested extent",
            )
            return result
        except (ValueError, TypeError, KeyError, IndexError, ArithmeticError) as e:
            message = f"{node.op} ({node.id}): {e}"
            self.errors[node.id] = message
            self.records[node.id].update(status="failed", error=message)
            raise EvaluationError(message) from e
        finally:
            self._active.remove(node.id)

    def run(self, roots):
        results, errors = {}, {}
        for name, root in roots.items():
            node = root.node if hasattr(root, "node") else root
            try:
                results[name] = self.get(node)
            except EvaluationError as e:
                errors[name] = str(e)
        return results, errors

    def _new(self, node, values, fields, *, positions=None, axes=(), shape=None):
        origin = node.attributes["origin"]
        ids = tuple(f"{origin}:{i}" for i in range(len(values)))
        fields = {"key": np.arange(len(values), dtype=object), **fields}
        meta = {
            "name": node.attributes.get("name", node.op),
            "complete": True,
            "finite": True,
        }
        if positions is not None:
            meta["dimension"] = np.asarray(positions).shape[1]
        return Snapshot(
            node.id,
            values,
            ids,
            ids,
            fields,
            positions,
            tuple(axes),
            shape,
            metadata=meta,
        )

    def _derive(self, node, source, **changes):
        refs = tuple(Ref(source.node, oid) for oid in source.ids)
        base = dict(
            node=node.id, parents=tuple((r,) for r in refs), motion_parents=refs
        )
        base.update(changes)
        return source._with_changes(**base)

    def _index(
        self,
        node,
        source,
        addresses,
        *,
        preserve_ids=False,
        fields=None,
        placement="drop",
        shape=None,
        axes=(),
    ):
        addresses = np.asarray(addresses, dtype=np.int64)
        if len(addresses) > self.max_items:
            raise ValueError("Gather exceeds item budget")
        values = T.take(source.values, addresses)
        ids = tuple(
            source.ids[j] if preserve_ids else f"{node.id}:{i}"
            for i, j in enumerate(addresses)
        )
        refs = tuple(Ref(source.node, source.ids[j]) for j in addresses)
        attrs = {k: T.take(v, addresses) for k, v in source.fields.items()}
        if fields is not None:
            attrs.update(fields)
        if placement not in ("drop", "gather", "fixed"):
            raise ValueError("Unknown placement policy")
        pos = None
        if source.positions is not None:
            if placement == "gather":
                pos = T.take(source.positions, addresses)
            elif placement == "fixed":
                pos = source.positions
        metadata = {**measurements.reindex(source.metadata, addresses), "operation": node.op}
        return source._with_changes(
            node=node.id,
            values=values,
            ids=ids,
            sources=tuple(source.sources[j] for j in addresses),
            fields=attrs,
            positions=pos,
            axes=tuple(axes),
            shape=shape,
            parents=tuple((r,) for r in refs),
            motion_parents=refs,
            metadata=metadata,
        )

    def _execute(self, node):
        a, op = node.attributes, node.op
        if op == "sequence":
            n = T.size(self.expr(a["length"]), "Length", self.max_items)
            values = np.arange(n, dtype=object) * self.expr(a["step"]) + self.expr(
                a["start"]
            )
            return self._new(
                node, values, {"s": np.arange(n, dtype=object)}, axes=("s",), shape=(n,)
            )
        if op == "literal":
            if len(a["values"]) > self.max_items:
                raise ValueError("Literal exceeds item budget")
            fields = dict(a["fields"])
            if a["keys"] is not None:
                fields["key"] = np.asarray(a["keys"], dtype=object)
            if set(fields) & {"value", "index", "x", "y", "z", "s"}:
                raise ValueError("Attributes shadow reserved bindings")
            fields["s"] = np.arange(len(a["values"]), dtype=object)
            return self._new(
                node, a["values"], fields, axes=("s",), shape=(len(a["values"]),)
            )
        if op == "grid":
            shape = tuple(
                T.size(self.expr(v), "Axis size", self.max_items) for v in a["shape"]
            )
            fields = indexing.grid_fields(shape, a["axes"], max_items=self.max_items)
            ctx = {**fields, "index": np.arange(prod(shape), dtype=object)}
            values = T.broadcast(self.expr(a["values"], context=ctx), prod(shape))
            return self._new(node, values, fields, axes=a["axes"], shape=shape)
        if op == "young":
            partition = tuple(
                T.size(v, "Row length", self.max_items) for v in a["partition"]
            )
            if sum(partition) > self.max_items or any(
                x < y for x, y in zip(partition, partition[1:])
            ):
                raise ValueError(
                    "A Young diagram needs a nonincreasing partition within the item budget"
                )
            i = np.repeat(np.arange(len(partition)), partition).astype(object)
            j = np.asarray([j for n in partition for j in range(n)], dtype=object)
            ctx = {"i": i, "j": j, "index": np.arange(len(i), dtype=object)}
            return self._new(
                node,
                T.broadcast(self.expr(a["values"], context=ctx), len(i)),
                {"i": i, "j": j},
                axes=("i", "j"),
            )
        if op == "spiral":
            return self._spiral(node)
        if op == "case":
            bindings = {}
            for k, rule in a["bindings"].items():
                v = self.expr(rule)
                if v.ndim:
                    raise ValueError(
                        "A constructor parameter needs a scalar; reduce explicitly"
                    )
                bindings[k] = v.item()
            child = Evaluator(
                {**self.parameters, **bindings},
                max_items=self.max_items,
                max_nodes=self.max_nodes,
            )
            result = child.get(node.inputs[0])
            self.records[node.id].update(bindings=bindings, subtrace=child.records)
            if len(self.evaluated) + len(child.evaluated) > self.max_nodes:
                raise ValueError("Nested cases exceed node budget")
            self.evaluated.update(child.evaluated)
            if isinstance(result, IncidenceSnapshot):
                return result._with_changes(node=node.id)
            return self._derive(node, result)
        if op not in _PRIMITIVES:
            raise ValueError(f"Unregistered operation {op}")
        if op == "require":
            checks = self.get(node.inputs[1])
            if not isinstance(checks, IncidenceSnapshot):
                raise TypeError("A requirement needs an incidence of checks")
            failed = np.flatnonzero(~checks.mask)
            if len(failed):
                keys = checks.source.metadata.get("keys")
                examples = ([keys[i] for i in failed[:3]] if keys is not None
                            else [checks.source.fields["key"][i] for i in failed[:3]])
                raise ValueError(f"{a['message']}: {len(failed)} failing keys; examples {examples}")
            source = self.get(node.inputs[0])
            if not isinstance(source, Snapshot):
                raise TypeError("A requirement passes through integer items")
            return self._derive(node, source)
        source = self.get(node.inputs[0])
        if op == "incidence_boolean":
            operator = a["operator"]
            if operator not in ("and", "or", "not") or len(node.inputs) != (
                1 if operator == "not" else 2
            ):
                raise ValueError("Invalid incidence Boolean operation")
            if not isinstance(source, IncidenceSnapshot):
                raise TypeError("Boolean composition needs incidences")
            if operator == "not":
                mask, rule = ~source.mask, f"not({source.rule})"
            else:
                left = incidence_universe(node.inputs[0])
                right = incidence_universe(node.inputs[1])
                if left.id != right.id:
                    raise ValueError(
                        "Incidences need the same declared universe, including parameter scope"
                    )
                other = self.get(node.inputs[1])
                if source.source.ids != other.source.ids:
                    raise ValueError("Incidence universe occurrences do not agree")
                mask = (
                    source.mask & other.mask
                    if operator == "and"
                    else source.mask | other.mask
                )
                sign = "&" if operator == "and" else "|"
                rule = f"({source.rule} {sign} {other.rule})"
            return IncidenceSnapshot(node.id, source.source, mask, rule)
        if op == "incidence":
            return IncidenceSnapshot(
                node.id,
                source,
                T.broadcast(self.expr(a["rule"], source), len(source), boolean=True),
                str(a["rule"]),
            )
        if op == "reduce":
            return self._reduce(node, source)
        if op == "select":
            return self._index(
                node,
                source.source,
                np.flatnonzero(source.mask),
                preserve_ids=True,
                placement="gather" if node.kind == "arrangement" else "drop",
            )
        if not isinstance(source, Snapshot):
            raise ValueError("This operation needs integer items")
        if op == "items":
            return self._derive(node, source, positions=None)
        if op == "rank":
            return self._rank(node, source)
        if op == "values":
            metadata = measurements.changed_values(source.metadata, source.node)
            return self._derive(
                node,
                source,
                values=T.broadcast(self.expr(a["rule"], source), len(source)),
                metadata=metadata,
            )
        if op == "annotate":
            fields = {
                **source.fields,
                **{
                    name: T.broadcast(self.expr(rule, source), len(source))
                    for name, rule in a["fields"].items()
                },
            }
            if source.shape and set(a["fields"]) & set(source.axes):
                raise ValueError("Logical index axes are changed with index operations")
            return self._derive(node, source, fields=fields)
        if op in ("place", "positions", "move"):
            if op == "place":
                pos = T.coordinates(
                    [self.expr(e, source) for e in a["coordinates"]], len(source)
                )
            elif op == "positions":
                pos = np.asarray(a["positions"], dtype=float)
            else:
                if source.positions is None:
                    raise ValueError("Move needs an arrangement")
                delta = np.asarray(self.expr(a["displacement"], source), dtype=float)
                if delta.shape not in (
                    (source.positions.shape[1],),
                    source.positions.shape,
                ):
                    raise ValueError(
                        "Displacement needs a vector, or one vector per occurrence"
                    )
                pos = source.positions + delta
            return self._derive(
                node,
                source,
                positions=pos,
                metadata={**source.metadata, "dimension": pos.shape[1]},
            )
        if op == "order":
            values = T.broadcast(self.expr(a["field"], source), len(source))
            return self._index(
                node,
                source,
                np.argsort(values, kind="stable"),
                preserve_ids=True,
                placement="gather" if node.kind == "arrangement" else "drop",
            )
        if op in ("gather", "tile"):
            axis = a["axis"]
            dim = None if axis is None else indexing.axis_dimension(source.axes, source.shape, axis)
            bound = len(source) if dim is None else source.shape[dim]
            if op == "tile":
                times = T.size(self.expr(a["times"]), "Repeat count", self.max_items)
                if len(source) * times > self.max_items:
                    raise ValueError("Tiling exceeds item budget")
                indices = np.tile(np.arange(bound), times)
            else:
                given = a["indices"]
                indices = (
                    self.get(given).values
                    if isinstance(given, Node)
                    else self.expr(given)
                )
                indices = indexing.checked_indices(indices, bound, bijective=a.get("bijective", False))
            if dim is None:
                return self._index(node, source, indices)
            address, shape = indexing.gather_axis(source.shape, indices, dim, max_items=self.max_items)
            return self._index(
                node,
                source,
                address,
                fields=indexing.grid_fields(shape, source.axes, max_items=self.max_items),
                shape=shape,
                axes=source.axes,
            )
        if op == "roll":
            dim = indexing.axis_dimension(source.axes, source.shape, a["axis"])
            if source.positions is None:
                raise ValueError("Roll needs a placed index domain")
            if len(source) == 0:
                return self._derive(node, source)
            shifts = T.exact(T.broadcast(self.expr(a["shift"], source), len(source)))
            address = indexing.roll_axis(source.shape, shifts, dim)
            result = self._index(
                node,
                source,
                address,
                preserve_ids=True,
                placement="fixed",
                fields=indexing.grid_fields(source.shape, source.axes, max_items=self.max_items),
                shape=source.shape,
                axes=source.axes,
            )
            return result._with_changes(
                metadata={
                    **result.metadata,
                    "dimension": source.positions.shape[1],
                    "roll_axis": a["axis"],
                    "roll_shifts": shifts.tolist(),
                },
            )
        if op == "concat":
            return self._concat(node, source, self.get(node.inputs[1]))
        if op == "pad":
            return self._pad(node, source)
        raise ValueError(f"Unsupported operation {op}")

    def _rank(self, node, source):
        a = node.attributes
        if not a["order"] or not a["keys"]:
            raise ValueError("Rank needs member order and unique item keys")
        groups = (indexing.key_rows([self.expr(e, source) for _, e in a["groups"]], len(source))
                  if a["groups"] else ((),) * len(source))
        order = indexing.key_rows([self.expr(e, source) for e in a["order"]], len(source))
        keys = indexing.key_rows([self.expr(e, source) for _, e in a["keys"]], len(source))
        if len(set(keys)) != len(keys):
            raise ValueError("Rank item keys must be unique; choose an explicit identifying key")
        inverse, members, ranks = indexing.ordered_groups(groups, order)
        ids = tuple(f"{node.id}:key:{json.dumps(key, separators=(',', ':'))}" for key in keys)
        fields = {name: np.asarray([key[i] for key in keys], dtype=object)
                  for i, (name, _) in enumerate(a["keys"])}
        fields.setdefault("key", np.asarray([key[0] for key in keys], dtype=object)
                          if len(a["keys"]) == 1 else np.arange(len(keys), dtype=object))
        # Anchor lineage identifies the item being ranked. The counted predecessors
        # are a separate compact record, expanded only by contributor_ids(key).
        parents = tuple((Ref(source.node, oid),) for oid in source.ids)
        return Snapshot(node.id, ranks, ids, ids, fields, parents=parents, metadata={
            "reducer": "rank", "counted": "strict predecessors", "keys": keys,
            "population": tuple(len(members[g]) for g in inverse),
            "contributor_prefixes": {
                "version": 1,
                "groups": tuple(tuple(source.ids[i] for i in group) for group in members),
                "ranges": tuple((int(g), int(rank)) for g, rank in zip(inverse, ranks)),
            },
            "universe": source.node,
            "formula": "Count strict predecessors within declared groups, ordered by "
                       + ", ".join(str(e) for e in a["order"]),
            "complete": True, "finite": True,
        })

    def _reduce(self, node, incidence):
        a = node.attributes
        source = incidence.source
        groups = a["groups"]
        retained_shape = None
        if groups and source.shape is not None and all(
            e.op == "field" and e.args[0] in source.axes for _, e in groups
        ):
            retained_shape = tuple(
                source.shape[source.axes.index(e.args[0])] for _, e in groups
            )
        keys, inverse = indexing.group_keys(
            [self.expr(e, source) for _, e in groups], len(source), retained_shape=retained_shape
        )
        population = T.segment_sum(
            np.ones(len(source), dtype=object), inverse, len(keys)
        )
        selected = np.flatnonzero(incidence.mask)
        values = np.ones(len(selected), dtype=object)
        if a["reducer"] == "sum":
            values = T.exact(T.broadcast(self.expr(a["value"], source), len(source)))[
                selected
            ]
        reduced = T.segment_sum(values, inverse[selected], len(keys))
        if a["reducer"] == "any":
            reduced = (reduced != 0).astype(object)
        if a["reducer"] == "any":
            reduced = np.asarray([int(v) for v in reduced], dtype=object)
        ids = tuple(
            f"{node.id}:key:{json.dumps(key, separators=(',', ':'))}" for key in keys
        )
        fields = {
            name: np.asarray([key[i] for key in keys], dtype=object)
            for i, (name, _) in enumerate(groups)
        }
        fields.setdefault("key", (
            np.asarray([key[0] for key in keys], dtype=object)
            if len(groups) == 1
            else np.arange(len(keys), dtype=object)
        ))
        # One pass preserves source order within each group, including zero groups.
        contributors = [[] for _ in keys]
        for i in selected:
            contributors[inverse[i]].append(Ref(source.node, source.ids[i]))
        parents = tuple(tuple(group) for group in contributors)
        formula = f"{a['reducer']} over {{p in A : {incidence.rule}}}, grouped by " + (
            ", ".join(str(e) for _, e in groups) or "the whole finite domain"
        )
        return Snapshot(
            node.id,
            reduced,
            ids,
            ids,
            fields,
            parents=parents,
            metadata={
                "reducer": a["reducer"],
                "counted": "occurrences",
                "keys": keys,
                "population": population.tolist(),
                "contributor_ids": tuple(
                    tuple(r.occurrence for r in row) for row in parents
                ),
                "universe": source.node,
                "incidence": incidence.node,
                "formula": formula,
                "complete": True,
                "finite": True,
            },
        )

    def _spiral(self, node):
        a = node.attributes
        limit = T.size(self.expr(a["count"]), "Extent", self.max_items)
        n = T.size(self.expr(a["initial"]), "Initial run", self.max_items, minimum=1)
        coords, cycles, ends, seed_ends, widths, heights = [], [], [], [], [], []

        def add(x, y, cycle, seed=False):
            coords.append((x, y))
            cycles.append(cycle)
            ends.append(False)
            seed_ends.append(seed)
            widths.append(0)
            heights.append(0)

        for x in range(min(n, limit)):
            add(x, 0, 1, x == n - 1)
        minx, maxx, miny, maxy, k = 0, n - 1, 0, 0, 2
        while len(coords) < limit:
            if k % 2 == 0:
                maxy += 1
                row = [(x, maxy) for x in range(maxx, minx - 1, -1)]
                minx -= 1
                col = [(minx, y) for y in range(maxy, miny - 1, -1)]
            else:
                miny -= 1
                row = [(x, miny) for x in range(minx, maxx + 1)]
                maxx += 1
                col = [(maxx, y) for y in range(miny, maxy + 1)]
            complete = len(coords) + len(row) + len(col) <= limit
            for x, y in (row + col)[: limit - len(coords)]:
                add(x, y, k)
            if complete:
                ends[-1] = True
                widths[-1] = maxx - minx + 1
                heights[-1] = maxy - miny + 1
            k += 1
        pos = np.asarray(coords, dtype=float).reshape(-1, 2)
        fields = {
            "cycle": np.asarray(cycles, dtype=object),
            "cycle_end": np.asarray(ends, bool),
            "seed_end": np.asarray(seed_ends, bool),
            "width": np.asarray(widths, dtype=object),
            "height": np.asarray(heights, dtype=object),
        }
        ctx = {
            **fields,
            "index": np.arange(limit, dtype=object),
            "x": pos[:, 0],
            "y": pos[:, 1],
        }
        values = T.broadcast(self.expr(a["values"], context=ctx), limit)
        return self._new(node, values, fields, positions=pos)

    def _concat(self, node, left, right):
        if len(left) + len(right) > self.max_items:
            raise ValueError("Concatenation exceeds item budget")
        if set(left.fields) != set(right.fields):
            raise ValueError(
                "Concatenation needs matching attribute names; annotate missing attributes explicitly"
            )
        axis = node.attributes["axis"]
        shape, axes, address = None, (), np.arange(len(left) + len(right))
        if axis is not None:
            dim = indexing.axis_dimension(left.axes, left.shape, axis)
            if left.axes != right.axes or right.shape is None:
                raise ValueError("Non-concatenated axes must agree")
            address, shape = indexing.concat_axis(left.shape, right.shape, dim)
            axes = left.axes
        fields = {
            k: np.concatenate((left.fields[k], right.fields[k]))[address]
            for k in left.fields
        }
        if shape is not None:
            fields.update(indexing.grid_fields(shape, axes, max_items=self.max_items))
        refs = tuple(Ref(left.node, o) for o in left.ids) + tuple(
            Ref(right.node, o) for o in right.ids
        )
        parents = tuple(refs[i] for i in address)
        sources = left.sources + right.sources
        return Snapshot(
            node.id,
            np.concatenate((left.values, right.values))[address],
            tuple(f"{node.id}:{i}" for i in range(len(address))),
            tuple(sources[i] for i in address),
            fields,
            axes=axes,
            shape=shape,
            parents=tuple((r,) for r in parents),
            motion_parents=parents,
            metadata={"operation": "concat", "complete": True, "finite": True},
        )

    def _pad(self, node, source):
        a = node.attributes
        before = T.size(self.expr(a["before"]), "Before padding", self.max_items)
        after = T.size(self.expr(a["after"]), "After padding", self.max_items)
        count = before + len(source) + after
        if count > self.max_items:
            raise ValueError("Padding exceeds item budget")
        value = self.expr(a["value"])
        if value.ndim:
            raise ValueError("Padding fill must be scalar")
        sequence_axis = source.axes == ("s",) and source.shape is not None
        extra = set(source.fields) - {"key"} - ({"s"} if sequence_axis else set())
        if extra - set(a["attribute_fill"]):
            raise ValueError(
                "Declare padding fill for attributes: "
                + ", ".join(sorted(extra - set(a["attribute_fill"])))
            )
        ids = tuple(f"{node.id}:{i}" for i in range(count))
        vals = np.concatenate(
            (
                np.full(before, value.item(), dtype=object),
                source.values,
                np.full(after, value.item(), dtype=object),
            )
        )
        fields = {}
        for k, values in source.fields.items():
            if k == "key":
                fields[k] = np.asarray(
                    [f"pad:{node.id}:{i}" for i in range(before)]
                    + values.tolist()
                    + [f"pad:{node.id}:{before+len(source)+i}" for i in range(after)],
                    dtype=object,
                )
            elif k == "s" and sequence_axis:
                fields[k] = np.arange(count, dtype=object)
            else:
                fields[k] = np.concatenate(
                    (
                        np.full(before, a["attribute_fill"][k]),
                        values,
                        np.full(after, a["attribute_fill"][k]),
                    )
                )
        refs = (
            (None,) * before
            + tuple(Ref(source.node, o) for o in source.ids)
            + (None,) * after
        )
        sources = ids[:before] + source.sources + ids[before + len(source) :]
        return Snapshot(
            node.id,
            vals,
            ids,
            sources,
            fields,
            axes=("s",) if sequence_axis else (),
            shape=(count,) if sequence_axis else None,
            parents=tuple(() if r is None else (r,) for r in refs),
            motion_parents=refs,
            metadata={
                "operation": "pad",
                "fill": value.item(),
                "complete": True,
                "finite": True,
            },
        )
