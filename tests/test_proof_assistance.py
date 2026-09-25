"""Optional Z3 adapter: explicit goals, exact witnesses, and honest statuses."""

import subprocess
import sys
import unittest

from examples.proof_assistance import SPEC
from examples.quotient_equality import quotient_equality
from examples.statements import Goal, Z3Assistant, goals_from_statement, indicator_order_goal
from examples.statements.solver import decode_term
from examples.statements.terms import Term, literal, term
from examples.studio.statements import comparison_statement


class ProofAssistanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.assistant = Z3Assistant()
        except RuntimeError as error:
            raise unittest.SkipTest(str(error)) from error

    def statement(self, *, coprime=()):
        workspace = quotient_equality()
        return comparison_statement(
            workspace.state.roots, workspace.state.parameters, SPEC,
            {"vary": ["a", "b"], "assumptions": "a > 1 and b > 1",
             "coprime": [list(pair) for pair in coprime]},
        )

    def test_order_indicator_lemma_is_solver_valid_for_all_integers(self):
        result = self.assistant.check(indicator_order_goal())
        self.assertEqual(result.status, "solver_valid")
        self.assertNotEqual(result.status, "checked_proof")
        self.assertEqual(result.assignments, ())

    def test_false_indicator_variant_returns_an_exact_replayed_witness(self):
        x, y = Term("parameter", ("x",)), Term("parameter", ("y",))
        false = term("eq", term("add", term("indicator", term("le", x, y)),
                                term("indicator", term("le", y, x))), literal(1))
        result = self.assistant.check(Goal("false strict partition", false))
        self.assertEqual(result.status, "counterexample")
        self.assertTrue(result.independently_reproduced)
        values = {(kind, name): int(value) for kind, name, value in result.assignments}
        self.assertEqual(values[("parameter", "x")], values[("parameter", "y")])

    def test_inconsistent_assumptions_never_produce_a_vacuous_valid_badge(self):
        n = Term("parameter", ("n",))
        result = self.assistant.check(Goal(
            "inconsistent", term("eq", n, literal(0)),
            (term("lt", n, literal(0)), term("gt", n, literal(0))),
        ))
        self.assertEqual(result.status, "inconsistent_assumptions")

    def test_actual_quotient_statement_separates_coverage_obligations_and_equality(self):
        report = self.statement()
        goals = goals_from_statement(report)
        results = {goal.name: self.assistant.check(goal) for goal in goals}
        self.assertTrue(all(result.statement_fingerprint == report["fingerprint"]
                            for result in results.values()))
        self.assertEqual(results["left key domain equals expected domain"].status,
                         "solver_valid")
        keyed = [result for name, result in results.items()
                 if name.startswith("obligation") and "Keyed read" in name]
        self.assertTrue(keyed)
        self.assertTrue(all(result.status == "solver_valid" for result in keyed))
        equality = results["compared integer fields are equal"]
        self.assertEqual(equality.status, "counterexample")
        self.assertTrue(equality.independently_reproduced)
        values = {(kind, name): int(value) for kind, name, value in equality.assignments}
        self.assertGreater(values[("parameter", "a")], 1)
        self.assertGreater(values[("parameter", "b")], 1)

    def test_coprime_goal_is_explicitly_unsupported_until_gcd_has_a_sound_encoding(self):
        goals = goals_from_statement(self.statement(coprime=(("a", "b"),)))
        results = [self.assistant.check(goal) for goal in goals]
        self.assertTrue(results)
        self.assertTrue(all(result.status == "unsupported" for result in results))
        self.assertTrue(all("gcd" in result.reason for result in results))

    def test_floor_sum_translation_stops_before_backend_division_semantics_can_change(self):
        n, d = Term("parameter", ("n",)), Term("parameter", ("d",))
        quotient = term("floordiv", n, d)
        result = self.assistant.check(Goal(
            "floor division", term("eq", quotient, literal(0)),
            (term("ne", d, literal(0)),),
        ))
        self.assertEqual(result.status, "unsupported")
        self.assertIn("floordiv", result.reason)

    def test_wire_decoder_rejects_changed_sorts_code_and_unbounded_payloads(self):
        valid = term("eq", Term("parameter", ("n",)), literal(2)).data()
        self.assertEqual(decode_term(valid), term("eq", Term("parameter", ("n",)), literal(2)))
        invalid = [
            {**valid, "extra": True},
            {**valid, "sort": "integer"},
            {"op": "literal", "sort": "integer", "args": [2]},
            {"op": "parameter", "sort": "integer", "args": ["x" * 81]},
            {"op": "table", "sort": "integer",
             "args": [["1" * 1236], Term("parameter", ("n",)).data()]},
            {"op": "__import__", "sort": "integer", "args": []},
        ]
        for data in invalid:
            with self.subTest(data=data), self.assertRaises(ValueError):
                decode_term(data)

    def test_timeout_and_input_budgets_are_explicit(self):
        for timeout in (0, 60_001, True, 1.5):
            with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                self.assistant.check(indicator_order_goal(), timeout_ms=timeout)

    def test_statement_wire_identity_and_sections_are_validated(self):
        report = self.statement()
        for changed in (
            {**report, "fingerprint": "x" * 64},
            {**report, "hypotheses": {}},
            {**report, "obligations": {}},
            {**report, "conclusion": {}},
        ):
            with self.subTest(keys=changed.keys()), self.assertRaises(ValueError):
                goals_from_statement(changed)

    def test_ordinary_statement_import_does_not_load_the_optional_backend(self):
        probe = subprocess.run(
            [sys.executable, "-c",
             "import sys; import examples.statements; assert 'z3' not in sys.modules"],
            check=False, capture_output=True, text=True,
        )
        self.assertEqual(probe.returncode, 0, probe.stderr)


if __name__ == "__main__":
    unittest.main()
