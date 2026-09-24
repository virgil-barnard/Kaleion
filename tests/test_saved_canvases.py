"""Worked canvases open as ordinary editable captures in the existing studio."""

from collections import Counter
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np

from examples.studio.adapter import Studio
from examples.studio.catalog import EXAMPLES, example_text


CANVASES = Path(__file__).resolve().parents[1] / "examples" / "canvases"
LAST_OBJECT = {"02_floor_sums": "Pieces", "05_radon_reconstruction": "Image heights",
               "06_young_layers": "Cells", "07_equal_sums": "Moving pairs",
               "00_first_motion": "Markers", "01_triangle_packing": "Moving cells",
               "04_measured_plane": "Lifted plane"}


def opened(name):
    studio = Studio()
    studio.reopen((CANVASES / (name + ".json")).read_text(), studio.revision)
    return studio


class SavedCanvasTests(unittest.TestCase):
    def test_catalog_opens_only_registered_captures_without_evaluation(self):
        self.assertEqual(len(EXAMPLES), len({e['id'] for e in EXAMPLES}))
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
            for entry in EXAMPLES:
                with self.subTest(example=entry['id']):
                    text = example_text(entry['id'])
                    self.assertEqual(text, (CANVASES / (entry['id'] + '.json')).read_bytes())
                    studio = Studio()
                    studio.reopen(text.decode(), 0)
                    self.assertFalse(studio.workspace.state.errors)
                    if entry['focus'] is not None:
                        self.assertIn(entry['focus'], studio.workspace.state.results)
                    else:
                        self.assertFalse(studio.workspace.state.roots)
        for path in ('../studio/server', '%2e%2e/studio/server', '00_blank.json', 'missing', '00_blank?x'):
            with self.subTest(path=path), self.assertRaises(KeyError):
                example_text(path)

    def test_first_motion_uses_count_keys_and_keeps_labels_separate(self):
        studio = opened('00_first_motion')
        r = studio.workspace.state.results
        self.assertEqual(r['Counts'].values.tolist(), [4, 3, 2, 1, 0])
        self.assertEqual(r['Formula'].values.tolist(), [4, 3, 2, 1, 0])
        self.assertEqual(r['Markers'].values.tolist(), [0]*5)
        np.testing.assert_array_equal(r['Markers'].positions, [[i, 4-i] for i in range(5)])
        marker = r['Markers']
        read = studio.inspect('Markers', [marker.node, marker.ids[2]], studio.revision)['bindings'][0]
        self.assertEqual((read['site'], read['value']), ('y', '2'))
        receipt = studio.contributors(read['driver'], studio.revision)['measurement']
        self.assertEqual(receipt['contributor_count'], '2')
        self.assertEqual([(c['item']['fields']['i'], c['item']['fields']['j'])
                          for c in receipt['contributors']], [('2', '0'), ('2', '1')])
        preview = studio.preview_case({'n': '0'}, studio.revision)
        studio.commit(preview['token'], studio.revision)
        self.assertEqual(studio.workspace.state.results['Counts'].values.tolist(), [0])
        self.assertEqual(studio.workspace.state.results['Formula'].values.tolist(), [0])

    def test_triangle_packing_reuses_ordered_measurements_without_collisions(self):
        studio = opened('01_triangle_packing')
        r = studio.workspace.state.results
        self.assertEqual(r['Row weights'].values.tolist(), [6, 6, 5, 3, 0])
        self.assertEqual(r['Offsets'].values.tolist(), [0, 4, 7, 9, 10])
        self.assertEqual(r['Area'].values.tolist(), [10])
        cells = r['Moving cells']
        self.assertEqual(sorted(cells.positions[:, 0].tolist()), list(range(10)))
        self.assertEqual(cells.positions[:, 1].tolist(), [0]*10)
        offset = r['Offsets']
        receipt = studio.contributors([offset.node, offset.ids[2]], studio.revision)['measurement']
        self.assertEqual([c['weight'] for c in receipt['contributors']], ['4', '3'])

    def test_measured_plane_is_flat_then_exposes_a_shared_column(self):
        studio = opened('04_measured_plane')
        r = studio.workspace.state.results
        self.assertEqual(r['Lifted plane'].values.tolist(), [2]*12)
        np.testing.assert_array_equal(r['Lifted plane'].positions[:, 2], [2]*12)
        for _ in range(3):
            studio.history('undo', studio.revision, 'Lifted plane')
        self.assertEqual(studio.workspace.state.results['Lifted plane'].values.tolist(), [0]*12)
        for _ in range(3):
            studio.history('redo', studio.revision, 'Lifted plane')
        preview = studio.preview_case({'a': '6', 'b': '4', 'c': '5'}, studio.revision)
        studio.commit(preview['token'], studio.revision)
        report = studio.compare('Lifted plane', ['i', 'j'], 'value',
                                'Expected height', ['i', 'j'], 'value',
                                'Footprint', ['i', 'j'], studio.revision)
        different = [row for row in report['rows'] if row['status'] == 'different']
        self.assertEqual([(row['key'], row['left'], row['right'], row['residual'])
                          for row in different], [(['2', '1'], '6', '4', '2')])

    def test_cellwise_comparison_exposes_exact_shared_cell_witnesses(self):
        for name, equal, counted, box in [('03_cell_coverage', True, 24, 24),
                                         ('03_tied_coverage', False, 62, 60)]:
            with self.subTest(canvas=name):
                studio = opened(name)
                saved = studio.workspace.to_json()
                with patch('kaleion.evaluate.Evaluator.get', side_effect=AssertionError('execution')):
                    report = studio.compare('Cell owners', ['i', 'j', 'k'], 'value',
                                            'One per cell', ['i', 'j', 'k'], 'value',
                                            'Box', ['i', 'j', 'k'], studio.revision)
                self.assertEqual(report['passed'], equal)
                self.assertEqual(studio.workspace.to_json(), saved)
                r = studio.workspace.state.results
                self.assertEqual(r['Counted volume'].values.tolist(), [counted])
                self.assertEqual(r['Box volume'].values.tolist(), [box])
                self.assertEqual(r['One per cell'].values.tolist(), [1]*box)
                if not equal:
                    witnesses = [row for row in report['rows'] if row['status'] == 'different']
                    self.assertEqual([(row['key'], row['left'], row['right']) for row in witnesses],
                                     [(['2', '1', '0'], '2', '1'), (['2', '1', '1'], '2', '1')])
                    cell = r['Cell owners']
                    index = next(i for i in range(len(cell)) if int(cell.values[i]) == 2)
                    reads = studio.inspect('Cell owners', [cell.node, cell.ids[index]], studio.revision)['bindings']
                    self.assertEqual([read['value'] for read in reads], ['1', '1', '0'])

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
