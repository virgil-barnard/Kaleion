"""Independent arithmetic, lineage, and saved-motion checks for lesson 12."""

import math
import unittest
from unittest.mock import patch

import numpy as np

from kaleion import Collection, F, Inspection, Workspace
from kaleion.comparison import compare_keyed_values
from examples.residue_fibers import residue_definitions, residue_fibers
from examples.studio.coverage import unique_assignment


class ResidueFiberTests(unittest.TestCase):
    def test_counts_ranks_and_copies_in_coprime_nonunit_and_singleton_cases(self):
        for a, b in [(7, 5), (6, 4), (6, 6), (1, 5), (5, 1), (1, 1)]:
            with self.subTest(a=a, b=b):
                w = residue_fibers(a=a, b=b)
                self.assertFalse(w.state.errors)
                s = w.state.results
                d, length = math.gcd(a, b), math.lcm(a, b)
                self.assertEqual(s["Kernel size"].values.tolist(), [d])
                self.assertEqual(s["Period"].values.tolist(), [length])
                expected = [sum(n % a == r and n % b == t for n in range(a*b))
                            for r in range(a) for t in range(b)]
                self.assertEqual(s["Fiber sizes"].values.tolist(), expected)
                self.assertEqual(s["Predicted sizes"].values.tolist(), expected)
                self.assertEqual(s["Ranks"].values.tolist(), [n // length for n in range(a*b)])
                self.assertEqual(s["Copied sheets"].values.tolist(), list(range(a*b)))
                self.assertEqual(s["Copied sheets"].fields["n"].tolist(), list(range(length))*d)
                self.assertTrue(set(s["Copied sheets"].ids).isdisjoint(s["Integer line"].ids))
                self.assertEqual(len(set(s["Copied sheets"].ids)), a*b)

    def test_zero_fibers_are_present_and_naive_bijection_has_explicit_witnesses(self):
        w = residue_fibers()
        s, inspect = w.state.results, Inspection(w.state)
        domain = [(r, t) for r in range(6) for t in range(4)]
        report = compare_keyed_values(s["Fiber sizes"], s["Pair domain"],
                                      left_keys=("r", "s"), right_keys=("r", "s"), domain=domain)
        self.assertTrue(report.same_domain)
        self.assertEqual(len(report.nonzero), 24)
        self.assertEqual({x.residual for x in report.nonzero}, {-1, 1})
        occupied = inspect.measurement(inspect.find("Fiber sizes", (0, 0), by=("r", "s")))
        empty = inspect.measurement(inspect.find("Fiber sizes", (0, 1), by=("r", "s")))
        self.assertEqual([c.item.fields["n"] for c in occupied.contributors], [0, 12])
        self.assertEqual((empty.item.value, empty.contributor_count, empty.population), (0, 0, 24))
        # A tempting inverse over every pair fails without harming the evidence.
        roots = w.state.roots
        inverse = unique_assignment(roots["Remainder relation"], ["r", "s"],
                                    roots["Pair domain"], ["r", "s"], F.n, "address")
        w.set("Proposed inverse", inverse)
        self.assertEqual(set(w.state.errors), {"Proposed inverse"})
        w.set_parameters(a=7, b=5)
        self.assertFalse(w.state.errors)
        self.assertEqual(sorted(w.state.results["Proposed inverse"].fields["address"].tolist()), list(range(35)))

    def test_measured_rank_read_and_kernel_count_remain_inspectable(self):
        w = residue_fibers()
        w.undo()  # The placed state before Roll has pointwise rank bindings.
        inspect = Inspection(w.state)
        reads = inspect.bindings(inspect.find("Moving residues", 13, by=("n",)))
        receipt = inspect.measurement(reads[0].driver)
        self.assertEqual((receipt.item.value, receipt.contributor_count), (1, 1))
        self.assertEqual(receipt.contributors[0].item.value, 1)
        period_reads = inspect.bindings(inspect.find("Predicted sizes", (0, 0), by=("r", "s")))
        kernel = inspect.measurement(period_reads[0].driver)
        self.assertEqual([c.item.value for c in kernel.contributors], [0, 12])

    def test_kernel_action_preserves_residues_and_cycles_the_same_occurrences(self):
        w = residue_fibers()
        end = w.state.results["Moving residues"]
        w.undo()
        start = w.state.results["Moving residues"]
        self.assertEqual(set(start.ids), set(end.ids))
        end_by_id = {oid: i for i, oid in enumerate(end.ids)}
        for i, oid in enumerate(start.ids):
            j = end_by_id[oid]
            self.assertEqual(end.values[j], start.values[i])
            self.assertEqual(end.fields["n"][j], (int(start.values[i]) + 12) % 24)
            np.testing.assert_array_equal(end.positions[j, :2], start.positions[i, :2])
            self.assertEqual(end.positions[j, 2], 1 - start.positions[i, 2])

    def test_hidden_carry_separates_set_coordinates_from_group_addition(self):
        definitions = residue_definitions()
        length = definitions["Period"].bind(on=0)
        # Exhaust all original-group additions; no chart position is an input.
        pairs = Collection.grid(24, 24, values=(F.i + F.j) % 24)
        t, u, h, k = F.i % length, F.j % length, F.i // length, F.j // length
        with_carry = pairs.with_values((t+u) % length + length*((h+k+(t+u)//length) % 2))
        naive = pairs.with_values((t+u) % length + length*((h+k) % 2))
        w = Workspace({"Sum": pairs, "Carry": with_carry, "Naive": naive}, {"a": 6, "b": 4})
        np.testing.assert_array_equal(w.state.results["Sum"].values, w.state.results["Carry"].values)
        self.assertEqual(w.state.results["Naive"].values[11*24+1], 0)
        self.assertEqual(w.state.results["Sum"].values[11*24+1], 12)

    def test_saved_reverse_uses_captured_paths_and_retains_copy_ancestry(self):
        saved = residue_fibers().to_json()
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
            w = Workspace.from_json(saved)
            inspect = Inspection(w.state)
            # Follow the lifted value/annotation/tile chain to the original period.
            item = inspect.item(inspect.find("Copied sheets", 12, by=("value",)))
            ancestors = []
            while len(item.parents) == 1:
                item = inspect.item(item.parents[0]); ancestors.append(item.value)
            self.assertIn(0, ancestors)
            reverse = [w.undo() for _ in range(3)]
            for back in reversed(reverse):
                forward = w.redo()
                for t in (0, .25, .5, 1):
                    np.testing.assert_allclose(back.frame("Moving residues", t).positions,
                                               forward.frame("Moving residues", 1-t).positions,
                                               rtol=0, atol=1e-12)
            self.assertEqual(w.to_json(), saved)


if __name__ == "__main__":
    unittest.main()
