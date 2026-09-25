"""Independent witnesses for copied domains and the shared authoring instrument."""
import unittest
from unittest.mock import patch
import numpy as np

from kaleion import Collection, F, Inspection, Workspace, param
from kaleion.model import Ref
from examples.studio.adapter import Studio
from examples.division_relations import periodic_extension, guarded_remainder_addresses


class ReindexTests(unittest.TestCase):
    def setUp(self):
        self.studio = Studio()
        self.source = Collection.grid(2, 3, values=10*F.i+F.j).arrange(F.j, F.i)
        self.studio.workspace = Workspace({"Source": self.source})

    def apply(self, kind, *, name="Result", source="Source", axis="j", placement="indices", **choices):
        s = self.studio
        command = dict(action="reindex", name=name, args=dict(source=source, kind=kind, axis=axis,
                                                            placement=placement, **choices))
        p = s.preview(command, s.revision)
        return s.commit(p["token"], s.revision)

    def test_repeat_and_truncate_record_copies_and_exact_reverse_paths(self):
        s = self.studio
        before = s.workspace.state.results["Source"]
        forward = self.apply("tile", name="Source", times={"formula":"2"})
        copied = s.workspace.state.results["Source"]
        self.assertEqual(copied.values.tolist(), [0,1,2,0,1,2,10,11,12,10,11,12])
        self.assertEqual(copied.shape, (2,6))
        self.assertTrue(set(copied.ids).isdisjoint(before.ids))
        self.assertEqual(len(set(copied.ids)), 12)
        inspector=Inspection(s.workspace.state)
        first=inspector.item(copied.parents[0][0])
        duplicate=inspector.item(copied.parents[3][0])
        self.assertEqual(first.parents,duplicate.parents)
        self.assertEqual(duplicate.parents[0],Ref(before.node,before.ids[0]))
        self.assertEqual(forward["motion"][0]["before"].count(before.ids[0]), 2)
        frozen = s.workspace.to_json()
        with patch("kaleion.evaluate.Evaluator.get",side_effect=AssertionError("execution")):
            restored = Workspace.from_json(frozen)
            back = restored.undo(); again = restored.redo()
            for t in (0,.25,.5,1):
                np.testing.assert_allclose(back.frame("Source",t).positions,
                                           again.frame("Source",1-t).positions,rtol=0,atol=1e-12)
            self.assertEqual(restored.to_json(), frozen)

    def test_address_order_is_explicit_and_permutation_is_an_optional_claim(self):
        s = self.studio
        # Stored order deliberately disagrees with the declared destination order.
        addresses = Collection.literal([0,2,2],fields={"slot":[1,2,0]})
        s.workspace.set("Addresses", addresses)
        self.apply("gather", addresses="Addresses",field="value",order="slot",bijective=False)
        result = s.workspace.state.results["Result"]
        self.assertEqual(result.values.tolist(), [2,0,2,12,10,12])
        self.assertEqual(result.fields["j"].tolist(),[0,1,2,0,1,2])
        before = s.workspace.to_json()
        with self.assertRaisesRegex(ValueError,"bijection"):
            self.apply("gather",name="Invalid",addresses="Addresses",field="value",order="slot",bijective=True)
        self.assertEqual(s.workspace.to_json(),before)
        # Permutations also declare a new collection, rather than reusing identities.
        s.workspace.set("Permutation", Collection.literal([1,2,0]))
        self.apply("gather",name="Permuted",addresses="Permutation",field="value",order="index",bijective=True)
        self.assertEqual(s.workspace.state.results["Permuted"].values.tolist(),[1,2,0,11,12,10])

    def test_bad_order_and_out_of_range_addresses_do_not_commit(self):
        s = self.studio
        for values, slots, message in [([0,1],[0,0],"order must be unique"),
                                       ([-1],[0],"outside"),([2**100],[0],"outside")]:
            s.workspace.set("Addresses",Collection.literal(values,fields={"slot":slots}))
            frozen = s.workspace.to_json()
            with self.assertRaisesRegex(ValueError,message):
                self.apply("gather",addresses="Addresses",field="value",order="slot",bijective=False)
            self.assertIsNone(s.pending)
            self.assertEqual(s.workspace.to_json(),frozen)

    def test_join_zero_cells_is_explicit_and_rejects_incompatible_inputs(self):
        s = self.studio
        zero = Collection.grid(2,2,values=0)
        s.workspace.set("Zero",zero)
        self.apply("concat",other="Zero")
        result = s.workspace.state.results["Result"]
        self.assertEqual(result.shape,(2,5))
        self.assertEqual(result.values.tolist(),[0,1,2,0,0,10,11,12,0,0])
        copied_zero=Inspection(s.workspace.state).item(result.parents[3][0])
        self.assertEqual(copied_zero.parents[0].node,s.workspace.state.results["Zero"].node)
        # A literal zero is a declared occurrence, not a missing-source fallback.
        s.workspace.set("Bad",Collection.grid(3,2,values=0))
        with self.assertRaisesRegex(ValueError,"axes must agree"):
            self.apply("concat",other="Bad",name="Invalid")
        s.workspace.set("Unvalued",Collection.tuples(2,2))
        with self.assertRaisesRegex(ValueError,"tuples only"):
            self.apply("concat",other="Unvalued",name="Invalid")

    def test_zero_repeats_tuple_domains_and_three_dimensional_copies(self):
        s=self.studio
        s.workspace=Workspace({"Source":Collection.tuples(2,1,2).arrange(F.k,F.j,F.i)})
        self.apply("tile",axis="i",times={"formula":"2"})
        result=s.workspace.state.results["Result"]
        self.assertIsNone(result.values)
        self.assertEqual(result.shape,(4,1,2))
        self.assertEqual(result.positions.shape,(8,3))
        self.apply("tile",name="Empty",axis="i",times={"formula":"0"})
        self.assertEqual(s.workspace.state.results["Empty"].positions.shape,(0,3))
        self.apply("tile",name="Flat",axis=None,placement="unplaced",times={"formula":"2"})
        self.assertIsNone(s.workspace.state.results["Flat"].positions)
        self.assertEqual(s.workspace.state.results["Flat"].axes,())

    def test_repeated_zero_measurements_keep_receipts(self):
        s=self.studio
        counts=Collection.grid(2,3,values=0).where(F.j<F.i).count(by=F.i)
        s.workspace=Workspace({"Source":counts})
        self.apply("tile",axis=None,times={"formula":"2"})
        result=s.workspace.state.results["Result"]
        self.assertEqual(result.values.tolist(),[0,1,0,1])
        inspector=Inspection(s.workspace.state)
        receipts=[inspector.measurement(Ref(result.node,oid)) for oid in result.ids]
        self.assertEqual([r.contributor_count for r in receipts],[0,1,0,1])
        self.assertEqual(receipts[0].origin,receipts[2].origin)

    def test_address_order_guard_survives_parameter_changes(self):
        s=self.studio
        addresses=Collection.grid(3,values=F.i).annotate(slot=F.i%param("period"))
        s.workspace=Workspace({"Source":self.source,"Addresses":addresses},{"period":3})
        self.apply("gather",addresses="Addresses",field="value",order="slot",bijective=True)
        s.workspace.set_parameters(period=1)
        self.assertEqual(set(s.workspace.state.errors),{"Result"})
        self.assertIn("Address order must be unique",s.workspace.state.errors["Result"])
        self.assertEqual(s.workspace.state.results["Source"].values.tolist(),[0,1,2,10,11,12])


class PaperExtensionTests(unittest.TestCase):
    def test_periodic_factor_and_padding_have_independent_formulas(self):
        w=periodic_extension()
        for a,b in [(11,7),(12,8),(7,11),(7,7),(1,1)]:
            with self.subTest(a=a,b=b):
                w.set_parameters(a=a,b=b)
                s=w.state.results
                expected=[int((a*q+r)%b==0) for r in range(a) for q in range(b)]
                self.assertEqual(s["Moving factor"].values.tolist(),expected)
                self.assertEqual(s["Direct factor"].values.tolist(),expected)
                if a>=b:
                    self.assertEqual(s["Padded R"].values.tolist(),
                                     [int(q==a*r%b) for r in range(b) for q in range(a)])
                    self.assertFalse(w.state.errors)
                else:
                    self.assertEqual(set(w.state.errors),{"Zero columns","Padded R"})
                self.assertEqual(s["Moving factor"].shape,(a,b))

    def test_guarded_addresses_move_identical_labels_and_fail_for_nonunits(self):
        w=guarded_remainder_addresses();s=w.state.results
        # Inverse of multiplication by 11 mod 7, calculated independently.
        expected=[next(i for i in range(7) if 11*i%7==j) for j in range(7)]
        self.assertEqual(s["Guarded addresses"].fields["address"].tolist(),expected)
        self.assertEqual(s["Moving copies"].fields["original"].tolist(),expected)
        self.assertEqual(s["Moving copies"].values.tolist(),[9]*7)
        self.assertEqual(len(set(s["Moving copies"].ids)),7)
        first=Inspection(w.state).bindings(Ref(s["Guarded addresses"].node,s["Guarded addresses"].ids[0]))[0]
        receipt=Inspection(w.state).measurement(first.driver)
        self.assertEqual(receipt.contributor_count,1)
        self.assertEqual(receipt.contributors[0].weight,0)
        w.set_parameters(a=14)
        self.assertEqual(set(w.state.errors),{"Guarded addresses","Moving copies"})
        self.assertEqual(w.state.results["R relation"].cardinality,7)
        self.assertEqual(len(w.state.results["Scattered source"]),7)

    def test_copy_split_and_truncation_reverse_from_saved_paths(self):
        for build,name,steps in [(periodic_extension,"Moving factor",2),
                                 (guarded_remainder_addresses,"Moving copies",1)]:
            saved=build().to_json()
            with patch("kaleion.evaluate.Evaluator.get",side_effect=AssertionError("execution")):
                w=Workspace.from_json(saved)
                reverse=[w.undo() for _ in range(steps)]
                for back in reversed(reverse):
                    forward=w.redo()
                    for t in (0,.5,1):
                        np.testing.assert_allclose(back.frame(name,t).positions,forward.frame(name,1-t).positions,atol=1e-12,rtol=0)
                self.assertEqual(w.to_json(),saved)


if __name__ == "__main__":
    unittest.main()
