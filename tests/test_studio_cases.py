"""Explicit case requests, exact capture isolation, and failure visibility."""

import unittest
from unittest.mock import patch

from examples.studio.adapter import Studio, expression


def n(value):
    return {"integer": str(value)}


def op(symbol, left, right):
    return {"op": symbol, "args": [left, right]}


class StudioCaseTests(unittest.TestCase):
    def setUp(self):
        self.studio = Studio()

    def apply(self, action, name, **args):
        preview = self.studio.preview(dict(action=action, name=name, args=args), self.studio.revision)
        return self.studio.commit(preview["token"], self.studio.revision)

    def case(self, **parameters):
        preview = self.studio.preview_case(parameters, self.studio.revision)
        return self.studio.commit(preview["token"], self.studio.revision)

    def test_lattice_growth_retains_zero_groups_and_does_not_rebind_local_cases(self):
        self.case(n="2")
        p = {"parameter":"n"}
        self.apply("grid", "square", shape=[op("+", p, n(1))]*2, axes=["i","j"], value=n(1))
        self.apply("lens", "triangle", source="square", rule=op("<",op("+",{"field":"i"},{"field":"j"}),p))
        self.apply("measure", "rows", source="triangle", by=["i"], reducer="count")
        self.apply("measure", "total", source="triangle", by=[], reducer="count")
        frozen = self.studio.workspace.state.roots["rows"].with_params(n=2)
        self.studio.workspace.set("local", frozen)
        for size in (4, 0, 3):
            with self.subTest(n=size):
                self.case(n=str(size))
                results = self.studio.workspace.state.results
                self.assertEqual(results["rows"].values.tolist(), list(range(size,-1,-1)))
                self.assertEqual(results["total"].values.tolist(), [size*(size+1)//2])
                self.assertEqual(results["local"].values.tolist(), [2,1,0])
                zero = results["rows"]
                receipt = self.studio.contributors([zero.node,zero.ids[-1]],self.studio.revision)["measurement"]
                self.assertEqual(receipt["contributor_count"], "0")
        # New ordinary constructions use the applied parameter environment too.
        self.apply("field", "offset", source="rows", field="offset", value=p)
        self.assertEqual(self.studio.workspace.state.results["offset"].fields["offset"].tolist(), [3]*4)

    def test_failed_case_keeps_dependencies_failed_and_independent_roots_inspectable(self):
        self.case(n="3")
        self.apply("integers", "independent", values=["9"])
        self.apply("field", "residue", source="independent", field="r", value=op("%",{"field":"value"},{"parameter":"n"}))
        self.apply("measure", "sum", source="residue", by=[], reducer="sum", weight={"field":"r"})
        before = self.studio.workspace.state
        preview = self.studio.preview_case({"n":"0"}, self.studio.revision, "residue")
        self.assertIs(self.studio.workspace.state, before)
        self.assertEqual(set(preview["errors"]), {"residue","sum"})
        self.assertNotIn("rows", next(obj for obj in preview["objects"] if obj["name"]=="sum"))
        result = self.studio.commit(preview["token"], self.studio.revision)
        self.assertEqual(result["motion"], [])
        self.assertEqual(set(self.studio.workspace.state.results), {"independent"})
        self.studio.history("undo", self.studio.revision, "sum")
        self.assertIs(self.studio.workspace.state, before)
        self.assertEqual(self.studio.workspace.state.results["sum"].values.tolist(), [0])

    def test_parameter_transport_is_exact_and_saved_history_needs_no_execution(self):
        huge = 2**100+123
        self.case(offset=str(huge))
        self.apply("grid", "items", shape=["2"], axes=["i"], value=op("+",{"parameter":"offset"},{"field":"i"}))
        before = self.studio.workspace.state
        self.case(offset=str(huge+1))
        self.assertEqual(self.studio.state()["parameters"]["offset"],str(huge+1))
        saved = self.studio.workspace.to_json()
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
            self.studio.reopen(saved, self.studio.revision)
            self.studio.history("undo", self.studio.revision, "items")
            self.assertEqual(self.studio.workspace.state.results["items"].values.tolist(), [huge,huge+1])
            self.assertEqual(self.studio.workspace.state.results["items"].node,before.results["items"].node)
            self.studio.history("redo", self.studio.revision, "items")
            self.assertEqual(self.studio.workspace.to_json(), saved)

    def test_invalid_case_replaces_preview_but_never_changes_applied_state(self):
        self.case(n="2")
        saved = self.studio.workspace.to_json()
        for invalid in ({"n":3}, {"n":"1.5"}, {"n":"01"}, {"n":"9"*1236}, {"n":True},
                        {"a-b":"1"}, {"":"1"}, {"1n":"1"}, {"x"*33:"1"}, {"n":"2"},
                        {f"n{i}":"0" for i in range(17)}):
            with self.subTest(invalid=str(invalid)[:60]):
                preview = self.studio.preview_case({"n":"3"}, self.studio.revision)
                with self.assertRaises(ValueError):
                    self.studio.preview_case(invalid, self.studio.revision)
                with self.assertRaises(ValueError):
                    self.studio.commit(preview["token"], self.studio.revision)
                self.assertEqual(self.studio.workspace.to_json(), saved)
        with self.assertRaises(ValueError):
            expression({"parameter":"not a name"},{})
        with self.assertRaises(ValueError):
            self.apply("grid", "undeclared", shape=[{"parameter":"missing"}], axes=["i"], value=n(1))
        with self.assertRaises(ValueError):
            self.studio.preview_case({"n":"3"}, self.studio.revision-1)

    def test_case_and_construction_tokens_supersede_each_other_and_commit_once(self):
        self.case(n="2")
        old = self.studio.preview_case({"n":"3"}, self.studio.revision)
        ordinary = self.studio.preview(dict(action="integers", name="items", args={"values":["1"]}), self.studio.revision)
        with self.assertRaises(ValueError):
            self.studio.commit(old["token"],self.studio.revision)
        case = self.studio.preview_case({"n":"4"}, self.studio.revision)
        with self.assertRaises(ValueError):
            self.studio.commit(ordinary["token"],self.studio.revision)
        capture = self.studio.pending.state
        with patch("kaleion.evaluate.Evaluator.get",side_effect=AssertionError("execution")):
            result = self.studio.commit(case["token"], self.studio.revision)
        self.assertEqual(result["parameters"], {"n":"4"})
        self.assertEqual(result["objects"], [])
        self.assertIs(self.studio.workspace.state,capture)
        with self.assertRaises(ValueError):
            self.studio.commit(case["token"],self.studio.revision)


if __name__ == "__main__":
    unittest.main()
