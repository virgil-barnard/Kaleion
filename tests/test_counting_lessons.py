"""Independent finite oracles for the constructions in lessons 06–08."""

from collections import Counter
from functools import reduce
from itertools import product
from math import pi, sqrt
import unittest

import numpy as np

from kaleion import Collection, F, Motion, Workspace, cos, param, sin


def young_layers(heights):
    bound = max([1] + heights)
    grid = Collection.grid(len(heights), bound, values=1).arrange(F.i + 1, F.j + 1, 0)
    diagram = grid.where(F.j < Collection.literal(heights).bind(on=F.i))
    layers = diagram.count(by=F.j)
    conjugate = Collection.grid(bound, len(heights), values=1).where(
        F.j < layers.bind(on=F.i, key=F.j))
    earlier = Collection.grid(bound, bound, values=1).annotate(
        length=layers.bind(on=F.j, key=F.j))
    offsets = earlier.where(F.j < F.i).sum(by=F.i, value=F.length)
    cells = diagram.select()
    turned = cells.arrange(F.j + 1, F.i + 1, 0)
    strip = turned.arrange(F.i + 1 + offsets.bind(on=F.j, key=F.i), 1, 0)
    return {"grid": grid, "diagram": diagram, "layers": layers,
            "twice": conjugate.count(by=F.j), "offsets": offsets,
            "cells": cells, "turned": turned, "strip": strip}


def sum_construction(a, b, *, reorder=False):
    pairs = (Collection.grid(len(a), len(b), values=1)
             .annotate(a=Collection.literal(a).bind(on=F.i),
                       b=Collection.literal(b).bind(on=F.j))
             .annotate(total=F.a + F.b, pair_key=F.key)
             .with_values(F.total).arrange(F.a, F.b))
    driver = pairs.order_by(-F.pair_key) if reorder else pairs
    low, high = (min(a) + min(b), max(a) + max(b)) if a and b else (0, 0)
    bins = Collection.sequence(high - low + 1, start=low)
    domain = Collection.grid(pairs.count().scalar(), high - low + 1, values=1).annotate(
        s=bins.bind(on=F.j), total=driver.bind(on=F.i, key=F.pair_key, read=F.total))
    measurement = domain.where(F.s == F.total)
    counts = measurement.count(by=F.j).annotate(s=bins.bind(on=F.j))
    pair_pairs = Collection.grid(pairs.count().scalar(), pairs.count().scalar(), values=1).annotate(
        left=driver.bind(on=F.i, key=F.pair_key, read=F.total),
        right=driver.bind(on=F.j, key=F.pair_key, read=F.total))
    ranks = pair_pairs.where((F.left == F.right) & (F.j < F.i)).count(by=F.i)
    stacked = pairs.arrange(F.total, ranks.bind(on=F.pair_key, key=F.i))
    side = counts.bind(on=F.i, key=F.j)
    squares = Collection.grid(high - low + 1, min(len(a), len(b)), min(len(a), len(b)), values=1)
    return {"pairs": pairs, "measurement": measurement, "counts": counts,
            "ranks": ranks, "stacked": stacked, "energy": counts.sum(value=F.value**2),
            "quadruples": pair_pairs.where(F.left == F.right).count(),
            "squares": squares.where((F.j < side) & (F.k < side)).count()}


def measured_family(incidence, scales):
    total = incidence.count()
    cases = {k: total.with_params(n=k).annotate(scale=k) for k in scales}
    family = reduce(lambda left, right: left.concat(right), cases.values()).annotate(key=F.scale)
    return family, cases


def difference(series, last, step=1):
    return series.where(F.scale <= last - step).select().with_values(
        series.bind(on=F.scale + step, key=F.scale) - F.value)


def by_scale(snapshot):
    return dict(zip(map(int, snapshot.fields["scale"]), map(int, snapshot.values)))


class YoungLayerLessons(unittest.TestCase):
    def test_layers_conjugation_and_measured_packing_include_empty_columns(self):
        for heights in ([], [0, 0], [1], [5, 3, 2, 0]):
            with self.subTest(heights=heights):
                state = Workspace(young_layers(heights)).state
                self.assertFalse(state.errors)
                r = state.results
                bound = max([1] + heights)
                expected = [sum(h >= level for h in heights) for level in range(1, bound + 1)]
                self.assertEqual(r["layers"].values.tolist(), expected)
                self.assertEqual(r["twice"].values.tolist(), heights)
                self.assertEqual(sum(expected), sum(heights))
                self.assertEqual(r["offsets"].values.tolist(), [sum(expected[:k]) for k in range(bound)])
                self.assertEqual(sorted(r["strip"].positions[:, 0]), list(range(1, sum(heights) + 1)))
                self.assertEqual(r["strip"].ids, r["cells"].ids)
                ids = dict(zip(product(range(len(heights)), range(bound)), r["grid"].ids))
                for level in range(bound):
                    self.assertEqual(set(r["layers"].contributor_ids(level)),
                                     {ids[i, level] for i, h in enumerate(heights) if h > level})

    def test_layers_forget_column_order(self):
        ordered = Workspace(young_layers([5, 3, 2])).state.results
        unordered = Workspace(young_layers([2, 5, 3])).state.results
        np.testing.assert_array_equal(ordered["layers"].values, unordered["layers"].values)
        self.assertEqual(unordered["twice"].values.tolist(), [5, 3, 2])
        self.assertFalse(np.array_equal(ordered["diagram"].mask, unordered["diagram"].mask))

    def test_spatial_transpose_reverses_captured_path_after_reopening(self):
        roots = young_layers([3, 1, 0])
        workspace = Workspace({"cells": roots["cells"], "layers": roots["layers"]})
        initial = workspace.state.results["cells"]
        t = param("time")
        turn = Motion.custom((F.sx + F.sy + (F.sx - F.sy) * cos(pi * t)) / 2,
                             (F.sx + F.sy - (F.sx - F.sy) * cos(pi * t)) / 2,
                             (F.sy - F.sx) * sin(pi * t) / sqrt(2))
        forward = workspace.set("cells", roots["turned"], motion=turn)
        # Trigonometric endpoint sampling has sin(pi) roundoff; mathematical endpoints are integral.
        np.testing.assert_allclose(forward.frame("cells", 1).positions,
                                   initial.positions[:, [1, 0, 2]], atol=1e-12, rtol=0)
        workspace.undo()
        restored = Workspace.from_json(workspace.to_json())
        replay = restored.redo()
        np.testing.assert_array_equal(forward.frame("cells", .25).positions,
                                      replay.reverse().frame("cells", .75).positions)
        self.assertEqual(initial.ids, restored.state.results["cells"].ids)


class AdditiveStructureLessons(unittest.TestCase):
    def test_counts_and_ranks_preserve_multiplicity_zero_bins_and_key_alignment(self):
        for a, b in (([], []), ([], [2]), ([0], [0]), ([-3, 1], [-2, 2]), ([0, 1, 2], [0, 2])):
            with self.subTest(a=a, b=b):
                state = Workspace(sum_construction(a, b, reorder=True)).state
                self.assertFalse(state.errors)
                r = state.results
                pairs = list(product(a, b))
                oracle = Counter(x + y for x, y in pairs)
                low, high = (min(oracle), max(oracle)) if oracle else (0, 0)
                self.assertEqual(dict(zip(map(int, r["counts"].fields["s"]), map(int, r["counts"].values))),
                                 {s: oracle[s] for s in range(low, high + 1)})
                occupied = {(s, rank) for s, count in oracle.items() for rank in range(count)}
                self.assertEqual(set(map(tuple, r["stacked"].positions)), occupied)
                self.assertEqual(r["stacked"].ids, r["pairs"].ids)
                source = r["measurement"].source
                for bin_key, s in enumerate(range(low, high + 1)):
                    expected_ids = {oid for idx, oid in enumerate(source.ids)
                                    if int(source.fields["j"][idx]) == bin_key
                                    and sum(pairs[int(source.fields["i"][idx])]) == s}
                    self.assertEqual(set(r["counts"].contributor_ids(bin_key)), expected_ids)

    def test_energy_agrees_with_independent_equal_sum_quadruples_and_square_cells(self):
        for a, b, expected in (([0, 1, 2, 3], [0, 1, 2, 3], 44),
                               ([0, 1, 3, 7], [0, 1, 3, 7], 28),
                               ([-2, 1], [0, 3, 4], None), ([], [0], 0)):
            with self.subTest(a=a, b=b):
                state = Workspace(sum_construction(a, b)).state
                self.assertFalse(state.errors)
                direct = sum(x + y == u + v for x, y, u, v in product(a, b, a, b))
                if expected is not None:
                    self.assertEqual(direct, expected)
                for name in ("energy", "quadruples", "squares"):
                    self.assertEqual(int(state.results[name].values[0]), direct)


class LatticeCountingLessons(unittest.TestCase):
    def test_parameter_family_differences_and_contributors_survive_reordered_cases(self):
        maximum = 6
        n = param("n")
        grid = Collection.grid(maximum + 1, maximum + 1, values=1)
        triangle = grid.where(F.i + F.j <= n)
        counts, cases = measured_family(triangle, reversed(range(maximum + 1)))
        first = difference(counts, maximum)
        second = difference(first, maximum - 1)
        probe = Collection.sequence(maximum - 1, start=0).annotate(scale=F.value)
        driven = probe.with_values(second.bind(on=F.scale, key=F.scale)).arrange(F.scale, F.value)
        workspace = Workspace({"counts": counts, "first": first, "second": second, "probe": probe,
                               "driven": driven, "case": cases[3], "incidence": triangle.with_params(n=3)})
        self.assertFalse(workspace.state.errors)
        r = workspace.state.results
        oracle = {k: len([(x, y) for x in range(k + 1) for y in range(k + 1 - x)])
                  for k in range(maximum + 1)}
        self.assertEqual(by_scale(r["counts"]), oracle)
        self.assertEqual(by_scale(r["first"]), {k: k + 2 for k in range(maximum)})
        self.assertEqual(by_scale(r["second"]), {k: 1 for k in range(maximum - 1)})
        np.testing.assert_array_equal(r["driven"].positions[:, 1], np.ones(maximum - 1))
        self.assertEqual(r["probe"].ids, r["driven"].ids)
        incidence = r["incidence"]
        contributors = {oid for oid, selected in zip(incidence.source.ids, incidence.mask) if selected}
        self.assertEqual(set(r["case"].contributor_ids(())), contributors)
        reopened = Workspace.from_json(workspace.to_json())
        self.assertEqual(set(reopened.state.results["case"].contributor_ids(())), contributors)

    def test_interior_reciprocity_and_rational_period_need_their_stated_domains(self):
        maximum = 8
        n = param("n")
        grid = Collection.grid(maximum + 1, maximum + 1, values=1)
        closed, _ = measured_family(grid.where(F.i + F.j <= n), range(maximum + 1))
        interior, _ = measured_family(grid.where((F.i > 0) & (F.j > 0) & (F.i + F.j < n)), range(maximum + 1))
        rational, _ = measured_family(grid.where(2 * (F.i + F.j) <= n), range(maximum + 1))
        first = difference(rational, maximum)
        stride = difference(rational, maximum, step=2)
        state = Workspace({"closed": closed, "interior": interior, "rational": rational,
                           "ordinary_second": difference(first, maximum - 1),
                           "stride_second": difference(stride, maximum - 2, step=2)}).state
        self.assertFalse(state.errors)
        r = state.results
        self.assertEqual(by_scale(r["closed"])[0], 1)
        self.assertEqual(by_scale(r["interior"])[0], 0)
        for k in range(1, maximum + 1):
            self.assertEqual(by_scale(r["interior"])[k], (1 - k) * (2 - k) // 2)
            self.assertEqual(by_scale(r["closed"])[k] - by_scale(r["interior"])[k], 3 * k)
        expected = {k: sum(2 * (x + y) <= k for x, y in product(range(k + 1), repeat=2))
                    for k in range(maximum + 1)}
        self.assertEqual(by_scale(r["rational"]), expected)
        self.assertGreater(len(set(r["ordinary_second"].values)), 1)
        self.assertEqual(set(r["stride_second"].values), {1})


if __name__ == "__main__":
    unittest.main()
