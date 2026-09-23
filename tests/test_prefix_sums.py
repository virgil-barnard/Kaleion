"""Exact ordered accumulation, keyed reuse, and compact captured evidence."""

import unittest
from unittest.mock import patch

import numpy as np

from kaleion import Collection, Evaluator, F, Inspection, Motion, Ref, Workspace, graph, load_graph, param, wrap


class PrefixSumTests(unittest.TestCase):
    def test_young_offsets_match_dense_reference_and_pack_the_original_cells(self):
        heights = Collection.literal([5, 3, 2, 0])
        grid = Collection.grid(4, 5, values=1)
        diagram = grid.where(F.j < heights.bind(on=F.i))
        layers = diagram.count(by=F.j)
        offsets = layers.group_by().order_by(F.j).prefix_sums(key=F.j)
        pairs = Collection.grid(5, 5).annotate(length=layers.bind(on=F.j, key=F.j))
        reference = pairs.where(F.j < F.i).sum(by=F.i, value=F.length)
        cells = diagram.select().arrange(F.i, F.j)
        strip = cells.arrange(F.i + offsets.bind(on=F.j, key=F.j), 0)
        workspace = Workspace(dict(grid=grid, layers=layers, offsets=offsets, reference=reference, cells=cells))
        state = workspace.state
        self.assertFalse(state.errors)
        self.assertEqual(state.results["layers"].values.tolist(), [3, 3, 2, 1, 1])
        self.assertEqual(state.results["offsets"].values.tolist(), [0, 3, 6, 8, 9])
        np.testing.assert_array_equal(state.results["offsets"].values, state.results["reference"].values)
        move = workspace.set("cells", strip, motion=Motion.arc(height=2))
        self.assertEqual(sorted(workspace.state.results["cells"].positions[:, 0]), list(range(10)))
        self.assertEqual(workspace.state.results["cells"].ids, state.results["cells"].ids)
        back = workspace.undo()
        np.testing.assert_array_equal(move.frame("cells", .25).positions, back.frame("cells", .75).positions)
        inspector = Inspection(workspace.state)
        measured = state.results["offsets"]
        receipt = inspector.measurement(Ref(measured.node, measured.ids[3]))
        self.assertEqual([c.weight for c in receipt.contributors], [3, 3, 2])
        self.assertEqual(receipt.contributor_count, 3)
        self.assertEqual(receipt.item.value, 8)
        count = inspector.measurement(receipt.contributors[2].item.ref)
        self.assertEqual(count.contributor_count, 2)
        self.assertEqual([c.item.fields["i"] for c in count.contributors], [0, 1])

    def test_quotient_columns_use_the_same_prefix_and_rank_contract(self):
        grid = Collection.grid(7, 11, values=11*F.i + 7*F.j)
        region = grid.where(F.value >= 77)
        counts = region.count(by=F.i)
        offsets = counts.group_by().order_by(F.i).prefix_sums(key=F.i)
        ranks = region.group_by(F.i).order_by(F.j).ranks()
        cells = region.select()
        packed = cells.arrange(offsets.bind(on=F.i, key=F.i) + ranks.bind(on=F.key), 0)
        state = Workspace(dict(counts=counts, offsets=offsets, packed=packed)).state
        self.assertFalse(state.errors)
        self.assertEqual(state.results["counts"].values.tolist(), [0, 1, 3, 4, 6, 7, 9])
        self.assertEqual(state.results["offsets"].values.tolist(), [0, 0, 1, 4, 8, 14, 21])
        self.assertEqual(sorted(state.results["packed"].positions[:, 0]), list(range(30)))
        measured = state.results["offsets"]
        receipt = Inspection(state).measurement(Ref(measured.node, measured.ids[1]))
        self.assertEqual(receipt.item.value, 0)
        self.assertEqual(receipt.contributor_count, 1)
        self.assertEqual(receipt.contributors[0].weight, 0)
        self.assertEqual(Inspection(state).measurement(receipt.contributors[0].item.ref).contributor_count, 0)

    def test_grouped_signed_weights_composite_keys_and_order_are_independent_of_storage(self):
        records = [(0, 3, -2), (1, 2, 8), (0, 1, 5), (0, 2, 0), (1, 1, -8), (1, 3, 9)]
        source = Collection.literal([99]*len(records), fields={
            "g": [g for g, k, w in records], "member": [k for g, k, w in records],
            "weight": [w for g, k, w in records],
        })
        normal = source.group_by(F.g).order_by(F.member).prefix_sums(key=(F.g, F.member), value=F.weight)
        shuffled = source.order_by(-F.key).arrange(F.value, 7)
        reordered = shuffled.group_by(F.g).order_by(F.member).prefix_sums(key=(F.g, F.member), value=F.weight)
        state = Workspace(dict(source=source, normal=normal, reordered=reordered)).state
        original = state.results["source"]
        for name in ("normal", "reordered"):
            result = state.results[name]
            for i, key in enumerate(zip(result.fields["g"], result.fields["member"])):
                g, k = key
                earlier = sorted((m, j, w) for j, (h, m, w) in enumerate(records) if h == g and m < k)
                self.assertEqual(result.values[i], sum(w for m, j, w in earlier))
                self.assertEqual(result.contributor_ids(key), tuple(original.ids[j] for m, j, w in earlier))
        normal_result = state.results["normal"]
        cancelled = Inspection(state).measurement(Ref(normal_result.node, normal_result.ids[-1]))
        self.assertEqual(cancelled.item.value, 0)
        self.assertEqual([c.weight for c in cancelled.contributors], [-8, 8])

    def test_empty_selected_domains_and_retained_zero_items_have_different_evidence(self):
        empty = Collection.grid(3, 0)
        counts = empty.count(by=F.i)
        prefixes = counts.group_by().order_by(F.i).prefix_sums(key=F.i)
        no_items = empty.where(True).group_by(F.i).order_by(F.j).prefix_sums(key=(F.i, F.j))
        state = Workspace(dict(counts=counts, prefixes=prefixes, no_items=no_items)).state
        self.assertEqual(state.results["prefixes"].values.tolist(), [0, 0, 0])
        self.assertEqual(len(state.results["prefixes"].contributor_ids(2)), 2)
        self.assertEqual(len(state.results["no_items"]), 0)
        self.assertEqual(len(Collection.literal([]).group_by().order_by(F.key).prefix_sums().evaluate()), 0)
        evens = Collection.sequence(6).where(F.value % 2 == 0)
        selected = evens.group_by().order_by(-F.value).prefix_sums().evaluate()
        self.assertEqual(selected.values.tolist(), [10, 6, 0])

    def test_ambiguous_order_keys_and_noninteger_weights_fail_without_erasing_independent_work(self):
        source = Collection.literal([2, 2, 1])
        groups = source.group_by()
        state = Workspace(dict(count=groups.count(),
                               tied=groups.order_by(F.value).prefix_sums(),
                               resolved=groups.order_by(F.value, F.key).prefix_sums())).state
        self.assertEqual(state.results["count"].values.tolist(), [3])
        self.assertIn("ties within a group", state.errors["tied"])
        self.assertEqual(state.results["resolved"].values.tolist(), [1, 3, 0])
        with self.assertRaisesRegex(ValueError, "Declare member order"):
            groups.prefix_sums()
        with self.assertRaisesRegex(ValueError, "explicit item key"):
            groups.order_by(F.key).prefix_sums(key=())
        repeated = source.gather([0, 0])
        with self.assertRaisesRegex(ValueError, "item keys must be unique"):
            repeated.group_by().order_by(F.index).prefix_sums().evaluate()
        # Explicit new occurrence addressing permits repeated source identities.
        self.assertEqual(repeated.group_by().order_by(F.index).prefix_sums(key=F.index).evaluate().values.tolist(), [0, 2])
        for weight in (True, 0.5, F.value / 2):
            with self.subTest(weight=str(weight)), self.assertRaisesRegex(ValueError, "exact integers"):
                groups.order_by(F.key).prefix_sums(value=weight).evaluate()
        driver = Collection.literal([4])
        with self.assertRaisesRegex(ValueError, "Missing driver key"):
            groups.order_by(F.key).prefix_sums(value=driver.bind(on=F.key)).evaluate()

    def test_large_weights_use_exact_scan_with_linear_evidence_and_bounded_work(self):
        size, weight = 160, 2**100 + 7
        source = Collection.literal([weight]*size)
        prefix = source.group_by().order_by(F.key).prefix_sums()
        engine = Evaluator(max_items=size)
        result = engine.get(prefix.node)
        self.assertEqual(result.values.tolist(), [i*weight for i in range(size)])
        evidence = result.metadata["contributor_prefixes"]
        self.assertEqual(sum(map(len, evidence["groups"])), size)
        self.assertEqual(len(evidence["ranges"]), size)
        self.assertNotIn("contributor_ids", result.metadata)
        self.assertTrue(all(len(p) == 1 for p in result.parents))
        self.assertTrue(all(record["extent"] <= size for record in engine.records.values()))
        self.assertNotIn("grid", {record["operation"] for record in engine.records.values()})
        fixed = Collection.literal(np.array([2**62, 2**62, 1], dtype=np.int64))
        self.assertEqual(fixed.group_by().order_by(F.key).prefix_sums().evaluate().values.tolist(), [0, 2**62, 2**63])
        overflow = Collection.literal([2**4095, 2**4095, 0])
        with self.assertRaisesRegex(ValueError, "bit budget"):
            overflow.group_by().order_by(F.key).prefix_sums().evaluate()

    def test_reindex_and_placement_preserve_measurements_but_value_changes_remove_the_claim(self):
        source = Collection.literal([4, 0, -4, 8])
        prefix = source.group_by().order_by(F.key).prefix_sums()
        moved = prefix.gather([3, 1]).arrange(F.key, F.value).where(F.key == 3).select()
        state = Workspace(dict(source=source, prefix=prefix, moved=moved)).state
        result = state.results["moved"]
        self.assertEqual(result.values.tolist(), [0])
        receipt = Inspection(state).measurement(Ref(result.node, result.ids[0]))
        self.assertEqual([c.weight for c in receipt.contributors], [4, 0, -4])
        self.assertEqual(receipt.origin.node, state.results["prefix"].node)
        with self.assertRaisesRegex(ValueError, "repeated occurrences"):
            prefix.gather([0, 0]).evaluate().contributor_ids(0)
        changed = prefix.with_values(F.value + 1).evaluate()
        with self.assertRaisesRegex(ValueError, "value transformations"):
            changed.contributor_ids(1)
        self.assertNotIn("contributor_prefixes", changed.metadata)

    def test_scoped_weights_reads_and_saved_history_are_inspectable_without_evaluation(self):
        driver = Collection.literal([0, 2, 5])
        source = Collection.literal([99, 99, 99])
        weight = param("scale") * driver.bind(on=F.key) - 4
        prefix = source.group_by().order_by(F.key * param("direction")).prefix_sums(value=weight)
        up = prefix.with_params(scale=2, direction=1)
        down = prefix.with_params(scale=3, direction=-1)
        points = source.arrange(F.key, up.bind(on=F.key))
        workspace = Workspace(dict(up=up, down=down, points=points))
        self.assertEqual(workspace.state.results["up"].values.tolist(), [0, -4, -4])
        self.assertEqual(workspace.state.results["down"].values.tolist(), [13, 11, 0])
        workspace.set("points", source.arrange(F.key, down.bind(on=F.key)))
        workspace.undo()
        saved = workspace.to_json()
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("unexpected execution")):
            reopened = Workspace.from_json(saved)
            result = reopened.state.results["up"]
            receipt = Inspection(reopened.state).measurement(Ref(result.node, result.ids[2]))
            self.assertEqual([c.item.value for c in receipt.contributors], [99, 99])
            self.assertEqual([c.weight for c in receipt.contributors], [-4, 0])
            self.assertEqual([c.reads[0].value for c in receipt.contributors], [0, 2])
            first = Inspection(reopened.state).measurement(Ref(result.node, result.ids[0]), limit=0)
            self.assertEqual((first.item.value, first.contributor_count, first.contributors), (0, 0, ()))
            reopened.redo()
            self.assertEqual(reopened.state.results["points"].positions[:, 1].tolist(), [13, 11, 0])
            reopened.undo()
            self.assertEqual(reopened.to_json(), saved)
        restored = wrap(load_graph(graph({"prefix": down.node}))["prefix"]).evaluate()
        self.assertEqual(restored.values.tolist(), [13, 11, 0])


if __name__ == "__main__":
    unittest.main()
