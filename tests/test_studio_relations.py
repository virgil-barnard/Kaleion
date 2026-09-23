"""Quick relation reuse and axis totals lower to captured, exact constructions."""
from itertools import product
import unittest
from unittest.mock import patch

from kaleion import Collection, F, Workspace, param
from examples.studio.adapter import Studio


class RelationWorkbenchTests(unittest.TestCase):
    def studio(self, roots, parameters=None):
        studio = Studio()
        studio.workspace = Workspace(roots, parameters or {}, max_items=2000, max_history=40)
        return studio

    def apply(self, studio, action, name, **args):
        preview = studio.preview(dict(action=action, name=name, args=args), studio.revision)
        studio.commit(preview['token'], studio.revision)
        return studio.workspace.state.results[name]

    def reuse(self, studio, source, target, mapping, name='Copy'):
        return self.apply(studio, 'reuse_lens', name, source=source, target=target,
                          mapping=mapping, capture=studio.workspace.state.results[source].node)

    def total(self, studio, source, axes, name='Total', reducer='count', weight=None):
        return self.apply(studio, 'total', name, source=source, axes=axes,
                          reducer=reducer, weight=weight or {'field': 'value'})

    def test_unary_binary_ternary_rules_transfer_by_fields_not_mask_or_shape(self):
        for rule, fields, expected in [
            (F.i % 2 == 0, {'i': 'value'}, [True, False, False, True]),
            (F.i < F.j, {'i': 'value', 'j': 'index'}, [False, False, True, True]),
            (F.i + F.j == F.k, {'i': 'value', 'j': 'index', 'k': 'twice'}, [True, True, False, False]),
        ]:
            with self.subTest(fields=fields):
                target = Collection.literal([0, 1, -1, -2]).annotate(twice=2*F.value)
                studio = self.studio({'Lens': Collection.grid(2, 3, 4).where(rule), 'Target': target})
                original = studio.workspace.state.results['Lens']
                copied = self.reuse(studio, 'Lens', 'Target', fields)
                self.assertEqual(copied.mask.tolist(), expected)
                self.assertEqual(copied.source.ids, studio.workspace.state.results['Target'].ids)
                self.assertEqual(studio.workspace.state.results['Lens'].source.ids, original.source.ids)
                self.assertEqual(copied.source.values.tolist(), [0, 1, -1, -2])

    def test_captured_local_parameters_freeze_in_copy_without_rebinding_destination(self):
        lens = Collection.grid(5).where(F.i < param('p')).with_params(p=param('q')+1).with_params(q=1)
        target = Collection.sequence(param('p'), start=-1)
        studio = self.studio({'Lens': lens, 'Target': target}, {'p': 4, 'q': 99})
        before = studio.workspace.to_json()
        with patch('kaleion.evaluate.Evaluator.get', side_effect=AssertionError('evaluation')):
            info = next(o for o in studio.state()['objects'] if o['name'] == 'Lens')['reusable_rule']
        self.assertEqual(info['parameters'], {'p': '2'})
        self.assertEqual(studio.workspace.to_json(), before)
        copied = self.reuse(studio, 'Lens', 'Target', {'i': 'value'})
        self.assertEqual(len(copied.source), 4)
        self.assertEqual(copied.mask.tolist(), [True, True, True, False])
        studio.workspace.set_parameters(p=5)
        self.assertEqual(studio.workspace.state.results['Copy'].mask.tolist(), [True, True, True, False, False])

    def test_unsupported_reads_and_invalid_bindings_leave_workspace_unchanged(self):
        driver = Collection.literal([2])
        source = Collection.grid(3)
        studio = self.studio({'Read lens': source.where(F.i < driver.scalar()),
                              'Plain': source.where(F.i < 2), 'Target': Collection.sequence(4)})
        before = studio.workspace.to_json()
        with patch('kaleion.evaluate.Evaluator.get', side_effect=AssertionError('evaluation')):
            rules = {o['name']: o.get('reusable_rule') for o in studio.state()['objects']}
        self.assertFalse(rules['Read lens']['available'])
        self.assertIn('dependency bindings', rules['Read lens']['reason'])
        for name, target, mapping in [('Read lens', 'Target', {'i': 'index'}),
                                      ('Plain', 'Target', {}), ('Plain', 'Target', {'i': 'missing'}),
                                      ('Plain', 'Target', {'i': 'index', 'j': 'value'}),
                                      ('Plain', 'Plain', {'i': 'i'})]:
            with self.assertRaises(ValueError):
                self.reuse(studio, name, target, mapping)
            self.assertEqual(studio.workspace.to_json(), before)
        with self.assertRaisesRegex(ValueError, 'earlier capture'):
            self.apply(studio, 'reuse_lens', 'Stale', source='Plain', target='Target',
                       mapping={'i': 'index'}, capture='old')

    def test_axis_reductions_keep_order_zeros_exact_weights_and_contributors(self):
        huge = 2**100 + 1
        box = Collection.grid(2, 3, 4, values=huge + F.i - 2*F.j)
        studio = self.studio({'Lens': box.where(F.i + F.j <= F.k)})
        counts = self.total(studio, 'Lens', ['j'], name='By i k')
        self.assertEqual(counts.axes, ())  # Measured keys do not invent grid axes.
        self.assertEqual(counts.positions.tolist(), [[i, k] for i, k in product(range(2), range(4))])
        self.assertEqual(counts.values.tolist(), [sum(i+j <= k for j in range(3)) for i, k in product(range(2), range(4))])
        sums = self.total(studio, 'Lens', ['j', 'k'], name='Weights', reducer='sum')
        expected = [sum(huge+i-2*j for j, k in product(range(3), range(4)) if i+j <= k) for i in range(2)]
        self.assertEqual(sums.values.tolist(), expected)
        total = self.total(studio, 'Lens', ['i', 'j', 'k'], reducer='sum')
        self.assertEqual(total.values.tolist(), [sum(expected)])
        receipt = studio.contributors([sums.node, sums.ids[0]], studio.revision)
        self.assertEqual(int(receipt['measurement']['contributor_count']), 9)
        # A reduced object supplies exact values to another construction through ordinary reads.
        copied = self.apply(studio, 'field', 'Again', source='Weights', field='copied', value={
            'read': {'object': 'Weights', 'on': {'field': 'i'}, 'key': {'field': 'i'}, 'value': {'field': 'value'}}})
        self.assertEqual(copied.context()['copied'].tolist(), expected)
        # The retained measurement keys remain usable for a second reduction.
        line = self.total(studio, 'By i k', ['k'], name='Line', reducer='sum')
        self.assertEqual(line.values.tolist(), [9, 6])
        self.assertEqual(self.total(studio, 'Line', ['i'], name='Grand total', reducer='sum').values.tolist(), [15])
        # Existing measurements may retain text keys; do not invent numeric positions for them.
        colors = Collection.literal([2, 3, 5], fields={'color': ['red', 'red', 'blue'], 'bin': [0, 1, 0]})
        text = self.studio({'Measured': colors.sum(by=(F.color, F.bin))})
        reduced = self.total(text, 'Measured', ['bin'], reducer='sum')
        self.assertIsNone(reduced.positions)
        self.assertEqual(dict(zip(reduced.context()['color'].tolist(), reduced.values.tolist())), {'red': 5, 'blue': 5})

    def test_empty_reduced_axes_retain_declared_fibers_and_validate_choices(self):
        studio = self.studio({'Empty': Collection.grid(2, 0, 3).where(F.i == 1)})
        result = self.total(studio, 'Empty', ['j'], name='Zeros')
        self.assertEqual(result.positions.tolist(), [[i, k] for i, k in product(range(2), range(3))])
        self.assertEqual(result.values.tolist(), [0]*6)
        self.assertEqual(self.total(studio, 'Empty', ['j', 'k'], name='Rows', reducer='sum').values.tolist(), [0, 0])
        self.assertEqual(self.total(studio, 'Empty', ['i', 'j', 'k']).values.tolist(), [0])
        before = studio.workspace.to_json()
        for axes in ([], ['i', 'i'], ['value'], ['missing'], [1]):
            with self.assertRaises(ValueError):
                self.total(studio, 'Empty', axes, name='Invalid')
            self.assertEqual(studio.workspace.to_json(), before)

    def test_reused_rules_and_totals_survive_captured_undo_and_core_save(self):
        studio = self.studio({'Lens': Collection.grid(3).where(F.i > 0), 'Target': Collection.grid(2, 3)})
        self.reuse(studio, 'Lens', 'Target', {'i': 'j'})
        self.total(studio, 'Copy', ['j'])
        saved = studio.workspace.to_json()
        reopened = Studio()
        with patch('kaleion.evaluate.Evaluator.get', side_effect=AssertionError('evaluation')):
            reopened.reopen(saved, 0)
            self.assertEqual(reopened.workspace.state.results['Total'].values.tolist(), [2, 2])
            self.assertTrue(next(o for o in reopened.state()['objects'] if o['name'] == 'Copy')['reusable_rule']['available'])
            reopened.history('undo', reopened.revision, 'Total')
            self.assertNotIn('Total', reopened.workspace.state.results)
            reopened.history('redo', reopened.revision, 'Copy')
            self.assertEqual(reopened.workspace.state.results['Total'].values.tolist(), [2, 2])


if __name__ == '__main__':
    unittest.main()
