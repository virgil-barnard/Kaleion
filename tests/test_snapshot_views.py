"""Independent contracts for the lesson-only captured-data adapters; no Plotly."""

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np

from kaleion import Collection, F, Workspace
from kaleion.model import Snapshot

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "notebooks"))
try:
    from snapshot_views import compare_keyed_values, keyed_values, rectangular_values
finally:
    sys.path.pop(0)


def captured(values, **fields):
    ids = tuple(f"point-{i}" for i in range(len(values)))
    return Snapshot("fixture", np.array(values, dtype=object), ids, ids,
                    fields={name: np.array(items, dtype=object) for name, items in fields.items()},
                    positions=np.zeros((len(values), 3)))


class SnapshotViewsTests(unittest.TestCase):
    def test_named_axes_ignore_storage_order_and_coincident_placement(self):
        source = captured([23, 0, 13, 21], u=[20, 10, 10, 20], v=[3, 1, 3, 1])
        expected = ([10, 20], [1, 3], [[0, 21], [13, 23]])
        self.assertEqual(rectangular_values(source, x="u", y="v"), expected)
        shuffled = captured([21, 13, 0, 23], u=[20, 10, 10, 20], v=[1, 3, 1, 3])
        self.assertEqual(rectangular_values(shuffled, x="u", y="v"), expected)
        self.assertEqual(rectangular_values(source, x="v", y="u"),
                         ([1, 3], [10, 20], [[0, 13], [21, 23]]))

    def test_exact_values_and_composite_keys_are_not_cast_to_fixed_width(self):
        big = 2**100 + 3
        source = captured([big, -big, 0], a=[big, -big, 0], b=[2, 1, 0], c=[7, 7, 7])
        data = keyed_values(source, keys=("a", "b", "c"))
        self.assertEqual(data, {(big, 2, 7): big, (-big, 1, 7): -big, (0, 0, 7): 0})
        self.assertEqual(list(data), [(big, 2, 7), (-big, 1, 7), (0, 0, 7)])
        self.assertTrue(all(type(v) is int for v in data.values()))
        self.assertEqual(keyed_values(source, keys=("a",)), {(big,): big, (-big,): -big, (0,): 0})
        self.assertEqual(rectangular_values(source, x="a", y="c"),
                         ([-big, 0, big], [7], [[-big, 0, big]]))

    def test_duplicate_keys_fail_even_when_values_agree(self):
        for values in ([0, 0], [1, 2]):
            with self.subTest(values=values):
                source = captured(values, u=[1, 1], v=[2, 2])
                with self.assertRaisesRegex(ValueError, "Duplicate key.*1, 2"):
                    keyed_values(source, keys=("u", "v"))
                with self.assertRaisesRegex(ValueError, "Duplicate key"):
                    rectangular_values(source, x="u", y="v")

    def test_missing_cell_is_not_filled_with_zero(self):
        source = captured([0, 3, 4], u=[0, 0, 1], v=[0, 1, 0])
        self.assertEqual(keyed_values(source, keys=("u", "v"))[(0, 0)], 0)
        with self.assertRaisesRegex(ValueError, "missing key.*1, 1.*absent is not zero"):
            rectangular_values(source, x="u", y="v")

    def test_observed_domain_does_not_invent_an_absent_axis_label(self):
        source = captured([0, 2], u=[0, 2], v=[7, 7])
        self.assertEqual(rectangular_values(source, x="u", y="v"),
                         ([0, 2], [7], [[0, 2]]))
        empty = captured([], u=[], v=[])
        self.assertEqual(keyed_values(empty, keys=("u", "v")), {})
        self.assertEqual(rectangular_values(empty, x="u", y="v"), ([], [], []))
        with self.assertRaisesRegex(ValueError, "Missing key field"):
            rectangular_values(empty, x="u", y="absent")

    def test_invalid_key_declarations_and_noninteger_keys_fail(self):
        source = captured([3], u=[0], v=[1])
        for keys in ((), ("u", "u"), ("",), (3,), ("missing",)):
            with self.subTest(keys=keys), self.assertRaises(ValueError):
                keyed_values(source, keys=keys)
        for keys in ("u", {"u", "v"}, None):
            with self.subTest(keys=keys), self.assertRaises(TypeError):
                keyed_values(source, keys=keys)
        with self.assertRaisesRegex(ValueError, "distinct"):
            rectangular_values(source, x="u", y="u")
        for key in (0.0, 0.5, True, np.bool_(False), "0", None):
            with self.subTest(key=key), self.assertRaisesRegex(TypeError, "exact integers"):
                keyed_values(captured([3], u=[key]), keys=("u",))
        with self.assertRaisesRegex(TypeError, "captured Snapshot"):
            keyed_values(Collection.sequence(1), keys=("s",))

    def test_adapters_do_not_evaluate_or_mutate_captured_measurements(self):
        domain = Collection.grid(2, 3, 2)
        counts = domain.where(F.k < F.i).count(by=(F.i, F.j))
        workspace = Workspace({"counts": counts})
        saved = workspace.to_json()
        incidence = domain.where(F.k == 0).evaluate()
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("reevaluation")):
            snapshot = Workspace.from_json(saved).state.results["counts"]
            before = snapshot.contributor_ids((1, 2))
            data = keyed_values(snapshot, keys=("i", "j"))
            xs, ys, rows = rectangular_values(snapshot, x="i", y="j")
            self.assertEqual((xs, ys, rows), ([0, 1], [0, 1, 2], [[0, 1], [0, 1], [0, 1]]))
            self.assertEqual(snapshot.contributor_ids((0, 2)), ())
            self.assertEqual(len(before), 1)
            data[(1, 2)] = -9
            rows[2][1] = -8
            xs.append(99)
            self.assertEqual(snapshot.values.tolist(), [0, 0, 0, 1, 1, 1])
            self.assertEqual(snapshot.contributor_ids((1, 2)), before)
            with self.assertRaises(TypeError):
                keyed_values(incidence, keys=("i", "j"))
        self.assertEqual(workspace.to_json(), saved)

    def test_comparison_aligns_distinct_fields_and_reports_exact_residuals(self):
        big = 2**100 + 7
        left = captured([0, big, -4], u=[2, 0, 1], v=[9, 9, 9])
        right = captured([-7, 0, big], x=[1, 2, 0], y=[9, 9, 9])
        report = compare_keyed_values(left, right, left_keys=("u", "v"),
                                      right_keys=("x", "y"))
        self.assertEqual(report.domain, ((2, 9), (0, 9), (1, 9)))
        self.assertTrue(report.same_domain)
        self.assertFalse(report.holds)
        self.assertEqual([(item.key, item.residual) for item in report.nonzero],
                         [((1, 9), 3)])
        self.assertEqual(report.to_dict()["residual"], "left - right")
        self.assertEqual(report.to_dict()["nonzero"],
                         [{"key": [1, 9], "left": -4, "right": -7, "residual": 3}])

    def test_explicit_domain_separates_missing_unexpected_and_zero(self):
        left = captured([0, 8, 99], u=[0, 2, 9], v=[0, 0, 9])
        right = captured([0, 4, 5], u=[0, 1, 2], v=[0, 0, 0])
        report = compare_keyed_values(
            left, right, left_keys=("u", "v"), domain=((0, 0), (1, 0), (2, 0)))
        self.assertEqual(report.missing_left, ((1, 0),))
        self.assertEqual(report.missing_right, ())
        self.assertEqual(report.unexpected_left, ((9, 9),))
        self.assertEqual(report.unexpected_right, ())
        self.assertEqual([(x.key, x.residual) for x in report.differences],
                         [((0, 0), 0), ((2, 0), 3)])
        self.assertFalse(report.same_domain)
        self.assertFalse(report.values_equal_on_common)
        self.assertFalse(report.holds)

    def test_expected_domain_exposes_a_row_missing_from_both_snapshots(self):
        left = captured([0, 1], u=[0, 1], v=[0, 0])
        right = captured([0, 1], u=[0, 1], v=[0, 0])
        observed = compare_keyed_values(left, right, left_keys=("u", "v"))
        self.assertTrue(observed.holds)
        declared = compare_keyed_values(
            left, right, left_keys=("u", "v"),
            domain=((0, 0), (1, 0), (0, 1), (1, 1)))
        self.assertEqual(declared.missing_left, ((0, 1), (1, 1)))
        self.assertEqual(declared.missing_right, ((0, 1), (1, 1)))
        self.assertTrue(declared.values_equal_on_common)
        self.assertFalse(declared.holds)

    def test_comparison_domain_validation_and_empty_cases(self):
        empty = captured([], u=[], v=[])
        inferred = compare_keyed_values(empty, empty, left_keys=("u", "v"))
        self.assertTrue(inferred.holds)
        self.assertEqual(inferred.domain, ())
        explicit = compare_keyed_values(empty, empty, left_keys=("u", "v"), domain=())
        self.assertTrue(explicit.holds)
        self.assertTrue(explicit.explicit_domain)
        one = captured([3], u=[0], v=[1])
        invalid = ({(0, 1)}, ((0,),), ((0, 1), (0, 1)), ((True, 1),), ((0.5, 1),))
        for domain in invalid:
            with self.subTest(domain=domain), self.assertRaises((TypeError, ValueError)):
                compare_keyed_values(one, one, left_keys=("u", "v"), domain=domain)
        with self.assertRaisesRegex(ValueError, "same number"):
            compare_keyed_values(one, one, left_keys=("u",), right_keys=("u", "v"))

    def test_comparison_reads_reopened_snapshots_without_evaluation(self):
        source = Collection.grid(3, 2, values=F.i - F.j).annotate(u=F.i, v=F.j)
        workspace = Workspace({"left": source, "right": source.with_values(F.value)})
        payload = workspace.to_json()
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("reevaluation")):
            restored = Workspace.from_json(payload)
            report = compare_keyed_values(
                restored.state.results["left"], restored.state.results["right"],
                left_keys=("u", "v"), domain=tuple((u, v) for u in range(3) for v in range(2)))
            self.assertTrue(report.holds)
            self.assertEqual(len(report.differences), 6)
        self.assertEqual(workspace.to_json(), payload)


if __name__ == "__main__":
    unittest.main()
