# Future Kaleion lessons

The five investigations in the preceding plan now have notebooks: lessons
[04](04_measured_motion.md), [05](05_finite_radon.md), [06](06_young_layers.md),
[07](07_additive_structure.md), and [08](08_ehrhart_counts.md). This document preserves
their original briefs and explicitly identifies remaining extensions. The
[review notes](REVIEW_NOTES.md) record what the delivered constructions reveal.

Two further investigations are now delivered: [09 · Norm fibers](09_norm_fibers.md)
and [10 · Hermitian partitions](10_hermitian_partitions.md). They bring finite-field
motion, projective quotienting, polars, and measured partitions into Kaleion. The
[UI discovery notes](UI_DISCOVERY_NOTES.md) connect them to earlier lessons. The
following candidates are planned, not implemented.

The [authoring refinement](../AUTHORING.md) is delivered in lessons 07 and 10:
grouping, strict member order and ranks, scoped coverage with guarded assignments,
and named measurement-driven coordinates. Future lessons should reuse those
choices. Weighted prefix sums, case families, arbitrary key-domain comparisons,
and explanations across driver bindings remain open; add them only when a concrete
construction establishes their contracts.

## Next · Symmetry, orbits, and Burnside counting

**Question:** Why can we not count necklaces by dividing the number of strings by
the number of rotations?

**Start with:** the 64 binary strings of length six and the six cyclic rotations.
Declare the action using integer bit positions. Relate a string to each rotation
that fixes it; count along both axes. Choose the least rotated code as an explicit
orbit key, preserving the strings that contribute to each class.

**Motion:** rotate the six positions of a selected string, then gather all strings
by their orbit keys. Derive orbit sizes and use measured ranks to separate members.
Show the same rotation acting on several strings at once. Undo restores the
original occurrences, including strings that never visibly moved.

**Explanation:** the fixed-string counts for rotations `0,...,5` are
`[64,2,4,8,4,2]`, whose average is 14 necklaces. Double-count pairs `(rotation,string)`
where the rotation fixes the string. Each orbit contributes six such pairs through
its stabilizers. Compare this count with the 14 explicitly formed orbit classes.

**Challenge:** constant and alternating strings have smaller orbits. Their
stabilizers explain the failure of uniform division and show that an action need
not move every point. Do not confuse a motion's stationary tracks with failed work.

**Capability questions:** a finite action family, explicit orbit representatives,
and unequal group sizes. Can the same product/group/rank recipes serve lessons
07, 09, and 10? Keep orbit quotienting distinct from arranging all members together.

## Next · Syndrome fibers and the limits of correction

**Question:** What does an error syndrome reveal, and what information does it lose?

**Start with:** 128 binary vectors of length seven. Let a three-row parity-check
matrix have the seven distinct nonzero binary columns. Compute each three-bit
syndrome using exact mod-two sums. Count and display its eight fibers of size 16;
the zero fiber consists of the 16 codewords of this small Hamming code.

**Motion:** choose a codeword, flip one bit, and watch the vector move to the
syndrome fiber labeled by that bit's check column. Build the single-error relation,
verify unique coverage, then use the derived correction argument to return it.
Separate this inferred correction from undo, which restores recorded history.

**Explanation and challenge:** distinct nonzero columns identify a single flipped
bit. Two flipped bits can share a syndrome with a different one-bit error, so the
single-error correction can produce the wrong codeword. Display both compatible
histories as witnesses. A duplicated check column supplies another ambiguity.

**Completion evidence:** all syndrome fibers and contributors, exhaustive
single-error checks, two-error witnesses, measured placement, and reversible motion.
Field addition must be declared; ordinary integer addition of bit-vector codes
does not implement it. This can begin as a small integer-expression recipe.

## Later · Exchange blocks in a Hermitian spread

**Question:** Can different families of disjoint secants cover exactly the same
curve points, and can one family be replaced while preserving a full partition?

**Start with:** lesson 10's exact Hermitian incidence and regular spread. The
norm-defined, triply ruled families in
[Dover, *A Search for Spreads of Hermitian Unitals*](https://arxiv.org/pdf/1702.01297)
provide a concrete construction to study. First transcribe a small case and check
all stated hypotheses; do not infer a block exchange from equal totals alone.

**Motion:** hold the covered point set fixed, change the selected line family,
and regroup the points using newly measured owners and ranks. Display which
blocks changed and which stayed fixed.

**Completion evidence:** explicit families, pointwise coverage and disjointness,
an invalid exchange with witnesses, contributor inspection, and exact undo. This
should exercise relation-family editing and finite set comparison. Assess bounded
pair domains and capture size before attempting higher field orders or a search
over spreads; no large search engine is implied by the current viewer.

## 06 · Young diagrams, conjugate partitions, and counting by layers

**Delivered:** [lesson 06](06_young_layers.md) includes derived conjugation, measured
prefix offsets, a 3D transpose, packing/undo, contributor inspection, and the ordering
counterexample. An animated horizontal-threshold sweep remains an optional extension
of the original brief below.

**Question:** How can horizontal and vertical counts describe the same cells?

**Start with:** nonnegative integer heights; then order them into a nonincreasing
partition. For `(5,3,2)`, the horizontal layer counts are `(3,3,2,1,1)`. Both sum to ten.
The general finite counting identity is

\[
\sum_i h_i=\sum_{t=1}^{\max_i h_i}\#\{i:h_i\ge t\}.
\]

**Original construction brief:** Build cells under the height profile, sweep a
horizontal threshold, and count the selected columns. Use those counts to construct
the conjugate diagram. Rotate or transpose the original cells so the two descriptions
can be compared by an explicit bijection. Next, unroll rows into a strip using
cumulative row lengths as displacement offsets. Keep fresh derived cells distinct
from reoriented original occurrences.

**Explanation:** Count the same finite set of pairs `(i,t)` with `1 <= t <= h_i` in two
orders. Conjugating a partition twice restores it. Empty partitions and zero heights
need explicit conventions; no maximum is needed if the empty sum is handled separately.

**Challenge:** Rearranging an unsorted height list preserves its layer counts, so layer
counts do not recover the original ordering. This connects to lesson 05's distinction
between sufficient measurements and lost information.

**Capability questions:** A static Young constructor already exists. A keyed threshold
on a finite grid can express derived diagrams. Does ordered packing justify a readable
grouped prefix-sum/rank recipe? Counts provide sizes but do not supply a within-group
ordering. Strict ranks now have a compact implementation shared by lessons 07 and
10. Weighted prefix sums can still be expressed through pair domains and reductions,
although inefficiently; shortening that recipe remains future work.

**Prerequisites:** counts, retained keys, and simple bijections. Introduce the term
conjugate partition after the reader sees the transpose. A Young diagram is not
automatically a standard or semistandard tableau.

**Completion evidence:** two count sequences, an exact cell correspondence, measured
offsets actually driving motion, empty/zero cases, and an ordering counterexample.

## 07 · Convolution, sumsets, and additive energy

**Delivered:** [lesson 07](07_additive_structure.md) implements the ordinary integer
version, including a sum-lens sweep, measured ranks, reversible stacks, energy squares,
and an independently checked quadruple count. Modular/cyclic convolution remains a
follow-up; it is not claimed by the integer example.

**Question:** How many ways can the same integer be formed as a sum?

**Start with:** two finite integer sets A and B and the arrangement `A × B`. A moving
lens selects pairs satisfying `a+b=s`. Its counts create

\[
r_{A,B}(s)=\#\{(a,b)\in A\times B:a+b=s\}.
\]

This is convolution of the two indicator functions. Work with ordinary integer sums
first; modulo p gives a later cyclic-convolution variant with a different declared domain.

**Original motion brief:** Sweep diagonals in the pair arrangement. Align equal-sum pairs
into stacks with explicit within-stack ranks. Their heights are the measured values.
Use these counts in another construction selecting equal-sum pairs of pairs.

For `A=B`, derive the additive energy

\[
E(A)=\sum_s r_{A,A}(s)^2
=\#\{(a,b,c,d)\in A^4:a+b=c+d\}.
\]

**Explanation:** Each sum s has r(s) representations. Choosing an ordered pair of
representations gives r(s)^2 equal-sum quadruples. Compare an arithmetic progression
with a scattered set of the same size to observe different collision patterns.

**Challenge:** A many-to-one sum map is not a permutation. Coincident points must keep
their multiplicities. If repeated input labels are allowed, say explicitly whether
we are measuring a set or an arrangement of occurrences.

**Capability questions:** Does a readable paired-domain constructor preserve both
source identities? Are ordered ranks and cumulative offsets recurring needs after
lesson 06? Explicit support bins are needed when displaying sums of zero multiplicity;
arbitrary observed-key reductions do not invent absent keys.

**Prerequisites:** Cartesian products and counting ordered pairs. Introduce convolution
through the picture before its signal-processing terminology.

**Completion evidence:** exact representation counts, the quadruple identity checked
independently, motion driven by measured multiplicities, and ordinary versus modular
boundary cases. The broader connection is developed in
[Yufei Zhao, Structure of Set Addition](https://yufeizhao.com/gtacbook/7.pdf).

## 08 · Ehrhart theory: counting lattice points as shapes grow

**Delivered:** [lesson 08](08_ehrhart_counts.md) constructs measured parameter families,
differences driving independent probes, interior/boundary comparisons, a written
reciprocity argument for the triangle, and a rational period-two counterexample.

**Question:** What kind of number sequence does an expanding integer-coordinate shape produce?

**Start with:** `i,j >= 0` and `i+j <= n`, for integer scale `n >= 0`. Scrubbing n yields
`1,3,6,10,...` lattice-point counts. Collect each count, its parameter case, and its
derivation into a new arrangement; construct successive difference sequences.

**Original motion brief:** Show exact integer dilation cases with a discrete case scrubber.
Animate the comparison of successive counting profiles separately from case evaluation.
Use measured differences as the heights or offsets of a second arrangement, making
the constant second difference visible.

**Explanation:** The triangle has `(n+1)(n+2)/2` points, proved by summing row lengths.
For general lattice polytopes the counting function is polynomial. Rational vertices
lead to quasipolynomials: polynomial formulas selected by the dilation's residue class.
Introduce interior/boundary lenses and the reciprocity relation

\[
L_P(-n)=(-1)^{\dim P}L_{P^\circ}(n),\qquad n>0.
\]

Negative n here means evaluating the counting polynomial at a negative integer.
It does **not** mean that reflecting a physically dilated shape automatically removes
its boundary. See [Coefficients and Roots of Ehrhart Polynomials](https://math.mit.edu/~rstan/papers/ehrhart.pdf)
and the authors' book [Computing the Continuous Discretely](https://matthbeck.github.io/ccd.html).

**Challenge:** A finite difference pattern suggests a conjecture but is not a general
proof. Include n=0, distinguish interior from boundary points, and try a rational
triangle whose residue classes reveal periodic coefficients.

**Capability questions:** What is the most readable way to construct an arrangement of
parameter-case measurements without evaluating values into anonymous literals? Finite
`with_params(...)` cases plus explicit case attributes and concatenation are available
now. Integer-scaled inequalities can express simple rational boundaries before adding
a rational-value domain. Avoid treating interpolated movie frames as dilation cases.

**Prerequisites:** integer grids and counting rows; introduce finite differences and
polynomial interpolation only after observing the sequence.

**Completion evidence:** a retained sequence of case definitions, exact count/difference
arrangements, one elementary general proof, a boundary experiment, and a quasipolynomial
counterexample to a naive universal polynomial claim for rational vertices.

## Follow-up questions preserved from the first two investigations

- **Three orthogonal quotient projections:** measure X along x, Y along y, and Z along z.
  Their key spaces differ. Find a useful explicit correspondence or a common incidence
  domain before proposing a combined motion; do not add their arrays by storage index.
- **Finite tomography with missing directions:** characterize two different images with
  identical selected projections. Lesson 05 contains the initial 2×2 ambiguity; a fuller
  lesson could study which local switches preserve prescribed measurements.
- **A generic explanation view:** expose target → matched driver occurrence → measured
  contributors from captured data. The notebook-specific explanations in 04–08 establish
  concrete examples; do not duplicate large contributor lists into every animation frame.
- **Explicit finite comparisons:** return keyed residuals and witnesses, with both key
  domains checked. Equality of totals, keyed values, subsets, or occurrences must be
  stated separately. These are groundwork for later analytical statements and proof aid.

## Further lesson candidates

- **Cyclic convolution and modular folding:** start with lesson 07's integer sum bins,
  fold them by `s mod p`, and measure the resulting residue multiplicities. Show why
  several integer bins can contribute to one residue and preserve those contributors.
  Compare ordinary convolution with circular convolution using the same input pairs;
  declare whether repeated residue labels describe sets or weighted occurrences.
  Completion evidence: exact folded counts, a wraparound example, and a reversible
  motion that keeps every contributing pair distinct. No Fourier transform is required.
- **Measurement-preserving switches:** start with the 2×2 ambiguity in lesson 05,
  add opposite signed changes at opposite corners, and prove all row/column sums
  stay fixed. Apply further line lenses to expose the hidden difference. Keep signed
  weights separate from binary incidence cardinality, and check when a switch stays
  inside the allowed image domain. Completion evidence: two distinct constructions,
  equal chosen measurements, and an additional measurement with an explicit witness.
- **Growing boxes and plane partitions:** extend lesson 06 to integer heights over
  a two-dimensional footprint. Count horizontal layers and compare the total with
  the sum of heights. A plane partition additionally requires monotonicity in both
  footprint directions; arbitrary height fields still satisfy layer counting.
  Derive layer areas and packing offsets, and inspect whether the 3D motion clarifies
  the grouping. Completion evidence: volume equality, contributor inspection, and a
  nonmonotone example that separates double counting from the partition constraint.

## How these lessons should influence architecture

Record each repeated authoring task before changing the core: paired domains,
key-aligned reuse, ordered packing, parameter families, and contributor inspection.
Prefer a small recipe or presentation helper when it resolves the problem. Add a
primitive only when an actual construction exposes a missing contract. Keep the
symbolic definition, exact evaluation, captured state, and animation independently usable.
