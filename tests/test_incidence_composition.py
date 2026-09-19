"""Composition must retain the universe and each predicate's parameter scope."""

import json
import unittest
from unittest.mock import patch

import numpy as np

from kaleion import (
    Arrangement, Collection, EvaluationError, Evaluator, F, Incidence,
    Workspace, graph, load_graph, param, wrap,
)


class IncidenceCompositionTests(unittest.TestCase):
    def test_bound_boolean_operations_and_selection(self):
        source = Collection.sequence(4).arrange(F.value, 0)
        incidence = source.where(F.value > param("n")).with_params(n=2)
        self.assertEqual((~incidence).evaluate().mask.tolist(), [True, True, False, False])
        self.assertEqual((incidence & incidence).evaluate().cardinality, 2)
        self.assertEqual((incidence | ~incidence).count().evaluate().values.tolist(), [4])
        selected = incidence.select()
        self.assertIsInstance(selected, Arrangement)
        result = selected.evaluate()
        self.assertEqual(result.values.tolist(), [3, 4])
        self.assertEqual(result.ids, source.evaluate().ids[2:])
        np.testing.assert_array_equal(result.positions, [[3, 0], [4, 0]])
        self.assertEqual(selected.where(F.value % 2 == 0).count().evaluate().values.tolist(), [1])

    def test_nested_bindings_keep_shape_predicate_and_driver_scopes(self):
        n, outer = param("n"), param("outer")
        source = Collection.sequence(n).arrange(F.value, 0)
        driver = Collection.literal([1]).with_values(F.value + n)
        rule = F.value >= driver.scalar() - 2
        # The outer case sets n=9. The inner case reads outer=3, then n=4.
        def bind(incidence):
            return incidence.with_params(n=outer + 1).with_params(outer=3, n=9)

        high = bind(source.where(rule))
        even = bind(source.where(F.value % 2 == 0))
        self.assertEqual((~high & even).select().evaluate(n=100).values.tolist(), [2])
        self.assertEqual((~high | even).evaluate(n=100).cardinality, 3)
        self.assertTrue(high.universe.same_definition(bind(source)))
        self.assertEqual(high.universe.evaluate().values.tolist(), [1, 2, 3, 4])
        # Moving the reduction outside the case does not move the predicate.
        self.assertEqual((~high).sum(value=F.value + n).evaluate(n=10).values.tolist(), [23])
        self.assertEqual((~high & even).with_params(n=0).select().evaluate().values.tolist(), [2])
        length = Collection.literal([3]).with_values(F.value + param("extra")).scalar()
        measured_case = source.where(F.value % 2 == 0).with_params(n=length).with_params(extra=1)
        self.assertEqual((~measured_case).select().evaluate(extra=99).values.tolist(), [1, 3])

    def test_same_scoped_universe_can_have_predicates_in_different_scopes(self):
        source = Collection.sequence(param("n"))
        inside = source.where(F.value < param("n")).with_params(n=4)
        outside = source.with_params(n=4).where(F.value > param("n"))
        self.assertTrue(inside.universe.same_definition(outside.universe))
        self.assertEqual((inside & outside).select().evaluate(n=2).values.tolist(), [3])
        self.assertEqual((outside & inside).select().evaluate(n=2).values.tolist(), [3])
        self.assertEqual((inside | outside).evaluate(n=2).cardinality, 4)
        selected = (inside & outside).select()
        self.assertIsInstance(selected, Collection)
        self.assertNotIsInstance(selected, (Arrangement, Incidence))
        self.assertIsNone(selected.evaluate(n=2).positions)

    def test_different_declared_universes_require_explicit_reconstruction(self):
        source = Collection.sequence(param("n"))
        four = source.where(True).with_params(n=4)
        for other in (
            source.where(True).with_params(n=3),
            Collection.sequence(param("n")).where(True).with_params(n=4),
            source.with_values(F.value + 1).where(True).with_params(n=4),
        ):
            with self.subTest(other=other.node.op):
                with self.assertRaisesRegex(ValueError, "same declared universe"):
                    four & other
                with self.assertRaisesRegex(ValueError, "same declared universe"):
                    four | other
        with self.assertRaises(TypeError):
            four & source

    def test_empty_cases_and_failed_predicates_do_not_become_false(self):
        source = Collection.grid(3, param("n"), values=1).arrange(F.i, F.j)
        empty = source.where(True).with_params(n=0)
        self.assertEqual((~empty | empty).count(by=F.i).evaluate().values.tolist(), [0, 0, 0])
        self.assertEqual((~empty).select().evaluate().positions.shape, (0, 2))
        good = source.where(True).with_params(n=1)
        bad = source.where(F.value % 0 == 0).with_params(n=1)
        results, errors = Evaluator().run({"good": good, "bad": good | bad})
        self.assertEqual(results["good"].cardinality, 3)
        self.assertIn("bad", errors)
        with self.assertRaises(EvaluationError):
            (~bad).evaluate()

    def test_graph_and_captured_history_roundtrip(self):
        source = Collection.sequence(4).arrange(F.value, 0)
        low = source.where(F.value <= param("limit")).with_params(limit=2)
        even = source.where(F.value % 2 == 0).with_params(limit=2)
        combined = (~low | even) & ~low
        encoded = json.loads(json.dumps(graph({"mask": combined.node, "items": combined.select().node})))
        restored = {name: wrap(node) for name, node in load_graph(encoded).items()}
        self.assertTrue(restored["mask"].same_definition(combined))
        self.assertEqual(restored["items"].evaluate().values.tolist(), [3, 4])
        workspace = Workspace({"mask": low, "counts": low.count(by=F.s)})
        forward = workspace.set("mask", combined)
        workspace.undo()
        payload = workspace.to_json()
        with patch.object(Evaluator, "_execute", side_effect=AssertionError("must use captures")):
            reopened = Workspace.from_json(payload)
            replay = reopened.redo()
            np.testing.assert_array_equal(replay.frame("mask", 0.5).positions,
                                          forward.frame("mask", 0.5).positions)
        self.assertEqual(reopened.state.results["mask"].mask.tolist(), [False, False, True, True])
        counts = reopened.state.results["counts"]
        self.assertEqual(counts.values.tolist(), [1, 1, 0, 0])
        self.assertEqual(counts.contributor_ids(2), ())


if __name__ == "__main__":
    unittest.main()
