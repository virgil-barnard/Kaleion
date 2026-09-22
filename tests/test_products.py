"""Named source roles checked against independently enumerated tuples."""

from itertools import product
import unittest
from unittest.mock import patch

from kaleion import Collection, F, Inspection, Motion, Product, Workspace, param


class ProductTests(unittest.TestCase):
    def test_duplicate_labels_and_reordered_sources_keep_distinct_reads(self):
        left = Collection.literal([7, 7, 2], keys=[4, 4, -1]).order_by(F.value)
        right = Collection.literal([9, 3], keys=[90, 30]).arrange(F.value, 100)
        pair = Product(left=left, right=right)
        domain = pair.domain.annotate(a=pair.read("left"), b=pair.read("right"),
                                     original=pair.read("left", F.key))
        state = Workspace({"pairs": domain, "left": left, "right": right}).state
        self.assertFalse(state.errors)
        snapshot = state.results["pairs"]
        self.assertEqual(list(zip(snapshot.fields["a"], snapshot.fields["b"])),
                         list(product([2, 7, 7], [9, 3])))
        self.assertEqual(len(set(snapshot.ids)), 6)
        self.assertEqual(snapshot.values.tolist(), [1] * 6)
        self.assertIsNone(snapshot.positions)
        inspect = Inspection(state)
        reads = inspect.bindings(inspect.find("pairs", (2, 1), by=("left", "right")))
        self.assertEqual([r.driver.occurrence for r in reads],
                         [state.results["left"].ids[2], state.results["right"].ids[1],
                          state.results["left"].ids[2]])
        self.assertEqual([r.value for r in reads], [7, 3, 4])

    def test_empty_factor_retains_other_role_domain_for_zero_measurements(self):
        bins = Collection.literal([10, 20, 30])
        pairs = Product(item=Collection.literal([]), bin=bins)
        domain = pairs.domain.annotate(a=pairs.read("item"), b=pairs.read("bin"))
        counts = domain.where(F.a == F.b).count(by=F.bin)
        state = Workspace({"pairs": domain, "counts": counts}).state
        self.assertFalse(state.errors)
        self.assertEqual(state.results["pairs"].shape, (0, 3))
        self.assertEqual(state.results["counts"].values.tolist(), [0, 0, 0])
        inspect = Inspection(state)
        for key in range(3):
            receipt = inspect.measurement(inspect.find("counts", key))
            self.assertEqual(receipt.population, 0)
            self.assertEqual(receipt.contributors, ())

    def test_symbolic_sizes_case_scope_and_three_roles_are_lazy_and_exact(self):
        huge = 2**90 + 3
        source = Collection.sequence(param("n"), start=huge)
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("eager execution")):
            triple = Product(a=source, b=Collection.literal([2, 5]), c=Collection.literal([8]))
            values = triple.domain.with_values(triple.read("a") + triple.read("b") * triple.read("c"))
        state = Workspace({"small": values.with_params(n=1), "large": values.with_params(n=2)}, {"n": 0}).state
        self.assertFalse(state.errors)
        self.assertEqual(state.results["small"].values.tolist(), [huge + 16, huge + 40])
        self.assertEqual(state.results["large"].values.tolist(), [huge + 16, huge + 40, huge + 17, huge + 41])
        self.assertEqual(state.results["large"].shape, (2, 2, 1))

    def test_domains_fail_explicitly_and_unrelated_roots_remain_usable(self):
        source = Collection.sequence(2)
        for factors in ({"a": source}, {k: source for k in "abcd"},
                        {"value": source, "b": source}, {"not valid": source, "b": source},
                        {"class": source, "b": source}):
            with self.assertRaises(ValueError):
                Product(**factors)
        with self.assertRaises(TypeError):
            Product(a=source.where(True), b=source)
        pair = Product(a=source, b=source)
        with self.assertRaises(KeyError):
            pair.read("missing")
        with self.assertRaises(TypeError):
            pair.factors["a"] = source
        failed = Product(a=Collection.sequence(param("missing")), b=source)
        state = Workspace({"bad": failed.domain, "good": source}).state
        self.assertIn("bad", state.errors)
        self.assertEqual(state.results["good"].values.tolist(), [1, 2])
        oversized = Product(a=Collection.sequence(5), b=Collection.sequence(5))
        self.assertIn("bad", Workspace({"bad": oversized.domain}, max_items=20).state.errors)

    def test_saved_role_reads_and_undo_use_captured_sources(self):
        pair = Product(a=Collection.literal([1, 4]), b=Collection.literal([2, 6]))
        domain = pair.domain.annotate(left=pair.read("a"), right=pair.read("b"))
        placed = domain.arrange(F.left, F.right)
        workspace = Workspace({"pairs": placed})
        moved = workspace.set("pairs", placed.place(F.left + F.right, 0), motion=Motion.arc(height=1))
        workspace.undo()
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
            restored = Workspace.from_json(workspace.to_json())
            replay = restored.redo()
            inspect = Inspection(restored.state)
            point = inspect.find("pairs", (1, 0), by=("a", "b"))
            annotation = inspect.item(inspect.item(point).parents[0]).parents[0]
            self.assertEqual([r.value for r in inspect.bindings(annotation)], [4, 2])
            self.assertEqual(replay.frame("pairs", .3).positions.tolist(), moved.frame("pairs", .3).positions.tolist())

    def test_named_products_express_line_incidence_and_sum_bins(self):
        p = 3
        points = Collection.grid(p, p).annotate(u=F.i, v=F.j)
        lines = Collection.grid(p + 1, p).annotate(m=F.i, t=F.j)
        pair = Product(point=points, line=lines)
        domain = pair.domain.annotate(u=pair.read("point", F.u), v=pair.read("point", F.v),
                                     m=pair.read("line", F.m), t=pair.read("line", F.t))
        incidence = domain.where(((F.m < p) & ((F.v - F.m * F.u - F.t) % p == 0)) |
                                 ((F.m == p) & (F.u == F.t)))
        state = Workspace({"lines": incidence.count(by=F.line), "points": incidence.count(by=F.point)}).state
        self.assertEqual(state.results["lines"].values.tolist(), [3] * 12)
        self.assertEqual(state.results["points"].values.tolist(), [4] * 9)
        sums = Product(a=Collection.literal([0, 1, 3]), b=Collection.literal([0, 2]))
        values = sums.domain.with_values(sums.read("a") + sums.read("b"))
        bins = Product(pair=values, bin=Collection.sequence(7, start=0))
        counts = bins.domain.where(bins.read("pair") == bins.read("bin")).count(by=F.bin).evaluate()
        self.assertEqual(counts.values.tolist(), [1, 1, 1, 2, 0, 1, 0])


if __name__ == "__main__":
    unittest.main()
