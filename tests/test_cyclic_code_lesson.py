"""Independent binary arithmetic checks for the actual lesson 11 definitions.

Only tagged construction cells are loaded. No Plotly or notebook kernel is needed.
"""

from collections import Counter
from functools import reduce
from itertools import combinations, product
import json
from operator import xor
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np

from kaleion import F, Motion, Workspace


ROOT = Path(__file__).resolve().parents[1]
LESSON = {}
for cell in json.loads((ROOT / "notebooks/11_cyclic_code_plane.ipynb").read_text())["cells"]:
    if "kaleion-construction" in cell.get("metadata", {}).get("tags", []):
        exec(compile("".join(cell["source"]), "11_cyclic_code_plane.ipynb", "exec"), LESSON)


def multiply(a, b):
    """Carryless schoolbook product, using bitwise arithmetic as an oracle."""
    value = 0
    while b:
        if b & 1:
            value ^= a
        a <<= 1
        b >>= 1
    return value


def divide(value, divisor):
    quotient = 0
    while value and value.bit_length() >= divisor.bit_length():
        shift = value.bit_length() - divisor.bit_length()
        quotient ^= 1 << shift
        value ^= divisor << shift
    return quotient, value


def word_span(generator, dimension):
    return [reduce(xor, (generator << j for j in range(dimension) if m & (1 << j)), 0)
            for m in range(2**dimension)]


def model(generator=11):
    polynomial = LESSON["coefficients"](generator)
    copies, G = LESSON["generator_rows"](polynomial, 4)
    _, quotient, reciprocal = LESSON["dual_polynomial"](polynomial)
    _, H = LESSON["generator_rows"](reciprocal, 3)
    code = LESSON["span"](G, 4)
    dual = LESSON["span"](H, 3)
    geometry = LESSON["fano_supports"](code, H)
    return polynomial, copies, G, H, quotient, reciprocal, code, dual, geometry


class CyclicCodeLesson(unittest.TestCase):
    def test_polynomial_rows_spans_and_reciprocal_match_independent_oracles(self):
        for generator in (11, 13):
            with self.subTest(generator=generator):
                _, _, G, H, quotient, reciprocal, code, dual, _ = model(generator)
                state = Workspace({"G": G, "H": H, "q": quotient, "reciprocal": reciprocal,
                                   "code": code["words"], "dual": dual["words"]}).state
                self.assertFalse(state.errors)
                q, remainder = divide(129, generator)
                self.assertEqual(remainder, 0)
                dual_generator = int(f"{q:05b}"[::-1], 2)
                self.assertEqual(state.results["q"].values.tolist(), [q])
                self.assertEqual(len(state.results["q"].contributor_ids(())), 1)
                self.assertEqual(state.results["reciprocal"].values.tolist(),
                                 [(dual_generator >> j) & 1 for j in range(7)])
                for name, stencil, dimension in (("G", generator, 4), ("H", dual_generator, 3)):
                    matrix = state.results[name]
                    by_key = {(int(r), int(j)): int(v) for r, j, v in zip(
                        matrix.fields["row"], matrix.fields["degree"], matrix.values)}
                    self.assertEqual(by_key, {(r, j): ((stencil << r) >> j) & 1
                                              for r in range(dimension) for j in range(7)})
                self.assertEqual(state.results["code"].values.tolist(), word_span(generator, 4))
                self.assertEqual(state.results["dual"].values.tolist(), word_span(dual_generator, 3))
                for name in ("code", "dual"):
                    words = set(map(int, state.results[name].values))
                    self.assertTrue(all((((w << 1) & 127) | (w >> 6)) in words for w in words))

    def test_zero_and_cancelled_contributors_survive_and_bindings_ignore_storage_order(self):
        _, _, G, H, _, _, code, _, _ = model()
        reordered = LESSON["span"](G.order_by(-F.seed).order_by(-F.row), 4)
        state = Workspace({**code, "reordered": reordered["words"]}).state
        self.assertFalse(state.errors)
        r = state.results
        self.assertEqual(r["words"].values.tolist(), r["reordered"].values.tolist())
        for m, j, count in zip(r["overlaps"].fields["message"],
                                r["overlaps"].fields["degree"], r["overlaps"].values):
            expected = {oid for oid, message, row, degree, term in zip(
                r["terms"].ids, r["terms"].fields["message"], r["terms"].fields["row"],
                r["terms"].fields["degree"], r["terms"].values)
                if message == m and degree == j and (int(m) & (1 << int(row)))
                and ((11 << int(row)) >> int(j)) & 1}
            self.assertEqual(set(r["overlaps"].contributor_ids((m, j))), expected)
            self.assertEqual(count, len(expected))
        self.assertEqual(r["overlaps"].contributor_ids((0, 0)), ())
        self.assertEqual(len(r["overlaps"].contributor_ids((5, 3))), 2)
        self.assertEqual(r["bits"].values[5*7+3], 0)
        with self.assertRaises(ValueError):
            r["bits"].contributor_ids((5, 3))  # parity no longer claims to be a cardinality
        changed_code = {**code, "words": code["words"].order_by(-F.message),
                        "weights": code["weights"].order_by(-F.message)}
        geometry = LESSON["fano_supports"](changed_code, H.order_by(-F.degree))
        supports = geometry["supports"].evaluate()
        for word, degree, value in zip(supports.fields["word"], supports.fields["degree"], supports.values):
            self.assertEqual(value, (int(word) >> int(degree)) & 1)
        ranks = geometry["ranks"].evaluate()
        expected_words = sorted(w for w in word_span(11, 4) if w.bit_count() == 3)
        self.assertEqual(dict(zip(ranks.fields["word"], ranks.values)),
                         {word: rank for rank, word in enumerate(expected_words)})

    def test_entire_kernels_fano_pairs_and_dual_complements(self):
        for generator in (11, 13):
            _, _, G, H, _, _, code, dual, geometry = model(generator)
            q = divide(129, generator)[0]
            h = int(f"{q:05b}"[::-1], 2)
            for matrix, dimension, stencil, expected in (
                (G, 4, generator, set(word_span(h, 3))),
                (H, 3, h, set(word_span(generator, 4))),
            ):
                checks = LESSON["parity_checks"](matrix, dimension)
                state = Workspace(checks).state
                self.assertFalse(state.errors)
                self.assertEqual(set(state.results["kernel"].values), expected)
                actual = dict(zip(state.results["syndromes"].fields["word"],
                                  state.results["syndromes"].values))
                self.assertEqual(actual, {w: sum(((w & (stencil << r)).bit_count() % 2) << r
                                                 for r in range(dimension)) for w in range(128)})
            cross = LESSON["cross_parities"](G, H, 4, 3)[1].evaluate()
            self.assertFalse(any(cross.values))
            state = Workspace(geometry).state
            self.assertFalse(state.errors)
            self.assertEqual(set(state.results["columns"].values), set(range(1, 8)))
            lines = set(map(int, state.results["lines"].values))
            self.assertEqual(lines, {w for w in word_span(generator, 4) if w.bit_count() == 3})
            pairs = Counter(pair for w in lines for pair in combinations(
                [j for j in range(7) if w & (1 << j)], 2))
            self.assertEqual(pairs, {pair: 1 for pair in combinations(range(7), 2)})
            self.assertEqual({127-w for w in lines}, set(word_span(h, 3)) - {0})

    def test_field_products_trace_and_incidence_isomorphism_for_both_cubics(self):
        for generator in (11, 13):
            polynomial, _, _, _, _, _, _, _, geometry = model(generator)
            definitions = LESSON["field_model"](polynomial, geometry["columns"].order_by(-F.degree))
            state = Workspace(definitions).state
            self.assertFalse(state.errors)
            r = state.results
            mult = lambda x, y: divide(multiply(x, y), generator)[1]
            expected_products = [mult(x, y) for x, y in product(range(8), repeat=2)]
            self.assertEqual(r["multiply"].values.tolist(), expected_products)
            self.assertEqual(r["inverses"].values.tolist(), [1]*7)
            powers = [1]
            for _ in range(7):
                powers.append(mult(powers[-1], 2))
            self.assertEqual(r["powers"].values.tolist(), powers)
            self.assertEqual(powers[-1], 1)
            self.assertEqual(set(powers[:-1]), set(range(1, 8)))
            trace = [x ^ mult(x, x) ^ mult(mult(x, x), mult(x, x)) for x in range(8)]
            self.assertEqual(r["trace"].values.tolist(), trace)
            coordinate = {0: 0, **dict(zip(map(int, r["atlas"].values),
                                           map(int, r["atlas"].fields["vector"])))}
            self.assertEqual(set(coordinate.values()), set(range(8)))
            for x, y in product(range(8), repeat=2):
                self.assertEqual(coordinate[x ^ y], coordinate[x] ^ coordinate[y])
            expected = [[trace[mult(normal, z)] == 0 for z in powers[:-1]] for normal in powers[:-1]]
            np.testing.assert_array_equal(r["incidence"].mask.reshape(7, 7), expected)
            self.assertEqual(set(r["lines"].values), {w for w in word_span(generator, 4) if w.bit_count() == 3})
            self.assertEqual(set(r["dual_words"].values), {127-int(w) for w in r["lines"].values})
            for normal, row in zip(powers[:-1], expected):
                triple = [z for z, selected in zip(powers[:-1], row) if selected]
                self.assertEqual(len(triple), 3)
                self.assertEqual(reduce(xor, triple), 0)
                moved = {mult(z, 2) for z in triple}
                self.assertIn(moved, [{z for z in powers[:-1] if trace[mult(a, z)] == 0}
                                     for a in powers[:-1]])

    def test_one_error_rule_all_words_and_two_error_limit(self):
        for generator in (11, 13):
            _, _, _, H, _, _, _, _, _ = model(generator)
            syndromes = LESSON["parity_checks"](H, 3)["syndromes"]
            decoder = LESSON["single_error_rule"](syndromes.order_by(-F.word))
            state = Workspace({**decoder, "syndromes": syndromes}).state
            self.assertFalse(state.errors)
            r = state.results
            self.assertEqual(r["coverage"].values.tolist(), [1]*8)
            syndrome = dict(zip(map(int, r["syndromes"].fields["word"]), map(int, r["syndromes"].values)))
            correction = dict(zip(map(int, r["correction"].fields["syndrome"]), map(int, r["correction"].values)))
            self.assertEqual(correction[0], 0)
            self.assertEqual(len(r["correction"].contributor_ids(0)), 1)
            words = set(word_span(generator, 4))
            for word in words:
                for error in [0] + [1 << j for j in range(7)]:
                    received = word ^ error
                    self.assertEqual(received ^ correction[syndrome[received]], word)
                for j, k in combinations(range(7), 2):
                    received = word ^ (1 << j) ^ (1 << k)
                    decoded = received ^ correction[syndrome[received]]
                    self.assertIn(decoded, words)
                    self.assertNotEqual(decoded, word)

    def test_failed_factor_and_inverse_checks_leave_independent_results_available(self):
        polynomial, _, G, H, quotient, _, _, _, geometry = model()
        _, wrong_H = LESSON["generator_rows"](LESSON["coefficients"](quotient.scalar()), 3)
        wrong = LESSON["cross_parities"](G, wrong_H, 4, 3)[1].evaluate()
        self.assertEqual(wrong.values[2], 1)  # G row 0, wrong H row 2.
        bad = LESSON["coefficients"](15)
        _, bad_G = LESSON["generator_rows"](bad, 4)
        bad_words = LESSON["span"](bad_G, 4)["words"]
        bad_quotient = LESSON["dual_polynomial"](bad)[1]
        state = Workspace({"words": bad_words, "quotient": bad_quotient}).state
        self.assertEqual(set(state.errors), {"quotient"})
        self.assertIn(68, state.results["words"].values)
        self.assertNotIn(9, state.results["words"].values)
        broken = LESSON["field_model"](LESSON["coefficients"](9), geometry["columns"])
        field = Workspace(broken).state
        self.assertIn("multiply", field.errors)
        self.assertIn("powers", field.errors)
        self.assertIn(0, field.results["inverses"].values)

    def test_captured_generator_and_singer_motion_reverse_without_evaluation(self):
        polynomial, copies, G, _, _, _, _, _, geometry = model()
        start, turned, matrix = LESSON["generator_placements"](copies, G)
        workspace = Workspace({"coefficients": start.where(F.value == 1)})
        turn = workspace.set("coefficients", turned.where(F.value == 1), motion=LESSON["generator_turn"]())
        flatten = workspace.set("coefficients", matrix.where(F.value == 1),
                                motion=Motion.arc(height=1.3, axis=2, dimension=3))
        self.assertEqual(turn.start.results["coefficients"].source.ids,
                         flatten.end.results["coefficients"].source.ids)
        self.assertEqual(sum(flatten.frame("coefficients", 1).matched_after), 12)
        workspace.undo()
        payload = workspace.to_json()
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("unexpected evaluation")):
            replayed = Workspace.from_json(payload).redo()
            np.testing.assert_array_equal(replayed.frame("coefficients", .25).positions,
                                           flatten.reverse().frame("coefficients", .75).positions)
        field = LESSON["field_model"](polynomial, geometry["columns"])
        points = field["atlas"].annotate(seed_trace=field["trace"].bind(on=F.value))
        chart = LESSON["fano_chart"]()
        ring, _ = LESSON["field_placements"](points, chart)
        workspace = Workspace({"ring": ring.where(F.seed_trace == 0)})
        seed = workspace.state.results["ring"].source
        for _ in range(7):
            points = LESSON["multiply_by_alpha"](points, field)
            ring, _ = LESSON["field_placements"](points, chart)
            transition = workspace.set("ring", ring.where(F.seed_trace == 0), motion=LESSON["support_turn"]())
            self.assertEqual(sum(transition.frame("ring", 1).matched_after), 3)
        end = workspace.state.results["ring"].source
        self.assertEqual(end.ids, seed.ids)
        np.testing.assert_array_equal(end.values, seed.values)
        np.testing.assert_array_equal(end.positions, seed.positions)
        workspace.undo()
        payload = workspace.to_json()
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("unexpected evaluation")):
            reopened = Workspace.from_json(payload)
            replayed = reopened.redo()
            for t in (0, .25, .5, .75, 1):
                np.testing.assert_array_equal(replayed.frame("ring", t).positions,
                                               transition.reverse().frame("ring", 1-t).positions)
            self.assertTrue(reopened.can_undo)


if __name__ == "__main__":
    unittest.main()
