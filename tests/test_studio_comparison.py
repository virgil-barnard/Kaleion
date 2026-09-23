"""Captured comparisons: exact quantities, independent domains, and evidence."""

import unittest
from unittest.mock import patch

from kaleion import Collection, F, Workspace, param
from examples.studio.adapter import Studio
from test_studio_weighted import radon


class StudioComparisonTests(unittest.TestCase):
    def studio(self, **roots):
        studio = Studio()
        studio.workspace = Workspace(roots, max_items=2000, max_history=40)
        return studio

    def compare(self, studio, **changes):
        args = dict(name="left",left_by=["key"],left_value="value",right="right",
                    right_by=["key"],right_value="value",expected="domain",expected_by=["key"])
        return studio.compare(**{**args,**changes},revision=studio.revision)

    def test_radon_comparison_exposes_false_reconstruction_and_retains_field_evidence(self):
        studio = radon(3,parameterized=True)
        choices = dict(name="recovered",left_by=["point_u","point_v"],left_value="recovered",
                       right="image",right_by=["u","v"],expected="image",expected_by=["u","v"])
        first = self.compare(studio,**choices)
        self.assertTrue(first["passed"])
        self.assertEqual(first["summary"]["equal"],"9")
        preview = studio.preview_case({"p":"4"},studio.revision)
        studio.commit(preview["token"],studio.revision)
        payload = studio.workspace.to_json()
        with patch("kaleion.evaluate.Evaluator.get",side_effect=AssertionError("execution")):
            studio.reopen(payload,studio.revision)
            report = self.compare(studio,**choices)
            self.assertFalse(report["passed"])
            row = report["rows"][0]
            self.assertEqual((row["key"],row["left"],row["right"],row["residual"]),(["0","0"],"-1","0","-1"))
            self.assertEqual(report["parameters"],{"p":"4"})
            receipt = studio.inspect_ref(row["left_ref"],studio.revision)
            self.assertEqual(receipt["item"]["value"],"56")
            self.assertEqual(receipt["item"]["fields"]["recovered"],"-1")
            self.assertEqual(receipt["measurement"]["contributor_count"],"5")
            self.assertEqual(studio.workspace.to_json(),payload)
            studio.history("undo",studio.revision,"recovered")
            self.assertTrue(self.compare(studio,**choices)["passed"])
            studio.history("redo",studio.revision,"recovered")
            self.assertEqual(self.compare(studio,**choices)["rows"],report["rows"])

    def test_lattice_counts_compare_to_formula_independently_of_order_and_placement(self):
        square = Collection.grid(5,5)
        measured = square.where(F.i+F.j<4).count(by=F.i)
        formula = Collection.grid(5,axes=("row",),values=4-F.row).gather([4,1,3,0,2]).arrange(F.value,0)
        domain = Collection.grid(5,axes=("expected_row",))
        studio = self.studio(left=measured,right=formula,domain=domain)
        report = self.compare(studio,left_by=["i"],right_by=["row"],expected_by=["expected_row"])
        self.assertTrue(report["passed"])
        self.assertEqual([r["left"] for r in report["rows"]],["4","3","2","1","0"])
        zero = report["rows"][-1]
        self.assertIsNotNone(zero["left_ref"])
        self.assertEqual(studio.inspect_ref(zero["left_ref"],studio.revision)["measurement"]["contributor_count"],"0")

    def test_missing_from_both_and_unexpected_keys_never_become_equal_zeroes(self):
        left = Collection.literal([0,3,99],fields={"k":[0,2,9]})
        right = Collection.literal([4,0,77],fields={"r":[2,0,8]})
        domain = Collection.literal([1,1,1],fields={"d":[0,1,2]})
        studio = self.studio(left=left,right=right,domain=domain)
        report = self.compare(studio,left_by=["k"],right_by=["r"],expected_by=["d"])
        self.assertFalse(report["passed"])
        self.assertEqual(report["summary"],dict(expected="3",equal="1",different="1",missing_left="1",missing_right="1",outside_left="1",outside_right="1"))
        missing = report["rows"][1]
        self.assertEqual(missing["status"],"missing")
        self.assertIsNone(missing["left_ref"])
        self.assertIsNone(missing["right_ref"])
        self.assertIsNone(missing["residual"])
        self.assertEqual(studio.inspect_ref(missing["expected_ref"],studio.revision)["item"]["fields"]["d"],"1")
        self.assertEqual([r["key"] for r in report["rows"] if r["status"]=="outside"],[["9"],["8"]])
        self.assertTrue(all(r["residual"] is None for r in report["rows"] if r["status"]=="outside"))

    def test_large_composite_keys_and_selected_fields_preserve_exact_residuals(self):
        big = 2**100+3
        left = Collection.literal([99,99],fields={"a":[big,0],"b":[0,big],"answer":[big,-big]})
        right = Collection.literal([7,7],fields={"u":[0,big],"v":[big,0],"truth":[-big-1,big]})
        domain = Collection.literal([0,0],fields={"du":[0,big],"dv":[big,0]})
        studio = self.studio(left=left,right=right,domain=domain)
        report = self.compare(studio,left_by=["a","b"],left_value="answer",right_by=["u","v"],right_value="truth",expected_by=["du","dv"])
        self.assertEqual([r["residual"] for r in report["rows"]],["1","0"])
        self.assertEqual(report["rows"][0]["key"],["0",str(big)])
        swapped = self.compare(studio,left_by=["b","a"],left_value="answer",right_by=["u","v"],right_value="truth",expected_by=["du","dv"])
        self.assertEqual(swapped["rows"][0]["residual"],str(2*big+1))

    def test_duplicate_keys_noninteger_fields_and_unavailable_sources_are_errors(self):
        base = Collection.literal([0,0],fields={"k":[0,0],"float":[1.0,2.0],"boolean":[True,False]})
        studio = self.studio(left=base,right=base,domain=base)
        for changes in ({"left_by":["k"]},{"right_by":["k"]},{"expected_by":["k"]},
                        {"left_value":"float"},{"left_value":"boolean"},{"left_by":["float"]},
                        {"left_value":"missing"},{"left_by":[]},{"right_by":["key","index"]},
                        {"expected_by":["key","index"]},{"name":"missing"}):
            with self.subTest(changes=changes),self.assertRaises((TypeError,ValueError)):
                self.compare(studio,**changes)
        failed = Collection.grid(2,values=F.i%param("absent"))
        studio = self.studio(left=failed,right=base,domain=base)
        with self.assertRaisesRegex(ValueError,"unavailable"):
            self.compare(studio)

    def test_empty_domain_and_incidence_inputs_have_explicit_meaning(self):
        empty = Collection.literal([])
        studio = self.studio(left=empty,right=empty,domain=empty)
        report = self.compare(studio)
        self.assertTrue(report["passed"])
        self.assertTrue(report["empty"])
        self.assertEqual(report["rows"],[])
        studio.workspace.set("left",Collection.literal([0]))
        report = self.compare(studio)
        self.assertFalse(report["passed"])
        self.assertEqual(report["summary"]["outside_left"],"1")
        studio.workspace.set("left",Collection.literal([0]).where(F.value==0))
        with self.assertRaisesRegex(ValueError,"select an incidence"):
            self.compare(studio)

    def test_query_preserves_pending_preview_and_rejects_stale_revision(self):
        root = Collection.literal([0,1])
        studio = self.studio(left=root,right=root,domain=root)
        preview = studio.preview(dict(action="integers",name="extra",args={"values":["2"]}),studio.revision)
        pending = studio.pending
        saved = studio.workspace.to_json()
        with patch("kaleion.evaluate.Evaluator.get",side_effect=AssertionError("execution")):
            self.assertTrue(self.compare(studio)["passed"])
        self.assertIs(studio.pending,pending)
        self.assertEqual(studio.workspace.to_json(),saved)
        revision = studio.revision
        studio.commit(preview["token"],revision)
        with self.assertRaisesRegex(ValueError,"out of date"):
            studio.compare("left",["key"],"value","right",["key"],"value","domain",["key"],revision)


if __name__ == "__main__":
    unittest.main()
