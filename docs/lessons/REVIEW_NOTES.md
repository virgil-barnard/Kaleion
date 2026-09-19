# Evidence for the next Kaleion review

These are observations from [lessons 01–08](README.md), not an approved redesign.
The new investigations fit the existing runtime operations. Their authoring code
shows where a clearer notation, reusable recipe, or faster evaluator might help.

## What the examples establish

| Repeated construction | Evidence | Question for the review |
| --- | --- | --- |
| Measure, bind by keys, change a target | 04's lifted plane, 05's reconstruction, 06's packing, 07's stacks, 08's probes | Can the author declare the target quantity and correspondence in one readable expression? |
| Pair domain, relation, reduction | Lines × pixels in 05; layers × layers in 06; pairs × bins and pairs × pairs in 07 | Would a paired-domain recipe expose source keys more clearly without hiding identity? |
| Ordered prefix and rank | 06's starting offsets; 07's equal-sum predecessor counts | What ordering must an eventual scan/rank convenience function require? |
| Exact case family | 08's measured dilations and finite differences | How should a family expose case parameters and measured contributors? |
| Keyed comparison with witnesses | 04's bump, 05's failed divisibility, 08's reciprocity residuals | Which equality is intended: totals, keyed values, subsets, or occurrences? |
| Contributor explanation | A column in 04, a pixel in 05, a layer in 06, a sum in 07, a dilation in 08 | Can a common inspector follow target → bound driver → original contributors? |

## Distinctions the interface must preserve

**Size does not determine order.** Young layer counts agree for `[5,3,2]` and
`[2,5,3]`. Packing needs an explicit within-group order. Reassigning values at keys
changes the mathematical input; reordering storage while preserving keys does not.

**Coincidence does not erase multiplicity.** Several ordered pairs can share the
position `(a+b,0)`. Lesson 07 preserves their identities and separates them with
measured ranks. A renderer may visually overlap them without implying deletion.

**Zero needs a domain.** Declared grid axes retain empty groups. A reduction over
arbitrary observed keys cannot manufacture bins that were never present. The
pair × bin construction deliberately includes zero-multiplicity sums.

**A case is part of a measurement.** In lesson 08, each count depends on a particular
integer dilation. Concatenation preserves symbolic inputs and parent lineage but
does not merge their reduction metadata into one contributor-query interface.
Keeping named case roots makes inspection possible today. A family view should
make that relationship accessible, including for zero counts and reordered cases.

**A further derivation changes the claim.** A difference or squared count is derived
from measurements; it is not itself the original subset cardinality. The graph can
preserve the derivation without attaching misleading count metadata to a new value.

**Motion is not a theorem or another evaluated case.** A smooth transpose, packing,
or lift shows a captured path. Integer dilations are discrete evaluations. Every
general identity in these lessons has a separate argument with stated assumptions.

## Small experiments to consider before changing the core

1. Write the same layer packing and sum stacking with a proposed paired-domain and
   ordered-rank recipe. Compare readability with the existing visible definitions.
   Keep source keys, ordering, zero groups, and identity explicit.
2. Sketch one explanation schema that handles the five concrete contributor examples.
   Include zero groups, weighted sums, a parameter case, and multiple derivation steps.
   Keep large contributor lists out of individual animation frames.
3. Specify finite keyed comparison results: domains on both sides, missing keys,
   residuals, and witnesses. Do not replace these distinctions with object `==`.
4. Give a parameter-family recipe a case key and accessible per-case measurement.
   Compare it with lesson 08's current `with_params` plus concatenation construction.

These are candidates for review, not missing prerequisites for continuing lessons.
A convenience operation should first make at least two real constructions clearer.

## Separation of responsibilities and practical limits

Definitions build the dependency graph; evaluation produces exact values; captured
states and transitions support replay; viewers consume those results. Lessons 06–08
share a small presentation-only [helper](../../notebooks/lesson_views.py), while their
mathematical definitions stay visible in the notebooks. The helper is not a new
runtime API or an authoring language.

Dense paired domains make the current small investigations explicit. They can grow
quadratically in the number of occurrences, and a pair-of-pairs domain grows as the
fourth power of the input-set size when both sets grow together. This is an execution
cost, not evidence that another mathematical object is necessary. Lazy pairs, sparse
reductions, scans, or accelerated backends should preserve the same exact contracts.

The current plots remain preliminary viewers. Plotly supplies interactive 3D;
the separate raster adapter supplies 1D/2D MP4. Neither establishes physical cell
area from marker size. Tests and [viewer validation](../../notebooks/VALIDATION.md)
record finite evidence and environment limitations.

For the review, start with 06's ordering counterexample, 07's collapse/stack motion,
and 08's measured family. They expose three different kinds of information the
future notation and interface must make visible before we choose touch gestures.
