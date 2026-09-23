"""Worked canvases open as ordinary editable captures in the existing studio."""

from collections import Counter
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np

from examples.studio.adapter import Studio


CANVASES = Path(__file__).resolve().parents[1] / "examples" / "canvases"
LAST_OBJECT = {"02_floor_sums": "Pieces", "05_radon_reconstruction": "Image heights",
               "06_young_layers": "Cells", "07_equal_sums": "Moving pairs"}


def opened(name):
    studio = Studio()
    studio.reopen((CANVASES / (name + ".json")).read_text(), studio.revision)
    return studio


class SavedCanvasTests(unittest.TestCase):
    def test_all_canvases_reopen_inspect_and_reverse_saved_motion_without_evaluation(self):
        for name, active in LAST_OBJECT.items():
            with self.subTest(canvas=name), patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
                studio = opened(name)
                saved = studio.workspace.to_json()
                self.assertFalse(studio.workspace.state.errors)
                self.assertEqual(list(studio.workspace.state.roots)[-1], active)
                self.assertLessEqual(studio.workspace.max_items, 2000)
                self.assertLessEqual(studio.workspace.max_history, 40)
                result = studio.workspace.state.results[active]
                receipt = studio.inspect(active, [result.node, result.ids[0]], studio.revision)
                self.assertEqual(receipt['item']['value'], str(result.values[0]))
                undo = studio.history("undo", studio.revision, active)
                redo = studio.history("redo", studio.revision, active)
                self.assertEqual(len(undo['motion']), 25)
                self.assertEqual(len(redo['motion']), 25)
                # Same recorded path, reversed, within float evaluation rounding.
                np.testing.assert_allclose([f['positions'] for f in undo['motion']],
                                           [f['positions'] for f in redo['motion']][::-1], atol=1e-12, rtol=0)
                self.assertEqual(studio.workspace.to_json(), saved)
                self.assertEqual(json.loads(saved)['schema'], 1)

    def test_equal_sums_retain_zero_bins_ranks_and_original_occurrences(self):
        studio = opened("07_equal_sums")
        r = studio.workspace.state.results
        oracle = Counter(a + b for a in range(4) for b in range(4))
        self.assertEqual(r['Counts'].values.tolist(), [oracle[s] for s in range(9)])
        self.assertEqual(r['Energy'].values.tolist(), [sum(n*n for n in oracle.values())])
        self.assertEqual(r['Moving pairs'].ids, r['Pairs'].ids)
        self.assertEqual(len(set(map(tuple, r['Moving pairs'].positions))), 16)
        zero = r['Counts']
        self.assertEqual(studio.contributors([zero.node, zero.ids[8]], studio.revision)['measurement']['contributor_count'], '0')
        rank = r['Ranks']
        self.assertEqual(studio.contributors([rank.node, rank.ids[12]], studio.revision)['measurement']['contributor_count'], '3')
        studio.history('undo', studio.revision, 'Moving pairs')
        self.assertEqual(len(set(map(tuple, studio.workspace.state.results['Moving pairs'].positions))), 7)

    def test_young_offsets_explain_measured_layers_and_pack_ten_cells(self):
        studio = opened("06_young_layers")
        r = studio.workspace.state.results
        self.assertEqual(r['Columns'].values.tolist(), [5, 3, 2, 0])
        self.assertEqual(r['Layers'].values.tolist(), [3, 3, 2, 1, 1])
        self.assertEqual(r['Offsets'].values.tolist(), [0, 3, 6, 8, 9])
        self.assertEqual(sorted(r['Cells'].positions[:, 0]), list(range(10)))
        offset = r['Offsets']
        receipt = studio.contributors([offset.node, offset.ids[3]], studio.revision)['measurement']
        self.assertEqual([c['weight'] for c in receipt['contributors']], ['3', '3', '2'])
        layer = studio.contributors(receipt['contributors'][2]['item']['ref'], studio.revision)['measurement']
        self.assertEqual(layer['contributor_count'], '2')

    def test_floor_sums_have_an_inspectable_non_coprime_case(self):
        studio = opened("02_floor_sums")
        r = studio.workspace.state.results
        self.assertEqual(r['Column counts'].values.tolist(), [11*u//7 for u in range(1, 7)])
        self.assertEqual(r['Row counts'].values.tolist(), [7*v//11 for v in range(1, 11)])
        self.assertEqual((r['Lower total'].values[0], r['Upper total'].values[0], r['Overlap total'].values[0]), (30, 30, 0))
        preview = studio.preview_case({'a': '12', 'b': '8'}, studio.revision, 'Overlap')
        self.assertFalse(preview['errors'])
        studio.commit(preview['token'], studio.revision)
        r = studio.workspace.state.results
        self.assertEqual(len(r['Rectangle']), 77)
        self.assertEqual(r['Overlap'].cardinality, 3)
        self.assertEqual((r['Lower total'].values[0], r['Upper total'].values[0]), (40, 40))

    def test_radon_reconstruction_has_weight_reads_and_a_composite_failure(self):
        studio = opened("05_radon_reconstruction")
        r = studio.workspace.state.results
        self.assertEqual(r['Image heights'].values.tolist(), [u*(v+1) for u in range(3) for v in range(3)])
        self.assertEqual(r['Recovered fields'].fields['remainder'].tolist(), [0]*9)
        back = r['Backprojection']
        receipt = studio.contributors([back.node, back.ids[0]], studio.revision)['measurement']
        self.assertEqual(receipt['contributor_count'], '4')
        self.assertTrue(all(c['reads'] for c in receipt['contributors']))
        line = studio.contributors(receipt['contributors'][0]['reads'][0]['driver'], studio.revision)['measurement']
        self.assertEqual(line['contributor_count'], '3')
        preview = studio.preview_case({'p': '4'}, studio.revision)
        self.assertFalse(preview['errors'])
        studio.commit(preview['token'], studio.revision)
        r = studio.workspace.state.results
        self.assertEqual(r['Recovered fields'].fields['recovered'][0], -1)
        self.assertEqual(r['Recovered fields'].fields['remainder'][0], 0)
        self.assertEqual(r['Image'].values[0], 0)

    def test_loaded_objects_accept_an_ordinary_new_construction_and_save(self):
        studio = opened('07_equal_sums')
        preview = studio.preview(dict(action='lens', name='My sum four', args=dict(
            source='Moving pairs', rule={'op': '=', 'args': [{'field': 'total'}, {'integer': '4'}]})), studio.revision)
        studio.commit(preview['token'], studio.revision)
        self.assertEqual(studio.workspace.state.results['My sum four'].cardinality, 3)
        saved = studio.workspace.to_json()
        with patch('kaleion.evaluate.Evaluator.get', side_effect=AssertionError('execution')):
            studio.reopen(saved, studio.revision)
            self.assertEqual(studio.workspace.state.results['My sum four'].cardinality, 3)


if __name__ == '__main__':
    unittest.main()
