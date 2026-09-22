"""Coverage over independent keys; guarded adoption is a composable definition."""

import unittest
from unittest.mock import patch

import numpy as np

from kaleion import Collection, F, Product, Workspace, param
from examples.studio.adapter import Studio
from examples.studio.coverage import unique_assignment


class StudioCoverageTests(unittest.TestCase):
    def studio(self, **roots):
        studio = Studio()
        studio.workspace = Workspace(roots, max_items=2000, max_history=40)
        self.assertFalse(studio.workspace.state.errors)
        return studio

    def report(self, studio, source="hits", by=None, expected="expected", expected_by=None):
        return studio.coverage(source, ["i"] if by is None else by, expected,
                               ["value"] if expected_by is None else expected_by, studio.revision)

    def command(self, report, value=None, field="owner"):
        return dict(action="assignment", name="assigned", args=dict(
            source=report["name"], by=report["by"], expected=report["expected"],
            expected_by=report["expected_by"], capture=report["capture"],
            expected_capture=report["expected_capture"], field=field,
            value={"field": "j"} if value is None else value))

    def test_balanced_totals_do_not_hide_zero_multiple_or_absent_groups(self):
        cells = Collection.grid(3, 3)
        hits = cells.where(F.j < F.i)
        studio = self.studio(hits=hits, selected=hits.select(), expected=Collection.literal([2, 0, 1]))
        before = studio.workspace.to_json()
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
            report = self.report(studio)
            selected = self.report(studio, "selected")
        self.assertEqual(studio.workspace.to_json(), before)
        self.assertEqual([r["count"] for r in report["rows"]], ["2", "0", "1"])
        self.assertEqual(sum(int(r["count"]) for r in report["rows"]), 3)
        self.assertEqual(report["summary"]["expected"], "3")
        self.assertFalse(report["passed"])
        self.assertTrue(report["rows"][1]["present"])
        self.assertFalse(selected["rows"][1]["present"])
        self.assertIsNone(selected["rows"][1]["group"])
        self.assertEqual(selected["rows"][1]["matches"], [])
        with self.assertRaisesRegex(ValueError, "exactly one"):
            studio.preview(self.command(report), studio.revision)
        self.assertIsNone(studio.pending)
        self.assertFalse(studio.workspace.can_undo)

    def test_outside_matches_fail_but_nonincident_candidates_do_not(self):
        cells = Collection.grid(4, 3)
        studio = self.studio(hits=cells.where(F.i == F.j), outside=cells.where(F.j == 0),
                             expected=Collection.literal([0, 1, 2]))
        good = self.report(studio)
        self.assertTrue(good["passed"])
        bad = self.report(studio, "outside")
        self.assertFalse(bad["passed"])
        self.assertEqual(bad["summary"]["outside"], "1")
        self.assertEqual(bad["unexpected"][0]["key"], ["3"])
        self.assertEqual(len(bad["unexpected"][0]["matches"]), 1)
        with self.assertRaisesRegex(ValueError, "outside matches"):
            studio.preview(self.command(bad), studio.revision)
        # A fully empty declared domain is explicit and vacuous, not a missing input.
        empty = self.studio(hits=Collection.grid(0, 3), expected=Collection.literal([]))
        report = self.report(empty)
        self.assertTrue(report["empty"])
        self.assertTrue(report["passed"])
        preview = empty.preview(self.command(report), 0)
        empty.commit(preview["token"], 0)
        self.assertEqual(len(empty.workspace.state.results["assigned"]), 0)

    def test_composite_keys_exact_integers_and_equal_valued_duplicates(self):
        huge = 2**90 + 1
        source = Collection.literal([0, huge, huge+1], fields={"target": [huge, huge, huge+1], "channel": ["a", "b", "a"]})
        expected = Collection.literal([9, 8, 7], fields={"id": [huge+1, huge, huge], "kind": ["a", "a", "b"]})
        studio = self.studio(hits=source, expected=expected)
        report = self.report(studio, by=["target", "channel"], expected_by=["id", "kind"])
        self.assertTrue(report["passed"])
        self.assertEqual(report["rows"][0]["key"], [str(huge+1), "a"])
        self.assertEqual(report["rows"][0]["key_types"], ["integer", "text"])
        p = studio.preview(self.command(report, {"field": "value"}), 0)
        studio.commit(p["token"], 0)
        self.assertEqual(studio.workspace.state.results["assigned"].fields["owner"].tolist(), [huge+1, 0, huge])
        repeated = self.studio(hits=Collection.literal([7, 7], fields={"i": [0, 0]}), expected=Collection.literal([0]))
        report = self.report(repeated)
        self.assertEqual(report["rows"][0]["count"], "2")
        self.assertFalse(report["passed"])

    def test_assignment_preserves_expected_identity_and_explains_its_value(self):
        expected = Collection.literal([2, 0, 1]).arrange(F.value, 0)
        hits = Collection.grid(3, 3).where(F.j == F.i)
        studio = self.studio(hits=hits, expected=expected)
        report = self.report(studio)
        p = studio.preview(self.command(report), 0)
        self.assertFalse(studio.workspace.can_undo)
        studio.commit(p["token"], 0)
        result = studio.workspace.state.results["assigned"]
        original = studio.workspace.state.results["expected"]
        self.assertEqual(result.ids, original.ids)
        self.assertEqual(result.values.tolist(), [2, 0, 1])
        self.assertEqual(result.fields["owner"].tolist(), [2, 0, 1])
        np.testing.assert_array_equal(result.positions, original.positions)
        saved = studio.workspace.to_json()
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
            receipt = studio.inspect_ref([result.node, result.ids[1]], studio.revision)
            self.assertEqual(receipt["bindings"][0]["value"], "0")
            measured = studio.inspect_ref(receipt["bindings"][0]["driver"], studio.revision)
            self.assertEqual(measured["measurement"]["contributor_count"], "1")
            self.assertEqual(measured["measurement"]["contributors"][0]["weight"], "0")
            studio.history("undo", studio.revision, "assigned")
            studio.history("redo", studio.revision, "assigned")
            studio.reopen(saved, studio.revision)
            self.assertEqual(self.report(studio)["rows"], report["rows"])
            restored = studio.workspace.state.results["assigned"]
            self.assertEqual(studio.inspect_ref([restored.node, restored.ids[1]], studio.revision)["bindings"], receipt["bindings"])
        # The assigned field is an ordinary keyed driver, independent of row order.
        driver = studio.workspace.state.roots["assigned"]
        probes = Collection.literal([1, 2, 0]).arrange(F.value, driver.bind(on=F.value, key=F.value, read=F.owner))
        self.assertEqual(probes.evaluate().positions[:, 1].tolist(), [1, 2, 0])

    def test_guards_remain_live_when_definition_parameters_change(self):
        cells = Collection.grid(4, 3)
        expected = Collection.literal([0, 1, 2])
        # At n=0: one match each; at n=1: an extra out-of-domain match.
        hits = cells.where((F.i == F.j) | ((F.i == 3) & (F.j == 0) & (param("n") == 1)))
        assignment = unique_assignment(hits, ["i"], expected, ["value"], F.j, "owner")
        self.assertEqual(assignment.evaluate(n=0).fields["owner"].tolist(), [0, 1, 2])
        with self.assertRaisesRegex((KeyError, ValueError), "Missing driver key"):
            assignment.evaluate(n=1)
        changing = cells.where((F.i == F.j) & (F.i >= param("lower")))
        guarded = unique_assignment(changing, ["i"], expected, ["value"], F.j, "owner")
        with self.assertRaisesRegex(ValueError, "exactly one"):
            guarded.evaluate(lower=1)
        sparse = unique_assignment(changing.select(), ["i"], expected, ["value"], F.j, "owner")
        with self.assertRaisesRegex((KeyError, ValueError), "Missing driver key"):
            sparse.evaluate(lower=1)

    def test_invalid_keys_inputs_and_stale_reports_never_adopt(self):
        studio = self.studio(hits=Collection.grid(2, 2).where(F.i == F.j), expected=Collection.literal([0, 1]),
                             duplicates=Collection.literal([0, 0]))
        for by, keys in (([], ["value"]), (["i", "i"], ["value", "key"]), (["i"], ["value", "key"]), (["unknown"], ["value"])):
            with self.subTest(by=by, keys=keys), self.assertRaises((ValueError, KeyError)):
                self.report(studio, by=by, expected_by=keys)
        with self.assertRaisesRegex(ValueError, "unique"):
            self.report(studio, expected="duplicates")
        with self.assertRaisesRegex(ValueError, "collection or arrangement"):
            self.report(studio, expected="hits", expected_by=["i"])
        report = self.report(studio)
        for field in ("value", "key", "index", "bad field"):
            with self.assertRaisesRegex(ValueError, "new field name"):
                studio.preview(self.command(report, field=field), 0)
        for capture in ("capture", "expected_capture"):
            command = self.command(report);command["args"][capture] = "old"
            with self.assertRaisesRegex(ValueError, "earlier capture"):
                studio.preview(command, 0)
        p = studio.preview(self.command(report), 0);studio.commit(p["token"], 0)
        with self.assertRaisesRegex(ValueError, "out of date"):
            studio.coverage("hits", ["i"], "expected", ["value"], 0)
        with self.assertRaises(ValueError):
            studio.commit(p["token"], 1)
        # An unavailable source never becomes an empty successful report.
        studio.workspace.set("unavailable", Collection.sequence(param("missing")))
        with self.assertRaises(KeyError):
            self.report(studio, source="unavailable")
        self.assertTrue(self.report(studio)["passed"])

    def test_hermitian_spread_uses_the_same_keys_and_missing_witnesses(self):
        # Restrict to the seven declared blocks before forming the 7x28 product;
        # the full 91x28 lesson exceeds the studio's 2000-item operation budget.
        from test_finite_geometry_lessons import HERMITIAN, pairing, vector_for
        vectors = [vector_for(i) for i in range(91)]
        curve_keys = [i for i, v in enumerate(vectors) if pairing(v, v) == 0]
        blocks = {i: {k for k in curve_keys if pairing(v, vectors[k]) == 0} for i, v in enumerate(vectors)}
        chosen = [i for i, points in blocks.items() if len(points) == 4 and (i == 0 or pairing(vectors[i], vectors[0]) == 0)]
        self.assertEqual(len(chosen), 7)
        points = HERMITIAN["projective_points"]()
        curve = points.where(F.self_pair == 0).select().order_by(-F.value)
        lines = HERMITIAN["projective_points"](labels=Collection.literal(chosen[::-1]))
        pairs = Product(line=lines, point=curve)
        domain = pairs.domain.annotate(point_code=pairs.read("point", F.value), owner=pairs.read("line", F.value))
        relation = HERMITIAN["hermitian_pair"](
            tuple(pairs.read("line", F[k]) for k in ("u", "v", "w")),
            tuple(pairs.read("point", F[k]) for k in ("u", "v", "w")), 3) == 0
        hits = domain.where(relation)
        without_polar = hits & hits.universe.where(F.owner != 0)
        studio = self.studio(hits=hits, expected=curve, without=without_polar, sparse=without_polar.select())
        report = self.report(studio, by=["point_code"])
        self.assertTrue(report["passed"])
        self.assertEqual(report["summary"]["unique"], "28")
        for source in ("without", "sparse"):
            broken = self.report(studio, source, by=["point_code"])
            self.assertFalse(broken["passed"])
            missing = [r for r in broken["rows"] if r["status"] == "missing"]
            self.assertEqual({int(r["key"][0]) for r in missing}, blocks[0])
            self.assertTrue(all(r["present"] == (source == "without") for r in missing))
        p = studio.preview(self.command(report, {"field": "owner"}, "block"), 0)
        studio.commit(p["token"], 0)
        result = studio.workspace.state.results["assigned"]
        expected_owner = {k: i for i in chosen for k in blocks[i]}
        self.assertEqual(result.fields["block"].tolist(), [expected_owner[int(k)] for k in result.values])


if __name__ == "__main__":
    unittest.main()
