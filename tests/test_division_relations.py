"""Exact witnesses for the papers and the shared UI transformation contract."""
from math import gcd
import unittest
from unittest.mock import patch

import numpy as np

from kaleion import Collection, F, Workspace, Inspection
from kaleion.model import Ref
from examples.division_relations import division_motion, relation_matrices, euclidean_step, euclidean_next
from examples.studio.adapter import Studio


def formula(text):
    return {"formula": text}


def read(source, on="i", key="i"):
    return {"read": {"object": source, "on": {"field": on},
                     "key": {"field": key}, "value": {"field": "value"}}}


class DivisionConstructionTests(unittest.TestCase):
    def test_counted_quotients_reconstruct_multiples_even_without_coprimality(self):
        w = division_motion()
        for a, b in [(11, 7), (7, 11), (12, 8), (1, 7), (7, 1), (1, 1)]:
            with self.subTest(a=a, b=b):
                w.set_parameters(a=a, b=b)
                self.assertFalse(w.state.errors)
                s = w.state.results
                self.assertEqual(s["Quotients"].values.tolist(), [a*i//b for i in range(b)])
                self.assertEqual(s["Remainders"].values.tolist(), [a*i % b for i in range(b)])
                self.assertEqual(s["Reconstructed multiples"].values.tolist(), [a*i for i in range(b)])
                original, moved = s["Residue table"], s["Moving table"]
                self.assertEqual(moved.ids, original.ids)
                np.testing.assert_array_equal(moved.values, original.values)
                # Every coincidence is retained; only the coprime case is a bijection.
                self.assertEqual(len(set(map(tuple, moved.positions))), a*b//gcd(a,b))
                for value, (x,y) in zip(moved.values, moved.positions):
                    self.assertEqual(value, int(b*x+y))

    def test_shift_reads_actual_zero_measurement_and_captured_contributors(self):
        w = division_motion()
        w.undo()  # wrapped endpoint
        w.undo()  # translated endpoint; its move reads a quotient per row
        moved = w.state.results["Moving table"]
        inspection = Inspection(w.state)
        for index, expected in [(0, 0), (66, 9)]:
            reads = inspection.bindings(Ref(moved.node, moved.ids[index]))
            self.assertEqual(reads[0].value, expected)
            receipt = inspection.measurement(reads[0].driver)
            self.assertEqual(receipt.contributor_count, expected)
        # Remainders are arithmetic derivatives, not mislabeled count evidence.
        remainders = w.state.results["Remainders"]
        with self.assertRaises(ValueError):
            inspection.measurement(Ref(remainders.node, remainders.ids[0]))

    def test_relation_extraction_composition_and_nonunit_counterexample(self):
        w = relation_matrices()
        s = w.state.results
        self.assertEqual(s["Q extraction"].values.tolist(), [0,1,3,4,6,7,9])
        self.assertEqual(s["R extraction"].values.tolist(), [0,4,1,5,2,6,3])
        np.testing.assert_array_equal(s["Composed Q"].values, s["Direct Q"].values)
        cycled = s["Cycled table"]
        self.assertEqual(cycled.values.reshape(7,11)[:,0].tolist(), [0,4,1,5,2,6,3])
        self.assertEqual(sorted(cycled.values), list(range(77)))
        # A zero weighted sum still has the unique matched column as evidence.
        qr = s["Q extraction"]
        receipt = Inspection(w.state).measurement(Ref(qr.node, qr.ids[0]))
        self.assertEqual(receipt.contributor_count, 1)
        self.assertEqual(receipt.contributors[0].weight, 0)
        w.set_parameters(a=12, b=8)
        self.assertFalse(w.state.errors)
        s = w.state.results
        self.assertEqual(s["R column coverage"].values.tolist(), [4,0,0,0,4,0,0,0])
        self.assertEqual(sum(s["Composed Q"].values), 48)
        self.assertEqual(sum(s["Direct Q"].values), 12)
        self.assertEqual(sum(s["Composed Q"].values != s["Direct Q"].values), 36)

    def test_euclidean_reassembly_uses_exact_addresses_and_an_explicit_extension(self):
        for r,b,q in [(3,4,1),(4,7,1),(3,4,2),(2,4,1),(1,1,0)]:
            with self.subTest(r=r,b=b,q=q):
                w = euclidean_step(r=r,b=b,q=q)
                s = w.state.results
                seed, moved, direct = (s[n] for n in ("Extended seed", "Moving extension", "Direct larger table"))
                self.assertEqual(len(s["Previous table"]), r*b)
                self.assertEqual(s["New cells"].cardinality, q*b*b)
                self.assertEqual(moved.ids, seed.ids)
                self.assertEqual(moved.values.tolist(), seed.values.tolist())
                self.assertEqual(len(set(map(tuple, moved.positions))), b*(r+q*b))
                by_slot = {(int(j),int(i)): int(v) for i,j,v in zip(direct.fields["i"],direct.fields["j"],direct.values)}
                self.assertEqual({tuple(p):int(v) for p,v in zip(moved.positions,moved.values)}, by_slot)
                # Exact comparison needs declared integer fields, never rounded positions.
                for i,k,v in zip(moved.fields["i"],moved.fields["destination"],moved.values):
                    self.assertEqual(v, by_slot[k,i])

    def test_every_recorded_stage_reverses_after_reopening_without_execution(self):
        for builder,name,steps in [(division_motion,"Moving table",3),
                                   (relation_matrices,"Cycled table",1),
                                   (euclidean_step,"Moving extension",2),
                                   (euclidean_next,"Moving extension",2)]:
            original = builder().to_json()
            with self.subTest(name=builder.__name__), patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
                w = Workspace.from_json(original)
                backwards = [w.undo() for _ in range(steps)]
                for reverse in reversed(backwards):
                    forward = w.redo()
                    for t in (0,.25,.5,.75,1):
                        np.testing.assert_allclose(reverse.frame(name,t).positions,
                                                   forward.frame(name,1-t).positions, atol=1e-12, rtol=0)
                self.assertEqual(w.to_json(), original)


class StudioTransformTests(unittest.TestCase):
    def setUp(self):
        self.studio = Studio()
        table = Collection.grid(3,4,values=10*F.i+F.j).arrange(F.j,F.i)
        driver = Collection.grid(3,values=F.i).order_by(-F.i)
        self.studio.workspace = Workspace({"Table":table,"Driver":driver})

    def apply(self, action, **args):
        s = self.studio
        p = s.preview(dict(action=action,name="Table",args={"source":"Table",**args}),s.revision)
        return s.commit(p["token"],s.revision)

    def test_displacement_and_roll_are_different_keyed_operations(self):
        s=self.studio
        original=s.workspace.state.results["Table"]
        response=self.apply("move",displacement=[read("Driver"),formula("0")])
        moved=s.workspace.state.results["Table"]
        self.assertEqual(moved.ids,original.ids)
        np.testing.assert_array_equal(moved.values,original.values)
        np.testing.assert_array_equal(moved.positions[:,0], [0,1,2,3,1,2,3,4,2,3,4,5])
        ref=[moved.node,moved.ids[8]]
        self.assertEqual(s.inspect("Table",ref,s.revision)["bindings"][0]["value"],"2")
        undo=s.history("undo",s.revision,"Table")
        np.testing.assert_allclose([f["positions"] for f in undo["motion"]],
                                   [f["positions"] for f in response["motion"]][::-1],atol=1e-12)
        response=self.apply("roll",axis="j",shift=read("Driver"))
        cycled=s.workspace.state.results["Table"]
        self.assertEqual(cycled.values.tolist(),[0,1,2,3,13,10,11,12,22,23,20,21])
        np.testing.assert_array_equal(cycled.positions,original.positions)
        self.assertEqual(set(cycled.ids),set(original.ids))
        self.assertNotEqual(cycled.ids,original.ids)
        # Labels follow identities, including when several source labels agree.
        self.assertEqual(dict(zip(cycled.ids,cycled.values)),dict(zip(original.ids,original.values)))

    def test_invalid_fiber_shift_and_dimension_leave_applied_work_untouched(self):
        s=self.studio
        original=s.workspace.to_json()
        for action,args in [("roll",dict(axis="j",shift=formula("j"))),
                            ("roll",dict(axis="absent",shift=formula("1"))),
                            ("move",dict(displacement=[formula("i")])),
                            ("move",dict(displacement=[read("Driver",on="j"),formula("0")]))]:
            with self.subTest(action=action,args=args), self.assertRaises(ValueError):
                self.apply(action,**args)
            self.assertEqual(s.workspace.to_json(),original)
            self.assertIsNone(s.pending)

    def test_scalar_notation_and_large_signed_cycles_preserve_exact_semantics(self):
        s=self.studio
        original=s.workspace.to_json()
        with patch("kaleion.evaluate.Evaluator.get",side_effect=AssertionError("execution")):
            spec=s.parse_formula("Table","(j + 2*i) % 4",s.revision)["expression"]
        self.assertEqual(spec["op"],"%")
        self.assertEqual(s.workspace.to_json(),original)
        self.apply("roll",axis="j",shift=formula(str(-(2**100+1))))
        self.assertEqual(s.workspace.state.results["Table"].values.tolist(),[1,2,3,0,11,12,13,10,21,22,23,20])
        with self.assertRaises(ValueError):
            s.parse_formula("Table","__import__('os')",s.revision)

    def test_scattered_three_dimensional_and_empty_one_dimensional_displacements(self):
        from kaleion import Arrangement
        s=self.studio
        points=Arrangement.points([9,9],[[0,1,2],[4,5,6]],keys=[20,10])
        driver=Collection.literal([0,3],keys=[10,20])
        s.workspace=Workspace({"Table":points,"Driver":driver})
        self.apply("move",displacement=[formula("0"),read("Driver",on="key",key="key"),formula("0")])
        moved=s.workspace.state.results["Table"]
        np.testing.assert_array_equal(moved.positions,[[0,4,2],[4,5,6]])
        self.assertEqual(moved.values.tolist(),[9,9])
        self.assertEqual(len(set(moved.ids)),2)
        s.workspace=Workspace({"Table":Collection.grid(0,values=0).arrange(F.i)})
        self.apply("move",displacement=[formula("i")])
        self.apply("roll",axis="i",shift=formula("3"))
        self.assertEqual(s.workspace.state.results["Table"].positions.shape,(0,1))


if __name__ == "__main__":
    unittest.main()
