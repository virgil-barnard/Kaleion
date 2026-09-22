"""Semantic authoring commands against independent finite constructions.

This experimental adapter is not part of the installed core API. No HTTP server
or browser is needed for these contracts; browser gestures have a separate gate.
"""

from collections import Counter
from itertools import product
import json
import unittest
from unittest.mock import patch
import numpy as np

from examples.studio.adapter import Studio, expression


def n(value):
    return {"integer": str(value)}


def f(name):
    return {"field": name}


def op(symbol, left, right):
    return {"op": symbol, "args": [left, right]}


def read(source, on, key="key", value="value"):
    return {"read": {"object": source, "on": f(on), "key": f(key), "value": f(value)}}


class StudioTests(unittest.TestCase):
    def setUp(self):
        self.studio = Studio()

    def apply(self, action, name, **args):
        studio = self.studio
        preview = studio.preview(dict(action=action, name=name, args=args), studio.revision)
        return studio.commit(preview["token"], studio.revision)

    def values(self, name):
        return self.studio.workspace.state.results[name].values.tolist()

    def grid(self, name, shape, axes, value=None):
        return self.apply("grid", name, shape=list(map(str, shape)), axes=axes, value=n(1) if value is None else value)

    def measure(self, name, source, by, reducer="count", **args):
        return self.apply("measure", name, source=source, by=by, reducer=reducer, **args)

    def test_quotient_counts_drive_independent_placement_and_explain_zero(self):
        self.grid("region", [7, 11], ["i", "j"], op("+", op("*", n(11), f("i")), op("*", n(7), f("j"))))
        self.apply("lens", "incidence", source="region", rule=op("≥", f("value"), n(77)))
        self.measure("counts", "incidence", ["i"])
        expected = [sum(11*i + 7*j >= 77 for j in range(11)) for i in range(7)]
        self.assertEqual(self.values("counts"), expected)
        self.grid("probes", [7, 1], ["i", "j"])
        self.apply("place", "probes", source="probes", coordinates=[f("i"), n(0)])
        next_state = self.apply("place", "probes", source="probes", coordinates=[f("i"), read("counts", "i", "i")])
        self.assertEqual([p[1] for p in self.studio.workspace.state.results["probes"].positions], expected)
        probe = next(o for o in next_state["objects"] if o["name"] == "probes")["rows"][0]
        receipt = self.studio.inspect("probes", probe["ref"], self.studio.revision)
        driver = receipt["bindings"][0]["driver"]
        count = self.studio.inspect_ref(driver, self.studio.revision)["measurement"]
        self.assertEqual(count["contributor_count"], "0")
        self.assertEqual(count["contributors"], [])

    def test_modular_lines_use_same_relation_and_group_controls(self):
        # Each point in F_3^2 lies on one line of every finite slope.
        self.grid("triples", [3, 3, 3], ["u", "v", "m"])
        self.apply("field", "with_intercept", source="triples", field="t",
                   value=op("%", op("-", f("v"), op("*", f("m"), f("u"))), n(3)))
        self.apply("lens", "through_origin", source="with_intercept", rule=op("=", f("t"), n(0)))
        self.measure("line_counts", "through_origin", ["m"])
        self.assertEqual(self.values("line_counts"), [3, 3, 3])
        self.measure("point_counts", "through_origin", ["u", "v"])
        expected = [sum((v-m*u) % 3 == 0 for m in range(3)) for u,v in product(range(3), repeat=2)]
        self.assertEqual(self.values("point_counts"), expected)
        self.assertIn(0, expected)

    def test_products_ranks_and_weights_are_composable_without_lesson_actions(self):
        a,b=[0,1,3],[0,2]
        self.apply("integers", "A", values=list(map(str,a)))
        self.apply("integers", "B", values=list(map(str,b)))
        self.apply("product", "pairs", factors={"left":{"source":"A","fields":["value"]},"right":{"source":"B","fields":["value"]}})
        self.apply("field", "sums", source="pairs", field="s", value=op("+",f("left_value"),f("right_value")))
        self.measure("counts", "sums", ["s"])
        expected=Counter(x+y for x,y in product(a,b))
        snap=self.studio.workspace.state.results["counts"]
        self.assertEqual(dict(zip(snap.fields["s"],snap.values)),expected)
        self.measure("ranks", "sums", ["s"], "rank", order=["index"], key="key")
        self.apply("place", "sums", source="sums", coordinates=[f("s"),read("ranks","key")])
        positions=self.studio.workspace.state.results["sums"].positions
        self.assertEqual(len({tuple(p) for p in positions}),len(a)*len(b))
        self.measure("energy", "counts", [], "sum", weight=op("*",f("value"),f("value")))
        self.assertEqual(self.values("energy"),[sum(c*c for c in expected.values())])

    def test_empty_product_keeps_declared_zero_groups_but_selection_does_not(self):
        self.apply("integers","empty",values=[])
        self.apply("integers","bins",values=["0","1","2"])
        self.apply("product","pairs",factors={"item":{"source":"empty","fields":["value"]},"bin":{"source":"bins","fields":["value"]}})
        self.apply("lens","hits",source="pairs",rule=op("=",f("item_value"),f("bin_value")))
        self.measure("counts","hits",["bin"])
        self.assertEqual(self.values("counts"),[0,0,0])
        self.apply("select","selected",source="hits")
        self.measure("selected_counts","selected",["bin"])
        self.assertEqual(self.values("selected_counts"),[])

    def test_exact_transport_and_signed_sum_contributors(self):
        huge=2**90+3
        self.apply("integers","weights",values=[str(huge),str(-huge),"0"])
        self.measure("sum","weights",[],"sum",weight=f("value"))
        self.assertEqual(self.values("sum"),[0])
        objects=json.loads(json.dumps(self.studio.state()))["objects"]
        self.assertEqual(objects[0]["rows"][0]["fields"]["value"],str(huge))
        ref=objects[-1]["rows"][0]["ref"]
        receipt=self.studio.inspect("sum",ref,self.studio.revision)["measurement"]
        self.assertEqual(receipt["contributor_count"],"3")
        self.assertEqual([c["weight"] for c in receipt["contributors"]],[str(huge),str(-huge),"0"])

    def test_preview_is_exact_capture_committed_once_and_stale_tokens_fail(self):
        command=dict(action="integers",name="A",args={"values":["2"]})
        p=self.studio.preview(command,0)
        ids=self.studio.pending.state.results["A"].ids
        self.assertFalse(self.studio.workspace.can_undo)
        with patch("kaleion.evaluate.Evaluator.get",side_effect=AssertionError("reevaluation")):
            self.studio.commit(p["token"],0)
        self.assertEqual(self.studio.workspace.state.results["A"].ids,ids)
        with self.assertRaises(ValueError):self.studio.commit(p["token"],0)
        with self.assertRaises(ValueError):self.studio.preview(command,0)

    def test_failures_invalidate_preview_without_poisoning_ready_objects(self):
        self.apply("integers","A",values=["1","2"])
        good=dict(action="field",name="ok",args={"source":"A","field":"v","value":n(5)})
        p=self.studio.preview(good,self.studio.revision)
        before=self.studio.workspace.state
        with self.assertRaises(ValueError):
            self.studio.preview(dict(action="field",name="bad",args={"source":"A","field":"v","value":op("//",f("value"),n(0))}),self.studio.revision)
        self.assertIs(self.studio.workspace.state,before)
        self.assertEqual(self.values("A"),[1,2])
        with self.assertRaises(ValueError):self.studio.commit(p["token"],self.studio.revision)
        self.apply("integers","duplicate_keys",values=["1","1"])
        with self.assertRaises(ValueError):
            self.studio.preview(dict(action="place",name="A",args={"source":"A","coordinates":[f("value"),read("duplicate_keys","value","value")]}),self.studio.revision)

    def test_saved_undo_redo_and_receipts_do_not_execute_graph(self):
        self.grid("A",[2,2],["i","j"])
        self.measure("counts","A",["i"])
        self.apply("place","A",source="A",coordinates=[f("i"),f("j")])
        moved=self.apply("place","A",source="A",coordinates=[f("i"),op("+",f("j"),read("counts","i","i"))])
        backward=self.studio.history("undo",self.studio.revision,"A")
        # Complementary float sample times differ by a few ULPs; endpoints and
        # identities are exact, while path coordinates are float64 presentation.
        np.testing.assert_allclose([f["positions"] for f in backward["motion"]],
                                   list(reversed([f["positions"] for f in moved["motion"]])),
                                   rtol=0, atol=1e-12)
        saved=self.studio.workspace.to_json()
        with patch("kaleion.evaluate.Evaluator.get",side_effect=AssertionError("execution")):
            self.studio.reopen(saved,self.studio.revision)
            redone=self.studio.history("redo",self.studio.revision,"A")
            self.assertEqual(redone["motion"],moved["motion"])
            row=next(o for o in redone["objects"] if o["name"]=="A")["rows"][0]
            self.assertEqual(self.studio.inspect("A",row["ref"],self.studio.revision)["bindings"][0]["value"],"2")

    def test_invalid_language_and_budget_are_explicit(self):
        for value in [{"integer":9007199254740993},{"integer":"1.5"},{"integer":"01"},{"python":"__import__('os')"},{"op":"call","args":[]}]:
            with self.subTest(value=value),self.assertRaises(ValueError):expression(value,{})
        with self.assertRaises(ValueError):
            self.grid("too_large",[50,50],["i","j"])
        self.assertEqual(self.studio.state()["objects"],[])
        with self.assertRaises(ValueError):self.apply("integers","huge",values=[str(2**4096)])
        with self.assertRaises(ValueError):self.apply("integers","wrong_shape",values="123")
        with self.assertRaises(ValueError):self.apply("integers","unknown",values=["1"],ignored_choice=True)


if __name__ == "__main__":
    unittest.main()
