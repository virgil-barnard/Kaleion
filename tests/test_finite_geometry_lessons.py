"""Independent small-field oracles for the actual lesson 09–10 constructions.

Only tagged definition cells are loaded. These tests do not import Plotly,
execute a notebook kernel, or duplicate the notebooks' construction recipes.
"""

from collections import Counter
from itertools import product
import json
from math import gcd, pi
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np

from kaleion import Collection, F, Motion, Workspace, cos, param, sin


ROOT = Path(__file__).resolve().parents[1]


def definitions(filename):
    namespace = {}
    sys.path.insert(0, str(ROOT / "notebooks"))
    try:
        document = json.loads((ROOT / "notebooks" / filename).read_text())
        for cell in document["cells"]:
            if "kaleion-construction" in cell.get("metadata", {}).get("tags", []):
                exec(compile("".join(cell["source"]), filename, "exec"), namespace)
    finally:
        sys.path.pop(0)
    return namespace


NORM = definitions("09_norm_fibers.ipynb")
HERMITIAN = definitions("10_hermitian_partitions.ipynb")


def multiply(left, right, p):
    """Independent schoolbook polynomial product, reduced by X²+1."""
    coefficients = [0, 0, 0]
    for j, a in enumerate((left % p, left // p)):
        for k, b in enumerate((right % p, right // p)):
            coefficients[j+k] += a*b
    coefficients[0] -= coefficients.pop()
    return sum((a % p)*p**j for j, a in enumerate(coefficients))


def power(value, exponent, p):
    result = 1
    for _ in range(exponent):
        result = multiply(result, value, p)
    return result


def pairing(left, right, p=3):
    terms = [multiply(x, power(y, p, p), p) for x, y in zip(left, right)]
    return sum(z % p for z in terms) % p + p*(sum(z // p for z in terms) % p)


def vector_for(key):
    if key < 81:
        return (1, key // 9, key % 9)
    return (0, 1, key-81) if key < 90 else (0, 0, 1)


class NormFiberLessons(unittest.TestCase):
    def test_coordinate_products_and_conjugates_match_polynomial_oracle(self):
        for p in (3, 7):
            q = p*p
            pairs = Collection.grid(q, q).with_values(NORM["field_multiply"](F.i, F.j, p))
            self.assertEqual(pairs.evaluate().values.tolist(),
                             [multiply(x, y, p) for x, y in product(range(q), repeat=2)])
            elements = Collection.sequence(q, start=0)
            conjugates = elements.with_values(NORM["field_conjugate"](F.value, p)).evaluate()
            norms = elements.with_values(NORM["field_norm"](F.value, p)).evaluate()
            self.assertEqual(conjugates.values.tolist(), [power(z, p, p) for z in range(q)])
            self.assertEqual(norms.values.tolist(), [power(z, p+1, p) for z in range(q)])
        self.assertEqual(NORM["field_sum"]([2, 2], 3), 1)
        self.assertEqual(NORM["field_multiply"](3, 3, 3), 2)

    def test_measured_fibers_phase_order_and_reordered_bindings(self):
        for p, beta in ((3, 3), (7, 16), (11, 58)):
            with self.subTest(p=p):
                points, counts = NORM["norm_fibers"](p)
                atlas, powers, anchors = NORM["phase_atlas"](points, p, beta)
                nonzero = points.where(F.value != 0).select()
                rings = NORM["in_norm_fibers"](nonzero, atlas, counts)
                reordered = NORM["in_norm_fibers"](
                    nonzero, atlas.order_by(-F.value), counts.order_by(-F.key))
                state = Workspace(dict(points=points, counts=counts, atlas=atlas,
                                       powers=powers, anchors=anchors, rings=rings,
                                       reordered=reordered)).state
                self.assertFalse(state.errors)
                r = state.results
                self.assertEqual(r["counts"].values.tolist(), [1]+[p+1]*(p-1))
                self.assertEqual(r["powers"].values.tolist(), [power(beta, k, p) for k in range(p+1)])
                self.assertEqual(set(r["atlas"].values), set(range(1, p*p)))
                for n in range(p):
                    expected = {oid for oid, z in zip(r["points"].ids, r["points"].values)
                                if power(int(z), p+1, p) == n}
                    self.assertEqual(set(r["counts"].contributor_ids(n)), expected)
                for code, n, k in zip(r["atlas"].values, r["atlas"].fields["norm"],
                                      r["atlas"].fields["phase"]):
                    anchor = min(z for z in range(1, p*p) if power(z, p+1, p) == n)
                    self.assertEqual(code, multiply(anchor, power(beta, int(k), p), p))
                np.testing.assert_array_equal(r["rings"].positions, r["reordered"].positions)
                self.assertEqual(r["rings"].ids, r["reordered"].ids)

    def test_generator_changes_preserve_values_and_invalid_models_fail(self):
        p, beta = 7, 16
        points, counts = NORM["norm_fibers"](p)
        atlas, _, _ = NORM["phase_atlas"](points, p, beta)
        other, _, _ = NORM["phase_atlas"](points, p, power(beta, 3, p))
        nonzero = points.where(F.value != 0).select()
        a = NORM["in_norm_fibers"](nonzero, atlas, counts).evaluate()
        b = NORM["in_norm_fibers"](nonzero, other, counts).evaluate()
        self.assertEqual(a.ids, b.ids)
        np.testing.assert_array_equal(a.values, b.values)
        self.assertEqual(b.fields["phase"].tolist(), [(3*int(k)) % 8 for k in a.fields["phase"]])
        for bad in (0, 1, 2, 49):
            with self.assertRaises(ValueError):
                NORM["phase_atlas"](points, p, bad)
        with self.assertRaises(ValueError):
            NORM["norm_fibers"](5)
        bad = Collection.sequence(25, start=0).where(NORM["field_norm"](F.value, 5) == 0)
        self.assertEqual(bad.evaluate().cardinality, 9)
        self.assertEqual(multiply(7, 22, 5), 0)

    def test_field_rotation_and_saved_reverse_path_are_distinct_from_relabeling(self):
        p, beta = 7, 16
        points, counts = NORM["norm_fibers"](p)
        atlas, _, _ = NORM["phase_atlas"](points, p, beta)
        source = points.where(F.value != 0).select()
        start = NORM["in_norm_fibers"](source, atlas, counts)
        transformed = source.with_values(NORM["field_multiply"](F.value, beta, p))
        end = NORM["in_norm_fibers"](transformed, atlas, counts)
        t = 2*pi*param("time")/(p+1)
        path = Motion.custom(F.sx*cos(t)-F.sy*sin(t), F.sx*sin(t)+F.sy*cos(t), F.sz)
        workspace = Workspace({"elements": start})
        forward = workspace.set("elements", end, motion=path)
        a, b = forward.start.results["elements"], forward.end.results["elements"]
        self.assertEqual(a.ids, b.ids)
        self.assertEqual(b.values.tolist(), [multiply(int(z), beta, p) for z in a.values])
        np.testing.assert_allclose(forward.frame("elements", 1).positions, b.positions,
                                   atol=1e-12, rtol=0)  # trig endpoint roundoff
        workspace.undo()
        payload = workspace.to_json()
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("unexpected evaluation")):
            reopened = Workspace.from_json(payload)
            replay = reopened.redo()
            np.testing.assert_array_equal(forward.frame("elements", .25).positions,
                                           replay.reverse().frame("elements", .75).positions)


class HermitianPartitionLessons(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vectors = [vector_for(key) for key in range(91)]
        cls.curve = {k for k, vector in enumerate(cls.vectors) if pairing(vector, vector) == 0}
        cls.lines = [{k for k in cls.curve if pairing(pole, cls.vectors[k]) == 0}
                     for pole in cls.vectors]

    def test_projective_quotient_counts_representatives_without_merging_motion(self):
        raw, normalized, sizes = HERMITIAN["projective_quotient"]()
        points = HERMITIAN["projective_points"](labels=sizes.with_values(F.key))
        state = Workspace(dict(raw=raw, normalized=normalized, sizes=sizes, points=points)).state
        self.assertFalse(state.errors)
        r = state.results
        expected = []
        for vector in product(range(9), repeat=3):
            if vector == (0, 0, 0):
                continue
            leading = next(v for v in vector if v)
            inverse = next(v for v in range(1, 9) if multiply(leading, v, 3) == 1)
            canonical = tuple(multiply(v, inverse, 3) for v in vector)
            expected.append(self.vectors.index(canonical))
        self.assertEqual(r["normalized"].values.tolist(), expected)
        self.assertEqual(r["raw"].ids, r["normalized"].ids)
        self.assertEqual(len(set(map(tuple, r["normalized"].positions))), 91)
        self.assertEqual(r["sizes"].values.tolist(), [8]*91)
        self.assertEqual(r["points"].values.tolist(), list(range(91)))
        for key in range(91):
            self.assertEqual(set(r["sizes"].contributor_ids(key)),
                             {oid for oid, result in zip(r["normalized"].ids, expected) if result == key})

    def test_all_polar_incidences_and_pairwise_design_counts(self):
        points = HERMITIAN["projective_points"]()
        incidence, line_counts, point_counts = HERMITIAN["hermitian_incidence"](points)
        state = Workspace(dict(incidence=incidence, lines=line_counts, points=point_counts)).state
        self.assertFalse(state.errors)
        r = state.results
        expected = np.array([[j in line for j in sorted(self.curve)] for line in self.lines])
        np.testing.assert_array_equal(r["incidence"].mask.reshape(91, 28), expected)
        self.assertEqual(Counter(r["lines"].values), {1: 28, 4: 63})
        self.assertEqual(r["points"].fields["key"].tolist(), sorted(self.curve))
        self.assertEqual(r["points"].values.tolist(), [10]*28)
        blocks = expected[[len(line) == 4 for line in self.lines]].astype(int)
        pair_counts = blocks.T @ blocks
        self.assertTrue(np.all(pair_counts[np.triu_indices(28, 1)] == 1))
        self.assertTrue(np.all(np.diag(pair_counts) == 9))

    def test_two_partitions_derive_unique_keys_ranks_and_missing_polar_witnesses(self):
        points = HERMITIAN["projective_points"]().order_by(-F.value)
        incidence, counts, _ = HERMITIAN["hermitian_incidence"](points)
        for focus, external in ((4, False), (85, False), (0, True), (90, True)):
            with self.subTest(focus=focus, external=external):
                definitions = HERMITIAN["hermitian_partition"](points, incidence, counts, focus, external=external)
                state = Workspace(definitions).state
                self.assertFalse(state.errors)
                r = state.results
                chosen = [key for key, line in enumerate(self.lines) if len(line) == 4
                          and (pairing(self.vectors[key], self.vectors[focus]) == 0
                               or (external and key == focus))]
                expected_groups = {key: sorted(self.lines[key]-{focus}) for key in chosen}
                expected_cover = Counter(k for group in expected_groups.values() for k in group)
                if not external:
                    expected_cover[focus] = 1  # The tangent supplies the singleton block.
                    self.assertEqual(r["unique_line"].values[
                        r["unique_line"].fields["key"].tolist().index(focus)], focus)
                self.assertEqual(r["cover_count"].fields["key"].tolist(), sorted(self.curve))
                self.assertEqual(r["cover_count"].values.tolist(), [expected_cover[k] for k in sorted(self.curve)])
                self.assertEqual(set(expected_cover.values()), {1})
                for index, point in enumerate(r["packed"].values):
                    point = int(point)
                    if point == focus:
                        expected_position = (-3., 1.)
                    else:
                        owner = next(key for key, group in expected_groups.items() if point in group)
                        row = r["unique_line"].fields["key"].tolist().index(point)
                        self.assertEqual(r["unique_line"].values[row], owner)
                        self.assertEqual(len(r["unique_line"].contributor_ids(point)), 1)
                        expected_position = (3.*chosen.index(owner), float(expected_groups[owner].index(point)))
                    self.assertEqual(tuple(r["packed"].positions[index]), expected_position)
                if external:
                    incomplete = definitions["other_hits"] & definitions["other_hits"].universe.where(F.i != focus)
                    cover = incomplete.count(by=F.point).evaluate()
                    self.assertEqual({int(k) for k,v in zip(cover.fields["key"],cover.values) if v == 0}, self.lines[focus])

    def test_partition_motion_roundtrip_and_invalid_pole_isolation(self):
        points = HERMITIAN["projective_points"]()
        incidence, counts, _ = HERMITIAN["hermitian_incidence"](points)
        a = HERMITIAN["hermitian_partition"](points, incidence, counts, 4)
        b = HERMITIAN["hermitian_partition"](points, incidence, counts, 0, external=True)
        workspace = Workspace({"curve": a["packed"]})
        forward = workspace.set("curve", b["packed"], motion=Motion.arc(height=2))
        self.assertEqual(forward.start.results["curve"].ids, forward.end.results["curve"].ids)
        workspace.undo()
        reopened = Workspace.from_json(workspace.to_json())
        replay = reopened.redo()
        np.testing.assert_array_equal(forward.frame("curve", .25).positions,
                                       replay.reverse().frame("curve", .75).positions)
        invalid = HERMITIAN["hermitian_partition"](points, incidence, counts, 0)
        isolated = Workspace({"points": points, "invalid": invalid["packed"]}).state
        self.assertEqual(len(isolated.results["points"]), 91)
        self.assertIn("invalid", isolated.errors)
        self.assertIn("exactly one", isolated.errors["invalid"])


if __name__ == "__main__":
    unittest.main()
