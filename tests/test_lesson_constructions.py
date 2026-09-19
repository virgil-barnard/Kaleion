"""Finite, independently checked constructions used by lessons 04 and 05."""

from fractions import Fraction
from itertools import product
import unittest

import numpy as np

from kaleion import Collection, F, Motion, Workspace, choose, vector


def plane_construction(a, b, c, *, reorder=False):
    box = (Collection.grid(a - 1, b - 1, c - 1, values=1)
           .annotate(u=F.i + 1, v=F.j + 1, w=F.k + 1))
    regions = [box.where(rule) for rule in (
        (a * F.v <= b * F.u) & (a * F.w <= c * F.u),
        (b * F.u <= a * F.v) & (b * F.w <= c * F.v),
        (c * F.u <= a * F.w) & (c * F.v <= b * F.w),
    )]
    heights = [region.count(by=(F.u, F.v)) for region in regions]
    plane = (Collection.grid(a - 1, b - 1, values=0)
             .annotate(u=F.i + 1, v=F.j + 1).arrange(F.u, F.v, 0))
    lifted = plane
    for height in heights:
        driver = height.order_by(-F.value) if reorder else height
        amount = driver.bind(on=(F.u, F.v), key=(F.u, F.v))
        lifted = lifted.with_values(F.value + amount).move(vector(0, 0, amount))
    return {"box": box, "plane": plane, "lifted": lifted,
            **{f"h{i}": height for i, height in enumerate(heights)}}


def finite_lines(p, values, *, cardinalities=False):
    pixels = Collection.grid(p, p, values=0).annotate(u=F.i, v=F.j)
    image = pixels.lookup(Collection.literal(values), address=F.key)
    lines = Collection.grid(p + 1, p, values=0).annotate(m=F.i, t=F.j)
    pairs = Collection.grid(p * p, p * (p + 1), values=1).annotate(
        u=pixels.bind(on=F.i, read=F.u), v=pixels.bind(on=F.i, read=F.v),
        m=lines.bind(on=F.j, read=F.m), t=lines.bind(on=F.j, read=F.t))
    rule = (((F.m < p) & ((F.v - F.m * F.u - F.t) % p == 0))
            | ((F.m == p) & (F.u == F.t)))
    sampling = pairs.annotate(weight=image.bind(on=(F.u, F.v), key=(F.u, F.v)))
    measurements = (sampling.where(rule & (F.weight == 1)).count(by=(F.m, F.t))
                    if cardinalities else
                    sampling.where(rule).sum(by=(F.m, F.t), value=F.weight))

    def inverse(measured):
        back = pairs.where(rule).sum(
            by=(F.u, F.v), value=measured.bind(on=(F.m, F.t), key=(F.m, F.t)))
        total = measured.where(F.m == 0).sum().scalar()
        numerator = back.with_values(F.value - total)
        return {"numerator": numerator, "remainders": numerator.with_values(F.value % p),
                "recovered": numerator.with_values(F.value // p)}

    roots = {"image": image, "pairs": pairs, "sampling": sampling, "measurements": measurements,
             "line_sizes": pairs.where(rule).count(by=(F.m, F.t)),
             "pixel_degrees": pairs.where(rule).count(by=(F.u, F.v)), **inverse(measurements)}
    return roots, inverse


def keyed(snapshot, names=("u", "v")):
    return dict(zip(zip(*(map(int, snapshot.fields[n]) for n in names)), map(int, snapshot.values)))


class MeasuredMotionLessons(unittest.TestCase):
    def test_column_counts_drive_geometry_with_zero_groups_and_key_alignment(self):
        for a, b, c in ((11, 7, 5), (2, 3, 5)):
            with self.subTest(parameters=(a, b, c)):
                state = Workspace(plane_construction(a, b, c, reorder=True)).state
                self.assertFalse(state.errors)
                r = state.results
                points = list(product(range(1, a), range(1, b), range(1, c)))
                ids = dict(zip(points, r["box"].ids))
                zero_groups = 0
                for axis in range(3):
                    counts = keyed(r[f"h{axis}"])
                    self.assertEqual(set(counts), set(product(range(1, a), range(1, b))))
                    for key, count in counts.items():
                        expected = [point for point in points if point[:2] == key
                                    and Fraction(point[axis], (a, b, c)[axis]) ==
                                    max(Fraction(v, d) for v, d in zip(point, (a, b, c)))]
                        self.assertEqual(count, len(expected))
                        self.assertEqual(set(r[f"h{axis}"].contributor_ids(key)), {ids[p] for p in expected})
                        zero_groups += count == 0
                self.assertGreater(zero_groups, 0)
                self.assertEqual(r["plane"].ids, r["lifted"].ids)
                self.assertEqual(set(r["lifted"].values), {c - 1})
                np.testing.assert_array_equal(r["lifted"].positions[:, 2], r["lifted"].values)

    def test_overlap_bump_and_captured_reverse_survive_reopening(self):
        roots = plane_construction(6, 4, 5)
        workspace = Workspace(roots)
        self.assertFalse(workspace.state.errors)
        before = workspace.state
        heights = keyed(before.results["lifted"])
        self.assertEqual({key: value - 4 for key, value in heights.items() if value != 4}, {(3, 2): 2})
        self.assertEqual([keyed(before.results[f"h{i}"])[3, 2] for i in range(3)], [2, 2, 2])
        forward = workspace.set("plane", roots["lifted"], motion=Motion())
        workspace.capture("Measured overlap bump")
        workspace.undo()
        reopened = Workspace.from_json(workspace.to_json())
        self.assertTrue(reopened.can_redo)
        backward = reopened.redo().reverse()
        np.testing.assert_array_equal(forward.frame("plane", .25).positions,
                                      backward.frame("plane", .75).positions)
        self.assertEqual(reopened.state.results["h0"].contributor_ids((3, 2)),
                         before.results["h0"].contributor_ids((3, 2)))


class FiniteRadonLessons(unittest.TestCase):
    def test_prime_line_counts_recover_zero_impulse_and_full_images(self):
        for p in (2, 3, 5):
            for name, values in (("zero", [0] * (p * p)),
                                 ("impulse", [1] + [0] * (p * p - 1)),
                                 ("full", [1] * (p * p))):
                with self.subTest(p=p, image=name):
                    roots, _ = finite_lines(p, values, cardinalities=True)
                    state = Workspace(roots).state
                    self.assertFalse(state.errors)
                    r = state.results
                    image = dict(zip(product(range(p), repeat=2), values))
                    self.assertEqual(keyed(r["recovered"]), image)
                    self.assertEqual(set(r["remainders"].values), {0})
                    self.assertEqual(set(r["line_sizes"].values), {p})
                    self.assertEqual(set(r["pixel_degrees"].values), {p + 1})
                    measured = keyed(r["measurements"], ("m", "t"))
                    self.assertEqual(len(measured), p * (p + 1))
                    for (m, t), value in measured.items():
                        # Generate a line's p points independently of the pair predicate.
                        line = ([(t, y) for y in range(p)] if m == p else
                                [(x, (m * x + t) % p) for x in range(p)])
                        self.assertEqual(value, sum(image[point] for point in line))
                        self.assertEqual(len(r["measurements"].contributor_ids((m, t))), value)
                    if name == "zero":
                        self.assertEqual(set(measured.values()), {0})

    def test_signed_large_weights_recover_after_measurement_reordering(self):
        p = 3
        values = [2**75 * (x - y) + x + 2 * y for x, y in product(range(p), repeat=2)]
        roots, inverse = finite_lines(p, values)
        roots.update(inverse(roots["measurements"].order_by(-F.value)))
        state = Workspace(roots).state
        self.assertFalse(state.errors)
        self.assertEqual(keyed(state.results["recovered"]), dict(zip(product(range(p), repeat=2), values)))
        self.assertEqual(set(state.results["remainders"].values), {0})

    def test_one_corrupted_line_exposes_exact_division_witnesses(self):
        p = 5
        roots, inverse = finite_lines(p, [1 if i % 3 == 0 else 0 for i in range(p * p)], cardinalities=True)
        corrupted = roots["measurements"].with_values(F.value + choose((F.m == 1) & (F.t == 0), 1, 0))
        roots.update(inverse(corrupted))
        state = Workspace(roots).state
        self.assertFalse(state.errors)
        witnesses = {key: value for key, value in keyed(state.results["remainders"]).items() if value}
        self.assertEqual(witnesses, {(x, x): 1 for x in range(p)})

    def test_composite_modulus_does_not_satisfy_prime_field_inverse(self):
        roots, _ = finite_lines(4, [1] + [0] * 15, cardinalities=True)
        state = Workspace(roots).state
        self.assertFalse(state.errors)  # The ring computations are valid; the theorem does not apply.
        self.assertNotEqual(keyed(state.results["recovered"]), keyed(state.results["image"]))
        self.assertNotEqual(set(state.results["remainders"].values), {0})


if __name__ == "__main__":
    unittest.main()
