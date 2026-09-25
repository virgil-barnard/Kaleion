"""Statement translation checked against independent mathematical constructions."""

import itertools
import json
from math import gcd
import unittest
from unittest.mock import patch

from kaleion import Collection, F, Workspace, param
from examples.quotient_equality import quotient_equality
from examples.save_canvases import cell_coverage
from examples.statements import Expansion, Unsupported
from examples.statements.terms import evaluate, render, literal, term
from examples.studio.adapter import Studio


SPEC = dict(name="Moving cover", left_by=["i", "j"], left_value="value",
            right="Independent ones", right_by=["i", "j"], right_value="value",
            expected="Independent ones", expected_by=["i", "j"])
OPTIONS = dict(vary=["a", "b"], assumptions="a > 1 and b > 1", coprime=[["a", "b"]])


def values(domain, value, parameters):
    sizes = [evaluate(n, parameters) for _, n in domain]
    return [evaluate(value, parameters, dict(zip((v.args[0] for v, _ in domain), key)))
            for key in itertools.product(*(range(n) for n in sizes))]


class ConstructionStatementTests(unittest.TestCase):
    def test_quotient_expansion_respects_keys_and_independent_floor_sums(self):
        workspace = quotient_equality()
        expansion = Expansion(workspace.state.parameters, ["a", "b"])
        domain, cover = expansion.keyed(workspace.state.roots["Moving cover"], ["i", "j"], "value")
        total_domain, total = expansion.keyed(workspace.state.roots["Counted area"], ["key"], "value")
        # One translation is reused at cases other than the captured one.
        for a, b in [(7, 5), (11, 7), (6, 4), (9, 6), (1, 5), (4, 1), (2, 2)]:
            with self.subTest(a=a, b=b):
                parameters = dict(a=a, b=b)
                expected = [1 + int(a*i == b*j) for i in range(1, b) for j in range(1, a)]
                self.assertEqual(values(domain, cover, parameters), expected)
                floor_sum = sum(a*i//b for i in range(1, b)) + sum(b*j//a for j in range(1, a))
                self.assertEqual(values(total_domain, total, parameters), [floor_sum])
                self.assertEqual(floor_sum, (a-1)*(b-1)+gcd(a, b)-1)
        self.assertIn("[", render(cover))
        self.assertIn("Σ", render(total))
        self.assertTrue(expansion.projections)

    def test_same_primitives_expand_three_dimensional_coverage(self):
        workspace = cell_coverage()
        expansion = Expansion(workspace.state.parameters, ["a", "b", "c"])
        domain, owners = expansion.keyed(workspace.state.roots["Cell owners"], ["i", "j", "k"], "value")
        for a, b, c in [(5, 4, 3), (6, 4, 5), (3, 3, 3)]:
            expected = []
            for i, j, k in itertools.product(range(1, a), range(1, b), range(1, c)):
                scaled = [b*c*i, a*c*j, a*b*k]
                expected.append(scaled.count(max(scaled)))
            self.assertEqual(values(domain, owners, dict(a=a, b=b, c=c)), expected)

    def test_native_zero_groups_empty_axes_and_totals_keep_their_domains(self):
        n, m = param("n"), param("m")
        source = Collection.grid(n, m).where(F.i+F.j < 3)
        expansion = Expansion(dict(n=4, m=4), ["n", "m"])
        rows, counts = expansion.keyed(source.count(by=F.i), ["i"], "value")
        total_domain, total = expansion.keyed(source.count(), ["key"], "value")
        for parameters, expected in [(dict(n=4, m=4), [3, 2, 1, 0]), (dict(n=4, m=0), [0]*4), (dict(n=0, m=4), [])]:
            self.assertEqual(values(rows, counts, parameters), expected)
            self.assertEqual(values(total_domain, total, parameters), [sum(expected)])
        # A reduction has retained fields, but no native rectangular axes.
        with self.assertRaisesRegex(Unsupported, "Observed grouping"):
            expansion.compile(source.count(by=F.i).count(by=F.i))

    def test_local_cases_are_simultaneous_and_do_not_share_a_node_only_cache(self):
        n, m, offset = param("n"), param("m"), param("offset")
        shared = Collection.grid(n, values=offset+F.i)
        first = shared.with_params(n=m, offset=n)
        second = shared.with_params(n=m, offset=n+1)
        e = Expansion(dict(n=7, m=2, offset=90), ["n", "m"])
        a, x = e.keyed(first, ["i"], "value")
        b, y = e.keyed(second, ["i"], "value")
        self.assertEqual(values(a, x, dict(n=11, m=3)), [11, 12, 13])
        self.assertEqual(values(b, y, dict(n=11, m=3)), [12, 13, 14])
        d, literal_seven = e.keyed(Collection.grid(1, values=n+7), ["i"], "value")
        self.assertEqual(values(d, literal_seven, dict(n=11)), [18])
        # A parameter spelling never captures the printer's bound coordinates.
        p = param("t")
        d, x = Expansion({"t": 7}, ["t"]).keyed(Collection.grid(p, values=p+F.i), ["i"], "value")
        self.assertEqual(values(d, x, {"t": 2}), [2, 3])

    def test_exact_integers_simultaneous_fields_and_signed_floor_division(self):
        big = 2**100+3
        source = Collection.grid(3, values=big+F.i).annotate(x_=F.value, y_=F.value+1)
        e = Expansion({"d": -2}, ["d"])
        d, x = e.keyed(source.with_values((F.y_-F.x_) + F.value//param("d")), ["i"], "value")
        self.assertEqual(values(d, x, {"d": -2}), [1+(big+i)//-2 for i in range(3)])
        self.assertIn(str(big), json.dumps(x.data()))
        self.assertNotIn(float(big).hex(), json.dumps(x.data()))
        with self.assertRaisesRegex(ValueError, "two integers"):
            term("add", literal(True), literal(1))
        d, x = Expansion({}).keyed(Collection.literal([big, big+1]), ["key"], "value")
        self.assertEqual(values(d, x, {}), [big, big+1])

    def test_divisor_obligations_precede_masks_and_keep_scalar_shape(self):
        d = param("d")
        source = Collection.grid(0).where(False)
        scalar = Expansion({"d": 2}, ["d"])
        scalar.compile(source.sum(value=1//d))
        obligation = [c for c in scalar.conditions if c.reason == "Integer divisor is nonzero"][0]
        self.assertEqual(obligation.dimensions, ())
        self.assertFalse(evaluate(obligation.predicate, {"d": 0}))
        column = Expansion({"d": 2}, ["d"])
        column.compile(source.sum(value=1//(F.i+d)))
        self.assertEqual(len([c for c in column.conditions if c.reason == "Integer divisor is nonzero"][0].dimensions), 1)
        nonempty = Expansion({})
        nonempty.compile(Collection.grid(2).where(False).sum(value=1//F.i))
        c = [c for c in nonempty.conditions if c.reason == "Integer divisor is nonzero"][0]
        self.assertEqual(values(c.dimensions, c.predicate, {}), [False, True])
        modulo = Expansion({"d": 2}, ["d"])
        modulo.compile(Collection.grid(1, values=-7 % d))
        c = [c for c in modulo.conditions if c.reason == "Modulus is a positive integer"][0]
        self.assertFalse(evaluate(c.predicate, {"d": -2}))
        self.assertTrue(evaluate(c.predicate, {"d": 2}))

    def test_scalar_and_keyed_reads_expose_coverage_and_preserve_requirements(self):
        n = param("n")
        driver = Collection.grid(n, values=F.i+10)
        target = Collection.grid(3, values=driver.bind(on=F.i, key=F.i))
        e = Expansion({"n": 3}, ["n"])
        d, x = e.keyed(target, ["i"], "value")
        self.assertEqual(values(d, x, {"n": 3}), [10, 11, 12])
        c = [c for c in e.conditions if c.reason.startswith("Keyed read")][0]
        self.assertEqual(values(c.dimensions, c.predicate, {"n": 2}), [True, True, False])
        # Reduction total has one occurrence, even for an empty input.
        d, x = e.keyed(Collection.grid(2, values=driver.count().scalar()), ["i"], "value")
        self.assertEqual(values(d, x, {"n": 0}), [0, 0])
        checked = driver.require(Collection.grid(1).where(n>1), message="size greater than one")
        e.compile(checked)
        self.assertTrue(any(c.reason == "Recorded requirement: size greater than one" for c in e.conditions))
        arbitrary = Collection.grid(3).annotate(k_=F.i%2)
        with self.assertRaisesRegex(Unsupported, "Keyed expansion"):
            e.compile(Collection.grid(3, values=arbitrary.bind(on=F.i, key=F.k_)))

    def test_unsupported_transforms_geometry_and_observed_domains_do_not_guess(self):
        root = Collection.grid(3)
        for source, reason in [(root.gather([2, 0]), "No sound expansion"),
                               (root.arrange(F.i, 0).with_values(F.x), "geometry is separate"),
                               (root.where(True).count(by=F.value), "Observed grouping")]:
            with self.subTest(reason=reason), self.assertRaisesRegex(Unsupported, reason):
                Expansion({}).compile(source)
        # A small reusable DAG can have an exponentially large printed tree.
        doubled = Collection.grid(1, values=param("n"))
        for _ in range(20):
            doubled = doubled.with_values(F.value+F.value)
        self.assertEqual(doubled.evaluate(n=2).values.tolist(), [2**21])
        with self.assertRaisesRegex(Unsupported, "term budget"):
            Expansion({"n": 2}, ["n"]).keyed(doubled, ["i"], "value")


class StatementAdapterTests(unittest.TestCase):
    def studio(self, a=7, b=5):
        s = Studio()
        s.workspace = quotient_equality(a, b)
        return s

    def test_request_preserves_captures_and_marks_a_countercase_outside_assumptions(self):
        studio = self.studio()
        payload = studio.workspace.to_json()
        with patch("kaleion.evaluate.Evaluator.get", side_effect=AssertionError("execution")):
            report = studio.expand_comparison(SPEC, OPTIONS, 0)
            self.assertEqual(report["status"], "conjecture")
            self.assertEqual(report["proof"], "not-attempted")
            self.assertTrue(report["finite_passed"])
            self.assertTrue(all(h["satisfied"] for h in report["hypotheses"]))
            self.assertEqual(studio.workspace.to_json(), payload)
            studio.reopen(payload, 0)
            reopened = studio.expand_comparison(SPEC, OPTIONS, studio.revision)
            self.assertEqual(report["fingerprint"], reopened["fingerprint"])
            with self.assertRaisesRegex(ValueError, "out of date"):
                studio.expand_comparison(SPEC, OPTIONS, 0)
        false_case = self.studio(6, 4).expand_comparison(SPEC, OPTIONS, 0)
        self.assertFalse(false_case["finite_passed"])
        self.assertFalse(false_case["hypotheses"][-1]["satisfied"])
        self.assertEqual(false_case["proof"], "not-attempted")

    def test_statement_identity_changes_with_intent_and_old_finite_questions_stay_usable(self):
        studio = self.studio()
        original = studio.expand_comparison(SPEC, OPTIONS, 0)
        for options in [{**OPTIONS, "vary": ["a"]}, {**OPTIONS, "coprime": []}, {**OPTIONS, "assumptions": "a > 2"}]:
            report = studio.expand_comparison(SPEC, options, 0)
            self.assertNotEqual(original["fingerprint"], report["fingerprint"])
        fixed_options = dict(vary=[], assumptions="a > 1", coprime=[])
        fixed = studio.expand_comparison(SPEC, fixed_options, 0)
        studio.workspace = Workspace(studio.workspace.state.roots, {"b": 5, "a": 7}, max_items=2000, max_history=40)
        reordered = studio.expand_comparison(SPEC, fixed_options, 0)
        self.assertEqual(fixed["fingerprint"], reordered["fingerprint"])
        studio.workspace.set("Moving cover", studio.workspace.state.roots["Moving cover"].gather(list(reversed(range(24)))))
        report = studio.expand_comparison(SPEC, OPTIONS, 0)
        self.assertTrue(report["finite_passed"])
        self.assertEqual(report["status"], "unsupported")
        self.assertEqual(report["blocker"]["operation"], "gather")
        self.assertNotIn("conclusion", report)

    def test_assumptions_are_restricted_and_never_executed_as_python(self):
        studio = self.studio()
        for options in [{**OPTIONS, "vary": ["absent"]}, {**OPTIONS, "vary": ["a", "a"]},
                        {**OPTIONS, "assumptions": "__import__('os')"},
                        {**OPTIONS, "assumptions": "value > 1"},
                        {**OPTIONS, "coprime": [["a", "absent"]]}, {**OPTIONS, "proof": True}]:
            with self.subTest(options=options), self.assertRaises(ValueError):
                studio.expand_comparison(SPEC, options, 0)
        undefined = studio.expand_comparison(SPEC, {**OPTIONS, "assumptions": "0 * (a // (b-b)) = 0"}, 0)
        self.assertFalse(undefined["hypotheses_defined"])
        self.assertFalse(undefined["obligations"][0]["captured"]["satisfied"])

    def test_matching_zero_fields_do_not_erase_a_missing_expected_key(self):
        n = param("n")
        for size in (0, 3):
            studio = Studio()
            studio.workspace = Workspace({"left": Collection.grid(n, values=0),
                                          "right": Collection.grid(n, values=0),
                                          "domain": Collection.grid(n+1, values=1)}, {"n": size},
                                         max_items=2000, max_history=40)
            spec = dict(name="left", left_by=["i"], left_value="value", right="right", right_by=["i"],
                        right_value="value", expected="domain", expected_by=["i"])
            report = studio.expand_comparison(spec, dict(vary=["n"], assumptions="n >= 0", coprime=[]), 0)
            self.assertFalse(report["finite_passed"])
            self.assertNotEqual(report["conclusion"]["domains"]["left"], report["conclusion"]["domains"]["expected"])
            self.assertIn("dom(L) = {", report["text"])
            self.assertEqual(report["proof"], "not-attempted")


if __name__ == "__main__":
    unittest.main()
