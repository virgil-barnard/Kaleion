"""Independent quotient constructions, keyed addition, and captured evidence."""
from math import gcd
import unittest
from unittest.mock import patch

import numpy as np

from kaleion import Inspection, Workspace
from kaleion.comparison import keyed_items
from examples.quotient_equality import quotient_equality
from examples.studio.adapter import Studio


class QuotientEqualityTests(unittest.TestCase):
    def report(self, workspace):
        studio = Studio()
        studio.workspace = workspace
        return studio.compare("Moving cover", ["i", "j"], "value", "Independent ones",
                              ["i", "j"], "value", "Independent ones", ["i", "j"], 0)

    def test_finite_cases_match_independent_floor_sums_and_overlap_correction(self):
        for a, b in [(7, 5), (11, 7), (6, 4), (9, 6), (4, 4), (2, 2), (1, 5)]:
            with self.subTest(a=a, b=b):
                workspace = quotient_equality(a, b)
                self.assertFalse(workspace.state.errors)
                result = workspace.state.results
                np.testing.assert_array_equal(result["Column quotients"].values,
                                              [a * i // b for i in range(1, b)])
                np.testing.assert_array_equal(result["Row quotients"].values,
                                              [b * j // a for j in range(1, a)])
                report = self.report(workspace)
                self.assertEqual(report["passed"], gcd(a, b) == 1)
                self.assertEqual(int(report["summary"]["different"]), gcd(a, b) - 1)
                self.assertEqual(sum(result["Equality residual"].values), gcd(a, b) - 1)
                self.assertEqual(result["Counted area"].values[0], (a-1)*(b-1)+gcd(a,b)-1)
                for row in report["rows"]:
                    i, j = map(int, row["key"])
                    expected = 1 + int(a * (i+1) == b * (j+1))
                    self.assertEqual(int(row["left"]), expected)
                    self.assertEqual(row["right"], "1")
                if a == 1:
                    self.assertTrue(report["empty"])

    def test_keys_align_reversed_storage_and_independent_occurrences(self):
        result = quotient_equality().state.results
        a, b = result["Lower cells"], result["Upper cells"]
        self.assertNotEqual(list(keyed_items(a, keys=("i","j"))), list(keyed_items(b, keys=("i","j"))))
        left, right = result["Moving cover"], result["Independent ones"]
        self.assertTrue(set(left.ids).isdisjoint(right.ids))
        self.assertTrue(np.all(left.values == 1))
        self.assertTrue(np.all(right.values == 1))

    def test_zero_membership_and_both_overlap_contributors_are_inspectable(self):
        workspace = quotient_equality(6, 4)
        inspector = Inspection(workspace.state)
        for name in ("Lower cells", "Upper cells"):
            ref = inspector.find(name, (1, 2), by=("i", "j"))
            self.assertEqual(inspector.measurement(ref).contributor_count, 1)
        zero = inspector.find("Lower cells", (0, 4), by=("i", "j"))
        self.assertEqual(inspector.item(zero).value, 0)
        self.assertEqual(inspector.measurement(zero).contributor_count, 0)
        overlap = [r for r in self.report(workspace)["rows"] if r["status"] == "different"]
        self.assertEqual([(r["key"], r["residual"]) for r in overlap], [(["1", "2"], "1")])

    def test_saved_case_evidence_and_reverse_motion_need_no_evaluation(self):
        workspace = quotient_equality()
        expected = workspace.state.results["Moving cover"]
        workspace.set_parameters(a=6, b=4)
        payload = workspace.to_json()
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
            restored = Workspace.from_json(payload)
            self.assertFalse(self.report(restored)["passed"])
            restored.undo()
            self.assertTrue(self.report(restored)["passed"])
            np.testing.assert_array_equal(restored.state.results["Moving cover"].positions, expected.positions)
            reverse = restored.undo()
            forward = restored.redo()
            for t in (0, .25, 1):
                a = reverse.frame("Moving cover", t)
                b = forward.frame("Moving cover", 1-t)
                np.testing.assert_allclose(a.positions, b.positions, atol=1e-12)
            restored.redo()
            self.assertFalse(self.report(restored)["passed"])


if __name__ == "__main__":
    unittest.main()
