"""Offline presentation contracts; Plotly checks are optional, no browser needed."""

import importlib.util
import unittest

import numpy as np

from kaleion import Arrangement, Collection, F, Motion, Workspace
from kaleion.viewers._display import CHANGING, MATCH, MISS, NEUTRAL, prepare

HAS_PLOTLY = importlib.util.find_spec("plotly") is not None
if HAS_PLOTLY:
    from kaleion.viewers.plotly import animation_figure, snapshot_figure, transition_figure


class DisplayContracts(unittest.TestCase):
    def test_large_integer_labels_are_exact_and_unplaced_data_is_rejected(self):
        values = [2**80 + 1, 2**80 + 2]
        items = Collection.literal(values)
        with self.assertRaisesRegex(ValueError, "placement"):
            prepare(items.evaluate())
        shown = prepare(items.arrange(F.index).evaluate())
        self.assertEqual(shown.labels, tuple(map(str, values)))
        np.testing.assert_array_equal(shown.positions, [[0, 0], [1, 0]])
        self.assertTrue(all(str(v) in h for v, h in zip(values, shown.hover)))

    def test_unfiltered_false_and_true_membership_are_distinct(self):
        arrangement = Collection.sequence(3).arrange(F.s, 0)
        self.assertEqual(prepare(arrangement.evaluate()).colors, (NEUTRAL,) * 3)
        self.assertEqual(prepare(arrangement.where(F.value % 2 == 0).evaluate()).colors,
                         (MISS, MATCH, MISS))

    def test_changed_labels_are_discrete_and_undo_uses_original_path_fraction(self):
        arrangement = Collection.sequence(1, start=7).arrange(0, 0)
        workspace = Workspace({"a": arrangement})
        forward = workspace.set("a", arrangement.with_values(12))
        undo = workspace.undo()
        self.assertEqual(prepare(forward.frame("a", 0)).labels, ("7",))
        self.assertEqual(prepare(forward.frame("a", 1)).labels, ("12",))
        self.assertEqual(prepare(forward.frame("a", 0.25)).labels, ("7 → 12",))
        self.assertEqual(prepare(undo.frame("a", 0.75)).labels, ("7 → 12",))
        self.assertEqual(prepare(undo.frame("a", 1)).labels, ("7",))

    def test_membership_changes_and_creation_opacity_survive_rendering(self):
        arrangement = Collection.sequence(2).arrange(F.s, 0)
        workspace = Workspace({"a": arrangement.where(F.value == 1)})
        change = workspace.set("a", arrangement.where(F.value == 2))
        self.assertEqual(prepare(change.frame("a", 0.5)).colors, (CHANGING, CHANGING))
        self.assertEqual(prepare(change.frame("a", 1)).colors, (MISS, MATCH))
        created = Workspace().set("a", arrangement)
        np.testing.assert_array_equal(prepare(created.frame("a", 0)).opacity, [0, 0])
        np.testing.assert_array_equal(prepare(created.frame("a", 1)).opacity, [1, 1])


@unittest.skipUnless(HAS_PLOTLY, "Install kaleion[notebooks] for Plotly adapter tests")
class PlotlyContracts(unittest.TestCase):
    def test_plotly_serialization_does_not_round_exact_labels(self):
        value = 2**80 + 1
        fig = snapshot_figure(Collection.literal([value]).arrange(0, 0).evaluate())
        self.assertIn(str(value), fig.to_json())
        self.assertIn(str(value), fig.data[0].hovertext[0])

    def test_motion_bounds_include_midpoint_and_keep_reversed_endpoints(self):
        source = Arrangement.points([1], [(0, 0)])
        workspace = Workspace({"a": source})
        workspace.set("a", source.place(2, 0), motion=Motion.arc(height=3))
        undo = workspace.undo()
        fig = transition_figure(undo, "a", steps=3)
        self.assertLess(fig.layout.yaxis.range[0], 0)
        self.assertGreater(fig.layout.yaxis.range[1], 3)
        self.assertEqual(tuple(fig.frames[0].data[0].x), (2.0,))
        self.assertEqual(tuple(fig.frames[-1].data[0].x), (0.0,))
        self.assertEqual(fig.frames[1].data[0].y[0], 3.0)

    def test_empty_and_3d_views_and_dimension_mismatch(self):
        empty = Collection.sequence(0).arrange(F.s, 0).evaluate()
        self.assertEqual(len(snapshot_figure(empty).data[0].x), 0)
        space = Arrangement.points([1], [(1, 2, 3)]).evaluate()
        self.assertEqual(snapshot_figure(space).data[0].type, "scatter3d")
        with self.assertRaisesRegex(ValueError, "dimension"):
            animation_figure([empty, space])
        with self.assertRaisesRegex(ValueError, "one label"):
            animation_figure([empty], labels=[])

    def test_failed_evaluation_is_marked_in_retained_geometry(self):
        arrangement = Collection.sequence(2).arrange(F.s, 0)
        workspace = Workspace({"a": arrangement})
        transition = workspace.set("a", arrangement.with_values(F.value // 0))
        self.assertIn("a", workspace.state.errors)
        fig = transition_figure(transition, "a", steps=2)
        self.assertIn("failed operation", fig.layout.title.text)
        self.assertIn("failed operation", fig.frames[-1].layout.title.text)


if __name__ == "__main__":
    unittest.main()
