# From an observed equality to a conjecture

September 23, 2026 · Updated September 25 · No proof integration implemented

An author should eventually be able to select two constructions that agree in
the finite case on the canvas, choose which constants become variables, state
assumptions, and ask a proof assistant to attempt a general proof. The original
observation and its provenance must remain inspectable throughout. The general
construction UI now implements a bounded portion of this sequence, without
coupling the canvas or evaluator to a proof engine.

The [quotient equality investigation](QUOTIENT_EQUALITY.md) now implements a
bounded prerequisite: a portable finite question with explicit keys/domain,
original captured workspace and three capture identifiers. Its generic statement
names the compared fields; Open rechecks those captures.
[Construction expansion](ALGEBRAIC_STATEMENTS.md) now follows supported integer
definitions, retains domains and local scopes, and records chosen global
parameters and explicit author assumptions. Construction obligations must follow
from those assumptions. Arbitrary literal promotion, broader operation/domain
translation, and machine-checked proofs remain future work. The
[proof-assistance study](PROOF_ASSISTANCE.md) recommends separate Python-friendly
search/algebra adapters and a durable checked-proof path.

## The proposed authoring sequence

1. **Name the comparison.** Choose both construction roots and their captured
   cases. State whether the claim concerns keyed values, sets of occurrences,
   total measurements, or a declared correspondence. Equal-looking placement,
   equal cardinality, and isomorphism are distinct claims. The existing finite
   keyed-value report supplies one possible witness, not a universal equality.
2. **Choose what varies.** Promote specified parameter bindings or literal
   occurrences in the definitions. Do not globally replace every matching
   numeral: `7` can independently be a modulus, extent, label, or coordinate.
   Show each selected occurrence and its scope, and ask whether selected uses
   share one variable. Preserve literals that were not selected.
3. **Lift the construction and its domain.** A variable size must change the
   domain definition, grouping coverage and relevant driver definitions too.
   Replacing snapshot values or relabeling the picture does not generalize the
   construction. Keep local bindings distinct from workspace parameters and
   identify any fixed captured lookup table that has not been generalized.
4. **State the claim.** Give variable domains, quantifiers and assumptions such
   as positive extents, a nonzero divisor, coprimality, or a prime modulus.
   Exact arithmetic and finite set semantics stay separate from floating
   placement. Surface required side conditions; do not silently assume them.
5. **Explore and attempt proof.** Try new finite cases and preserve any
   counterexample. Translate the supported definitions and assumptions to a
   chosen proof system, attempt automation, and retain the exact statement and
   result. Unsupported operations or incomplete provenance need an explanation,
   not an invented theorem.

At every step the original finite witness remains available. Editing the
conjecture creates a new statement revision; an earlier proof result must not
silently attach to the edited statement.

## Evidence states must remain distinct

| Result | What the interface may say |
| --- | --- |
| Equal in one or several captured cases | The specified finite comparisons passed |
| Candidate generalization | Conjecture under the displayed domains and assumptions |
| Exact counterexample | The claim fails at the recorded admissible assignment |
| Prover timeout, unknown, or unsupported translation | No proof obtained; the claim is unresolved |
| Proof accepted by the configured checker | This exact translated statement was checked, with its assumptions, dependencies and checker version recorded |

Provenance explains how a result was constructed; it is not itself a proof
certificate. A proof of the translated statement also depends on a faithful
translation of Kaleion's operator meanings. That boundary must be explicit;
animation, floating coincidence, and successful finite checks cannot cross it.

## Information-hiding boundaries

The construction graph continues to own mathematical definitions and scope.
Captured inspection owns finite witnesses and contributor references. The bounded
statement adapter owns comparison meaning, selected parameter abstractions and
assumptions. A separate proof adapter would own backend translation and
checker interaction. Presentation would display those results without assigning
proof status itself. Neither the UI nor core evaluation should import a
particular assistant's tactics or wire format.

Start with an explicit export recipe for one investigation. Introduce shared
statement objects, schema extensions or core primitives only when that concrete
round trip demonstrates a necessary contract. Record semantic versions and
unsupported operations so a saved claim cannot acquire a changed meaning.

## First future investigation

Revisit [lesson 02](lessons/02_floor_sum_proof.md). From the coprime case
`a = 11, b = 7`, form the candidate statement

\[
\sum_{x=1}^{b-1}\left\lfloor\frac{ax}{b}\right\rfloor +
\sum_{y=1}^{a-1}\left\lfloor\frac{by}{a}\right\rfloor
= (a-1)(b-1).
\]

Declare integer `a,b > 1` and `gcd(a,b) = 1`, retaining the exact lattice domains
and complementary incidences from the construction. Removing coprimality gives
the small counterexample `a = 6, b = 4`: the left side is 16 and the right side
is 15. Test that the author can locate this assumption and that a tool reports
the counterexample separately from a failed proof attempt. The notebook's
mathematical argument is a starting specification; translating and checking it
in a proof assistant remains future work.

The current [field guide](FIELD_GUIDE.md) serves a smaller prerequisite: authors
can see which object a field describes. It does not generalize definitions,
infer hypotheses, build conjectures, or certify proofs.
