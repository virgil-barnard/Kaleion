# Discovery paths through codes, duality, and motion

**Status:** A–B's main constructions are delivered in
[11 · A code becomes a projective plane](11_cyclic_code_plane.md), including the
extension-field incidence correspondence and synchronized Singer-cycle motion.
Its syndrome-correction coda begins C; full covering/coset motion and D–H remain
proposed. Updated September 20, 2026. Small algebraic fixtures were checked while
preparing these briefs; notebook validation is recorded separately. Educational
effectiveness for novice authors remains to be tested.

The eventual goal is a novice authoring a construction and noticing an unfamiliar
relationship. For now, build complete investigations that reveal the decisions
such an interface must expose. A lesson should provide an editable experiment,
an inspectable reason for its result, and an assumption the reader can change.
Camera movement alone is not a mathematical experiment.

The immediate path uses one binary Hamming code across polynomial, matrix,
incidence, geometric, and spectral views. Later branches exercise local iteration,
topological equivalence, and measurements of histories. These are independent
lessons with shared definitions, not a requirement to learn every topic in order.

## A · A polynomial becomes a matrix, then a code

**Seed.** Use binary arithmetic with coefficient order `x^0,...,x^6`. In
`F_2[x]/(x^7-1)`, take

\[
g(x)=1+x+x^3,\qquad c(x)=m(x)g(x),\quad \deg m<4.
\]

Display the seven coefficients as a strip, then bend it into a ring. Multiplication
by x is a cyclic coefficient shift. Keep the exact shift operation distinct from
its sampled wraparound presentation. Stack the coefficient vectors of
`g,xg,x^2g,x^3g` to obtain

\[
G=\begin{pmatrix}
1&1&0&1&0&0&0\\
0&1&1&0&1&0&0\\
0&0&1&1&0&1&0\\
0&0&0&1&1&0&1
\end{pmatrix}.
\]

**Motion and observation.** Turn message bits on one at a time. A selected row
sends its coefficients into the output slots; pairs of contributions give zero
modulo two. Enumerate the 16 messages and arrange outputs by Hamming weight.
The same result is readable as polynomial convolution and `mG`.

**Challenge.** Shift each completed codeword around the ring and check membership.
Then choose a different degree-three binary stencil that does not divide `x^7-1`.
Its four shifts can still generate a linear code, but closure under cyclic shift
must be checked again. For a concrete failure use `g_bad=1+x+x^2+x^3`.

**Software questions.** A declared coefficient convention, keyed paired domains,
convolution through exact products and sums, and changing arithmetic while keeping
the representation legible. This starts as a small coordinate recipe; no general
finite-field class or polynomial solver is needed. Retain integer contribution
counts before reducing modulo two. [MIT's polynomial-code notes](https://math.mit.edu/~djk/18.310/Lecture-Notes/polynomial_hamming_codes_2007.html)
provide background; [Sage's cyclic-code reference](https://doc.sagemath.org/html/en/reference/coding/sage/coding/cyclic_code.html)
states the generator/divisor construction.

## B · The constraints become generators; a plane appears

**Question.** Which seven-bit masks give even overlap with every generated word?
Inspect all 128 masks and retain those passing every parity check. Their eight
members form the dual code. Here

\[
h(x)=(x^7+1)/g(x)=1+x+x^2+x^4,
\qquad g^\perp(x)=x^4h(x^{-1})=1+x^2+x^3+x^4.
\]

The rows of H are the coefficient vectors of `g_perp,x*g_perp,x^2*g_perp`:

\[
H=\begin{pmatrix}
1&0&1&1&1&0&0\\
0&1&0&1&1&1&0\\
0&0&1&0&1&1&1
\end{pmatrix}.
\]

**Motion design.** Reverse the quotient stencil, shift it into rows, and pass those rows
over G. Each overlap has even parity: `G H^T = 0` over `F_2`. Let H switch roles
from checking C to generating its dual, then use G to check the dual. Exact row
operations can change a displayed basis while leaving the generated set fixed.
Lesson 11 constructs and checks the reciprocal and overlap table; animated
quotient reversal, row superposition, and basis changes remain extensions.

**A second discovery.** H's columns are the seven distinct nonzero three-bit
vectors. Place those columns as the seven points of the Fano plane. Each of C's
seven weight-three words selects a line. The seven nonzero dual words select their
four-point complements. Fold the same support masks between coefficient strips
and this geometry; coordinate distance never defines Hamming distance.

**Challenge and evidence.** Using h itself instead of its reciprocal gives an
orthogonality failure; retain the offending row pair. Check both spans, all
cross-parities, every point pair's unique line, and the complement correspondence.
The independent finite checks confirm these statements for this declared ordering.
[MIT's matrix Hamming-code notes](https://math.mit.edu/~djk/18.310/Lecture-Notes/matrix_hamming_codes_2007.html)
explain the parity-column construction.

## C · Error correction becomes a covering problem

**Construction.** Around each of the 16 codewords, construct the original word and
its seven one-bit changes. Use H to label the eight syndrome fibers, each of size
16. Independently count how often every word is reached by a center/error pair.

**Motion.** Grow these eight-member neighborhoods, then regroup by received word.
Every one of the 128 words has exactly one owner: `16*(1+7)=128`. Translate all
codewords by one error pattern to reveal a syndrome fiber; change the error pattern
and watch the entire translated set move together. A zero error remains explicit.

**Discoverable claim.** This particular Hamming code corrects every single-bit
error through unique neighborhood coverage. Reuse `coverage.unique(...)` to adopt
the corresponding error argument, then let that measurement drive correction.
Distinguish inferred correction from undo of the recorded corruption.

**Challenge.** Inject two errors: the usual one-error rule returns a different
codeword. Inspect both explanations of the received word. Duplicating a parity
column gives a more immediate ambiguity. A pretty partition alone is insufficient;
check the complete declared 128-word domain. Hamming distance counts differing
coordinates, so the 2D/3D arrangement is an organizational chart.

## D · The dual emerges where cancellation stops

**Seed.** Form the 16-by-128 relation between codewords c and trial masks u. Give
each pair the integer weight `1-2*(c dot u mod 2)` and sum over codewords:

\[
S(u)=\sum_{c\in C}(-1)^{c\cdot u}
=\begin{cases}16,&u\in C^\perp,\\0,&u\notin C^\perp.\end{cases}
\]

**Motion.** For a failing mask, find a codeword `c0` with odd overlap. Pair each
word with `c+c0`; their signed contributions cancel. For a dual mask all signs
are positive. Reuse the measured sums to lift independent mask probes. The eight
survivors reconstruct the dual from a new perspective. Preserve both contributors
of a cancellation even when their sum is zero.

**Further reach.** Regroup this same signed table by the weights of c and u. This
leads to the MacWilliams identity. Define `W_C(X,Y)=sum_c X^(7-wt(c))*Y^wt(c)`;
the checked example has

\[
W_C=X^7+7X^4Y^3+7X^3Y^4+Y^7,\qquad
W_{C^\perp}=X^7+7X^3Y^4,
\]

with `W_dual(X,Y)=W_C(X+Y,X-Y)/16`. The motion design should expose regrouping
and signed contributions before introducing the polynomial substitution. The
general cancellation argument and weight transform are developed in
[Guruswami's course notes](https://errorcorrectingcodes.wordpress.com/2010/02/07/notes-5-1-fourier-transform-macwillams-identities-and-lp-bound/).

**Feasibility and challenge.** The 2,048-entry signed measurement already executes
with current Kaleion primitives and matches an independent integer oracle at all
128 masks. Removing the word encoded by 11 produces sums `-1,1,15`, exposing
the role of linearity. Binary character sums
need only exact signed integers. Characters over larger fields would require a
separately specified representation. Request full Fourier transforms through
bounded/factorized constructions rather than defaulting to exponentially large
dense matrices.

## E · A polynomial absorbs the errors

**Seed.** Evaluate all degree-below-three polynomials over `F_7` at `0,...,6`.
This gives 343 words of a length-seven evaluation Reed–Solomon code. Select
`f=1+2x+3x^2` and corrupt positions 1 and 5, adding 2 and 3 respectively.

**Motion.** Sweep candidate polynomials as discrete field-valued point patterns;
matching positions light up and measured agreement counts move candidate probes.
Exactly one candidate agrees in at least five places. Then construct the error
locator `E=(x-1)(x-5)=x^2+x+5` and `Q=E*f`. Multiplication by E sends both sides of
`Q(a)=received(a)*E(a)` to zero at the erroneous positions. The same equations hold
at all remaining positions because the received values there equal f.

**Discoverable claim.** A bounded-degree error locator converts a noisy
interpolation problem into linear coefficient constraints. A later construction
can solve for monic degree-two E and degree-at-most-four Q before dividing Q by E;
this is the Berlekamp–Welch route. Display field samples without implying ordinary
real polynomial interpolation between their plotted coordinates.

**Evidence and gaps.** Enumeration checks minimum distance five, the sole candidate,
and all seven locator equations. For a three-error counterexample, replace f's
values at positions 2, 3, and 4 by those of `1+x+4x^2`: the received word is now
only two positions from that different codeword. A reusable
elimination trace would need explicit pivots, row operations, and exact prime-field
arithmetic. Begin with the visible finite recipe before extracting a solver.
This reconnects polynomial interpolation to the original discovery ambition.

## F · A closed path can hide an error

**Seed.** A 3-by-3 periodic square grid has nine vertices, 18 edges, and nine
faces. Work with edge subsets over `F_2`. Vertex parity detects a path's endpoints.
Face boundaries supply local closed loops. The two incidence matrices satisfy
`boundary_1 * boundary_2 = 0` modulo two.

**Motion.** Extend an error path one edge at a time; its endpoint defects move.
Close a small loop, then remove it using face-boundary additions. Repeat with a
loop winding once around the periodic grid. The defects disappear again, but local
face additions cannot erase this loop. Switch between a flat periodic chart and a
torus embedding while preserving the logical incidences.

**Discoverable claim.** Equal local syndromes can conceal different global classes.
This gives an entry into homology and the mechanism behind toric/surface codes.
The proposed lesson first models binary chains and their checks; introduce the
quantum stabilizer interpretation as a separately explained next step.
[Dennis, Kitaev, Landahl, and Preskill](https://arxiv.org/abs/quant-ph/0110143)
describe the connection between error chains, homology, and encoded information.

**Evidence and gaps.** Both boundary matrices have rank eight over `F_2`, giving
first-homology dimension `18-8-8=2`. A checked winding loop is closed and outside
the face-boundary span. Treat vertices, edges, and faces as distinct occurrence
domains; use incidence to connect them. A graph/cell viewer and finite quotient
explanations are real needs. Enumerating all `2^18` edge subsets is unnecessary.

## G · A sliding tableau measures hidden order

**Seed.** Insert the permutation `[4,1,7,3,8,2,6,5]` by RSK row insertion. Each
entry either extends a row or bumps its first larger entry into the next row.

**Motion.** Preserve entry identities through every bump. Keep the source sequence
visible beside the evolving Young tableau, with a separate recording tableau.
Let a reader highlight increasing subsequences before revealing that the first
row's length measures the longest one. Then compare the first two rows with the
largest union of two disjoint increasing subsequences.

**Evidence and reach.** The checked shape is `(3,3,2)`. Independent enumeration
finds longest increasing length three and maximum two-subsequence union six.
The general connection is Schensted's theorem and its Greene extension; see
[Stanley's account](https://arxiv.org/abs/math/0512035). The insertion tableau alone
need not retain the input order; the recording tableau matters for inversion.

**Gaps.** Bounded data-dependent iteration, emitted intermediate states, and causal
explanation of an insertion chain. This is a second use, alongside elimination and
sandpiles, against which to test a future recurrence abstraction. A stored animation
alone is not a symbolic derivation of the algorithm.

## H · Avalanches reveal an abelian group

**Seed.** Put chips on the three nonsink vertices of `K_4`. A vertex with at least
three chips may fire, sending one chip to each neighbor, including the sink.

**Motion.** Run different legal firing schedules side by side. Count each vertex's
firings to derive a new arrangement, then bind those counts into cumulative edge
flows. The measured firing vector u satisfies `final = initial - L*u`, with L the
reduced Laplacian. Keep sink absorption explicit.

**Further reach.** Explore addition followed by stabilization on recurrent states;
these form the sandpile group. Grouping all stable states together would make a
false claim. For this graph there are 27 stable states but 16 recurrent ones.
Independently construct all 16 spanning trees and investigate the equal counts.
[Perkinson, Perlman, and Wilmes](https://arxiv.org/abs/1112.6163) develop the
stabilization, group, Laplacian, and spanning-tree connections.

**Evidence and gaps.** Two opposite legal firing priorities give the same final
state and firing counts for every initial vector in `{0,...,6}^3`. Reachability
from the maximal stable configuration yields 16 recurrent states; direct tree
enumeration also gives 16. General claims need their stated finite connected graph
and accessible sink assumptions. This exercises bounded recurrence, event counts,
schedule comparison, and reuse of measured histories as transformation arguments.

## Development order and the novice interface

Continue lesson 11 with C–D. Their common seven-bit domain lets a reader change
viewpoint without learning a new example each time. Follow with F for the largest
conceptual leap, and use E, G, and H to test genuine execution/authoring gaps.
Keep the previously planned Burnside and Hermitian block-exchange lessons active.
Assign notebook numbers when work begins, avoiding a fixed schedule for every idea.

| Author's intended action | Demonstrations that exercise it | Likely responsibility |
| --- | --- | --- |
| Choose what a label represents | Binary words, polynomial coefficients, field values | Explicit coordinate/arithmetic recipe |
| Shift, translate, or superpose a pattern | Generators, cosets, signed cancellation | Existing operations with named operands and arithmetic |
| Compare two constructions of the same set | Span versus kernel, spectrum versus dual | Declared key domains, equality scope, witnesses |
| Count events and reuse the counts | Syndrome coverage, signed sums, firing histories | Measurements, provenance, keyed bindings |
| Repeat a local rule until a condition holds | Elimination, RSK insertion, stabilization | Bounded recurrence and emitted evidence, if recipes justify it |
| Explain why an item moved or survived | A parity failure, cancellation partner, insertion bump | Captured read/contributor evidence |
| Change the chart while preserving a relation | Fano supports, periodic grid versus torus | Placement and viewer, independent of logical incidence |

For each implemented lesson, record what the author must choose from a blank
workspace. Include a transfer task with unfamiliar inputs, and a way to inspect
why the result changes. These tasks will test a later novice UI more meaningfully
than counting how many preset demonstrations it can replay. Novice usability
remains an empirical question for actual users.

Following the project's Parnas criterion, keep numerical representation, operation
execution, retained evidence, and presentation separately owned. Shared mathematical
structure can justify a recipe without implying a new class or evaluator opcode.
The immediate code/dual route can begin with current integer expressions,
incidences, reductions, groups, bindings, and motion. General recurrence, finite
comparison, solver traces, and cell-complex presentation should earn their contracts
through the later examples.

## Scope of the preliminary checks

The original [recorded fixture results](../reviews/2026-09-discovery-path-fixtures.json)
identify the code ordering and finite cases checked with independent Python
arithmetic, enumeration, and binary row reduction. Only the signed code/dual sum
was additionally evaluated through Kaleion. This is feasibility evidence for a
plan, not notebook validation or a performance benchmark. Lesson 11 now provides
separate executable evidence for the code/dual/field/plane route; these planning
fixtures remain unchanged. No new runtime operation or dependency was needed.
