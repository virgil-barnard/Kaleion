# 03 · Three incidences fill a box

**Status:** available. [Open the notebook](../../notebooks/03_three_incidence_box.ipynb).

**Question:** What replaces a reciprocal floor sum in three dimensions?

**Background:** lesson 02, Cartesian coordinates, and the difference between a joint
gcd of one and pairwise coprimality.

## Construction and statement

Use `D = {1,...,a-1} × {1,...,b-1} × {1,...,c-1}`. The incidence X selects points
where `x/a` is a largest normalized coordinate; Y and Z use the other coordinates.
Weak inequalities deliberately include ties in each qualifying incidence.

For pairwise coprime `a,b,c > 1`,

\[
\begin{aligned}
&\sum_{x=1}^{a-1}\lfloor bx/a\rfloor\lfloor cx/a\rfloor
+\sum_{y=1}^{b-1}\lfloor ay/b\rfloor\lfloor cy/b\rfloor\\
&\quad+\sum_{z=1}^{c-1}\lfloor az/c\rfloor\lfloor bz/c\rfloor
=(a-1)(b-1)(c-1).
\end{aligned}
\]

## Narrative

1. Rotate the box and isolate X, Y, or Z. Ask how an ownership rule can be stated
   independently of the camera and mesh.
2. Scrub sections orthogonal to a chosen axis. Each section of its corresponding
   incidence is a rectangle with two floor-quotient side lengths.
3. Assemble the separated pieces and undo along their captured paths.
4. Use the largest-coordinate argument for coverage and pairwise coprimality for
   absence of ties.
5. Inspect pair and triple intersections when the assumptions change.

## Evidence and challenges

- `(11,7,5)` gives `86 + 80 + 74 = 240` with no shared voxels.
- `(6,4,5)` has joint gcd one but a shared pair of points in X and Y.
- `(4,6,8)` also exercises a triple intersection; inclusion–exclusion must add it back.

Try each `SLICE_AXIS`, including sections of area zero. Keep the distinction between
logical coordinates, unit-cell counts, and mesh styling explicit. The notebook's
small-volume budget is a display limit, not part of the mathematical theorem.

## Next connection

The sections in this notebook count different incidences along their respective
axes. In [lesson 04](04_measured_motion.md), all three are reduced along **one common
axis**. That produces a common key domain whose counts can drive another arrangement
and reveal a stronger, pointwise equality.
