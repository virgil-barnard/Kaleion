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
A pair-of-layers incidence and weighted reduction derive the offsets; their values
drive the original cells' placement. No evaluated list is inserted as a new source.

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

Layer counting, conjugation, prefix sums, keyed placement, and reversible motion fit
the existing operations. Counts provide sizes but do not supply an ordering. The
dense pair-of-layers construction is a clear recipe for small examples; it suggests
an eventual readable scan operation without requiring a new mathematical object now.

The measured count exposes its original contributors. The prefix sum is a further
weighted derivation, with its own contributing layer-pair occurrences. Keeping these
levels distinct will matter to a generic explanation view.

Exports in `build/notebooks/young-layers/` include four offline HTML figures, three
workspaces, `checks.json`, and `layer-explanation.json`. The 3D motion exports to
interactive HTML. See the [Sage partition reference](https://doc.sagemath.org/html/en/reference/combinat/sage/combinat/partition.html)
for established conjugation terminology and alternative diagram conventions.
