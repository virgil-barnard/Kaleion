"""Optional Z3 adapter: explicit goals, exact witnesses, and honest statuses."""

from math import gcd
import subprocess
import sys
import unittest

from examples.proof_assistance import SPEC, run
from examples.quotient_equality import quotient_equality
from examples.statements import (GOAL_SCHEMA, Goal, Z3Assistant, coprime_interior_goal,
                                 goals_from_statement, indicator_order_goal,
                                 named_rule_plan)
from examples.statements.goals import decode_goal, decode_term
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
        self.assertTrue(all(result.goal_fingerprint == goal.fingerprint
                            for goal, result in zip(goals, results.values())))
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

    def test_coprime_statement_uses_named_bezout_rule_for_every_goal(self):
        goals = goals_from_statement(self.statement(coprime=(("a", "b"),)))
        results = [self.assistant.check(goal) for goal in goals]
        self.assertTrue(results)
        self.assertTrue(all(result.status == "solver_valid" for result in results))
        self.assertTrue(all("bezout-coprime/1" in result.rules for result in results))
        comparison = next(result for goal, result in zip(goals, results)
                          if goal.source == "comparison")
        self.assertEqual(comparison.rules,
                         ("bezout-coprime/1", "coprime-interior/1"))

    def test_coprime_interior_lemma_is_solver_valid_but_not_checked_proof(self):
        result = self.assistant.check(coprime_interior_goal())
        self.assertEqual(result.status, "solver_valid")
        self.assertEqual(result.rules,
                         ("bezout-coprime/1", "coprime-interior/1"))
        self.assertNotEqual(result.status, "checked_proof")

    def test_named_rule_plan_is_backend_neutral_and_readable(self):
        goal = coprime_interior_goal()
        steps = named_rule_plan(goal.hypotheses, goal.domain)
        self.assertEqual([step.rule for step in steps],
                         ["bezout-coprime/1", "coprime-interior/1"])
        self.assertEqual(steps[0].witnesses, ("u", "v"))
        self.assertIn("Choose u and v in ℤ", steps[0].statement)
        self.assertEqual(steps[1].uses, ("bezout-coprime/1",))
        self.assertIn("≠", steps[1].statement)
        result = self.assistant.check(goal)
        self.assertEqual(result.rule_steps, steps)
        payload = result.data()
        self.assertEqual([step["rule"] for step in payload["rule_steps"]],
                         ["bezout-coprime/1", "coprime-interior/1"])
        self.assertIn("conclusion", payload["rule_steps"][0])

    def test_goal_fingerprint_tracks_theorem_semantics_not_its_display_label(self):
        goal = indicator_order_goal()
        renamed = Goal("a different explanation", goal.proposition,
                       goal.hypotheses, goal.domain,
                       goal.statement_fingerprint, "different presentation source")
        changed = Goal(goal.name, term("not", goal.proposition),
                       goal.hypotheses, goal.domain,
                       goal.statement_fingerprint, goal.source)
        self.assertEqual(goal.fingerprint, renamed.fingerprint)
        self.assertNotEqual(goal.fingerprint, changed.fingerprint)
        self.assertEqual(len(goal.fingerprint), 64)
        payload = goal.data()
        self.assertEqual(payload["schema"], GOAL_SCHEMA)
        self.assertEqual(payload["goal_fingerprint"], goal.fingerprint)
        self.assertEqual(decode_goal(payload), goal)
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            decode_goal({**payload, "proposition": changed.proposition.data()})
        # Presentation is intentionally outside request identity.
        self.assertEqual(decode_goal({**payload, "name": "renamed"}).fingerprint,
                         goal.fingerprint)
        self.assertEqual(self.assistant.check(goal).goal_fingerprint,
                         goal.fingerprint)

    def test_report_pairs_every_attempt_with_the_exact_theorem_request(self):
        report = run()
        self.assertEqual(len(report["attempts"]), 18)
        for row in report["attempts"]:
            request = decode_goal(row["request"])
            self.assertEqual(request.fingerprint, row["goal_fingerprint"])
            self.assertEqual(request.statement_fingerprint,
                             row["statement_fingerprint"])

    def test_bezout_rule_matches_neutral_gcd_for_signed_and_zero_cases(self):
        a, b = Term("parameter", ("a",)), Term("parameter", ("b",))
        coprime = term("eq", term("gcd", a, b), literal(1))
        for left, right in ((7, 5), (-7, 5), (0, 1), (0, -1),
                            (6, 4), (0, 0)):
            goal = Goal(
                f"gcd case {left},{right}", Term("literal", (True,), "boolean"),
                (term("eq", a, literal(left)), term("eq", b, literal(right)),
                 coprime),
            )
            result = self.assistant.check(goal)
            expected = ("solver_valid" if gcd(left, right) == 1
                        else "inconsistent_assumptions")
            with self.subTest(left=left, right=right):
                self.assertEqual(result.status, expected)
                self.assertEqual(result.rules, ("bezout-coprime/1",))

    def test_general_gcd_claim_remains_unsupported(self):
        a, b = Term("parameter", ("a",)), Term("parameter", ("b",))
        proposition = term("eq", term("gcd", a, b), literal(2))
        result = self.assistant.check(Goal("general gcd", proposition))
        self.assertEqual(result.status, "unsupported")
        self.assertIn("gcd", result.reason)

    def test_coprime_interior_rule_does_not_cover_the_rectangle_boundary(self):
        a, b = Term("parameter", ("a",)), Term("parameter", ("b",))
        i, j = Term("bound", ("i",)), Term("bound", ("j",))
        one = literal(1)
        goal = Goal(
            "closed rectangle includes the common corner",
            term("ne", term("mul", a, term("add", i, one)),
                 term("mul", b, term("add", j, one))),
            (term("gt", a, one), term("gt", b, one),
             term("eq", term("gcd", a, b), one)),
            ((i, b), (j, a)),
        )
        result = self.assistant.check(goal)
        self.assertEqual(result.status, "counterexample")
        self.assertTrue(result.independently_reproduced)
        self.assertEqual(result.rules, ("bezout-coprime/1",))
        self.assertEqual([step.rule for step in result.rule_steps],
                         ["bezout-coprime/1"])

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
        neutral_probe = subprocess.run(
            [sys.executable, "-c",
             "import sys; import examples.statements.rules; assert 'z3' not in sys.modules"],
            check=False, capture_output=True, text=True,
        )
        self.assertEqual(neutral_probe.returncode, 0, neutral_probe.stderr)


if __name__ == "__main__":
    unittest.main()
