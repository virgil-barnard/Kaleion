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
    from snapshot_views import keyed_values, rectangular_values
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


if __name__ == "__main__":
    unittest.main()
