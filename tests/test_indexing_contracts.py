"""Independent coordinate oracles for the shared rectangular address rules."""

from itertools import product
import unittest

import numpy as np

from kaleion import Collection, EvaluationError, Evaluator, F, param


class IndexingContracts(unittest.TestCase):
    def test_roll_on_every_axis_with_large_signed_fiber_shifts(self):
        shape = (2, 3, 4)
        coordinates = list(product(*(range(n) for n in shape)))
        source = Collection.grid(*shape, values=100 * F.i + 10 * F.j + F.k).arrange(F.i, F.j, F.k)
        for dimension, axis in enumerate("ijk"):
            other_axes = [i for i in range(3) if i != dimension]
            shift = param("large") + F["ijk"[other_axes[0]]] - 2 * F["ijk"[other_axes[1]]]
            rolled = source.roll(axis=axis, shift=shift)
            for large in (2**100, -(2**100)):
                with self.subTest(axis=axis, large=large):
                    engine = Evaluator({"large": large})
                    original, result = engine.get(source.node), engine.get(rolled.node)
                    by_coordinate = dict(zip(coordinates, original.ids))
                    expected_values, expected_ids = [], []
                    for target in coordinates:
                        origin = list(target)
                        distance = large + target[other_axes[0]] - 2 * target[other_axes[1]]
                        origin[dimension] = (target[dimension] - distance) % shape[dimension]
                        expected_values.append(100 * origin[0] + 10 * origin[1] + origin[2])
                        expected_ids.append(by_coordinate[tuple(origin)])
                    self.assertEqual(result.values.tolist(), expected_values)
                    self.assertEqual(result.ids, tuple(expected_ids))
                    self.assertTrue(np.shares_memory(original.positions, result.positions))
                    np.testing.assert_array_equal(result.positions, coordinates)
                    for name in "ijk":
                        np.testing.assert_array_equal(result.fields[name], original.fields[name])
            with self.assertRaisesRegex(EvaluationError, "constant along each shifted fiber"):
                source.roll(axis=axis, shift=F[axis]).evaluate()

    def test_gather_tile_and_concat_keep_their_distinct_item_policy(self):
        shape = (2, 3, 4)
        source = Collection.grid(*shape, values=100 * F.i + 10 * F.j + F.k).arrange(F.i, F.j, F.k)
        for dimension, axis in enumerate("ijk"):
            addresses = [shape[dimension] - 1, 0, shape[dimension] - 1]
            constructions = {
                "gather": source.gather(addresses, axis=axis),
                "tile": source.tile(2, axis=axis),
                "concat": source.concat(source.with_values(F.value + 1000), axis=axis),
            }
            for name, construction in constructions.items():
                with self.subTest(operation=name, axis=axis):
                    result = construction.evaluate()
                    destination = list(shape)
                    destination[dimension] = len(addresses) if name == "gather" else 2 * shape[dimension]
                    expected = []
                    for point in product(*(range(n) for n in destination)):
                        origin = list(point)
                        origin[dimension] = (addresses[point[dimension]] if name == "gather"
                                             else point[dimension] % shape[dimension])
                        value = 100 * origin[0] + 10 * origin[1] + origin[2]
                        if name == "concat" and point[dimension] >= shape[dimension]:
                            value += 1000
                        expected.append(value)
                    self.assertEqual(result.values.tolist(), expected)
                    self.assertEqual(result.shape, tuple(destination))
                    self.assertEqual(len(set(result.ids)), len(result))
                    self.assertTrue(set(result.ids).isdisjoint(source.evaluate().ids))
                    self.assertIsNone(result.positions)
        small = Collection.grid(2, 2)
        with self.assertRaisesRegex(EvaluationError, "item budget"):
            Evaluator(max_items=4).get(small.gather([1, 0, 1], axis="i").node)


if __name__ == "__main__":
    unittest.main()
