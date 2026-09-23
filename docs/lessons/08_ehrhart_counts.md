# 08 · Count lattice points as a triangle grows

**Status:** available. [Open the notebook](../../notebooks/08_ehrhart_counts.ipynb).

**Question:** When does a growing shape produce a polynomial sequence of counts?

**Background:** integer grids and sums. Finite differences, Ehrhart polynomials,
reciprocity, and quasipolynomials are introduced through concrete triangles.

## Construction and explanation

For each integer `n >= 0`, count points with `i,j >= 0` and `i+j <= n`. The default
cases `n=0,...,8` give `[1,3,6,10,15,21,28,36,45]`. Counting row lengths proves

\[
L(n)=\sum_{i=0}^n(n-i+1)=\frac{(n+1)(n+2)}2.
\]

Finite `with_params` definitions are concatenated into a measured family with an
explicit `scale` key. Keyed differences derive new arrangements; a separate row
of probes moves to the counts, first differences, and constant second differences.

For `n >= 1`, the strict interior has `i,j > 0` and `i+j < n`, so

\[
I(n)=\frac{(n-1)(n-2)}2=L(-n).
\]

Here L(-n) evaluates the polynomial; it does not reflect a dilated shape. At `n=0`,
the closed set is one point and the strict-inequality lens is empty. The reciprocity
comparison excludes that case. The elementary formula also handles the empty
interiors for `n=1,2`.

## Narrative

1. Scrub exact integer dilations; count selected points in a fixed finite universe.
2. Inspect the first and second difference arrangements.
3. Let these three measured fields move independent probes. The final height is one.
   Three moves and three undos produce 102 sampled frames.
4. Prove the row-count formula. A finite difference table alone is not a proof for all n.
5. Compare closed, interior, and boundary counts; check reciprocity residuals.
6. Replace the triangle with the rational triangle `2(i+j) <= n`.
7. Inspect one count's parameter case and its original lattice-point contributors.

## The rational counterexample

For vertices `(0,0),(1/2,0),(0,1/2)`, let `q=floor(n/2)`. Its count is
`(q+1)(q+2)/2`, giving `[1,1,3,3,6,6,10,10,15]` through scale eight. Equivalently,

\[
L_Q(n)=\begin{cases}(n+2)(n+4)/8&n\text{ even},\\
(n+1)(n+3)/8&n\text{ odd}.\end{cases}
\]

This is a quasipolynomial of period two. Consecutive second differences vary;
second differences with stride two are one. There is no single polynomial agreeing
at every scale: infinitely many even arguments force the even polynomial, which
fails on odd arguments. The notebook proves this case; the general lattice-polytope
and reciprocity theorems are background, with a reference to
[Coefficients and Roots of Ehrhart Polynomials](https://math.mit.edu/~rstan/papers/ehrhart.pdf).

## What this teaches us about Kaleion

Parameter families and differences work without evaluating measurements into new
literals. Concatenation retains the operation graph and parent lineage, but does
not expose the inputs' reduction metadata as one merged `contributor_ids` interface.
The notebook therefore keeps each measured case and corresponding incidence as a
root, and links the profile occurrence to that case by its scale key. This is a
concrete ergonomics issue for the upcoming review.

Try another `MAX_N` from 4 to 12 or change a boundary while keeping the finite
universe large enough. Counts in the dilation scrubber are exact cases; the probe
motion is separate presentation, with fixed axes and independent screen scales.

Exports in `build/notebooks/ehrhart-counts/` include five offline HTML figures, two
workspaces, `checks.json`, `case-explanation.json`, and `integer-dilations.mp4`.
The video holds exact cases at 12 fps rather than interpolating lattice counts.

## Functions and authoring scaffolding

The [notebook](../../notebooks/08_ehrhart_counts.ipynb) defines two top-level
functions. See the [cross-lesson inventory](HELPER_INVENTORY.md).

| Local function | Responsibility and assumptions |
| --- | --- |
| `measured_family(incidence)` | Build a count definition for each scale from zero through the notebook's `MAX_N`; bind that case's parameter, annotate its scale, concatenate, and place the family. Return both the family and the individual measurement roots. No evaluated count is fed back as an anonymous literal. |
| `difference(series, last, step=1)` | Restrict to the scales with an available successor, bind that successor by its scale key, and subtract the current value. This is a finite keyed difference with an explicit stride and endpoint. |

**Shared functions used.** [lesson_views.py](../../notebooks/lesson_views.py)
provides `profiles`, `replay`, and `save_figures`; profiles use `style` internally.
Public `animation_figure` and `write_mp4` also consume captured samples.

**Inline scaffolding.** A fixed finite lattice domain carries closed, interior,
and rational-triangle lenses. Counts, successive differences, and parity
subfamilies drive probes and plots. Parameter-case checks, contributor receipts,
staged edits/undo, transition sampling, and exports are assembled explicitly.
The discrete dilation video holds exact cases; it does not treat interpolated
membership as a new mathematical case.

**Studio transfer, separate from notebook counts.** The shared
[case controller](../PARAMETER_CASES.md) declares `n`, uses `$n + 1` as both grid
lengths, relates `i + j < $n`, and counts retaining `i`. Inline browser construction
checks `[2,1,0]`, `[4,3,2,1,0]`, and `[0]` across cases. `web/cases.js` owns inputs
and reports; the adapter evaluates ordinary definitions; `web/replay.js` only
presents captured transformation samples. No notebook function changes or
measured-family abstraction are implied by this single-case interaction.

**Abstraction evidence.** The measured family is a strong candidate for a recipe
with explicit case keys and accessible per-case evidence. The notebook keeps
separate case roots because concatenation does not combine their active reduction
metadata. `Sweep` already presents parameter cases, but it does not by itself
supply this reusable measured arrangement. Difference/shift ergonomics can be
considered independently of the family and its evidence representation.
