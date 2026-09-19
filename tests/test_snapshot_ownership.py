"""External data is copied; unchanged validated snapshot buffers can be shared."""

from dataclasses import replace
import unittest
from unittest.mock import patch

import numpy as np

from kaleion import Collection, Evaluator, F, Motion, Ref, Snapshot, Workspace, param, vector
from kaleion import model
from kaleion.model import snapshot_dict
from kaleion.expressions import evaluate_expression


class SnapshotOwnershipTests(unittest.TestCase):
    def test_numpy_integer_inputs_remain_exact_after_capture(self):
        values = np.empty(1, dtype=object)
        values[0] = np.int64(2**62)
        result = Snapshot("root", values, ("a",), ("a",),
                          {"weight": np.array([2**62], dtype=np.int64)})
        squared = evaluate_expression(F.value**2 + F.weight * F.weight,
                                      result.context(), {}, None, length=1)
        self.assertEqual(squared.tolist(), [2**125])

    def test_constructor_detaches_arrays_identity_and_lineage_containers(self):
        values = np.array([2, 3], dtype=object)
        positions = np.array([[0., 1.], [1., 2.]])
        keys = np.array([0, 1])
        readonly_keys = keys.view()
        readonly_keys.flags.writeable = False
        ids, sources = ["a", "b"], ["x", "y"]
        parents = [[Ref("old", "x")], [Ref("old", "y")]]
        motion_parents = [parents[0][0], parents[1][0]]
        axes, shape = ["s"], [2]
        metadata = {"note": ["captured"]}
        result = Snapshot("root", values, ids, sources, {"key": readonly_keys},
                          positions, axes, shape, parents, motion_parents, metadata)
        expected = snapshot_dict(result)
        values[:] = 99
        positions[:] = 99
        keys[:] = 99
        ids[0], sources[0], axes[0], shape[0] = "changed", "changed", "changed", 99
        parents[0].clear()
        motion_parents.clear()
        metadata["note"].append("changed")
        self.assertEqual(snapshot_dict(result), expected)
        self.assertIsInstance(result.ids, tuple)
        self.assertIsInstance(result.parents[0], tuple)

    def test_public_replacement_copies_even_readonly_snapshot_inputs(self):
        original = Collection.sequence(3).arrange(F.value, 0).evaluate()
        copied = replace(original, node="external copy")
        self.assertFalse(np.shares_memory(original.values, copied.values))
        self.assertFalse(np.shares_memory(original.positions, copied.positions))
        self.assertFalse(np.shares_memory(original.fields["key"], copied.fields["key"]))

    def test_placement_and_annotation_share_only_unchanged_buffers(self):
        source = Collection.grid(2, 3, values=3 * F.i + F.j)
        placed = source.arrange(F.j, -F.i)
        annotated = placed.annotate(weight=F.value + 2**80)
        moved = annotated.move(vector(2, -1))
        relabeled = moved.with_values(F.value + 10)
        engine = Evaluator()
        results, errors = engine.run(dict(source=source, placed=placed,
                                         annotated=annotated, moved=moved, relabeled=relabeled))
        self.assertFalse(errors)
        base, a, b, c, d = results.values()
        for result in (a, b, c):
            self.assertTrue(np.shares_memory(base.values, result.values))
            self.assertEqual(result.ids, base.ids)
        self.assertTrue(np.shares_memory(a.positions, b.positions))
        self.assertFalse(np.shares_memory(b.positions, c.positions))
        self.assertTrue(np.shares_memory(c.positions, d.positions))
        self.assertFalse(np.shares_memory(c.values, d.values))
        for name in base.fields:
            self.assertTrue(np.shares_memory(base.fields[name], d.fields[name]))
        self.assertEqual(d.values.tolist(), list(range(10, 16)))
        np.testing.assert_array_equal(c.positions, [[2, -1], [3, -1], [4, -1],
                                                   [2, -2], [3, -2], [4, -2]])
        self.assertEqual(b.fields["weight"].tolist(), [2**80 + i for i in range(6)])
        for result in results.values():
            self.assertFalse(result.values.flags.writeable)
            with self.assertRaises(ValueError):
                result.values[0] = 999

    def test_internal_updates_revalidate_changed_inputs_without_recopying_others(self):
        original = Collection.sequence(2).arrange(F.value, 0).evaluate()
        with patch("kaleion.model.exact", wraps=model.exact) as exact, \
             patch("kaleion.model.readonly", wraps=model.readonly) as readonly:
            renamed = original._with_changes(node="runtime case")
            self.assertEqual(exact.call_count, 0)
            self.assertEqual(readonly.call_count, 0)
        self.assertIs(renamed.values, original.values)
        values = np.array([7, 8], dtype=object)
        values.flags.writeable = False
        changed = original._with_changes(values=values)
        values.flags.writeable = True
        values[:] = 99
        self.assertEqual(changed.values.tolist(), [7, 8])
        self.assertEqual(original.values.tolist(), [1, 2])
        for changes in (
            {"values": [True, False]}, {"values": [2**4097, 0]},
            {"values": [1]}, {"positions": [[1, 2, 3]]},
            {"positions": [[float("nan"), 0], [1, 0]]},
            {"fields": {"key": [0]}}, {"parents": [(Ref("x", "a"),)]},
        ):
            with self.subTest(changes=tuple(changes)):
                with self.assertRaises(ValueError):
                    original._with_changes(**changes)
        with self.assertRaises(TypeError):
            original._with_changes(unknown=True)

    def test_mutable_field_elements_and_references_are_rejected(self):
        mutable = np.empty(1, dtype=object)
        mutable[0] = {"not": "a scalar"}
        with self.assertRaisesRegex(ValueError, "scalar"):
            Snapshot("root", [1], ("a",), ("a",), {"bad": mutable})
        with self.assertRaises(ValueError):
            Ref("root", ["mutable"])

    def test_cases_empty_results_and_captured_history_keep_their_meaning(self):
        source = Collection.sequence(param("n")).arrange(F.value, 0)
        bound = source.with_params(n=3)
        counts = bound.where(F.value % 2 == 0).count(by=F.s)
        workspace = Workspace({"points": bound, "counts": counts}, {"n": 0})
        before = workspace.state
        forward = workspace.set("points", bound.move(vector(1, 2)), motion=Motion.arc())
        workspace.undo()
        with patch.object(Evaluator, "_execute", side_effect=AssertionError("use retained state")):
            reopened = Workspace.from_json(workspace.to_json())
            backward = reopened.redo().reverse()
            np.testing.assert_array_equal(forward.frame("points", .75).positions,
                                          backward.frame("points", .25).positions)
        self.assertEqual(workspace.state.results["counts"].values.tolist(), [0, 1, 0])
        self.assertEqual(workspace.state.results["counts"].contributor_ids(0), ())
        self.assertIs(workspace.state, before)
        empty = source.evaluate(n=0)
        renamed = empty._with_changes(node="empty case")
        self.assertIs(renamed.values, empty.values)
        self.assertEqual(renamed.positions.shape, (0, 2))


if __name__ == "__main__":
    unittest.main()
