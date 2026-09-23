"""Read captured occurrences, measurements, and keyed bindings without execution.

An Inspection belongs to one captured State. It resolves scoped references and
reconstructs declared field reads from saved inputs; it never runs graph nodes.
Receipts are finite evidence, not universal proofs or mathematical arrangements.
"""

from dataclasses import dataclass
from types import MappingProxyType

import numpy as np

from . import tensor as T
from .expressions import evaluate_expression
from .indexing import align, key_rows, row_keys
from .ir import Expr, dependencies
from .measurements import is_measurement
from .model import Ref, Snapshot, plain


def _ref(ref):
    return [ref.node, ref.occurrence]


def _scalar(value):
    return value.item() if isinstance(value, np.generic) else value


@dataclass(frozen=True)
class CapturedItem:
    ref: Ref
    value: int | None
    fields: object
    position: tuple | None
    source: str
    parents: tuple[Ref, ...]

    def to_dict(self):
        return dict(ref=_ref(self.ref), value=self.value, fields=plain(self.fields),
                    position=plain(self.position), source=self.source,
                    parents=[_ref(ref) for ref in self.parents])


@dataclass(frozen=True)
class BindingRead:
    site: str
    target: Ref
    driver: Ref
    key: tuple
    read: str
    value: object

    def to_dict(self):
        return dict(site=self.site, target=_ref(self.target), driver=_ref(self.driver),
                    key=plain(self.key), read=self.read, value=plain(self.value))


@dataclass(frozen=True)
class Contribution:
    item: CapturedItem
    weight: int
    reads: tuple[BindingRead, ...]

    def to_dict(self):
        return dict(item=self.item.to_dict(), weight=self.weight,
                    reads=[read.to_dict() for read in self.reads])


@dataclass(frozen=True)
class MeasurementReceipt:
    item: CapturedItem
    origin: Ref
    key: tuple
    reducer: str
    formula: str
    population: int
    contributor_count: int
    contributors: tuple[Contribution, ...]

    @property
    def truncated(self):
        return len(self.contributors) < self.contributor_count

    def to_dict(self):
        return dict(item=self.item.to_dict(), origin=_ref(self.origin), key=plain(self.key),
                    reducer=self.reducer, formula=self.formula, population=self.population,
                    contributor_count=self.contributor_count, truncated=self.truncated,
                    contributors=[item.to_dict() for item in self.contributors])


class Inspection:
    """Queries over one captured state, including a reopened workspace's state.

    find() uses declared field names; item() uses scoped occurrence references.
    measurement() follows preserved evidence to its original measured operation.
    bindings() inspects a pointwise operation's input, never its changed output.
    Only keyed bindings are explained; scalar/positional reads and bindings nested
    inside another binding's key/read need a later, separately stated contract.
    """

    def __init__(self, state):
        self._results = dict(state.results)
        self._snapshots = dict(state.evaluated)
        self._snapshots.update((value.node, value) for value in state.results.values())
        self._records, self._nodes, self._indexes = {}, {}, {}

        def records(scope):
            for node_id, record in scope.items():
                if record.get("status") == "ready":
                    self._records[record["evaluation"]] = (node_id, record, scope)
                if "subtrace" in record:
                    records(record["subtrace"])

        records(state.provenance["trace"])
        pending = [root.node for root in state.roots.values()]
        while pending:
            node = pending.pop()
            if node.id not in self._nodes:
                self._nodes[node.id] = node
                pending.extend(node.parents())

    def _snapshot(self, node):
        if node not in self._snapshots:
            raise KeyError(f"No captured result for {node}; inspection cannot execute it")
        result = self._snapshots[node]
        if not isinstance(result, Snapshot):
            raise TypeError("Inspect a collection/arrangement occurrence, not an incidence or frame")
        return result

    def _locate(self, ref):
        if not isinstance(ref, Ref):
            raise TypeError("Use a scoped Ref, obtained with find() or from a receipt")
        snapshot = self._snapshot(ref.node)
        if ref.node not in self._indexes:
            self._indexes[ref.node] = {oid: i for i, oid in enumerate(snapshot.ids)}
        if ref.occurrence not in self._indexes[ref.node]:
            raise KeyError(f"Occurrence {ref.occurrence!r} is absent from {ref.node}")
        return snapshot, self._indexes[ref.node][ref.occurrence]

    def find(self, root, key, *, by=("key",)):
        """Find one named result occurrence by explicit scalar/composite fields.

        Values and screen proximity never supply an implicit correspondence.
        Absent or duplicate matching keys fail; equal labels do not merge items.
        """
        if root not in self._results:
            raise KeyError(f"No ready captured root {root!r}")
        snapshot = self._snapshot(self._results[root].node)
        if (not isinstance(by, (tuple, list)) or not by
                or any(not isinstance(name, str) for name in by) or len(set(by)) != len(by)):
            raise ValueError("by needs distinct declared field names")
        columns = [snapshot.context()[name] for name in by]
        keys = key_rows(columns, len(snapshot))
        wanted = key if isinstance(key, tuple) else (key,)
        matches = [i for i, candidate in enumerate(keys) if candidate == wanted]
        if len(matches) != 1:
            raise ValueError(f"Expected one occurrence at {wanted!r}; found {len(matches)}")
        return Ref(snapshot.node, snapshot.ids[matches[0]])

    def item(self, ref):
        """Return one detached, immutable item description with scoped parents."""
        snapshot, i = self._locate(ref)
        return CapturedItem(ref, None if snapshot.values is None else int(snapshot.values[i]),
                            MappingProxyType({k: _scalar(v[i]) for k, v in snapshot.fields.items()}),
                            None if snapshot.positions is None else tuple(snapshot.positions[i].tolist()),
                            snapshot.sources[i], snapshot.parents[i])

    def _execution(self, node):
        if node not in self._records:
            raise KeyError(f"Missing captured execution context for {node}")
        definition, record, scope = self._records[node]

        def resolve(source):
            entry = scope.get(source.id, {})
            if entry.get("status") != "ready":
                raise KeyError(f"No ready captured dependency {source.id}; inspection cannot execute it")
            return self._snapshot(entry["evaluation"])

        return self._nodes[definition], record["parameters"], resolve

    @staticmethod
    def _expressions(value, site):
        if isinstance(value, Expr):
            if value.op == "aligned":
                yield site, value
            elif value.op in ("scalar", "lookup"):
                raise ValueError(f"{value.op} driver reads are not yet inspectable; use captured parents")
            else:
                for i, arg in enumerate(value.args):
                    yield from Inspection._expressions(arg, f"{site}/{value.op}[{i}]")

    def _read_plans(self, rule, site, source, params, resolve):
        for location, binding in self._expressions(rule, site):
            driver_node, on, key, read = binding.args
            if any(dependencies((on, key, read))):
                raise ValueError("Nested driver reads inside binding keys/read are not yet inspectable")
            driver = resolve(driver_node)

            def ev(expr, data):
                return evaluate_expression(expr, data.context(), params, resolve, length=len(data))

            target_keys = row_keys(ev(on, source), len(source))
            driver_keys = row_keys(ev(key, driver), len(driver))
            addresses = align(driver_keys, target_keys)
            values = ev(read, driver)
            if values.ndim == 0:
                values = T.broadcast(values, len(driver))
            if len(values) != len(driver):
                raise ValueError("Driver read shape mismatch")
            yield location, source, driver, target_keys, addresses, values, str(read)

    @staticmethod
    def _reads_at(plans, i):
        for site, source, driver, keys, addresses, values, read in plans:
            j = int(addresses[i])
            value = values[j]
            value = tuple(value.tolist()) if isinstance(value, np.ndarray) else _scalar(value)
            yield BindingRead(site, Ref(source.node, source.ids[i]),
                              Ref(driver.node, driver.ids[j]), keys[i], read, value)

    def bindings(self, ref):
        """Explain keyed reads of one captured Values/Annotate/Place/Move step.

        Follow item(ref).parents to inspect an earlier step. This is a replay of
        declared field reads on captured inputs, not an execution event trace.
        """
        self._locate(ref)
        node, params, resolve = self._execution(ref.node)
        if node.op not in ("values", "annotate", "place", "move"):
            raise ValueError("Inspect a values/annotate/place/move step; follow captured parents otherwise")
        source = resolve(node.inputs[0])
        _, i = self._locate(Ref(source.node, ref.occurrence))
        if node.op == "annotate":
            rules = node.attributes["fields"].items()
        elif node.op == "place":
            rules = zip("xyz", node.attributes["coordinates"])
        else:
            field = "rule" if node.op == "values" else "displacement"
            rules = ((field, node.attributes[field]),)
        plans = tuple(plan for site, rule in rules
                      for plan in self._read_plans(rule, site, source, params, resolve))
        return tuple(self._reads_at(plans, i))

    def measurement(self, ref, *, limit=32):
        """Inspect one retained measurement and at most limit contributors.

        Count/rank contributors have unit weight; sum/prefix weights are reconstructed
        from captured inputs and the recorded expression. Zero/negative weights
        remain contributors. The limit bounds expanded contributor records, not
        stored parent references or the work of interpreting the weight field.
        Reindexing may copy a measured item; its origin stays explicitly scoped.
        """
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 0:
            raise ValueError("limit must be a nonnegative integer")
        item = self.item(ref)
        source, _ = self._locate(ref)
        if not is_measurement(source.metadata):
            raise ValueError("This item has no active measurement claim; inspect its parents")
        origin = ref
        for _ in range(100):
            snapshot, i = self._locate(origin)
            node, params, resolve = self._execution(origin.node)
            if node.op in ("reduce", "rank", "prefix_sum"):
                break
            if len(snapshot.parents[i]) != 1:
                raise ValueError("Measurement origin needs one preserved parent per derived occurrence")
            origin = snapshot.parents[i][0]
        else:
            raise ValueError("Measurement origin exceeds inspection depth budget")
        meta = snapshot.metadata
        key = meta["keys"][i]
        ids = snapshot.contributor_ids(key)
        universe = self._snapshot(meta["universe"])
        rule = node.attributes.get("value") if meta["reducer"] in ("sum", "prefix_sum") else None
        weights = None if rule is None else T.exact(T.broadcast(evaluate_expression(
            rule, universe.context(), params, resolve, length=len(universe)), len(universe)))
        plans = () if rule is None else tuple(self._read_plans(rule, "weight", universe, params, resolve))
        contributions = []
        for oid in ids[:limit]:
            child = Ref(universe.node, oid)
            _, j = self._locate(child)
            reads = tuple(self._reads_at(plans, j))
            contributions.append(Contribution(self.item(child), 1 if weights is None else int(weights[j]), reads))
        return MeasurementReceipt(item, origin, key, meta["reducer"], meta["formula"],
                                  int(meta["population"][i]), len(ids), tuple(contributions))
