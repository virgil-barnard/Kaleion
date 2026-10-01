# Kaleion Lean challenges

This directory is a separate checked-proof experiment. It is not imported by the
Python package, evaluator, canvas, or saved workspace format.

The first challenge deliberately has two files:

- `IndicatorOrderChallenge.lean` is generated from Kaleion goal
  `d86610f8ec97af19ec0140991615020802c3e479d17bf5fc5e43d143a238ebb6`.
  Its source SHA-256 is
  `23aa0bfc6d8615613f671b7a3ef40212811dbf2f35d299a49365a70ce86f1491`.
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

The repository workflow adds an axiom audit scoped to `KaleionProofs` and
LeanChecker beyond an ordinary build. Nano-Do is not currently a gate because its
0.3.2 parser rejects Lean 4.28+ exporter streams (lean-action issue 169); it must be
re-enabled without `sorry` once compatible. No proof status is currently written
into a Kaleion workspace. A CI pass supports the exact committed proposition under
the pinned toolchain; it does not elevate finite evidence, Z3 results, other
exported requests, or the translation layer to checked proofs.
