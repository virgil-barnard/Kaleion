"""Linked views read explicit capture versions and retain zero evidence."""

import unittest
from unittest.mock import patch

from kaleion import Collection, F, Workspace
from examples.studio.adapter import Studio


class StudioViewTests(unittest.TestCase):
    def studio(self, **roots):
        studio = Studio()
        studio.workspace = Workspace(roots, max_items=2000, max_history=40)
        self.assertFalse(studio.workspace.state.errors)
        return studio

    def ref(self, studio, name, index=0):
        return next(o for o in studio.state()["objects"] if o["name"] == name)["rows"][index]["ref"]

    def test_absent_coverage_key_has_expected_point_but_no_invented_candidate(self):
        cells = Collection.grid(3, 3, values=7).arrange(F.j, -F.i)
        hits = cells.where(F.j < F.i)
        studio = self.studio(hits=hits, surviving=hits.select(), expected=Collection.literal([2, 0, 1]))
        saved = studio.workspace.to_json()
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
            report = studio.coverage("surviving", ["i"], "expected", ["value"], 0)
            left = studio.capture(report["expected_capture"], 0)
            right = studio.capture(report["capture"], 0)
            missing = report["rows"][1]
            self.assertIn(missing["expected_ref"], [row["ref"] for row in left["rows"]])
            self.assertEqual(missing["matches"], [])
            self.assertEqual(missing["members"], [])
            self.assertFalse(any(row["fields"]["i"] == "0" for row in right["rows"]))
            raw = studio.capture(studio.workspace.state.results["hits"].node, 0)
            self.assertEqual(sum(row["match"] for row in raw["rows"]), 3)
            self.assertEqual(len(raw["rows"]), 9)
        self.assertEqual(studio.workspace.to_json(), saved)

    def test_quotient_measurement_keeps_source_for_zero_and_complete_contributors(self):
        cells = Collection.grid(7, 11, values=11*F.i+7*F.j).arrange(F.j, -F.i)
        counts = cells.where(F.value >= 77).count(by=F.i)
        studio = self.studio(counts=counts)
        before = studio.workspace.to_json()
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
            for i, count in enumerate([0, 1, 3, 4, 6, 7, 9]):
                evidence = studio.contributors(self.ref(studio, "counts", i), 0)
                m = evidence["measurement"]
                source = studio.capture(evidence["universe"], 0)
                self.assertEqual(len(source["rows"]), 77)
                self.assertEqual(source["roots"], [])
                self.assertEqual(m["contributor_count"], str(count))
                self.assertEqual(m["population"], "11")
                self.assertEqual([(int(c["item"]["fields"]["i"]), int(c["item"]["fields"]["j"])) for c in m["contributors"]],
                                 [(i, j) for j in range(11) if 11*i+7*j >= 77])
                self.assertTrue(all(c["item"]["ref"] in [r["ref"] for r in source["rows"]] for c in m["contributors"]))
        self.assertEqual(studio.workspace.to_json(), before)

    def test_zero_and_signed_weights_and_large_evidence_are_not_truncated(self):
        huge = 2**90 + 1
        cells = Collection.literal([huge, huge, huge], fields={"weight": [0, -7, 7]})
        studio = self.studio(total=cells.sum(value=F.weight), many=Collection.grid(40).count())
        evidence = studio.contributors(self.ref(studio, "total"), 0)
        self.assertEqual(evidence["measurement"]["item"]["value"], "0")
        self.assertEqual([c["weight"] for c in evidence["measurement"]["contributors"]], ["0", "-7", "7"])
        view = studio.capture(evidence["universe"], 0)
        self.assertEqual([r["fields"]["value"] for r in view["rows"]], [str(huge)] * 3)
        self.assertEqual(len({tuple(r["ref"]) for r in view["rows"]}), 3)
        many = studio.contributors(self.ref(studio, "many"), 0)["measurement"]
        self.assertEqual(len(many["contributors"]), 40)
        self.assertFalse(many["truncated"])

    def test_previous_driver_capture_survives_named_placement_save_and_history(self):
        counts = Collection.grid(3, 2).count(by=F.i).arrange(F.i, F.value)
        probes = Collection.literal([2, 0, 1]).arrange(F.value, counts.bind(on=F.value, key=F.i))
        studio = self.studio(counts=counts, probes=probes)
        ref = self.ref(studio, "probes")
        binding = studio.inspect_ref(ref, 0)["bindings"][0]
        old_view = studio.capture(binding["driver"][0], 0)
        command = dict(action="place", name="counts", args=dict(source="counts", coordinates=[{"field":"i"}, {"integer":"99"}]))
        preview = studio.preview(command, 0)
        studio.commit(preview["token"], 0)
        saved = studio.workspace.to_json()
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
            studio.reopen(saved, studio.revision)
            old = studio.capture(binding["driver"][0], studio.revision)
            self.assertEqual(old["rows"], old_view["rows"])
            self.assertEqual(old["roots"], [])
            current = studio.capture(studio.workspace.state.results["counts"].node, studio.revision)
            self.assertEqual([r["position"][1] for r in current["rows"]], [99., 99., 99.])
            self.assertEqual([r["position"][1] for r in old["rows"]], [2., 2., 2.])
            self.assertEqual(studio.contributors(binding["driver"], studio.revision)["measurement"]["contributor_count"], "2")
            studio.history("undo", studio.revision, "counts")
            self.assertEqual(studio.capture(binding["driver"][0], studio.revision)["roots"], ["counts"])
            studio.history("redo", studio.revision, "counts")
            self.assertEqual(studio.capture(binding["driver"][0], studio.revision)["rows"], old["rows"])
        self.assertEqual(studio.workspace.to_json(), saved)

    def test_empty_and_unavailable_are_distinct_and_queries_preserve_preview(self):
        studio = self.studio(empty=Collection.grid(0, 3), counts=Collection.grid(0, 3).count(by=F.j))
        pending = studio.preview(dict(action="integers", name="idea", args=dict(values=["9"])), 0)
        saved = studio.workspace.to_json()
        for capture in (None, 1, "", "not-a-capture"):
            with self.subTest(capture=capture), self.assertRaises(ValueError):
                studio.capture(capture, 0)
        with self.assertRaises(ValueError):
            studio.capture(studio.workspace.state.results["empty"].node, 1)
        with self.assertRaises((ValueError, KeyError)):
            studio.contributors(["not-a-capture", "no-item"], 0)
        empty = studio.capture(studio.workspace.state.results["empty"].node, 0)
        self.assertEqual(empty["rows"], [])
        self.assertEqual(empty["axes"], ["i", "j"])
        for i in range(3):
            evidence = studio.contributors(self.ref(studio, "counts", i), 0)
            self.assertEqual(evidence["measurement"]["population"], "0")
            self.assertEqual(studio.capture(evidence["universe"], 0)["rows"], [])
        # Query bounds do not depend solely on a workspace's evaluation budget.
        oversized = Studio()
        oversized.workspace = Workspace({"large": Collection.sequence(2001)}, max_items=2100, max_history=40)
        with self.assertRaisesRegex(ValueError, "2000 captured occurrences"):
            oversized.capture(oversized.workspace.state.results["large"].node, 0)
        self.assertEqual(studio.revision, 0)
        self.assertEqual(studio.pending.token, pending["token"])
        self.assertEqual(studio.workspace.to_json(), saved)


if __name__ == "__main__":
    unittest.main()
