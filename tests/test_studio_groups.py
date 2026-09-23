"""Captured groups are selections; measurements/lenses are explicit constructions."""

from itertools import product
import unittest
from unittest.mock import patch

from kaleion import Collection, F, Workspace, param
from examples.studio.adapter import Studio


class CapturedGroupTests(unittest.TestCase):
    def studio(self, **roots):
        session = Studio()
        session.workspace = Workspace(roots, max_items=2000, max_history=40)
        return session

    def lens(self, studio, source, by, group, name="lens", capture=None):
        report = studio.groups(source, by, studio.revision)
        command = dict(action="group_lens", name=name, args=dict(
            source=source, by=by, group=group, capture=capture or report["capture"]))
        preview = studio.preview(command, studio.revision)
        return studio.commit(preview["token"], studio.revision)

    def test_sum_fibers_and_modular_lines_share_captured_group_query(self):
        sums = Collection.grid(3, 3, values=F.i + F.j)
        triples = Collection.grid(3, 3, 3)
        lines = triples.where((F.j - F.i - F.k) % 3 == 0)
        studio = self.studio(sums=sums, lines=lines)
        before = studio.workspace.to_json()
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
            additive = studio.groups("sums", ["value"], 0)
            modular = studio.groups("lines", ["k"], 0)
        self.assertEqual(studio.workspace.to_json(), before)
        self.assertEqual([g["count"] for g in additive["groups"]], ["1", "2", "3", "2", "1"])
        self.assertEqual(additive["domain"], "observed keys")
        self.assertEqual(modular["domain"], "declared axes")
        self.assertEqual([g["count"] for g in modular["groups"]], ["3"] * 3)
        snapshot = studio.workspace.state.results["lines"].source
        for k, group in enumerate(modular["groups"]):
            expected = {snapshot.ids[index] for index,(i,j,slope) in enumerate(product(range(3), repeat=3))
                        if slope == k and (j-i-k) % 3 == 0}
            self.assertEqual({ref[1] for ref in group["matches"]}, expected)
            self.assertEqual(group["population"], "9")

    def test_empty_axis_total_and_observed_domains_are_distinct(self):
        empty = Collection.grid(4, 0).annotate(copy=F.i)
        studio = self.studio(empty=empty)
        retained = studio.groups("empty", ["i"], 0)
        self.assertEqual([g["key"] for g in retained["groups"]], [["0"], ["1"], ["2"], ["3"]])
        self.assertTrue(all(g["members"] == g["matches"] == [] for g in retained["groups"]))
        self.assertEqual(studio.groups("empty", ["copy"], 0)["groups"], [])
        total = studio.groups("empty", [], 0)
        self.assertEqual(total["groups"][0]["count"], "0")
        self.assertEqual(total["groups"][0]["key"], [])
        self.lens(studio, "empty", ["i"], 2)
        self.assertEqual(studio.workspace.state.roots["lens"].count(by=F.i).evaluate().values.tolist(), [0]*4)

    def test_zero_incidence_fiber_keeps_universe_and_changes_history_only_on_apply(self):
        cells = Collection.grid(3, 4)
        incidence = cells.where((F.i > 0) & (F.j < F.i))
        studio = self.studio(hits=incidence)
        report = studio.groups("hits", ["i"], 0)
        self.assertEqual([g["count"] for g in report["groups"]], ["0", "1", "2"])
        self.assertEqual([g["population"] for g in report["groups"]], ["4"]*3)
        command=dict(action="group_lens",name="empty_row",args=dict(source="hits",capture=report["capture"],by=["i"],group=0))
        preview=studio.preview(command,0)
        self.assertFalse(studio.workspace.can_undo)
        studio.commit(preview["token"],0)
        result=studio.workspace.state.results["empty_row"]
        self.assertEqual(result.source.ids,studio.workspace.state.results["hits"].source.ids)
        self.assertFalse(result.mask.any())
        self.assertEqual(studio.groups("empty_row",["i"],1)["groups"][0]["population"],"4")
        self.assertTrue(studio.workspace.can_undo)

    def test_field_inspection_preserves_a_ready_measurement_preview(self):
        cells = Collection.grid(6, 6)
        studio = self.studio(hits=cells.where((F.j - 2*F.i - 1) % 6 == 0))
        command = dict(action="measure", name="counts", args=dict(
            source="hits", by=["j"], reducer="count"))
        preview = studio.preview(command, 0)
        saved = studio.workspace.to_json()
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
            report = studio.groups("hits", ["j"], 0)
        self.assertEqual([g["population"] for g in report["groups"]], ["6"]*6)
        self.assertEqual([g["count"] for g in report["groups"]], ["0", "2"]*3)
        self.assertEqual(studio.workspace.to_json(), saved)
        studio.commit(preview["token"], 0)
        self.assertEqual(studio.workspace.state.results["counts"].values.tolist(), [0, 2]*3)

    def test_group_lens_intersects_original_mask_and_scoped_parameters(self):
        cells = Collection.grid(3, 4)
        incidence = cells.where(F.j < param("n")).with_params(n=2)
        studio = self.studio(hits=incidence)
        self.lens(studio,"hits",["i"],1)
        result=studio.workspace.state.results["lens"]
        self.assertEqual(result.mask.tolist(),[i==1 and j<2 for i,j in product(range(3),range(4))])
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
            before=studio.groups("lens",["i"],studio.revision)
            saved=studio.workspace.to_json()
            studio.history("undo",studio.revision,"lens")
            studio.history("redo",studio.revision,"lens")
            studio.reopen(saved,studio.revision)
            after=studio.groups("lens",["i"],studio.revision)
        self.assertEqual(before["groups"],after["groups"])

    def test_composite_keys_and_repeated_values_do_not_imply_member_order(self):
        source=Collection.literal([7,7,9,7],fields={"a":[2,1,2,1],"b":[0,0,1,0]})
        studio=self.studio(points=source)
        report=studio.groups("points",["a","b"],0)
        self.assertEqual([g["key"] for g in report["groups"]],[["2","0"],["1","0"],["2","1"]])
        self.assertEqual([g["count"] for g in report["groups"]],["1","2","1"])
        tied=dict(action="measure",name="ranks",args=dict(source="points",by=["a","b"],reducer="rank",order=["value"],key="key"))
        with self.assertRaisesRegex(ValueError,"ties"):
            studio.preview(tied,0)
        self.assertFalse(studio.workspace.can_undo)
        tied["args"]["order"]=["value","key"]
        p=studio.preview(tied,0);studio.commit(p["token"],0)
        self.assertEqual(studio.workspace.state.results["ranks"].values.tolist(),[0,0,0,1])

    def test_group_keys_keep_exact_types_and_no_zero_is_invented_for_absence(self):
        huge=2**90+1
        source=Collection.literal([huge,huge+1,huge],keys=[1,"1",1])
        studio=self.studio(points=source)
        report=studio.groups("points",["value"],0)
        self.assertEqual([g["key"] for g in report["groups"]],[[str(huge)],[str(huge+1)]])
        mixed=studio.groups("points",["key"],0)
        self.assertEqual([g["key_types"] for g in mixed["groups"]],[["integer"],["text"]])
        self.lens(studio,"points",["key"],1)
        self.assertEqual(studio.workspace.state.results["lens"].mask.tolist(),[False,True,False])
        selected=source.where(F.value==huge).select()
        studio=self.studio(filtered=selected)
        self.assertEqual(len(studio.groups("filtered",["value"],0)["groups"]),1)

    def test_bad_stale_and_oversized_queries_leave_ready_captures_available(self):
        studio=self.studio(good=Collection.grid(2,2),bad=Collection.sequence(param("missing")),
                           empty=Collection.grid(0,50,50))
        before=studio.workspace.state
        for by in (["missing"],["i","i"],"i"):
            with self.subTest(by=by),self.assertRaises((ValueError,KeyError)):
                studio.groups("good",by,0)
        with self.assertRaises(KeyError):studio.groups("bad",["key"],0)
        with self.assertRaisesRegex(ValueError,"budget"):studio.groups("empty",["j","k"],0)
        with self.assertRaises(ValueError):studio.groups("good",["i"],1)
        for group in (-1,2,True):
            with self.assertRaises(ValueError):self.lens(studio,"good",["i"],group)
        with self.assertRaisesRegex(ValueError,"earlier capture"):
            self.lens(studio,"good",["i"],0,capture="outdated")
        self.assertIs(studio.workspace.state,before)
        self.assertEqual([g["count"] for g in studio.groups("good",["i"],0)["groups"]],["2","2"])


if __name__ == "__main__":
    unittest.main()
