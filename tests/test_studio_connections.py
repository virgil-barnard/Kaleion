"""Named definition paths must not imply a live or cross-case correspondence."""

import unittest
from unittest.mock import patch

from kaleion import Collection, F, Workspace, param
from examples.studio.adapter import Studio
from examples.studio.connections import definition_connections


class StudioConnectionTests(unittest.TestCase):
    def test_nearest_named_inputs_and_keyed_reads_are_distinct(self):
        source = Collection.literal([2, 0, 3])
        relation = source.where(F.value > 0)
        counts = relation.group_by(F.key).count()
        probes = Collection.literal([0, 0, 0])
        placed = probes.arrange(F.key, counts.bind(on=F.key))
        roots = dict(source=source, relation=relation, counts=counts,
                     probes=probes, placed=placed)
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("No evaluation")):
            result = definition_connections(roots)
        edges = {(e["source"], e["target"], e["kind"]) for e in result["edges"]}
        self.assertEqual(edges, {("source", "relation", "input"),
                                 ("relation", "counts", "input"),
                                 ("probes", "placed", "input"),
                                 ("counts", "placed", "read")})

    def test_changed_root_is_not_mistaken_for_the_earlier_driver(self):
        driver = Collection.literal([0, 4])
        target = Collection.literal([0, 0]).arrange(F.key, driver.bind(on=F.key))
        report = definition_connections(dict(driver=driver.arrange(F.key, F.value), target=target))
        self.assertFalse(any(e["source"] == "driver" for e in report["edges"]))
        self.assertIn(dict(target="target", definition=driver.node.id,
                           reason="earlier or unnamed read"), report["boundaries"])

    def test_local_case_is_a_boundary_but_its_named_output_can_connect(self):
        source = Collection.grid(param("n"), axes=("i",))
        local = source.with_params(n=2)
        total = local.sum()
        report = definition_connections(dict(source=source, local=local, total=total))
        self.assertEqual(report["edges"], [dict(source="local", target="total", kind="input")])
        self.assertIn(dict(target="local", definition=local.node.id,
                           reason="local parameter case"), report["boundaries"])

    def test_aliases_are_explicit_and_equal_values_do_not_create_edges(self):
        a, b = Collection.literal([1, 1]), Collection.literal([1, 1])
        report = definition_connections(dict(a=a, alias=a, b=b, total=a.sum()))
        self.assertEqual({(e["source"], e["target"]) for e in report["edges"]},
                         {("a", "total"), ("alias", "total")})

    def test_failed_and_empty_roots_keep_definition_paths_after_save_and_undo(self):
        studio = Studio()
        source = Collection.literal([1])
        empty = Collection.literal([])
        broken = source.arrange(F.key, F.value // param("d"))
        studio.workspace = Workspace(dict(source=source, empty=empty, broken=broken), dict(d=0),
                                     max_items=2000, max_history=40)
        self.assertIn("broken", studio.workspace.state.errors)
        studio.workspace.set("zero", empty.sum())
        saved = studio.workspace.to_json()
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("No evaluation")):
            studio.reopen(saved, studio.revision)
            before = studio.state()["connections"]
            studio.history("undo", studio.revision, "source")
            studio.history("redo", studio.revision, "source")
            self.assertEqual(studio.state()["connections"], before)
        self.assertEqual({e["target"] for e in before["edges"]}, {"broken", "zero"})


if __name__ == "__main__":
    unittest.main()
