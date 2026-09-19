"""Grouping, strict order, coverage, and driven placement through the public API."""

import unittest
from unittest.mock import patch

import numpy as np

from kaleion import Collection, Coverage, Evaluator, F, Motion, Workspace, graph, load_graph, param, wrap


class GroupingTests(unittest.TestCase):
    def test_ranks_match_predecessor_sets_with_composite_keys_and_reordering(self):
        records = [(0, 2, 2**80), (1, 2, 3), (0, 1, -(2**80)),
                   (0, 3, 2**80), (1, 1, 3), (2, 1, 0)]
        source = Collection.literal([v for g, k, v in records], fields={
            "g": [g for g, k, v in records], "id": [k for g, k, v in records],
        })
        ranks = source.group_by(F.g).order_by(F.value, F.id).ranks(key=(F.g, F.id))
        rearranged = source.order_by(-F.key).group_by(F.g).order_by(F.value, F.id).ranks(key=(F.g, F.id))
        state = Workspace({"source": source, "ranks": ranks, "rearranged": rearranged}).state
        self.assertFalse(state.errors)
        original = state.results["source"]
        expected = {}
        for g, k, value in records:
            earlier = sorted((v, j, i) for i, (h, j, v) in enumerate(records)
                             if h == g and (v, j) < (value, k))
            expected[(g, k)] = tuple(original.ids[i] for _, _, i in earlier)
        for name in ("ranks", "rearranged"):
            result = state.results[name]
            for i, key in enumerate(zip(result.fields["g"], result.fields["id"])):
                self.assertEqual(result.values[i], len(expected[key]))
                self.assertEqual(result.contributor_ids(key), expected[key])

    def test_group_counts_keep_rectangular_zero_groups_and_selected_ranks_do_not_invent_items(self):
        empty = Collection.grid(3, 0).where(True).group_by(F.i)
        coverage = empty.coverage()
        state = Workspace({"counts": coverage.counts, "missing": coverage.missing,
                           "overlaps": coverage.overlaps,
                           "ranks": empty.order_by(F.j).ranks(key=(F.i, F.j)),
                           "owners": coverage.unique(value=F.j)}).state
        self.assertEqual(state.results["counts"].values.tolist(), [0, 0, 0])
        self.assertEqual(state.results["missing"].cardinality, 3)
        self.assertEqual(state.results["overlaps"].cardinality, 0)
        self.assertEqual(len(state.results["ranks"]), 0)
        self.assertIn("coverage exactly one", state.errors["owners"])
        total = Collection.literal([]).group_by().count().evaluate()
        self.assertEqual(total.values.tolist(), [0])
        self.assertEqual(total.contributor_ids(()), ())
        selected = Collection.sequence(6).where(F.value % 2 == 0)
        self.assertEqual(selected.group_by().order_by(-F.value).ranks().evaluate().values.tolist(), [2, 1, 0])

    def test_ties_and_duplicate_item_keys_fail_without_poisoning_counts(self):
        source = Collection.literal([2, 2, 1], keys=[10, 20, 30])
        groups = source.group_by()
        state = Workspace({"counts": groups.count(),
                           "ambiguous": groups.order_by(F.value).ranks(),
                           "resolved": groups.order_by(F.value, F.key).ranks()}).state
        self.assertEqual(state.results["counts"].values.tolist(), [3])
        self.assertIn("ties within a group", state.errors["ambiguous"])
        self.assertEqual(state.results["resolved"].values.tolist(), [1, 2, 0])
        repeated = source.gather([0, 0])
        with self.assertRaisesRegex(ValueError, "item keys must be unique"):
            repeated.group_by().order_by(F.index).ranks().evaluate()
        with self.assertRaisesRegex(ValueError, "Declare member order"):
            groups.ranks()
        with self.assertRaises(TypeError):
            bool(groups)
        with self.assertRaises(TypeError):
            bool(groups.coverage())

    def test_rank_evidence_is_linear_and_expands_only_the_requested_prefix(self):
        n = 160  # Its predecessor matrix would exceed this evaluator's item budget.
        source = Collection.sequence(n, start=0)
        ranks = source.group_by().order_by(F.value).ranks()
        engine = Evaluator(max_items=n)
        result = engine.get(ranks.node)
        self.assertEqual(result.values.tolist(), list(range(n)))
        prefix = result.metadata["contributor_prefixes"]
        self.assertEqual(sum(map(len, prefix["groups"])), n)
        self.assertEqual(len(prefix["ranges"]), n)
        self.assertNotIn("contributor_ids", result.metadata)
        self.assertEqual(result.contributor_ids(0), ())
        self.assertEqual(result.contributor_ids(n-1), source.evaluate().ids[:-1])
        self.assertTrue(all(r["extent"] <= n for r in engine.records.values()))
        self.assertNotIn("grid", {r["operation"] for r in engine.records.values()})

    def test_rank_contributors_survive_gather_order_and_placement_but_not_relabeling(self):
        source = Collection.literal([30, 10, 20], keys=[7, 9, 11])
        ranks = source.group_by().order_by(F.value).ranks()
        expected = ranks.evaluate().contributor_ids(7)
        arranged = ranks.order_by(-F.key).arrange(x=F.key, y=F.value)
        selected = arranged.where(F.key != 9).select()
        self.assertEqual(selected.evaluate().contributor_ids(7), expected)
        self.assertEqual(ranks.gather([2, 0]).evaluate().contributor_ids(7), expected)
        with self.assertRaisesRegex(ValueError, "repeated occurrences"):
            ranks.gather([0, 0]).evaluate().contributor_ids(7)
        changed = arranged.with_values(F.value + 10).evaluate()
        with self.assertRaisesRegex(ValueError, "value transformations"):
            changed.contributor_ids(7)
        self.assertNotIn("contributor_prefixes", changed.metadata)
        self.assertIn("prior_measurement", changed.metadata)
        with self.assertRaises(TypeError):
            selected.evaluate().metadata["contributor_prefixes"]["groups"][0][0] = "edited"

    def test_parameter_cases_and_saved_prefix_evidence_reopen_without_execution(self):
        source = Collection.sequence(5, start=0)
        ranks = source.group_by().order_by(F.value * param("direction")).ranks()
        up, down = ranks.with_params(direction=1), ranks.with_params(direction=-1)
        a = source.arrange(x=F.key, y=up.bind(on=F.key))
        b = source.arrange(x=F.key, y=down.bind(on=F.key))
        workspace = Workspace({"points": a, "up": up, "down": down})
        move = workspace.set("points", b, motion=Motion.arc(height=2))
        workspace.capture("Change the declared order")
        workspace.undo()
        payload = workspace.to_json()
        expected = source.evaluate().ids[1:][::-1]
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("unexpected execution")):
            reopened = Workspace.from_json(payload)
            self.assertEqual(reopened.state.results["down"].contributor_ids(0), expected)
            redo = reopened.redo()
            np.testing.assert_array_equal(move.frame("points", .25).positions,
                                           redo.reverse().frame("points", .75).positions)
        restored = wrap(load_graph(graph({"ranks": down.node}))["ranks"]).evaluate()
        self.assertEqual(restored.values.tolist(), [4, 3, 2, 1, 0])


class CoverageTests(unittest.TestCase):
    def test_composite_keys_retain_a_field_named_key_instead_of_overwriting_it_with_ordinals(self):
        source = Collection.literal([4, 3, 2, 1], keys=[20, 10, 20, 10],
                                    fields={"band": [1, 0, 0, 1]})
        groups = source.group_by(F.key, F.band)
        counts = groups.count().evaluate()
        self.assertEqual(counts.fields["key"].tolist(), [20, 10, 20, 10])
        self.assertEqual(counts.values.tolist(), [1, 1, 1, 1])
        ranks = source.group_by(F.band).order_by(F.value).ranks(key=(F.key, F.band))
        driver = ranks.bind(on=(F.key, F.band), key=groups.key)
        placed = source.arrange(x=F.value, y=driver).evaluate()
        np.testing.assert_array_equal(placed.positions[:, 1], [1, 1, 0, 0])
        owners = groups.coverage().on_keys(F.key == 20).unique()
        result = owners.evaluate()
        self.assertEqual(result.values.tolist(), [4, 2])
        self.assertEqual(result.contributor_ids((20, 0)), (source.evaluate().ids[2],))

    def test_equal_totals_hide_missing_and_duplicate_coverage(self):
        domain = Collection.grid(3, 2, values=0)
        relation = domain.where((F.i == 2) | ((F.i == 1) & (F.j == 0)))
        report = relation.group_by(F.i).coverage()
        state = Workspace({"counts": report.counts, "missing": report.missing,
                           "overlaps": report.overlaps, "owners": report.unique()}).state
        self.assertEqual(state.results["counts"].values.tolist(), [0, 1, 2])
        self.assertEqual(sum(state.results["counts"].values), 3)
        self.assertEqual(state.results["missing"].source.fields["key"][state.results["missing"].mask].tolist(), [0])
        self.assertEqual(state.results["overlaps"].source.fields["key"][state.results["overlaps"].mask].tolist(), [2])
        self.assertIn("2 failing keys", state.errors["owners"])
        # An explicit restricted key domain has one actual contributor of value zero.
        scoped = report.on_keys(F.key > 0).on_keys(F.key < 2)
        assigned = scoped.unique().evaluate()
        self.assertEqual(assigned.fields["key"].tolist(), [1])
        self.assertEqual(assigned.values.tolist(), [0])
        self.assertEqual(len(assigned.contributor_ids(1)), 1)

    def test_composite_retained_keys_scope_and_driven_3d_placement(self):
        domain = Collection.grid(2, 3, 2).annotate(label=10*F.i+F.j)
        relation = domain.where(F.k == (F.i+F.j) % 2)
        groups = relation.group_by(F.i, F.j)
        report = groups.coverage().on_keys(F.i == 1)
        values = report.unique(value=F.label)
        target = Collection.literal([2, 0, 1], fields={"row": [1, 1, 1]})
        driver = values.bind(on=(F.row, F.value), key=groups.key)
        moved = target.arrange(z=driver, x=F.value, y=F.row)
        result = moved.evaluate()
        np.testing.assert_array_equal(result.positions, [[2, 1, 12], [0, 1, 10], [1, 1, 11]])
        self.assertEqual(len(values.evaluate().contributor_ids((1, 2))), 1)
        with self.assertRaisesRegex(ValueError, "Missing driver key"):
            Collection.literal([7]).arrange(x=values.bind(on=(1, F.value), key=groups.key)).evaluate()

    def test_missing_parameters_fail_instead_of_becoming_zero_coverage(self):
        domain = Collection.grid(2, 2)
        report = domain.where(F.j == param("selected")).group_by(F.i).coverage()
        state = Workspace({"domain": domain, "counts": report.counts,
                           "owners": report.unique(value=F.j)}).state
        self.assertEqual(len(state.results["domain"]), 4)
        self.assertIn("counts", state.errors)
        self.assertIn("owners", state.errors)
        self.assertNotIn("counts", state.results)
        with self.assertRaisesRegex(ValueError, "declared grouping"):
            Coverage(domain.group_by(F.i), domain.count())

    def test_require_preserves_evidence_and_failed_action_can_be_undone(self):
        source = Collection.grid(3, 2, values=F.j)
        incidence = source.where(F.j == param("chosen"))
        report = incidence.group_by(F.i).coverage()
        owners = report.unique(value=F.j)
        workspace = Workspace({"owners": owners, "counts": report.counts}, {"chosen": 0})
        original = workspace.state.results["owners"]
        workspace.set_parameters(chosen=4)
        self.assertEqual(workspace.state.results["counts"].values.tolist(), [0]*3)
        self.assertIn("owners", workspace.state.errors)
        workspace.undo()
        self.assertEqual(workspace.state.results["owners"].ids, original.ids)
        reopened = Workspace.from_json(workspace.to_json())
        self.assertEqual(reopened.state.results["owners"].contributor_ids(2), original.contributor_ids(2))
        reopened.redo()
        self.assertIn("owners", reopened.state.errors)
        with self.assertRaises(TypeError):
            source.require(True)

    def test_named_coordinates_preserve_positional_semantics_and_reject_gaps(self):
        source = Collection.sequence(4)
        a = source.arrange(F.value, -F.value, F.value*2)
        b = source.arrange(z=F.value*2, x=F.value, y=-F.value)
        np.testing.assert_array_equal(a.evaluate().positions, b.evaluate().positions)
        self.assertEqual(a.evaluate().ids, b.evaluate().ids)
        np.testing.assert_array_equal(a.place(x=F.x+1, y=F.y, z=F.z).evaluate().positions[:, 0], [2, 3, 4, 5])
        with self.assertRaises(TypeError):
            source.arrange(F.value, y=0)
        for named in ({"y": 0}, {"x": 0, "z": 0}, {"x": 0, "height": 1}):
            with self.assertRaises(ValueError):
                source.arrange(**named)


if __name__ == "__main__":
    unittest.main()
