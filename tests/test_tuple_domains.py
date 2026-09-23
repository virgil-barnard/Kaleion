"""Tuple locations have no implicit numeric contents, including through history."""
import json
from itertools import product
import unittest
from unittest.mock import patch

import numpy as np
from kaleion import Collection, F, Inspection, Workspace, param
from kaleion.model import Ref, Snapshot
from examples.studio.adapter import Studio


class TupleDomainTests(unittest.TestCase):
    def test_tuple_coordinates_relations_counts_and_zero_fibers(self):
        domain = Collection.tuples(2, 3, 4)
        relation = domain.where(F.i + F.j == F.k)
        workspace = Workspace({'tuples': domain, 'relation': relation,
                               'counts': relation.group_by(F.i, F.j).count(),
                               'empty': Collection.tuples(2, 0, 3).group_by(F.i, F.k).count()})
        self.assertFalse(workspace.state.errors)
        result = workspace.state.results['tuples']
        self.assertIsNone(result.values)
        self.assertNotIn('value', result.context())
        self.assertEqual(list(zip(result.fields['i'], result.fields['j'], result.fields['k'])),
                         list(product(range(2), range(3), range(4))))
        self.assertEqual(workspace.state.results['counts'].values.tolist(), [1]*6)
        self.assertEqual(workspace.state.results['empty'].values.tolist(), [0]*6)
        ref = Ref(workspace.state.results['counts'].node, workspace.state.results['counts'].ids[0])
        receipt = Inspection(workspace.state).measurement(ref)
        self.assertIsNone(receipt.contributors[0].item.value)
        self.assertEqual(receipt.contributors[0].weight, 1)
        self.assertEqual(receipt.contributors[0].item.fields['k'], 0)

    def test_value_assignment_preserves_identity_and_exactness(self):
        domain = Collection.tuples(2, 3).arrange(F.i, F.j)
        valued = domain.with_values(2**100 + 10*F.i - F.j)
        workspace = Workspace({'source': domain, 'valued': valued,
                               'weighted': domain.sum(value=3*F.i-F.j)})
        original, result = (workspace.state.results[k] for k in ('source', 'valued'))
        self.assertEqual(result.ids, original.ids)
        np.testing.assert_array_equal(result.positions, original.positions)
        self.assertEqual(result.values.tolist(), [2**100+10*i-j for i,j in product(range(2),range(3))])
        self.assertEqual(workspace.state.results['weighted'].values.tolist(), [3])
        receipt = Inspection(workspace.state).item(Ref(result.node,result.ids[2]))
        self.assertEqual(receipt.parents, (Ref(original.node, original.ids[2]),))
        self.assertIsNone(Inspection(workspace.state).item(receipt.parents[0]).value)

    def test_missing_contents_fail_without_poisoning_independent_roots(self):
        domain = Collection.tuples(1)
        roots = {'sum': domain.sum(), 'lens': domain.where(F.value == 0),
                 'scalar': Collection.literal([1]).with_values(domain.scalar()),
                 'lookup': Collection.literal([0]).lookup(domain),
                 'gather': Collection.literal([7]).gather(domain),
                 'pad': domain.pad(1,0), 'mixed': domain.concat(domain.with_values(1)),
                 'count': domain.count()}
        state = Workspace(roots).state
        self.assertEqual(set(state.errors), set(roots)-{'count'})
        self.assertEqual(state.results['count'].values.tolist(),[1])
        with self.assertRaises(ValueError):
            Snapshot('x', None, ('a',), ('a',), fields={'value':[0]})

    def test_reindex_join_and_boolean_selection_keep_absence_and_lineage(self):
        domain = Collection.tuples(4)
        selected = domain.where((F.i == 1) | (F.i == 3)).select()
        repeated = selected.gather([1,0,1])
        state = Workspace({'source':domain, 'repeat':repeated, 'join':domain.concat(domain)}).state
        self.assertFalse(state.errors)
        result = state.results['repeat']
        self.assertIsNone(result.values)
        self.assertEqual(result.fields['i'].tolist(), [3,1,3])
        self.assertEqual(len(set(result.ids)),3)
        self.assertEqual(result.sources[0], result.sources[2])
        self.assertIsNone(state.results['join'].values)
        self.assertEqual(len(state.results['join']),8)

    def test_schema_two_reopens_undo_redo_and_motion_without_evaluation(self):
        domain = Collection.tuples(2, 2).arrange(F.i,F.j)
        workspace = Workspace({'shape':domain})
        workspace.set('shape',domain.move((1,2)))
        saved = workspace.to_json()
        self.assertEqual(json.loads(saved)['schema'],2)
        with patch('kaleion.evaluate.Evaluator.get',side_effect=AssertionError('re-evaluated')):
            loaded = Workspace.from_json(saved)
            reverse = loaded.undo()
            frame = reverse.frame('shape',.4)
            self.assertEqual(frame.values_before,(None,)*4)
            self.assertEqual(frame.values_after,(None,)*4)
            loaded.redo()
            self.assertIsNone(loaded.state.results['shape'].values)
            self.assertEqual(loaded.to_json(),saved)
        legacy = Workspace({'grid':Collection.grid(2)})
        self.assertEqual(json.loads(legacy.to_json())['schema'],1)
        np.testing.assert_array_equal(Workspace.from_json(legacy.to_json()).state.results['grid'].values,[1,2])
        downgraded=json.loads(saved);downgraded['schema']=1
        with self.assertRaisesRegex(ValueError,'schema 2'):
            Workspace.from_json(json.dumps(downgraded))

    def test_tuple_product_does_not_invent_contents_and_retains_empty_shape(self):
        studio=Studio()
        studio.workspace=Workspace({'A':Collection.tuples(2), 'B':Collection.tuples(0)})
        command=dict(action='product',name='Pairs',args={'factors':{
            'left':{'source':'A','fields':['i']}, 'right':{'source':'B','fields':['i']}}})
        preview=studio.preview(command,studio.revision)
        studio.commit(preview['token'],studio.revision)
        result=studio.workspace.state.results['Pairs']
        self.assertIsNone(result.values)
        self.assertEqual(result.shape,(2,0))
        self.assertEqual(result.axes,('left','right'))
        total=studio.workspace.state.roots['Pairs'].group_by(F.left).count().evaluate()
        self.assertEqual(total.values.tolist(),[0,0])

    def test_index_formula_protocol_is_exact_bounded_and_captured(self):
        studio=Studio()
        def apply(name,value,shape=['2','3']):
            preview=studio.preview(dict(action='grid',name=name,args=dict(shape=shape,axes=['i','j'],value=value)),studio.revision)
            studio.commit(preview['token'],studio.revision)
        apply('Tuples',None)
        self.assertNotIn('value',studio.state()['objects'][0]['fields'])
        apply('Values',{'formula':f'{2**100} + 10*i - j'})
        self.assertEqual(studio.workspace.state.results['Values'].values.tolist(),[2**100+10*i-j for i,j in product(range(2),range(3))])
        before=studio.workspace.to_json()
        for text in ['i/2', 'i.real', '__import__("os")', '[1][0]', '2**1000000000', 'True', 'i + missing', '1//0']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                apply('Invalid',{'formula':text})
            self.assertEqual(studio.workspace.to_json(),before)
        studio.workspace.set_parameters(n=4)
        apply('Parameter formula',{'formula':'n*i + j'})
        self.assertEqual(studio.workspace.state.results['Parameter formula'].values.tolist(),[0,1,2,4,5,6])
        self.assertIn('n',str(studio.workspace.state.roots['Parameter formula'].node.attributes['values']))
        studio.workspace.set_parameters(i=9)
        with self.assertRaisesRegex(ValueError,'both an index/field and a parameter'):
            apply('Ambiguous',{'formula':'i+j'})
        # Even when undone, a tuple state retained for redo needs the new format.
        old=Workspace({'ordinary':Collection.grid(1)})
        old.set('tuples',Collection.tuples(0))
        old.undo()
        self.assertEqual(json.loads(old.to_json())['schema'],2)


if __name__ == '__main__':
    unittest.main()
