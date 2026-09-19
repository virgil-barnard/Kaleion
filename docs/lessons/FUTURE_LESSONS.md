# Future Kaleion lessons

These investigations are planned; their notebooks are not yet implemented. Lessons
[04](04_measured_motion.md) and [05](05_finite_radon.md) implement the first two
investigations from the preceding plan. This document preserves the remaining ideas
and the specific design questions they should answer.

## 06 · Young diagrams, conjugate partitions, and counting by layers

**Question:** How can horizontal and vertical counts describe the same cells?

**Start with:** nonnegative integer heights; then order them into a nonincreasing
partition. For `(5,3,2)`, the horizontal layer counts are `(3,3,2,1,1)`. Both sum to ten.
The general finite counting identity is

\[
\sum_i h_i=\sum_{t=1}^{\max_i h_i}\#\{i:h_i\ge t\}.
\]

**Proposed construction and motion:** Build cells under the height profile, sweep a
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
ordering. Pair domains and reductions can express prefix counts now, although inefficiently.

**Prerequisites:** counts, retained keys, and simple bijections. Introduce the term
conjugate partition after the reader sees the transpose. A Young diagram is not
automatically a standard or semistandard tableau.

**Completion evidence:** two count sequences, an exact cell correspondence, measured
offsets actually driving motion, empty/zero cases, and an ordering counterexample.

## 07 · Convolution, sumsets, and additive energy

**Question:** How many ways can the same integer be formed as a sum?

**Start with:** two finite integer sets A and B and the arrangement `A × B`. A moving
lens selects pairs satisfying `a+b=s`. Its counts create

\[
r_{A,B}(s)=\#\{(a,b)\in A\times B:a+b=s\}.
\]

This is convolution of the two indicator functions. Work with ordinary integer sums
first; modulo p gives a later cyclic-convolution variant with a different declared domain.

**Proposed motion:** Sweep diagonals in the pair arrangement. Align equal-sum pairs
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

**Question:** What kind of number sequence does an expanding integer-coordinate shape produce?

**Start with:** `i,j >= 0` and `i+j <= n`, for integer scale `n >= 0`. Scrubbing n yields
`1,3,6,10,...` lattice-point counts. Collect each count, its parameter case, and its
derivation into a new arrangement; construct successive difference sequences.

**Proposed motion:** Show exact integer dilation cases with a discrete case scrubber.
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
  contributors from captured data. The notebook-specific explanations in 04/05 establish
  concrete examples; do not duplicate large contributor lists into every animation frame.
- **Explicit finite comparisons:** return keyed residuals and witnesses, with both key
  domains checked. Equality of totals, keyed values, subsets, or occurrences must be
  stated separately. These are groundwork for later analytical statements and proof aid.

## How these lessons should influence architecture

Record each repeated authoring task before changing the core: paired domains,
key-aligned reuse, ordered packing, parameter families, and contributor inspection.
Prefer a small recipe or presentation helper when it resolves the problem. Add a
primitive only when an actual construction exposes a missing contract. Keep the
symbolic definition, exact evaluation, captured state, and animation independently usable.
