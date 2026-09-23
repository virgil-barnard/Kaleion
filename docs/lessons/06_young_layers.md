# 06 · Turn a diagram; count its layers

**Status:** available. [Open the notebook](../../notebooks/06_young_layers.ipynb).

**Question:** How can two different lists describe the same cells, and what do those
lists forget?

**Background:** nonnegative integers, grouping, and counting. The notebook introduces
partitions and conjugation through their pictures. It uses column heights; a Young
diagram is not yet a standard or semistandard tableau, which needs a constrained filling.

## Construction and explanation

For a finite height list, select cells `(i, level)` with `1 <= level <= h_i`. Counting
by columns recovers the heights; counting by layers gives

\[
c_\ell=\#\{i:h_i\ge\ell\},\qquad \sum_i h_i=\sum_{\ell\ge1}c_\ell.
\]

Both sums count the same pairs in different orders. For a nonincreasing height list,
every occupied layer is an initial interval. Transposing therefore produces the
conjugate partition, and transposing twice restores the original. Trailing zero
columns remain stored even though the partition notation normally omits them.

Prefix offsets `o_l = sum(c_t for t < l)` place those layers into consecutive intervals.
The measured layers declare their order and use `prefix_sums(key=F.j)` to derive
offsets with compact contributor ranges. Their values drive the original cells'
placement. The small pair-of-layers construction remains an independent finite
reference; no evaluated list is inserted as a new source.

## Narrative

1. Start with heights `[5,3,2,0]`; derive layer counts `[3,3,2,1,1]`.
2. Compare a freshly constructed conjugate with the transposed original occurrences.
   Their occupied coordinates agree; their identities differ.
3. Inspect the measured offsets `[0,3,6,8,9]`.
4. Turn the original cells through 3D, pack them into ten positions, and undo both
   moves. The 84 frames sample two captured transitions and their reversals.
5. Explain the counting identity and the role of ordering in the packing recipe.
6. Compare `[5,3,2]` with `[2,5,3]`: identical layer counts cannot recover column order.
7. Choose `LAYER`, inspect its contributors, and reopen the saved investigation.

## Experiments and boundaries

- Try another decreasing height list, a single cell, all zeros, or an empty list.
  The empty example retains one declared zero layer; it never takes an empty maximum.
- Predict the prefix offsets before showing the strip. The original column index
  supplies within-layer rank only because the heights are ordered.
- Change the values assigned to column keys. Distinguish this from reordering a
  driver's storage while preserving its keys, which leaves keyed action unchanged.
- Cell markers show centers, not rigid square meshes. Area means the number of
  declared unit cells; screen marker size does not change it.

## What this teaches us about Kaleion

Layer counting, conjugation, prefix sums, keyed placement, and reversible motion
compose through ordinary measured collections. Counts provide sizes but do not
supply an ordering. The dense reference explains the mathematics; the new
`prefix_sum` operation avoids its quadratic intermediate work and evidence.

The measured count exposes its original contributors. The prefix sum is a further
weighted derivation whose contributors are the earlier measured layers. Its receipt
leads to each layer count, then to the original cells. These are different levels
of evidence, even when the source value and weight happen to agree.

Exports in `build/notebooks/young-layers/` include four offline HTML figures, three
workspaces, `checks.json`, and `layer-explanation.json`. The 3D motion exports to
interactive HTML. See the [Sage partition reference](https://doc.sagemath.org/html/en/reference/combinat/sage/combinat/partition.html)
for established conjugation terminology and alternative diagram conventions.

## Functions and authoring scaffolding

This [notebook](../../notebooks/06_young_layers.ipynb) defines **no local functions**.
Its mathematical recipes and playback orchestration are inline. See the
[cross-lesson inventory](HELPER_INVENTORY.md) for their recurring responsibilities.

| Inline responsibility | Primitives and choices required |
| --- | --- |
| Build and conjugate a diagram | Validate a finite nonincreasing height list, bind heights to a cell domain, select occupied cells, and count by columns or levels. A second construction checks conjugation twice. |
| Distinguish identity from shape | Move the original selected occurrences into the transposed placement; compare occupied coordinates with a separately constructed diagram without claiming identical occurrences. |
| Measure packing offsets | Declare `layers.group_by().order_by(F.j).prefix_sums(key=F.j)` and bind the offsets by `j` into strip placement. Keep the dense level/predecessor sum as a small independent reference. |
| Show turning and packing | Declare a custom three-dimensional turn and an arc path, commit both changes, undo both, and assemble sampled frames, captions, and identity-based colors. |
| Explain and challenge | Recover layer contributors by source ID; use `Inspection.measurement` for the offset and each earlier layer's receipt; inspect an unordered-height counterexample and distinguish equal counts from preserved order. |
| Preserve the investigation | Save three workspaces, figures, explanation data, and checks that contributors survive reopening. |

**Shared functions used.** [lesson_views.py](../../notebooks/lesson_views.py)
supplies `cell_panels`, `profiles`, `replay`, and `save_figures`.
`cell_panels` uses `xy_cells`; panels and profiles use `style`; `replay` delegates
to the public animation viewer. These helpers consume captured data and do not
own conjugation or prefix construction.
Public `Grouping.prefix_sums` owns the weighted ordered measurement, and
`Inspection.measurement` supplies captured offset/earlier-layer receipts. The
lesson keeps the choice of layers, keys, packing rule, dense comparison, and
narrative inline. Saved offset receipts are checked again after reopening.

**Abstraction evidence.** The weighted exclusive prefix is the substantial
delivered construction: each offset is a sum of earlier measured lengths, with
an explicit order and a first value of zero. The strict ranks now used in 07 and
10 count predecessors; `prefix_sums` sums their weights. Both share strict ordering
and compact contributor ranges. Quotient-column packing provides a second use of
the new contract in core and studio tests. Sampling and captions
are a separate, smaller presentation extraction.
