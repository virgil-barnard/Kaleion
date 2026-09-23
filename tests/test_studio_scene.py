"""Scene adapters preserve exact captures, dimensions and source semantics."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from kaleion import Collection, F, Workspace
from examples.studio.adapter import Studio


class SceneContracts(unittest.TestCase):
    def test_empty_declared_shape_and_3d_incidence_survive_read_only_queries(self):
        source = Collection.grid(2, 3, 4, values=2**100+1).arrange(F.k, -F.i, F.j)
        studio = Studio()
        studio.workspace = Workspace({'Solid': source.where(F.i == 1),
                                      'Empty': Collection.grid(0, 3, 4)})
        saved = studio.workspace.to_json()
        with patch('kaleion.evaluate.Evaluator.get', side_effect=AssertionError('execution')):
            objects = {o['name']: o for o in studio.state()['objects']}
            solid, empty = objects['Solid'], objects['Empty']
            self.assertEqual((solid['axes'], solid['shape'], solid['dimension']),
                             (['i', 'j', 'k'], ['2', '3', '4'], 3))
            self.assertEqual(len(solid['rows']), 24)
            self.assertEqual(sum(r['match'] for r in solid['rows']), 12)
            self.assertEqual(solid['rows'][-1]['position'], [3., -1., 2.])
            self.assertEqual(solid['rows'][-1]['fields']['value'], str(2**100+1))
            self.assertEqual(empty['shape'], ['0', '3', '4'])
            self.assertEqual(empty['rows'], [])
            self.assertEqual(studio.capture(solid['capture'], 0)['rows'], solid['rows'])
        self.assertEqual(studio.workspace.to_json(), saved)

    def test_sequence_controls_use_exact_builder_and_reject_invalid_bounds(self):
        studio = Studio()
        command = {'action': 'sequence', 'name': 'Terms', 'args': {
            'length': {'integer': '4'}, 'start': {'integer': str(2**100+1)},
            'step': {'integer': '-7'}}}
        preview = studio.preview(command, 0)
        self.assertEqual(studio.workspace.state.roots, {})
        studio.commit(preview['token'], 0)
        self.assertEqual(studio.workspace.state.results['Terms'].values.tolist(),
                         [2**100+1-7*i for i in range(4)])
        before = studio.workspace.to_json()
        command['name'] = 'Invalid'
        for n in (-1, 2001):
            command['args']['length'] = {'integer': str(n)}
            with self.assertRaises(ValueError):
                studio.preview(command, studio.revision)
            self.assertEqual(studio.workspace.to_json(), before)
        command['name'] = 'Empty'
        command['args']['length'] = {'integer': '0'}
        preview = studio.preview(command, studio.revision)
        studio.commit(preview['token'], studio.revision)
        self.assertEqual(len(studio.workspace.state.results['Empty']), 0)

    def test_saved_box_has_independent_finite_partition_and_inspectable_zero_overlap(self):
        path = Path(__file__).resolve().parents[1] / 'examples/canvases/03_incidence_box.json'
        studio = Studio()
        with patch('kaleion.evaluate.Evaluator.get', side_effect=AssertionError('execution')):
            studio.reopen(path.read_text(), 0)
            results = studio.workspace.state.results
            self.assertEqual(len(results['Box']), 240)
            masks = [results[name].mask for name in ('X region', 'Y region', 'Z region')]
            self.assertTrue(all(sum(int(m[i]) for m in masks) == 1 for i in range(240)))
            self.assertEqual([int(results[n+' volume'].values[0]) for n in 'XYZ'], [86, 80, 74])
            shared = results['Shared cells']
            self.assertEqual(shared.cardinality, 0)
            self.assertEqual(len(shared.source), 240)
            measured = results['X volume']
            receipt = studio.contributors([measured.node, measured.ids[0]], studio.revision)
            self.assertEqual(receipt['measurement']['contributor_count'], '86')
            self.assertEqual(json.loads(studio.workspace.to_json())['schema'], 1)


if __name__ == '__main__':
    unittest.main()
