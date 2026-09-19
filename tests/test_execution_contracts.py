"""Work-sharing regressions checked against independent finite results."""

import unittest
from unittest.mock import patch

import numpy as np

from kaleion import Collection, Evaluator, F, Motion, Transition, Workspace, choose, param, vector
from kaleion.expressions import evaluate_expression


class ExecutionContracts(unittest.TestCase):
    def test_grouped_contributors_preserve_order_zeros_and_signed_weights(self):
        source = Collection.literal(
            [0, -5, 7, 2, 2**80, 4, 99], fields={"group": [2, 1, 2, 0, 1, 3, 4]}
        )
        incidence = source.where(F.index != 6)
        counts = incidence.count(by=F.group).evaluate()
        sums = incidence.sum(by=F.group).evaluate()
        self.assertEqual(counts.fields["key"].tolist(), [2, 1, 0, 3, 4])
        self.assertEqual(counts.values.tolist(), [2, 2, 1, 1, 0])
        self.assertEqual(sums.values.tolist(), [7, 2**80 - 5, 2, 4, 0])
        ids = source.evaluate().ids
        expected = {2: (ids[0], ids[2]), 1: (ids[1], ids[4]), 0: (ids[3],), 3: (ids[5],), 4: ()}
        for result in (counts, sums):
            for key, contributors in expected.items():
                self.assertEqual(result.contributor_ids(key), contributors)
            self.assertEqual(tuple(tuple(ref.occurrence for ref in group) for group in result.parents),
                             tuple(expected.values()))

    def test_motion_prepares_once_for_validation_playback_and_undo(self):
        source = Collection.sequence(5, start=10).arrange(F.index, 0)
        target = (source.items.gather([3, 1, 3, 0]).with_values(F.value * 10)
                  .gather([2, 0, 1]).arrange(F.index, 2))
        workspace = Workspace({"points": source.where(F.value % 2 == 0)})
        original = Transition._prepare_tracks
        prepared = []

        def prepare(transition, name):
            prepared.append(name)
            return original(transition, name)

        with patch.object(Transition, "_prepare_tracks", prepare):
            forward = workspace.set("points", target.where(F.value >= 130), motion=Motion.arc(height=2))
            reverse = workspace.undo()
            with patch.object(Evaluator, "_execute", side_effect=AssertionError("playback must use captures")):
                for t in np.linspace(0, 1, 21):
                    a, b = forward.frame("points", t), reverse.frame("points", 1 - t)
                    np.testing.assert_allclose(a.positions, b.positions, atol=1e-12, rtol=0)
                    np.testing.assert_allclose(a.opacity, b.opacity, atol=1e-12, rtol=0)
                    self.assertEqual(a.label_pairs, b.label_pairs)
                    self.assertEqual(a.matched_before, b.matched_before)
                    self.assertEqual(a.matched_after, b.matched_after)
                workspace.redo().validate()
            self.assertEqual(prepared, ["points"])
        start = forward.frame("points", 0)
        end = forward.frame("points", 1)
        np.testing.assert_array_equal(start.positions, [[3, 0], [3, 0], [1, 0], [0, 0], [2, 0], [4, 0]])
        np.testing.assert_array_equal(end.positions[:3], [[0, 2], [1, 2], [2, 2]])
        self.assertEqual(end.opacity.tolist(), [1, 1, 1, 0, 0, 0])
        self.assertEqual(start.values_before, (13, 13, 11, 10, 12, 14))
        self.assertEqual(end.values_after, (130, 130, 110, None, None, None))
        self.assertEqual(start.matched_before, (False, False, False, True, True, True))
        self.assertEqual(end.matched_after, (True, True, False, None, None, None))
        np.testing.assert_array_equal(forward.frame("points", 0.5).positions[:3, 1], [3, 3, 3])

    def test_captured_motion_owns_the_path_and_motion_mapping(self):
        source = Collection.sequence(1).arrange(0, 0)
        workspace = Workspace({"point": source})
        captured = workspace.set("point", source.move(vector(2, 0)))
        t = param("time")
        path = [(1 - t) * F.sx + t * F.tx, (1 - t) * F.sy + t * F.ty + 4 * t * (1 - t)]
        motions = {"point": Motion(path)}
        transition = Transition(captured.before, captured.after, motions)
        reverse = transition.reverse()  # Also share work if reversed before first sample.
        path[1] = F.sy
        motions["point"] = Motion()
        np.testing.assert_array_equal(transition.frame("point", 0.5).positions, [[1, 1]])
        np.testing.assert_array_equal(reverse.frame("point", 0.5).positions, [[1, 1]])
        with self.assertRaises(TypeError):
            transition.motions["point"] = Motion()

    def test_field_interpreter_uses_injected_sources_and_retains_eager_errors(self):
        driver = Collection.literal([2**80, 7], keys=[1, 0])
        captured = driver.evaluate()
        requested = []

        def resolve(node):
            requested.append(node.id)
            return captured

        result = evaluate_expression(driver.bind(on=F.key) + 1,
                                     {"key": [0, 1]}, {}, resolve, length=2)
        self.assertEqual(result.tolist(), [8, 2**80 + 1])
        self.assertEqual(requested, [driver.node.id])
        with self.assertRaises(ArithmeticError):
            evaluate_expression(choose(True, 1, 1 // param("zero")), {}, {"zero": 0}, resolve)
        with self.assertRaisesRegex(ValueError, "external drivers"):
            Motion.custom(driver.scalar()).positions(np.zeros((1, 1)), np.zeros((1, 1)), 0.5)


if __name__ == "__main__":
    unittest.main()
