"""Definition inspection preserves scope, exact syntax and captured history."""

import json
from pathlib import Path
import unittest
from unittest.mock import patch

from kaleion import Collection, F, Product, Workspace, param, vector
from kaleion.api import wrap
from kaleion.history import State
from kaleion.ir import Expr, Node
from examples.studio.adapter import Studio


CANVASES = Path(__file__).resolve().parents[1] / "examples" / "canvases"


class ConstructionInspectionTests(unittest.TestCase):
    def studio(self, parameters=None, **roots):
        studio = Studio()
        studio.workspace = Workspace(roots, parameters, max_items=2000, max_history=40)
        return studio

    def read(self, studio, name, path=()):
        return studio.construction(name, list(path), studio.revision)

    def follow(self, studio, entry):
        return self.read(studio, entry["target"]["root"], entry["target"]["path"])

    def test_saved_canvases_expand_actual_definitions_without_execution_or_history_edits(self):
        for path in sorted(CANVASES.glob("*.json")):
            with self.subTest(canvas=path.stem):
                studio = Studio()
                with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
                    studio.reopen(path.read_text(), studio.revision)
                    before = studio.workspace.to_json()
                    pending = [obj["construction"] for obj in studio.state()["objects"]]
                    seen = set()
                    while pending:
                        data = pending.pop()
                        marker = (data["definition"], data["local_depth"], json.dumps(data["parameters"], sort_keys=True))
                        if marker in seen:
                            continue
                        seen.add(marker)
                        self.assertEqual(json.loads(data["canonical"])["op"], data["operation"])
                        self.assertTrue(data["capture"])
                        for entry in data["inputs"]:
                            child = self.follow(studio, entry)
                            self.assertEqual(child["definition"], entry["definition"])
                            pending.append(child)
                    self.assertEqual(studio.workspace.to_json(), before)

    def test_placement_reveals_keyed_read_and_preserves_an_earlier_driver_after_reopen(self):
        driver = Collection.literal([9, 4], keys=[1, 0], name="Heights")
        points = Collection.literal([0, 1]).arrange(F.value, driver.bind(on=F.value))
        studio = self.studio(Heights=driver, Points=points)
        old_capture = studio.workspace.state.results["Heights"].node
        studio.workspace.set("Heights", driver.arrange(F.key, 99))
        saved = studio.workspace.to_json()
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
            studio.reopen(saved, studio.revision)
            data = self.read(studio, "Points")
            self.assertEqual(data["arguments"][1]["label"], "y coordinate")
            read = data["reads"][0]
            self.assertEqual((read["on"], read["key"], read["value"]), ("value", "key", "value"))
            source = self.follow(studio, read)
            self.assertEqual(source["capture"], old_capture)
            self.assertEqual(source["names"], [])
            self.assertEqual(source["context"], "Earlier or unnamed input")
            self.assertEqual([r["fields"]["value"] for r in studio.capture(source["capture"], studio.revision)["rows"]], ["9", "4"])
            self.assertEqual(self.read(studio, "Heights")["operation"], "place")
            self.assertEqual(studio.workspace.to_json(), saved)

    def test_local_input_never_substitutes_global_namesake_including_equal_cases(self):
        base = Collection.sequence(param("n"), start=0)
        nested = base.with_params(n=param("n") + 1).with_params(n=2)
        studio = self.studio({"n": 6}, Global=base, Nested=nested, Same=base.with_params(n=6))
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
            first = self.follow(studio, self.read(studio, "Nested")["inputs"][0])
            second = self.follow(studio, first["inputs"][0])
            self.assertEqual(first["parameters"], {"n": "2"})
            self.assertEqual(second["parameters"], {"n": "3"})
            self.assertEqual(second["extent"], 3)
            self.assertEqual(second["local_depth"], 2)
            self.assertEqual(second["names"], [])
            self.assertNotEqual(second["capture"], self.read(studio, "Global")["capture"])
            same = self.follow(studio, self.read(studio, "Same")["inputs"][0])
            self.assertEqual(same["names"], [])
            self.assertEqual(same["context"], "Local case input")

    def test_case_binding_reads_use_outer_scope_and_uncaptured_failed_local_inputs_stay_unavailable(self):
        size = Collection.literal([4])
        base = Collection.sequence(param("n") - 3)
        studio = self.studio({"n": 5}, Size=size, Global=base,
                             Bound=base.with_params(n=size.scalar()), Bad=base.with_params(n=2))
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
            bound = self.read(studio, "Bound")
            scalar = self.follow(studio, bound["reads"][0])
            self.assertEqual(scalar["names"], ["Size"])
            self.assertEqual(scalar["parameters"], {"n": "5"})
            inside = self.follow(studio, bound["inputs"][0])
            self.assertEqual(inside["parameters"], {"n": "4"})
            bad = self.read(studio, "Bad")
            self.assertEqual(bad["status"], "failed")
            self.assertTrue(bad["error"])
            failed_input = self.follow(studio, bad["inputs"][0])
            self.assertEqual(failed_input["status"], "unavailable")
            self.assertIsNone(failed_input["capture"])
            self.assertIsNone(failed_input["parameters"])
            self.assertEqual(failed_input["names"], [])
            self.assertEqual(failed_input["arguments"][0]["text"], "($n − 3)")

    def test_order_weight_and_tuple_read_remain_distinct_from_occurrence_values(self):
        cells = Collection.literal([8, 8, 8], fields={"g": [0, 0, 0], "w": [0, -7, 7]})
        prefix = cells.group_by(F.g).order_by(F.index).prefix_sums(key=F.key, value=F.w)
        target = cells.arrange(F.index, prefix.bind(on=vector(F.g, F.key), key=vector(F.g, F.key)))
        studio = self.studio(Cells=cells, Prefix=prefix, Target=target)
        data = self.read(studio, "Prefix")
        args = {a["label"]: a["text"] for a in data["arguments"]}
        self.assertEqual(args["Contribution weight"], "w")
        self.assertEqual(args["Group keys (in order)"], 'g ← g')
        self.assertEqual(args["Strict member order"], '[index]')
        self.assertEqual(args["Unique item keys"], 'key ← key')
        self.assertIn("current item is excluded", data["notes"][0])
        read = self.read(studio, "Target")["reads"][0]
        self.assertEqual((read["on"], read["key"]), ("(g, key)", "(g, key)"))

    def test_product_expansion_and_aliases_do_not_invent_a_new_constructor(self):
        left, right = Collection.literal([7, 7]), Collection.literal([2])
        product = Product(left=left, right=right)
        studio = self.studio(Left=left, Alias=left, Right=right, Pairs=product.domain)
        data = self.read(studio, "Pairs")
        self.assertEqual(data["operation"], "grid")
        self.assertEqual(data["arguments"][1]["text"], '["left", "right"]')
        self.assertEqual(len(data["reads"]), 2)
        count = self.follow(studio, data["reads"][0])
        incidence = self.follow(studio, count["inputs"][0])
        source = self.follow(studio, incidence["inputs"][0])
        self.assertEqual(source["names"], ["Left", "Alias"])
        self.assertEqual(source["extent"], 2)

    def test_unfamiliar_or_failed_constructor_keeps_exact_definition_and_independent_roots(self):
        huge = 2**100 + 1
        source = Collection.literal([huge, huge], name="Exact")
        unknown = wrap(Node("future_recipe", "collection", (source.node,),
                            {"rule": Expr("future_rule", (F.value, huge))}))
        studio = self.studio(Exact=source, Unfamiliar=unknown)
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
            data = self.read(studio, "Unfamiliar")
            self.assertEqual(data["status"], "failed")
            self.assertIn(str(huge), data["arguments"][0]["text"])
            self.assertEqual(json.loads(data["canonical"])["op"], "future_recipe")
            literal = self.follow(studio, data["inputs"][0])
            self.assertIn(str(huge), literal["arguments"][0]["text"])
            self.assertEqual(literal["names"], ["Exact"])
            self.assertEqual(literal["status"], "ready")

    def test_missing_capture_and_invalid_navigation_cannot_trigger_evaluation(self):
        source = Collection.sequence(3)
        studio = self.studio(Result=source.arrange(F.value, 0))
        state = studio.workspace.state
        studio.workspace.state = State(state.roots, state.parameters, state.results,
                                       state.errors, {}, state.provenance)
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
            child = self.follow(studio, self.read(studio, "Result")["inputs"][0])
            self.assertIsNone(child["capture"])
            self.assertEqual(child["status"], "ready")
            self.assertIn("unavailable", child["notes"][0])
            for path in (["input:9"], ["read:-1"], [0], ["input:0"] * 101):
                with self.assertRaises(ValueError):
                    self.read(studio, "Result", path)
            with self.assertRaises(ValueError):
                studio.construction("Result", [], studio.revision + 1)
            with self.assertRaises(ValueError):
                self.read(studio, "absent")


if __name__ == "__main__":
    unittest.main()
