"""Captured explanations checked independently of graph execution and plotting."""

from dataclasses import replace
import json
import unittest
from unittest.mock import patch

from kaleion import Collection, F, Inspection, Motion, Ref, Workspace, param, vector


class InspectionTests(unittest.TestCase):
    def test_binding_reads_use_operation_inputs_and_explicit_keys(self):
        huge = 2**100 + 5
        table = Collection.literal([huge, -4], keys=[7, -3]).order_by(F.value)
        source = Collection.literal([-3, 7], keys=[11, 22])
        changed = source.with_values(2 * table.bind(on=F.value))
        state = Workspace({"changed": changed}).state
        inspect = Inspection(state)
        ref = inspect.find("changed", 22)
        reads = inspect.bindings(ref)
        self.assertEqual(len(reads), 1)
        self.assertEqual(reads[0].key, (7,))
        self.assertEqual(reads[0].value, huge)
        self.assertEqual(inspect.item(reads[0].target).value, 7)
        self.assertEqual(inspect.item(reads[0].driver).value, huge)
        self.assertEqual(inspect.item(ref).value, 2 * huge)
        self.assertNotEqual(reads[0].target.node, ref.node)
        self.assertEqual(reads[0].target.occurrence, ref.occurrence)

    def test_coordinate_and_multiple_reads_remain_distinct(self):
        table = Collection.literal([2, 5], keys=[4, 9]).arrange(F.key, F.value / 2)
        source = Collection.literal([4, 9]).arrange(F.value, 0)
        changed = source.move(vector(table.bind(on=F.x), table.bind(on=F.x, read=F.y)))
        inspect = Inspection(Workspace({"moved": changed}).state)
        ref = inspect.find("moved", 1)
        reads = inspect.bindings(ref)
        self.assertEqual([r.value for r in reads], [5, 2.5])
        self.assertEqual([r.key for r in reads], [(9.0,), (9.0,)])
        self.assertEqual(inspect.item(ref).position, (14.0, 2.5))
        self.assertEqual(inspect.item(reads[0].target).position, (9.0, 0.0))

    def test_signed_zero_weights_are_contributors_and_receipts_are_bounded(self):
        huge = 2**100 + 1
        source = Collection.literal([90, 80, 70], fields={"weight": [huge, -huge, 0]})
        measured = source.sum(value=F.weight)
        inspect = Inspection(Workspace({"total": measured}).state)
        ref = inspect.find("total", 0)
        receipt = inspect.measurement(ref)
        self.assertEqual(receipt.item.value, 0)
        self.assertEqual(receipt.contributor_count, 3)
        self.assertEqual([c.weight for c in receipt.contributors], [huge, -huge, 0])
        self.assertEqual([c.item.value for c in receipt.contributors], [90, 80, 70])
        self.assertEqual(receipt.key, ())
        short = inspect.measurement(ref, limit=1)
        self.assertTrue(short.truncated)
        self.assertEqual(short.contributor_count, 3)
        self.assertEqual(len(short.contributors), 1)
        self.assertEqual(inspect.measurement(ref, limit=0).contributors, ())
        decoded = json.loads(json.dumps(receipt.to_dict()))
        self.assertEqual(decoded["contributors"][0]["weight"], huge)
        with self.assertRaises(TypeError):
            receipt.item.fields["key"] = 99

    def test_zero_groups_and_empty_reduced_axis_have_receipts(self):
        source = Collection.grid(3, 0, values=1)
        measured = source.where(True).count(by=F.i).arrange(F.i, F.value)
        inspect = Inspection(Workspace({"counts": measured}).state)
        for key in range(3):
            receipt = inspect.measurement(inspect.find("counts", key))
            self.assertEqual((receipt.key, receipt.item.value, receipt.population), ((key,), 0, 0))
            self.assertEqual(receipt.contributors, ())
            self.assertFalse(receipt.truncated)

    def test_any_is_presence_not_a_cardinality(self):
        source = Collection.literal([5, 6, 7], fields={"group": [1, 1, 2]})
        measured = source.where(F.value < 7).any(by=F.group)
        inspect = Inspection(Workspace({"presence": measured}).state)
        nonempty = inspect.measurement(inspect.find("presence", 1))
        empty = inspect.measurement(inspect.find("presence", 2))
        self.assertEqual(nonempty.reducer, "any")
        self.assertEqual((nonempty.item.value, nonempty.contributor_count), (1, 2))
        self.assertEqual([c.item.value for c in nonempty.contributors], [5, 6])
        self.assertEqual((empty.item.value, empty.population, empty.contributor_count), (0, 1, 0))

    def test_rank_and_repeated_gather_follow_the_original_measurement(self):
        source = Collection.literal([30, 10, 20], keys=[3, 1, 2], fields={"group": [1, 1, 1]})
        ranked = source.group_by(F.group).order_by(F.value).ranks()
        copied = ranked.gather([0, 0, 1]).arrange(F.index, F.value)
        workspace = Workspace({"ranked": copied, "changed": copied.with_values(F.value + 1)})
        inspect = Inspection(workspace.state)
        with self.assertRaisesRegex(ValueError, "found 2"):
            inspect.find("ranked", 3)
        snapshot = workspace.state.results["ranked"]
        receipts = [inspect.measurement(Ref(snapshot.node, oid)) for oid in snapshot.ids]
        self.assertEqual([r.item.value for r in receipts], [2, 2, 0])
        self.assertEqual([c.item.value for c in receipts[0].contributors], [10, 20])
        self.assertEqual(receipts[0].origin, receipts[1].origin)
        changed = inspect.find("changed", 1)
        with self.assertRaisesRegex(ValueError, "no active measurement"):
            inspect.measurement(changed)
        parent = inspect.item(changed).parents[0]
        self.assertEqual(inspect.measurement(parent).item.value, 0)

    def test_nested_cases_and_same_occurrences_keep_their_scopes(self):
        n = param("n")
        source = Collection.sequence(3, start=0)
        table = source.with_values(F.value + n)
        changed = source.with_values(table.bind(on=F.key) * n)
        measured = source.sum(value=table.bind(on=F.key) * n)
        roots = {"a": changed.with_params(n=2),
                 "b": changed.with_params(n=param("outer")).with_params(outer=5),
                 "sum": measured.with_params(n=5)}
        inspect = Inspection(Workspace(roots, {"n": 100}).state)
        a = inspect.item(inspect.find("a", 1)).parents[0]
        b_case = inspect.item(inspect.find("b", 1)).parents[0]
        b = inspect.item(b_case).parents[0]
        self.assertEqual(a.occurrence, b.occurrence)
        self.assertNotEqual(a.node, b.node)
        self.assertEqual(inspect.bindings(a)[0].value, 3)
        self.assertEqual(inspect.bindings(b)[0].value, 6)
        receipt = inspect.measurement(inspect.find("sum", 0))
        self.assertEqual(receipt.item.value, 90)
        self.assertEqual([c.weight for c in receipt.contributors], [25, 30, 35])
        self.assertEqual([c.reads[0].value for c in receipt.contributors], [5, 6, 7])

    def test_reopened_motion_and_inspection_need_no_operation_execution(self):
        source = Collection.grid(3, 4, values=1)
        counts = source.where(F.j < F.i).count(by=F.i)
        target = Collection.sequence(3, start=0).arrange(F.value, 0)
        moved = target.move(vector(0, counts.bind(on=F.value, key=F.i)))
        workspace = Workspace({"target": target})
        transition = workspace.set("target", moved, motion=Motion.arc(height=1))
        workspace.capture("Measured motion")
        workspace.undo()
        payload = workspace.to_json()
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
            reopened = Workspace.from_json(payload)
            replay = reopened.redo()
            inspect = Inspection(reopened.state)
            read = inspect.bindings(inspect.find("target", 2))[0]
            receipt = inspect.measurement(read.driver)
            self.assertEqual([c.item.fields["j"] for c in receipt.contributors], [0, 1])
            self.assertEqual(receipt.item.value, 2)
            self.assertEqual(replay.frame("target", .25).positions.tolist(),
                             transition.frame("target", .25).positions.tolist())
        self.assertEqual(workspace.to_json(), payload)

    def test_missing_capture_failed_root_and_unsupported_reads_do_not_invent_evidence(self):
        source = Collection.sequence(2)
        bad = source.with_values(param("absent"))
        driver = source.count()
        target = source.with_values(driver.bind(on=0))
        state = Workspace({"ready": target, "failed": bad}).state
        inspect = Inspection(state)
        with self.assertRaisesRegex(KeyError, "No ready captured root"):
            inspect.find("failed", 0)
        ref = inspect.find("ready", 0)
        driver_ref = inspect.bindings(ref)[0].driver
        incomplete = replace(state, evaluated={k: v for k, v in state.evaluated.items()
                                               if k != driver_ref.node})
        with self.assertRaisesRegex(KeyError, "inspection cannot execute"):
            Inspection(incomplete).bindings(ref)
        with self.assertRaisesRegex(ValueError, "follow captured parents"):
            inspect.bindings(driver_ref)
        nested = source.with_values(source.bind(on=source.bind(on=F.key), key=F.value))
        nested_inspect = Inspection(Workspace({"nested": nested}).state)
        with self.assertRaisesRegex(ValueError, "Nested driver reads"):
            nested_inspect.bindings(nested_inspect.find("nested", 0))
        for construction, method in (
            (source.with_values(driver.scalar()), "bindings"),
            (source.lookup(source, address=F.index), "bindings"),
            (source.sum(value=driver.scalar()), "measurement"),
        ):
            query = Inspection(Workspace({"result": construction}).state)
            with self.assertRaisesRegex(ValueError, "driver reads are not yet inspectable"):
                getattr(query, method)(query.find("result", 0))
        self.assertEqual(inspect.measurement(driver_ref).item.value, 2)


if __name__ == "__main__":
    unittest.main()
