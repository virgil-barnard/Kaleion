# 07 · How many ways can a sum occur?

**Status:** available. [Open the notebook](../../notebooks/07_additive_structure.ipynb).

**Question:** What does the distribution of equal sums reveal about two integer sets?

**Background:** ordered pairs and counting. Lesson 06's distinction between counts
and order is helpful, but all definitions are included here.

## Construction and explanation

For finite integer sets A and B, construct their ordered pairs and measure

\[
r_{A,B}(s)=\#\{(a,b)\in A\times B:a+b=s\}
=(\mathbf1_A*\mathbf1_B)(s).
\]

This is discrete convolution of indicator functions. A pair × bin measurement domain
retains every declared sum bin, including zeros. The default sets are both `{0,1,2,3}`;
their counts are `[1,2,3,4,3,2,1]`.

Moving `(a,b)` to `(a+b,0)` produces coincidences without removing occurrences. Count
earlier pairs with the same sum to derive a rank for each pair. These measured ranks
then separate the coincident pairs into consecutive vertical slots.

The construction now declares that directly:
`pairs.group_by(F.total).order_by(F.pair_key).ranks(key=F.pair_key)`.
Binding those ranks by pair key supplies `y` in `arrange(x=F.total, y=height)`.
Member order, grouping, correspondence, and coordinate choice remain visible.
Ranks use compact ordered-prefix evidence rather than a dense predecessor matrix.

Each sum has `r(s)` representations, so it gives `r(s)^2` ordered pairs of
representations. Grouping quadruples by their common sum proves

\[
\sum_s r_{A,B}(s)^2
=\#\{(a,b,c,d)\in A\times B\times A\times B:a+b=c+d\}.
\]

For A=B this is the additive energy E(A). The notebook derives the same number
from squared counts, a quadruple incidence, and unit cells in squares whose sides
are the measured counts.

## Narrative

1. Build the pair arrangement and sweep its equal-sum diagonal lens.
2. Read the representation-count profile as a convolution.
3. Collapse equal sums, then stack their occurrences using measured predecessor ranks.
   Undo both moves; the 84 frames retain the original pair identities.
4. Build the measured squares and explain why their total is 44.
5. Compare `{0,1,2,3}` with `{0,1,3,7}`. Both have 16 ordered pairs, but their
   energies are 44 and 28, respectively.
6. Choose `SUM` and follow a count contributor through its measurement-domain
   occurrence to the original ordered pair.

## Experiments and boundaries

- Try gaps, negative integers, unequal set sizes, or an empty input set. Empty inputs
  use the explicitly declared zero bin with count zero.
- Unique input labels are required: repeated labels would define multiplicities,
  not the set indicators used in the written formula.
- Translate either set. Predict which features shift and which counts remain the same.
- Ordinary integer sums have no wraparound. Modular folding and cyclic convolution
  remain a follow-up with a different declared bin domain.
- An energy value measures collisions; it does not uniquely identify a set.

## What this teaches us about Kaleion

Many-to-one placement is different from deleting duplicates. An ordering and a count
of predecessors supply the slots needed for packing; counts alone do not. Explicit
measurement domains supply missing zero bins. The dense pair-of-pairs construction
remains only for the independent additive-energy count; it is intentionally small
and is not an efficient general convolution implementation. See the
[authoring guide](../AUTHORING.md) for the rank and placement contracts.

Exports in `build/notebooks/additive-structure/` include five offline HTML figures,
three workspaces, `checks.json`, `sum-explanation.json`, and `sum-stacks.mp4`.
The video uses the existing 2D raster adapter and the same captured frames as Plotly;
it is not a screen recording of the interactive figure.

For the broader mathematical setting, see [Yufei Zhao, Structure of Set Addition](https://yufeizhao.com/gtacbook/7.pdf).

## Functions and authoring scaffolding

The [notebook](../../notebooks/07_additive_structure.ipynb) defines two top-level
functions. See the [cross-lesson inventory](HELPER_INVENTORY.md).

| Local function | Responsibility and assumptions |
| --- | --- |
| `integer_pairs(left_values, right_values)` | Construct two literal inputs; use `Product(left=left, right=right)` and explicit reads; name `a`, `b`, `total`, and `pair_key`; place the pairs. The sum remains a symbolic value. |
| `representation_counts(pairs, lower, upper)` | Declare an inclusive interval of sum bins, build the pair/bin matching incidence, and count retaining the bin. Return the profile and incidence, including bins with zero matches. The caller chooses the bin coverage. |

**Shared functions used.** Public `Product` supplies `.domain` and `.read` for
integer pairs, pair/bin measurements, and the independent pair-of-pairs energy
check. Bin grouping is now `F.bin`; declared semantic fields remain explicit.
[lesson_views.py](../../notebooks/lesson_views.py)
provides `cell_panels`, `profiles`, `replay`, and `save_figures`, using `xy_cells`
and `style` internally. Public `animation_figure` and `write_mp4` also present
captured samples.

**Inline scaffolding.** Equal-sum groups declare `order_by(F.pair_key)` before
`ranks`; measured ranks drive stack placement by explicit bindings. The energy
comparison uses both squared representation counts and a dense quadruple
incidence as a finite check. Alternative input sets, a moving diagonal lens,
staged edits and undo, sample labels/colors, contributor explanations, and
HTML/MP4/workspace exports remain inline.

**Abstraction evidence.** Named product factors now share the `Product` recipe
with 05. The recipe leaves multiplicity, key meaning, and zero-bin coverage visible;
it does not interpret a product as a set or hide its dense cost. Grouping, strict ordering, and ranks already
exist in the core; the remaining work is authoring clarity. The dense energy
construction is an explanatory reference, not an efficient convolution algorithm.
The [touch interaction study](../TOUCH_WORKSPACE.md) reuses this investigation to
test a movable lens, a derived count object, measured placement, and saved receipts.
