# Proof assistance for Kaleion

Research checked September 25, 2026 · Recommendation, not installed integrations

Keep the user-facing statement and orchestration Pythonic. Use separate adapters
for algebraic manipulation, counterexample search, and checked mathematical
proofs. No single package currently meets all three needs equally well. The new
[construction expansion](ALGEBRAIC_STATEMENTS.md) supplies typed integer terms,
bounded sums, domains, assumptions and source identities without committing the
canvas or evaluator to a solver's expression classes.

## Candidates and their roles

| Candidate | Useful role in Kaleion | Boundary to preserve |
| --- | --- | --- |
| [SymPy](https://docs.sympy.org/latest/modules/assumptions/refine.html) | Python-native symbolic expressions, algebraic presentation, assumption-aware rewrites through `refine`; good for suggesting a more recognizable formula | A simplified expression or `True` is not by itself a portable, independently checked theorem certificate. Record a proposed rewrite and its required conditions. Unknown Boolean expressions can remain unresolved. |
| [Z3 / Z3Py](https://z3prover.github.io/papers/programmingz3.html) | First candidate for bounded counterexample search, implication checks and small arithmetic obligations; direct Python interface, models and solver tactics | `sat`, `unsat`, `unknown` and resource exhaustion need different statuses. Quantifiers and nonlinear integer arithmetic will require guidance or fail to terminate; do not expect one call to prove arbitrary parameterized sums or number theory. |
| [Lean 4](https://lean-lang.org/faq/) with [mathlib](https://github.com/leanprover-community/mathlib4) | Preferred long-term target for reusable mathematical lemmas and durable checked proofs; broad library across algebra, number theory, combinatorics and geometry | Python can orchestrate translation and proof attempts, but Lean's proof language and toolchain are separate. Its kernel checks proof terms; the translator's fidelity to Kaleion is a further obligation. Record permitted axioms and dependencies. |
| [Knuckledragger](https://github.com/philzook58/knuckledragger) | Particularly interesting Python-first experiment: proof combinators, definitions and induction built around Z3 terms, with ordinary Python/Jupyter integration | Its documented trust model is larger than Lean/Rocq's, with ATP calls in the trusted reasoning chain. Evaluate it as an optional research adapter; do not present its results as Lean-kernel certificates. |

My recommendation is **Z3Py first for finding and explaining failures, Lean/mathlib
for the durable proof path**, with SymPy as an optional algebra assistant.
Knuckledragger deserves a focused comparison because it fits the desired Python
authoring style unusually well. Do not add all four as runtime dependencies now.
This is an architectural judgment based on the documented capabilities, not a
benchmark of these systems on Kaleion problems.

Primary documentation supports the distinctions: SymPy documents assumption-
dependent refinement; Programming Z3 describes its Python interface and solver
procedures; Lean describes proof terms checked by a small kernel; Knuckledragger
explicitly describes its Z3-based logic and trust boundary. For Lean checking,
follow the [reference manual's proof-validation guidance](https://lean-lang.org/doc/reference/latest/ValidatingProofs/).
Do not infer security or proof integrity from an exit code alone.

## What the first assistance must do

1. **Check whether the proposed assumptions describe any admissible case.** An
   inconsistent hypothesis can make an implication vacuous. A timeout on this
   check is not confirmation of consistency.
2. **Separate definition obligations from the desired equality.** Nonnegative
   ranges, nonzero divisors, positive moduli, singleton scalar reads, and complete
   unique key alignment must follow from the author hypotheses. Never silently
   assume them to make a solver succeed.
3. **Search for a finite witness with explicit bounds.** A model should supply
   parameters and a key that the ordinary Kaleion evaluator can independently
   reconstruct. Preserve the failed comparison and contributors. No witness
   found within bounds means only that the bounded search found none.
4. **Offer small, named proof steps.** Expand an indicator, split cases, substitute
   a keyed definition, exchange finite sums under declared finite domains, apply
   a divisibility lemma, or use a bijection. The user should be able to see which
   part of the picture a step concerns.
5. **Retain and recheck the result.** Store the statement fingerprint, translation
   version, arithmetic semantics, tool/library versions, assumptions/axioms,
   certificate or proof source, and checker result. Editing the claim invalidates
   that association; a stored status is never trusted on its own.

The first useful goal is smaller than the whole floor-sum theorem. For the
quotient canvas, linear-order case splitting gives

\[
[X\le Y]+[Y\le X]=1+[X=Y].
\]

Then use `X=b(j+1)` and `Y=a(i+1)`. A separate divisibility lemma proves that
coprime positive `a,b` have no such interior equality: from `a(i+1)=b(j+1)`,
coprimality forces `b | i+1`, contradicting `0<i+1<b`. Summing the pointwise
identity gives the area claim. Without coprimality, enumerate the diagonal by
`d=gcd(a,b)` to derive the correction `d−1`. These are mathematical proof plans,
not machine-checked results produced in this increment.

For the 3D ownership construction, preserve pairwise assumptions separately.
Having `gcd(a,b,c)=1` does not prevent two normalized coordinates from tying.
A useful countercase is `(a,b,c)=(6,4,5)`. The same comparison controls and
statement vocabulary can expose the tie before any proof integration.

## Translation traps worth settling first

- **Division conventions:** Kaleion's `//` floors, including for negative
  divisors; `%` requires positive integer moduli. A backend's totalized division
  at zero or signed remainder convention must not change the statement. Express
  the needed quotient/remainder law explicitly or add a proved compatibility
  lemma. Lean documents totalized division in its FAQ; it does not discharge our
  nonzero-divisor obligations automatically.
- **Integers versus naturals versus finite fields:** a constructor extent is a
  nonnegative integer obligation, not license to silently replace all integer
  subtraction with truncated natural subtraction. Residue representatives are
  not automatically finite-field elements. Prime/irreducibility assumptions and
  basis encodings will matter for the code/Fano/Hermitian lessons.
- **Coverage versus values:** prove the exact domain and key bijection before
  substituting a driver. Equal totals do not prove pointwise equality; empty or
  absent rows are not zero-valued occurrences. An isomorphism needs a specified
  map and preserved operations/relations, a different claim from field equality.
- **Partial/eager definitions:** retain side conditions before simplifying
  unused branches or zero summands. A scalar division by zero still fails when
  the source is empty. The translator already tests this distinction.
- **Provenance versus formal semantics:** an exact history establishes what was
  calculated, not that a translation preserves its meaning for every parameter.
  Initially review and test each lowering rule; later formalize those rules or
  include a checked correspondence certificate.

## A small adapter contract, when justified

The following is a proposed shape, **not an API currently available**:

```python
request = ProofRequest(statement, assumptions=author_choices)
attempt = assistant.try_prove(request, budget=budget)
# attempt.status: unsupported / counterexample / unknown / solver_valid /
#                 checked_proof / invalid_certificate
```

An algebra tool returns suggested transformations, not this proof result.
`solver_valid` identifies the backend's assurance; `checked_proof` identifies
the checker and permitted axioms. Both refer to the same exact statement. A
future external kernel must accept the translated theorem under those declared
assumptions with no untracked holes or added theorem axioms. UI controls should
offer **Explain**, **Find a failing case**, and eventually **Attempt proof**,
while solver choice and budgets stay in an advanced pane.

Next experiment: translate the small indicator lemma and one keyed-read domain
obligation to Z3Py; independently reconstruct any countermodel. In parallel as a
later comparison, formalize the coprime-interior lemma in Lean and try the same
lemma with Knuckledragger. Compare readable steps, assumptions, trust and failure
reporting before committing to a default proof engine.
