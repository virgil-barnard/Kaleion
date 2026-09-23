"""Compact relation syntax is an authoring view of ordinary captured expressions."""
from itertools import product
import json
import unittest
from unittest.mock import patch

from kaleion import Collection, F, Workspace
from examples.studio.adapter import Studio
from examples.studio.formulas import formula


class RelationNotationTests(unittest.TestCase):
    def studio(self, source=None, parameters=None):
        studio = Studio()
        studio.workspace = Workspace(
            {'Source': source if source is not None else Collection.tuples(5, 5)},
            parameters or {}, max_items=2000, max_history=40)
        return studio

    def command(self, text, name='Lens'):
        return dict(action='lens', name=name, args=dict(source='Source', rule={'formula': text}))

    def apply(self, studio, command):
        preview = studio.preview(command, studio.revision)
        studio.commit(preview['token'], studio.revision)
        return studio.workspace.state.results[command['name']]

    def test_modular_lattice_and_binary_projective_rules_share_one_contract(self):
        for text, n, predicate in [
            ('(j - 2*i - 1) % p = 0', 5, lambda i, j: j == (2*i+1) % 5),
            ('(j - 2*i - 1) % p = 0', 6, lambda i, j: j == (2*i+1) % 6),
            ('0 ≤ i < 4 and j ≠ i or i + j = 8', 5,
             lambda i, j: (i in range(4) and j != i) or (i, j) == (4, 4)),
            # Nonzero binary vectors label projective points and lines. This is
            # the F_2 dot product, not arithmetic in the seven-element residue ring.
            ('((i+1)%2*((j+1)%2) + ((i+1)//2)%2*(((j+1)//2)%2) '
             '+ (i+1)//4*((j+1)//4)) % 2 = 0', 7,
             lambda i, j: ((i+1) & (j+1)).bit_count() % 2 == 0),
        ]:
            with self.subTest(rule=text):
                studio = self.studio(Collection.tuples(n, n), {'p': n})
                result = self.apply(studio, self.command(text))
                self.assertEqual(result.mask.tolist(), [predicate(i, j) for i, j in product(range(n), repeat=2)])
                self.assertEqual(result.source.ids, studio.workspace.state.results['Source'].ids)
                self.assertIsNone(result.source.values)
                if n == 6:
                    # Slope 2 ceases to be invertible: reverse fibers are not
                    # singletons, and the declared zero fibers must survive.
                    reverse = self.apply(studio, dict(action='total', name='Reverse', args=dict(
                        source='Lens', axes=['i'], reducer='count', weight={'field': 'j'})))
                    self.assertEqual(reverse.values.tolist(), [0, 2, 0, 2, 0, 2])
                if n == 7:
                    lines = [{i for i in range(n) if predicate(i, j)} for j in range(n)]
                    self.assertEqual([len(line) for line in lines], [3]*7)
                    self.assertTrue(all(len(a & b) == 1 for k, a in enumerate(lines) for b in lines[k+1:]))

    def test_exact_integers_zero_groups_and_receipts_survive_text_authoring(self):
        huge = 2**100 + 1
        source = Collection.grid(3, 4, values=huge + F.i - F.j)
        studio = self.studio(source)
        lens = self.apply(studio, self.command(f'value ≥ {huge} and i > 0'))
        self.assertEqual(lens.cardinality, 5)
        counts = self.apply(studio, dict(action='total', name='Counts', args=dict(
            source='Lens', axes=['j'], reducer='count', weight={'field': 'value'})))
        self.assertEqual(counts.values.tolist(), [0, 2, 3])
        receipt = studio.contributors([counts.node, counts.ids[0]], studio.revision)
        self.assertEqual(receipt['measurement']['contributor_count'], '0')
        receipt = studio.contributors([counts.node, counts.ids[2]], studio.revision)
        self.assertEqual(receipt['measurement']['contributor_count'], '3')
        # Reopening and undo use the captures; no parser or evaluator is needed.
        saved = studio.workspace.to_json()
        nodes = json.loads(saved)['states'][0]['provenance']['graph']['nodes'].values()
        rules = [node['attributes']['rule'] for node in nodes if node['op'] == 'incidence']
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0]['$expr'], 'and')
        reopened = Studio()
        with patch('kaleion.evaluate.Evaluator.get', side_effect=AssertionError('evaluation')):
            reopened.reopen(saved, 0)
            reopened.history('undo', reopened.revision, 'Counts')
            reopened.history('redo', reopened.revision, 'Counts')
        self.assertEqual(reopened.workspace.state.results['Counts'].values.tolist(), [0, 2, 3])

    def test_syntax_conversion_is_read_only_and_keeps_a_valid_preview(self):
        studio = self.studio()
        preview = studio.preview(self.command('i < j'), studio.revision)
        before = studio.workspace.to_json()
        with patch('kaleion.evaluate.Evaluator.get', side_effect=AssertionError('evaluation')):
            spec = studio.parse_relation('Source', '0 <= i < j and j != 4', 0)['expression']
            # Syntax success makes no claim about domain evaluation.
            studio.parse_relation('Source', 'i < 1//0', 0)
            with self.assertRaises(ValueError):
                studio.parse_relation('Source', 'i <', 0)
            with self.assertRaisesRegex(ValueError, 'out of date'):
                studio.parse_relation('Source', 'i < j', 1)
        self.assertEqual(studio.workspace.to_json(), before)
        self.assertEqual(studio.pending.token, preview['token'])
        studio.commit(preview['token'], 0)
        result = self.apply(studio, dict(action='lens', name='Structured', args=dict(source='Source', rule=spec)))
        self.assertEqual(result.mask.tolist(), [0 <= i < j and j != 4 for i, j in product(range(5), repeat=2)])

    def test_invalid_rules_and_eager_boolean_fail_without_false_incidence(self):
        studio = self.studio()
        before = studio.workspace.to_json()
        for text in ['i <', 'unknown = 1', 'i / 2 = 1', 'i**2 = j', 'abs(i) = j',
                     'i.real = 0', 'i[0] = 1', '__import__("os")', 'True',
                     'not (i = j)', 'i & j', 'i := 0', 'i', '1.5 = j',
                     'i < 0 and 1//0 = 0', 'i >= 0 or 1//0 = 0', 'i '*130]:
            with self.subTest(text=text):
                old = studio.preview(self.command('i = j'), 0)
                with self.assertRaises((ValueError, TypeError)):
                    studio.preview(self.command(text, 'Invalid'), 0)
                self.assertEqual(studio.workspace.to_json(), before)
                with self.assertRaisesRegex(ValueError, 'no longer current'):
                    studio.commit(old['token'], 0)

    def test_empty_tuple_domain_still_checks_fields_and_boolean_type(self):
        studio = self.studio(Collection.tuples(2, 0))
        self.assertEqual(self.apply(studio, self.command('i < j')).cardinality, 0)
        before = studio.workspace.to_json()
        for text in ('value = 0', 'missing = 0', 'i'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                studio.preview(self.command(text, 'Invalid'), studio.revision)
            self.assertEqual(studio.workspace.to_json(), before)

    def test_ambiguous_names_require_explicit_controls_and_values_stay_arithmetic(self):
        studio = self.studio(parameters={'i': 2})
        with self.assertRaisesRegex(ValueError, 'both'):
            studio.parse_relation('Source', 'i < j', 0)
        result = self.apply(studio, dict(action='lens', name='Explicit', args=dict(source='Source', rule={
            'op': '<', 'args': [{'field': 'i'}, {'parameter': 'i'}]})))
        self.assertEqual(result.cardinality, 10)
        for text in ('i < j', 'i = j', 'i and j'):
            with self.assertRaises(ValueError):
                formula(text, fields=['i', 'j'])
        self.assertEqual(formula('2 × i − 1'), {
            'op': '-', 'args': [{'op': '*', 'args': [{'integer': '2'}, {'field': 'i'}]}, {'integer': '1'}]})

    def test_text_rule_reuses_captured_parameter_and_explicit_field_mapping(self):
        studio = self.studio(Collection.tuples(4), {'p': 2})
        self.apply(studio, self.command('i < p'))
        studio.workspace.set('Target', Collection.literal([3, 1, 0, 2]))
        result = self.apply(studio, dict(action='reuse_lens', name='Moved', args=dict(
            source='Lens', target='Target', mapping={'i': 'value'},
            capture=studio.workspace.state.results['Lens'].node)))
        self.assertEqual(result.mask.tolist(), [False, True, True, False])
        studio.workspace.set_parameters(p=3)
        self.assertEqual(studio.workspace.state.results['Lens'].cardinality, 3)
        self.assertEqual(studio.workspace.state.results['Moved'].mask.tolist(), [False, True, True, False])


if __name__ == '__main__':
    unittest.main()
