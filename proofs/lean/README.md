# Kaleion Lean challenges

This directory is a separate checked-proof experiment. It is not imported by the
Python package, evaluator, canvas, or saved workspace format.

The first challenge deliberately has two files:

- `IndicatorOrderChallenge.lean` is generated from Kaleion goal
  `d86610f8ec97af19ec0140991615020802c3e479d17bf5fc5e43d143a238ebb6`.
  Its source SHA-256 is
  `f6a1b7f6d504ff46abe36e5e052fb1f97ac9f1381e9b3491316365b29d1e9e66`.
- `IndicatorOrderProof.lean` imports that challenge and proves its named closed
  proposition. It must not restate the generated definition.

`tests/test_lean_requests.py` regenerates the challenge from the strict Kaleion
request and requires exact source equality. That test protects correspondence to
the current translator; it does not prove that the translator is mathematically
sound.

The project pins Lean through `lean-toolchain` and locks Mathlib plus every
transitive package revision in `lake-manifest.json`. With Lean's `lake` available,
run:

```sh
cd proofs/lean
lake build --wfail
```

The repository workflow adds three checks beyond an ordinary build: an axiom
audit scoped to `KaleionProofs`, LeanChecker, and Nano-Do with sorry disallowed.
No proof status is currently written into a Kaleion workspace. A CI pass supports
the exact committed proposition under the pinned toolchain; it does not elevate
finite evidence, Z3 results, other exported requests, or the translation layer to
checked proofs.
