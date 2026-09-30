"""Lean request generation without trusting source generation as a proof."""

from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from examples.lean_request import export, requests
from examples.statements import (Goal, UnsupportedLeanTerm, decode_lean_request,
                                 indicator_order_goal, lean_request)
from examples.statements.terms import Term, literal, term


class LeanRequestTests(unittest.TestCase):
    def test_exact_goal_becomes_a_closed_unproved_proposition(self):
        goal = indicator_order_goal()
        request = lean_request(goal)
        self.assertEqual(request.goal.fingerprint, goal.fingerprint)
        self.assertIn("public abbrev kaleionGoal_", request.source)
        self.assertTrue(request.definition.startswith("KaleionProofs."))
        self.assertIn("namespace KaleionProofs", request.source)
        self.assertIn(": Prop :=", request.source)
        self.assertIn("∀ (p0 p1 : ℤ)", request.source)
        self.assertIn("if (p0 ≤ p1)", request.source)
        for forbidden in ("theorem ", "axiom ", "sorry", "admit"):
            self.assertNotIn(forbidden, request.source.lower())
        self.assertEqual(
            request.source_sha256,
            sha256(request.source.encode("utf-8")).hexdigest(),
        )
        self.assertEqual(decode_lean_request(request.data()), request)

    def test_committed_challenge_is_the_exact_generated_order_goal(self):
        request = lean_request(indicator_order_goal())
        challenge = Path(
            "proofs/lean/KaleionProofs/IndicatorOrderChallenge.lean"
        ).read_text("utf-8")
        self.assertEqual(challenge, request.source)
        self.assertEqual(
            request.definition,
            "KaleionProofs.kaleionGoal_"
            "d86610f8ec97af19ec0140991615020802c3e479d17bf5fc5e43d143a238ebb6",
        )

    def test_committed_proof_cannot_hide_a_new_challenge_or_a_hole(self):
        proof = Path(
            "proofs/lean/KaleionProofs/IndicatorOrderProof.lean"
        ).read_text("utf-8")
        self.assertIn("import KaleionProofs.IndicatorOrderChallenge", proof)
        self.assertIn("kaleionGoal_d86610f8", proof)
        lowered = proof.lower()
        for forbidden in ("def kaleiongoal_", "axiom ", "sorry", "admit"):
            self.assertNotIn(forbidden, lowered)

    def test_lean_toolchain_and_mathlib_dependency_are_locked(self):
        root = Path("proofs/lean")
        toolchain = (root / "lean-toolchain").read_text("utf-8").strip()
        manifest = json.loads((root / "lake-manifest.json").read_text("utf-8"))
        mathlib = next(row for row in manifest["packages"]
                       if row["name"] == "mathlib")
        lakefile = (root / "lakefile.lean").read_text("utf-8")
        self.assertEqual(manifest["name"], "KaleionProofs")
        self.assertIn("package KaleionProofs where", lakefile)
        self.assertEqual(toolchain, "leanprover/lean4:v4.35.0-rc3")
        self.assertEqual(
            mathlib["rev"], "6bd5e549d902323693ddf9128120376848331c85"
        )
        self.assertEqual(mathlib["inputRev"], mathlib["rev"])
        self.assertIn(mathlib["rev"], lakefile)
        self.assertTrue(all(len(row["rev"]) == 40 for row in manifest["packages"]))

    def test_presentation_rename_keeps_exact_source_but_math_edits_do_not(self):
        goal = indicator_order_goal()
        renamed = Goal("new display name", goal.proposition, goal.hypotheses,
                       goal.domain, goal.statement_fingerprint, "new source label")
        changed = Goal(goal.name, term("not", goal.proposition), goal.hypotheses,
                       goal.domain, goal.statement_fingerprint, goal.source)
        self.assertEqual(lean_request(goal).source, lean_request(renamed).source)
        self.assertNotEqual(lean_request(goal).source, lean_request(changed).source)

    def test_names_are_mapped_without_becoming_lean_program_text(self):
        unsafe = "x); axiom injected : False; ("
        parameter = Term("parameter", (unsafe,))
        request = lean_request(Goal("safe mapping", term("eq", parameter, literal(1))))
        self.assertNotIn(unsafe, request.source)
        self.assertEqual(request.parameters, ((unsafe, "p0"),))
        self.assertIn("(p0 = (1 : ℤ))", request.source)

    def test_unsettled_semantics_and_free_coordinates_are_rejected(self):
        n = Term("parameter", ("n",))
        d = Term("parameter", ("d",))
        floor_goal = Goal("floor", term("eq", term("floordiv", n, d), literal(0)))
        with self.assertRaisesRegex(UnsupportedLeanTerm, "floordiv"):
            lean_request(floor_goal)
        free = Term("bound", ("i",))
        with self.assertRaisesRegex(UnsupportedLeanTerm, "explicit goal domain"):
            lean_request(Goal("free coordinate", term("eq", free, literal(0))))

    def test_tampered_manifest_cannot_rebind_a_goal_to_changed_source(self):
        request = lean_request(indicator_order_goal())
        payload = request.data()
        with self.assertRaisesRegex(ValueError, "regenerated source"):
            decode_lean_request({**payload, "source": payload["source"] + "\n"})
        with self.assertRaisesRegex(ValueError, "regenerated source"):
            decode_lean_request({**payload, "statement_fingerprint": "0" * 64})

    def test_real_quotient_requests_export_with_exact_manifests(self):
        emitted = requests()
        self.assertEqual(len(emitted), 3)
        comparison = emitted[-1]
        self.assertIsNotNone(comparison.goal.statement_fingerprint)
        self.assertEqual(dict(comparison.parameters), {"a": "p0", "b": "p1"})
        self.assertEqual(dict(comparison.coordinates), {"k[0]": "x0", "k[1]": "x1"})
        self.assertIn("Int.gcd", comparison.source)
        self.assertIn("if", comparison.source)

        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            manifest = export(directory)
            decoded = json.loads((directory / "manifest.json").read_text("utf-8"))
            self.assertEqual(decoded, manifest)
            self.assertEqual(len(decoded["requests"]), 3)
            for row in decoded["requests"]:
                path = directory / row["filename"]
                self.assertEqual(path.read_text("utf-8"), row["source"])
                request_data = {key: value for key, value in row.items()
                                if key != "filename"}
                self.assertEqual(
                    decode_lean_request(request_data).source_sha256,
                    row["source_sha256"],
                )


if __name__ == "__main__":
    unittest.main()
