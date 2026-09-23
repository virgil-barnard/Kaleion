"""The shared Measure command authors and restores exact prefix measurements."""

import unittest
from unittest.mock import patch

from examples.studio.adapter import Studio
from test_studio_weighted import apply, f, n, op, read


class StudioPrefixTests(unittest.TestCase):
    def test_layer_offsets_drive_reversible_placement_and_nested_saved_evidence(self):
        studio = Studio()
        apply(studio, "integers", "heights", values=["5", "3", "2", "0"])
        apply(studio, "grid", "grid", shape=["4", "5"], axes=["i", "j"], value=n(1))
        apply(studio, "lens", "diagram", source="grid", rule=op("<", f("j"), read("heights", f("i"), f("key"))))
        apply(studio, "measure", "layers", source="diagram", by=["j"], reducer="count")
        before = studio.workspace.to_json()
        preview = studio.preview(dict(action="measure", name="offsets", args=dict(
            source="layers", by=[], reducer="prefix_sum", order=["j"], key="j", weight=f("value"))), studio.revision)
        self.assertEqual(studio.workspace.to_json(), before)
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
            studio.commit(preview["token"], studio.revision)
        self.assertEqual(studio.workspace.state.results["offsets"].values.tolist(), [0, 3, 6, 8, 9])
        apply(studio, "select", "cells", source="diagram")
        apply(studio, "place", "cells", source="cells", coordinates=[f("i"), f("j")])
        unplaced = studio.workspace.state.results["cells"].positions.tolist()
        apply(studio, "place", "cells", source="cells", coordinates=[op("+", f("i"), read("offsets", f("j"), f("j"))), n(0)])
        saved = studio.workspace.to_json()
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
            studio.reopen(saved, studio.revision)
            offsets = studio.workspace.state.results["offsets"]
            receipt = studio.contributors([offsets.node, offsets.ids[3]], studio.revision)["measurement"]
            self.assertEqual(receipt["reducer"], "prefix_sum")
            self.assertEqual([c["weight"] for c in receipt["contributors"]], ["3", "3", "2"])
            layer = studio.contributors(receipt["contributors"][2]["item"]["ref"], studio.revision)["measurement"]
            self.assertEqual(layer["contributor_count"], "2")
            first = studio.contributors([offsets.node, offsets.ids[0]], studio.revision)
            self.assertEqual(first["measurement"]["contributor_count"], "0")
            self.assertEqual(len(studio.capture(first["universe"], studio.revision)["rows"]), 5)
            studio.history("undo", studio.revision, "cells")
            self.assertEqual(studio.workspace.state.results["cells"].positions.tolist(), unplaced)
            studio.history("redo", studio.revision, "cells")
            self.assertEqual(sorted(studio.workspace.state.results["cells"].positions[:, 0]), list(range(10)))

    def test_failed_order_preview_preserves_work_then_an_explicit_tiebreaker_succeeds(self):
        studio = Studio()
        apply(studio, "integers", "source", values=["2", "2", "1"])
        before = studio.workspace.to_json()
        args = dict(source="source", by=[], reducer="prefix_sum", order=["value"], key="key", weight=f("value"))
        with self.assertRaisesRegex(ValueError, "ties within a group"):
            studio.preview(dict(action="measure", name="offsets", args=args), studio.revision)
        self.assertEqual(studio.workspace.to_json(), before)
        args["order"] = ["value", "key"]
        preview = studio.preview(dict(action="measure", name="offsets", args=args), studio.revision)
        studio.commit(preview["token"], studio.revision)
        self.assertEqual(studio.workspace.state.results["offsets"].values.tolist(), [1, 3, 0])

    def test_parameter_weight_reads_keep_exact_values_and_failure_isolation(self):
        studio = Studio()
        proposed = studio.preview_case({"scale": "2"}, studio.revision)
        studio.commit(proposed["token"], studio.revision)
        big = 2**100
        apply(studio, "integers", "driver", values=[str(big), "0", "-4"])
        apply(studio, "integers", "items", values=["99", "99", "99"])
        scale = {"parameter": "scale"}
        weight = op("+", op("*", scale, read("driver", f("key"), f("key"))), op("//", n(0), scale))
        apply(studio, "measure", "prefix", source="items", by=[], reducer="prefix_sum", order=["key"], key="key", weight=weight)
        result = studio.workspace.state.results["prefix"]
        receipt = studio.contributors([result.node, result.ids[2]], studio.revision)["measurement"]
        self.assertEqual(receipt["item"]["value"], str(2*big))
        self.assertEqual([c["weight"] for c in receipt["contributors"]], [str(2*big), "0"])
        self.assertEqual([c["reads"][0]["value"] for c in receipt["contributors"]], [str(big), "0"])
        proposal = studio.preview_case({"scale": "-1"}, studio.revision)
        studio.commit(proposal["token"], studio.revision)
        self.assertEqual(studio.workspace.state.results["prefix"].values.tolist(), [0, -big, -big])
        saved = studio.workspace.to_json()
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
            studio.reopen(saved, studio.revision)
            studio.history("undo", studio.revision, "prefix")
            restored = studio.contributors([result.node, result.ids[2]], studio.revision)["measurement"]
            self.assertEqual(restored, receipt)
        failed = studio.preview_case({"scale": "0"}, studio.revision)
        self.assertIn("prefix", failed["errors"])
        studio.commit(failed["token"], studio.revision)
        self.assertEqual(studio.workspace.state.results["items"].values.tolist(), [99, 99, 99])


if __name__ == "__main__":
    unittest.main()
