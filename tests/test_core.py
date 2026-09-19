import json
from fractions import Fraction
from itertools import product
from math import gcd
import unittest
import numpy as np

from kaleion import (
    Arrangement,
    Collection,
    Construction,
    Evaluator,
    EvaluationError,
    F,
    Lens,
    Motion,
    Move,
    Values,
    Place,
    Sweep,
    Workspace,
    param,
    vector,
    graph,
    load_graph,
    wrap,
    choose,
    floor,
    ceil,
)


def quotient_fixture():
    a, b = param("a"), param("b")
    remainder = Collection.grid(b, a, values=F.i + b * F.j, name="Remainder").arrange(
        F.j, -F.i
    )
    region = Collection.grid(
        b, a, values=a * F.i + b * F.j, name="Quotient region"
    ).arrange(F.j, -F.i)
    lens = region.where(F.value >= a * b)
    counts = lens.count(by=F.i)
    addresses = (
        remainder.where(F.value % a == 0).select().order_by(F.value).with_values(F.i)
    )
    gathered = remainder.items.gather(addresses, axis="i").arrange(F.j, -F.i)
    rolled = gathered.roll(axis="j", shift=-counts.bind(on=F.i))
    return remainder, region, lens, counts, rolled


def box_incidence_fixture():
    a, b, c = param("a"), param("b"), param("c")
    box = (Collection.grid(a - 1, b - 1, c - 1, values=1)
           .annotate(u=F.i + 1, v=F.j + 1, w=F.k + 1)
           .arrange(F.u, F.v, F.w))
    x = box.where((a * F.v <= b * F.u) & (a * F.w <= c * F.u))
    y = box.where((b * F.u <= a * F.v) & (b * F.w <= c * F.v))
    z = box.where((c * F.u <= a * F.w) & (c * F.v <= b * F.w))
    return {
        "D": box, "X": x, "Y": y, "Z": z,
        "x_sections": x.count(by=F.u), "y_sections": y.count(by=F.v),
        "z_sections": z.count(by=F.w),
        "union": x | y | z, "XY": x & y, "XZ": x & z,
        "YZ": y & z, "XYZ": x & y & z,
    }


class SymbolicTests(unittest.TestCase):
    def test_integer_arithmetic_is_exact_before_overflow(self):
        big = 2**80
        source = Collection.literal([big, big + 1])
        result = source.with_values(F.value**2 + 1).evaluate()
        self.assertEqual(result.values.tolist(), [big * big + 1, (big + 1) ** 2 + 1])
        summed = source.sum().evaluate()
        self.assertEqual(summed.values.tolist(), [2 * big + 1])
        self.assertEqual(
            source.with_values(floor(F.value)).evaluate().values.tolist(),
            [big, big + 1],
        )
        self.assertEqual(
            source.with_values(ceil(F.value)).evaluate().values.tolist(), [big, big + 1]
        )
        with self.assertRaises(EvaluationError):
            source.with_values(F.value**4096).evaluate()

    def test_expression_and_boolean_contracts(self):
        x = Collection.sequence(5)
        rule = ((F.value % 2) == 0) | (F.value == 5)
        self.assertEqual(x.where(rule).select().evaluate().values.tolist(), [2, 4, 5])
        self.assertEqual(
            x.with_values(choose(F.value < 3, 10, 20)).evaluate().values.tolist(),
            [10, 10, 20, 20, 20],
        )
        with self.assertRaises(TypeError):
            bool(rule)
        with self.assertRaises(TypeError):
            bool(x)
        with self.assertRaises(TypeError):
            x == x
        with self.assertRaises(EvaluationError):
            x.where(F.value).evaluate()
        with self.assertRaises(EvaluationError):
            x.with_values(F.value / 2).evaluate()
        with self.assertRaises(EvaluationError):
            x.with_values(F.value % 0).evaluate()
        with self.assertRaises(EvaluationError):
            x.with_values(F.value % -3).evaluate()

    def test_snapshot_does_not_alias_inputs(self):
        v = np.array([1, 2, 3])
        p = np.array([[0.0, 0.0], [1.0, 1.0], [2.0, 2.0]])
        a = Arrangement.points(v, p)
        v[:] = 99
        p[:] = 99
        r = a.evaluate()
        self.assertEqual(r.values.tolist(), [1, 2, 3])
        np.testing.assert_array_equal(r.positions, [[0, 0], [1, 1], [2, 2]])
        with self.assertRaises(ValueError):
            r.values[0] = 5
        with self.assertRaises(TypeError):
            r.fields["new"] = np.arange(3)

    def test_typed_pipeline(self):
        source = Collection.sequence(3).arrange(F.index, 0)
        op = Values(F.value * 2) >> Move(vector(0, F.value)) >> Place(F.x + 1, F.y)
        r = (source | op).evaluate()
        self.assertEqual(r.values.tolist(), [2, 4, 6])
        np.testing.assert_array_equal(r.positions, [[1, 2], [2, 4], [3, 6]])

    def test_graph_roundtrip_and_corruption(self):
        *_, counts, rolled = quotient_fixture()
        encoded = json.loads(
            json.dumps(graph({"counts": counts.node, "rolled": rolled.node}))
        )
        restored = {k: wrap(n) for k, n in load_graph(encoded).items()}
        self.assertTrue(restored["rolled"].same_definition(rolled))
        self.assertEqual(
            restored["counts"].evaluate(a=11, b=7).values.tolist(),
            [0, 1, 3, 4, 6, 7, 9],
        )
        first = next(iter(encoded["nodes"]))
        encoded["nodes"][first]["inputs"] = [first]
        with self.assertRaisesRegex(ValueError, "cycle"):
            load_graph(encoded)

    def test_independent_cases_do_not_poison_shared_cache(self):
        base = Collection.sequence(param("n"))
        roots = {
            "four": base.with_params(n=4),
            "two": base,
            "three": base.with_params(n=3),
        }
        engine = Evaluator({"n": 2})
        results, errors = engine.run(roots)
        self.assertFalse(errors)
        self.assertEqual([len(results[k]) for k in roots], [4, 2, 3])
        self.assertEqual(len({results[k].node for k in roots}), 3)


class DiscoveryTests(unittest.TestCase):
    def test_three_incidence_box_has_floor_product_sections(self):
        roots = box_incidence_fixture()
        for extents in [(11, 7, 5), (2, 3, 5), (3, 5, 7)]:
            with self.subTest(extents=extents):
                state = Workspace(roots, dict(zip("abc", extents))).state
                self.assertFalse(state.errors)
                r = state.results
                points = list(product(*(range(1, v) for v in extents)))
                for axis, name in enumerate("XYZ"):
                    expected_mask = []
                    for p in points:
                        ratios = [Fraction(p[j], extents[j]) for j in range(3)]
                        expected_mask.append(ratios[axis] == max(ratios))
                    np.testing.assert_array_equal(r[name].mask, expected_mask)
                    self.assertEqual(r[name].source.ids, r["D"].ids)
                    others = [extents[j] for j in range(3) if j != axis]
                    areas = [(others[0] * t // extents[axis]) * (others[1] * t // extents[axis])
                             for t in range(1, extents[axis])]
                    sections = r[name.lower() + "_sections"]
                    self.assertEqual(sections.values.tolist(), areas)
                    self.assertEqual(sum(areas), r[name].cardinality)
                    for key, area in enumerate(areas, start=1):
                        self.assertEqual(len(sections.contributor_ids(key)), area)
                membership_count = sum(r[name].mask.astype(int) for name in "XYZ")
                np.testing.assert_array_equal(membership_count, np.ones(len(points), dtype=int))
                self.assertEqual(r["union"].cardinality, len(points))

    def test_three_incidence_pair_and_triple_overlap_accounting(self):
        roots = box_incidence_fixture()
        cases = [((6, 4, 5), [23, 19, 20], [2, 0, 0], 0),
                 ((4, 6, 8), [38, 38, 42], [4, 8, 2], 1),
                 ((2, 2, 2), [1, 1, 1], [1, 1, 1], 1)]
        for extents, volumes, pairs, triple in cases:
            with self.subTest(extents=extents):
                state = Workspace(roots, dict(zip("abc", extents))).state
                self.assertFalse(state.errors)
                r = state.results
                self.assertEqual([r[n].cardinality for n in "XYZ"], volumes)
                self.assertEqual([r[n].cardinality for n in ("XY", "XZ", "YZ")], pairs)
                self.assertEqual(r["XYZ"].cardinality, triple)
                self.assertTrue(r["union"].mask.all())
                self.assertEqual(sum(volumes) - sum(pairs) + triple, len(r["D"]))
                if extents == (6, 4, 5):
                    self.assertEqual(gcd(*extents), 1)
                    overlap = r["XY"]
                    shared = list(zip(*(overlap.source.fields[k][overlap.mask].tolist()
                                        for k in ("u", "v", "w"))))
                    self.assertEqual(shared, [(3, 2, 1), (3, 2, 2)])

    def test_floor_sum_incidences_cover_with_exact_diagonal_overlap(self):
        a, b = param("a"), param("b")
        rectangle = (
            Collection.grid(b - 1, a - 1, values=1)
            .annotate(u=F.i + 1, v=F.j + 1)
            .arrange(F.u, F.v)
        )
        lower = rectangle.where(b * F.v <= a * F.u)
        upper = rectangle.where(a * F.u <= b * F.v)
        columns, rows = lower.count(by=F.u), upper.count(by=F.v)
        roots = {
            "D": rectangle, "union": lower | upper, "overlap": lower & upper,
            "columns": columns, "rows": rows,
            "left": columns.sum(), "right": rows.sum(),
        }
        for av, bv in [(11, 7), (7, 11), (12, 8), (2, 3), (2, 2)]:
            with self.subTest(a=av, b=bv):
                state = Workspace(roots, {"a": av, "b": bv}).state
                self.assertFalse(state.errors)
                r = state.results
                self.assertEqual(r["columns"].values.tolist(),
                                 [av * x // bv for x in range(1, bv)])
                self.assertEqual(r["rows"].values.tolist(),
                                 [bv * y // av for y in range(1, av)])
                self.assertTrue(r["union"].mask.all())
                self.assertEqual(r["union"].source.ids, r["D"].ids)
                d = gcd(av, bv)
                overlap = r["overlap"]
                shared = list(zip(overlap.source.fields["u"][overlap.mask],
                                  overlap.source.fields["v"][overlap.mask]))
                self.assertEqual(shared, [(k * bv // d, k * av // d)
                                          for k in range(1, d)])
                total = r["left"].values[0] + r["right"].values[0]
                self.assertEqual(total - overlap.cardinality, (av - 1) * (bv - 1))

    def test_quotient_region_reorients_to_floor_columns_without_new_items(self):
        _, region, incidence, _, _ = quotient_fixture()
        a = param("a")
        reoriented = region.arrange(F.i, a - F.j).where(F.value >= a * param("b"))
        for av, bv in [(11, 7), (12, 8)]:
            with self.subTest(a=av, b=bv):
                original = incidence.evaluate(a=av, b=bv)
                moved = reoriented.evaluate(a=av, b=bv)
                self.assertEqual(moved.source.ids, original.source.ids)
                np.testing.assert_array_equal(moved.mask, original.mask)
                points = {tuple(p) for p in moved.source.positions[moved.mask]}
                self.assertEqual(points, {(x, y) for x in range(bv)
                                          for y in range(1, av * x // bv + 1)})

    def test_quotient_and_remainder_grid_of_cases(self):
        remainder, region, lens, counts, rolled = quotient_fixture()
        for a in range(2, 14):
            for b in range(2, 14):
                with self.subTest(a=a, b=b):
                    c = counts.evaluate(a=a, b=b)
                    self.assertEqual(c.values.tolist(), [a * i // b for i in range(b)])
                    expected = [
                        (a * i + b * j) % (a * b) for i in range(b) for j in range(a)
                    ]
                    r = rolled.evaluate(a=a, b=b)
                    self.assertEqual(r.values.tolist(), expected)
                    self.assertEqual(len(set(r.ids)), len(r))
        r = rolled.evaluate(a=6, b=4)
        self.assertLess(len(set(r.sources)), len(r))

    def test_count_contributors_zero_groups_and_columns(self):
        _, _, lens, counts, _ = quotient_fixture()
        c = counts.evaluate(a=11, b=7)
        self.assertEqual(c.values.tolist(), [0, 1, 3, 4, 6, 7, 9])
        self.assertEqual(c.metadata["population"], (11,) * 7)
        self.assertEqual(c.contributor_ids(0), ())
        self.assertEqual(len(c.contributor_ids(3)), 4)
        self.assertEqual(
            lens.count(by=F.j).evaluate(a=11, b=7).values.tolist(),
            [0, 0, 1, 1, 2, 3, 3, 4, 5, 5, 6],
        )
        self.assertIn("grouped by i", c.metadata["formula"])

    def test_window_and_composite_keys(self):
        g = Collection.grid(3, 4, values=10 * F.i + F.j).arrange(F.j, -F.i)
        inc = Lens(True).window((0, -2), (4, -1))(g)
        self.assertEqual(inc.count(by=F.i).evaluate().values.tolist(), [0, 0, 4])
        both = g.where(F.value % 2 == 0).count(by=(F.i, F.j)).evaluate()
        self.assertEqual(len(both), 12)
        self.assertEqual(sum(both.values), 6)

    def test_rearranged_counts_preserve_measurements_but_new_values_do_not_claim_them(
        self,
    ):
        _, _, _, counts, _ = quotient_fixture()
        a = counts.arrange(F.key, F.value).order_by(-F.key)
        self.assertEqual(len(a.evaluate(a=11, b=7).contributor_ids(3)), 4)
        changed = a.with_values(F.value + 1).evaluate(a=11, b=7)
        with self.assertRaises(ValueError):
            changed.contributor_ids(3)
        self.assertIn("prior_measurement", changed.metadata)

    def test_counts_are_sources_for_new_relations(self):
        _, _, _, counts, _ = quotient_fixture()
        arranged = counts.arrange(F.key, F.value, 0)
        counted_again = arranged.where(F.value >= 4).count().arrange(F.index, F.value)
        self.assertEqual(counted_again.evaluate(a=11, b=7).values.tolist(), [4])
        self.assertEqual(counted_again.evaluate(a=8, b=7).values.tolist(), [3])

    def test_arbitrary_3d_groups_and_driver_storage_order(self):
        _, _, _, counts, _ = quotient_fixture()
        driver = counts.arrange(F.value, F.key, -F.value)
        shuffled = driver.order_by(-F.key)
        cloud = Arrangement.points(
            [0, 1, 2, 3, 4, 5, 6, 7, 8], [[i % 3, i * i % 5, i % 2] for i in range(9)]
        )
        d = driver.bind(on=F.value % 7)
        shifted = cloud | Move(vector(d, 0, -d))
        permuted = cloud | Move(
            vector(shuffled.bind(on=F.value % 7), 0, -shuffled.bind(on=F.value % 7))
        )
        p = {"a": 11, "b": 7}
        np.testing.assert_array_equal(
            shifted.evaluate(**p).positions, permuted.evaluate(**p).positions
        )
        self.assertEqual(
            (cloud | Values(F.value + d)).evaluate(**p).values.tolist(),
            [0, 2, 5, 7, 10, 12, 15, 7, 9],
        )
        to_positions = cloud.move(
            driver.bind(on=F.value % 7, read=vector(F.x, F.y, F.z))
        ).evaluate(**p)
        np.testing.assert_array_equal(to_positions.positions[3], [4, 7, -3])

    def test_driver_missing_or_ambiguous_keys_fail(self):
        target = Collection.sequence(3, start=0).arrange(F.index, 0)
        for source in [
            Collection.literal([5], keys=[0]),
            Collection.literal([1, 2, 3], keys=[0, 0, 2]),
        ]:
            with self.assertRaises(EvaluationError):
                target.move(vector(source.bind(on=F.value), 0)).evaluate()
        bad = target.move(vector(1, 2, 3))
        engine = Evaluator()
        results, errors = engine.run({"good": target, "bad": bad})
        self.assertIn("good", results)
        self.assertIn("bad", errors)

    def test_constructor_binding_and_structural_roles(self):
        _, _, _, counts, _ = quotient_fixture()
        template = Construction(Arrangement.spiral(36, initial=param("n")), ("n",))
        seed = counts.where(F.key == 3).select().scalar()
        spiral = template(n=seed)
        r = spiral.evaluate(a=11, b=7)
        self.assertEqual(r.values[r.fields["cycle_end"]].tolist(), [10, 18, 28])
        moved = spiral.move(vector(100, 0)).evaluate(a=11, b=7)
        np.testing.assert_array_equal(moved.fields["cycle_end"], r.fields["cycle_end"])
        with self.assertRaises(ValueError):
            template(unknown=3)

    def test_spiral_contiguity_complete_prefixes_and_sieve(self):
        spiral = Arrangement.spiral(80, initial=param("n"))
        for n in range(1, 18):
            r = spiral.evaluate(n=n)
            np.testing.assert_array_equal(
                np.abs(np.diff(r.positions, axis=0)).sum(axis=1), np.ones(79)
            )
            self.assertEqual(len(set(map(tuple, r.positions))), 80)
            for i in np.flatnonzero(r.fields["cycle_end"]):
                k = int(r.fields["cycle"][i])
                self.assertEqual(r.values[i], k * (k + n - 1))
                p = r.positions[: i + 1]
                self.assertEqual(int(np.prod(p.max(axis=0) - p.min(axis=0) + 1)), i + 1)
        s = Arrangement.spiral(36, initial=param("n"))
        sweep = Sweep(s.where(F.cycle_end), "n", range(1, 18))
        actual = {m["value"] for m in sweep.retain(16)}
        expected = {v for v in range(2, 37) if any(v % d == 0 for d in range(2, v))}
        self.assertEqual(actual, expected)
        self.assertEqual(len(sweep.retain(1)), 9)

    def test_value_lookup_tile_pad_concat_and_young(self):
        seq = Collection.literal([0, 1, 2, 1])
        self.assertEqual(seq.lookup([7, 9, 5]).evaluate().values.tolist(), [7, 9, 5, 9])
        with self.assertRaises(EvaluationError):
            seq.lookup([7]).evaluate()
        self.assertEqual(seq.tile(2).evaluate().values.tolist(), [0, 1, 2, 1] * 2)
        self.assertEqual(seq.tile(0).evaluate().values.tolist(), [])
        self.assertEqual(
            seq.pad(2, 1).evaluate().values.tolist(), [0, 0, 0, 1, 2, 1, 0]
        )
        self.assertEqual(
            seq.concat(Collection.literal([8, 9])).evaluate().values.tolist(),
            [0, 1, 2, 1, 8, 9],
        )
        mat = Collection.grid(2, 3, values=F.i * 3 + F.j)
        self.assertEqual(
            mat.tile(2, axis="j").evaluate().values.tolist(),
            [0, 1, 2, 0, 1, 2, 3, 4, 5, 3, 4, 5],
        )
        joined = mat.concat(mat, axis="j").evaluate()
        self.assertEqual(joined.shape, (2, 6))
        self.assertEqual(joined.values.tolist(), [0, 1, 2, 0, 1, 2, 3, 4, 5, 3, 4, 5])
        young = Collection.young([4, 2, 1]).arrange(F.j, -F.i).evaluate()
        self.assertEqual(len(young), 7)
        self.assertIsNone(young.shape)
        with self.assertRaises(EvaluationError):
            Collection.young([2, 4]).evaluate()
        with self.assertRaises(EvaluationError):
            mat.pad(1, 1).evaluate()

    def test_empty_reductions_and_axes(self):
        empty = Collection.sequence(0).arrange(F.index, 0)
        self.assertEqual(empty.count().evaluate().values.tolist(), [0])
        self.assertEqual(empty.sum().evaluate().values.tolist(), [0])
        self.assertEqual(empty.where(True).any().evaluate().values.tolist(), [0])
        self.assertEqual(empty.count(by=F.key).evaluate().values.tolist(), [])
        grid = Collection.grid(0, 3).arrange(F.j, F.i)
        self.assertEqual(len(grid.roll(axis="j", shift=1).evaluate()), 0)
        self.assertEqual(grid.evaluate().positions.shape, (0, 2))
        self.assertEqual(
            Collection.grid(3, 0).count(by=F.i).evaluate().values.tolist(), [0, 0, 0]
        )
        self.assertEqual(
            Collection.grid(0, 3).count(by=F.j).evaluate().values.tolist(), [0, 0, 0]
        )
        seq = Collection.sequence(3).arrange(F.s)
        self.assertEqual(
            seq.roll(axis="s", shift=1).evaluate().values.tolist(), [3, 1, 2]
        )

    def test_permutation_and_boundary_checks(self):
        s = Collection.sequence(3)
        self.assertEqual(s.permute([2, 0, 1]).evaluate().values.tolist(), [3, 1, 2])
        for indices in ([0, 0, 1], [-1, 0, 1], [0, 1, 3]):
            with self.assertRaises(EvaluationError):
                s.permute(indices).evaluate()
        with self.assertRaises(EvaluationError):
            s.gather([-1]).evaluate()
        matrix = Collection.grid(2, 3).arrange(F.j, F.i)
        with self.assertRaises(EvaluationError):
            matrix.roll(axis="j", shift=F.j).evaluate()
        with self.assertRaises(EvaluationError):
            Arrangement.points([1], [[0, 0, 0]]).roll(axis="i", shift=1).evaluate()

    def test_extension_matrices_from_shared_primitives(self):
        for b, a in ((7, 11), (11, 7), (7, 7)):
            if b <= a:
                identity = Collection.grid(b, b, values=choose(F.i == F.j, 1, 0))
                result = identity.concat(Collection.grid(b, a - b, values=0), axis="j")
            else:
                identity = Collection.grid(a, a, values=choose(F.i == F.j, 1, 0))
                result = identity.tile((b + a - 1) // a, axis="i").gather(
                    range(b), axis="i"
                )
            values = result.evaluate().values.reshape(b, a)
            expected = np.asarray(
                [[int(j == i % a) for j in range(a)] for i in range(b)]
            )
            np.testing.assert_array_equal(values, expected)

    def test_fixed_gather_substitution_commutation_and_3d_plane(self):
        source = Collection.literal([2, 0, 1])
        table = Collection.literal([11, 13, 17])
        addresses = [2, 2, 0]
        a = source.gather(addresses).lookup(table).evaluate()
        b = source.lookup(table).gather(addresses).evaluate()
        np.testing.assert_array_equal(a.values, b.values)
        cube = Collection.grid(4, 4, 4).arrange(F.i, F.j, F.k)
        self.assertEqual(cube.where(F.x == 0).evaluate().cardinality, 16)


class HistoryTests(unittest.TestCase):
    def test_relation_edit_reverses_membership_presentation(self):
        source = Collection.sequence(4).arrange(F.index, 0)
        workspace = Workspace({"lens": source.where(F.value % 2 == 0)})
        forward = workspace.set("lens", source.where(F.value >= 3))
        backward = workspace.undo()
        frame = forward.frame("lens", 0.75)
        reverse = backward.frame("lens", 0.25)
        self.assertEqual(frame.matched_before, (False, True, False, True))
        self.assertEqual(frame.matched_after, (False, False, True, True))
        self.assertEqual(frame.matched_before, reverse.matched_before)
        self.assertEqual(frame.matched_after, reverse.matched_after)
        self.assertEqual(frame.fraction, reverse.fraction)
        self.assertEqual(
            workspace.state.results["lens"].mask.tolist(), [False, True, False, True]
        )

    def assert_reverse(self, forward, backward, name):
        for t in np.linspace(0, 1, 13):
            a = forward.frame(name, 1 - t)
            b = backward.frame(name, t)
            np.testing.assert_allclose(a.positions, b.positions, atol=1e-12)
            np.testing.assert_allclose(a.opacity, b.opacity, atol=1e-12)
            self.assertEqual(a.label_pairs, b.label_pairs)

    def test_curved_reverse_redo_and_branch(self):
        a = Collection.sequence(4).arrange(F.index, 0, 0)
        w = Workspace({"a": a})
        original = w.state
        t = w.set(
            "a", a.move(vector(5, 0, 1)), motion=Motion.arc(height=3, dimension=3)
        )
        self.assertGreater(t.frame("a", 0.5).positions[0, 1], 2)
        reverse = w.undo()
        self.assertIs(w.state, original)
        self.assert_reverse(t, reverse, "a")
        self.assertIs(w.redo(), t)
        w.undo()
        w.set("a", a.with_values(F.value + 1))
        self.assertFalse(w.can_redo)

    def test_lossy_gather_reduction_and_values_restore_exactly(self):
        a = Collection.sequence(4, start=10).arrange(F.index, 0)
        w = Workspace({"a": a})
        original = w.state
        lossy = a.items.gather([2, 2, 0]).arrange(F.index, 0)
        t = w.set("a", lossy)
        reverse = w.undo()
        self.assertIs(w.state, original)
        self.assert_reverse(t, reverse, "a")
        self.assertEqual(
            t.frame("a", 0.5).before_ids.count(original.results["a"].ids[2]), 2
        )
        reduced = a.where(F.value > 10).count().arrange(F.index, 0)
        t = w.set("a", reduced)
        self.assert_reverse(t, w.undo(), "a")
        t = w.set("a", a.with_values(0))
        self.assert_reverse(t, w.undo(), "a")
        self.assertEqual(w.state.results["a"].values.tolist(), [10, 11, 12, 13])

    def test_parameter_undo_zero_values_and_capture_freeze(self):
        _, _, _, c, _ = quotient_fixture()
        a = c.arrange(F.key, F.value)
        w = Workspace({"counts": a}, parameters={"a": 11, "b": 7})
        obs = w.capture("One group is empty.")
        t = w.set_parameters(a=12)
        self.assertEqual(
            w.state.results["counts"].values.tolist(), [0, 1, 3, 5, 6, 8, 10]
        )
        self.assertEqual(
            obs.state.results["counts"].values.tolist(), [0, 1, 3, 4, 6, 7, 9]
        )
        self.assert_reverse(t, w.undo(), "counts")
        self.assertEqual(w.state.parameters["a"], 11)

    def test_json_preserves_pending_redo_path_and_contributors(self):
        _, _, _, c, _ = quotient_fixture()
        a = c.arrange(F.key, F.value)
        w = Workspace({"a": a}, parameters={"a": 11, "b": 7})
        w.capture("counts")
        t = w.set("a", a.move(vector(2, 1)), motion=Motion.arc(height=3))
        w.undo()
        payload = w.to_json()
        other = Workspace.from_json(payload)
        self.assertTrue(other.can_redo)
        replay = other.redo()
        self.assert_reverse(t, replay.reverse(), "a")
        self.assertEqual(len(other.observations[0].state.results["a"].parents), 7)
        self.assertEqual(
            len(
                other.observations[0]
                .state.evaluated[
                    next(
                        k
                        for k, v in other.observations[0].state.evaluated.items()
                        if hasattr(v, "metadata")
                        and v.metadata.get("reducer") == "count"
                    )
                ]
                .contributor_ids(3)
            ),
            4,
        )

    def test_failure_isolation_and_failed_action_undo(self):
        a = Collection.sequence(3).arrange(F.index, 0)
        w = Workspace({"good": a, "bad": a})
        old = w.state
        w.set("bad", a.with_values(F.value % 0))
        self.assertIn("good", w.state.results)
        self.assertIn("bad", w.state.errors)
        w.undo()
        self.assertIs(w.state, old)

    def test_icarus_workspace_import_preserves_history_and_reexports_as_kaleion(self):
        points = Collection.sequence(3).arrange(F.index, 0)
        workspace = Workspace({"points": points})
        forward = workspace.set(
            "points", points.move(vector(2, 0)), motion=Motion.arc(height=1)
        )
        workspace.undo()
        original = json.loads(workspace.to_json())
        self.assertEqual(original["format"], "kaleion-python")
        legacy = {**original, "format": "icarus-python"}
        restored = Workspace.from_json(json.dumps(legacy))
        self.assertEqual(json.loads(restored.to_json()), original)
        self.assertTrue(restored.can_redo)
        self.assert_reverse(forward, restored.redo().reverse(), "points")
        with self.assertRaisesRegex(ValueError, "Unsupported workspace"):
            Workspace.from_json(json.dumps({**legacy, "format": "unknown"}))

    def test_invalid_motion_does_not_commit(self):
        a = Collection.sequence(2).arrange(F.index, 0)
        w = Workspace({"a": a})
        old = w.state
        with self.assertRaises(ValueError):
            w.set("a", a.move(vector(1, 0)), motion=Motion.custom(F.sx, F.sy))
        self.assertIs(w.state, old)
        self.assertFalse(w.can_undo)

    def test_creation_deletion_and_restoration(self):
        a = Collection.sequence(2).arrange(F.index)
        w = Workspace()
        t = w.set("a", a)
        self.assertEqual(t.frame("a", 0).opacity.tolist(), [0, 0])
        self.assert_reverse(t, w.undo(), "a")
        w.redo()
        obs = w.capture()
        t = w.remove("a")
        self.assertEqual(t.frame("a", 1).opacity.tolist(), [0, 0])
        w.undo()
        w.set("a", a.with_values(99))
        w.restore(obs)
        self.assertEqual(w.state.results["a"].values.tolist(), [1, 2])
        w.undo()
        self.assertEqual(w.state.results["a"].values.tolist(), [99, 99])

    def test_empty_arrangement_roundtrip(self):
        w = Workspace({"empty": Collection.sequence(0).arrange(F.index, 0, 0)})
        r = Workspace.from_json(w.to_json()).state.results["empty"]
        self.assertEqual(r.positions.shape, (0, 3))


if __name__ == "__main__":
    unittest.main()
