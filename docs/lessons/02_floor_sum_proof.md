# 02 · Two incidences fill a rectangle

**Status:** available. [Open the notebook](../../notebooks/02_floor_sum_proof.ipynb).

**Question:** Why do two reciprocal floor sums add to the number of cells in a rectangle?

**Background:** inequalities, integer quotient, greatest common divisor, and counting
points in rows or columns. Define the floor function before reading its notation.

## Construction and statement

On `D = {1,...,b-1} × {1,...,a-1}`, define

\[
P=\{(x,y):by\le ax\},\qquad Q=\{(x,y):ax\le by\}.
\]

For coprime integers `a,b > 1`,

\[
\sum_{x=1}^{b-1}\lfloor ax/b\rfloor+
\sum_{y=1}^{a-1}\lfloor by/a\rfloor=(a-1)(b-1).
\]

## Narrative

1. Reorient the earlier quotient-region incidence. Its retained counts are exactly
   `floor(a*i/b)` for `0 <= i < b`; the first count is zero.
2. Construct both incidences on one universe. Isolate each, then display their union.
3. Count a column of P and a row of Q. Interpret their bounds as floors.
4. Move the separated pieces back to their declared slots. Ask whether any cell is
   missing or selected twice.
5. Explain coverage by ordering; explain disjointness by coprimality.
6. Relax coprimality and inspect the shared diagonal points.

## Explanation and counterexample

Every point satisfies at least one inequality. A shared point satisfies `ax=by`.
Writing `d=gcd(a,b)` shows exactly `d-1` interior shared points, so for arbitrary
positive integers greater than one the sum is `(a-1)(b-1) + d - 1`.

The default case `(11,7)` gives `30 + 30 = 60`. The `(12,8)` case gives
`40 + 40 = 77 + 3`. These numbers illustrate the argument; they do not replace it.

## Experiments and software implications

- Change the parameter pair and predict the overlap count before inspecting it.
- Switch weak inequalities to strict ones and identify the resulting boundary policy.
- Compare equality of cardinalities with equality of selected occurrence sets.
- Undo the packing and verify identity preservation along the recorded path.

This lesson requires explicit union/intersection on a shared universe and makes
boundary conventions visible. Unit-cell area is the counting measure, not the area
of the marker glyphs. Its extension is [three incidences in a box](03_three_incidence_box.md).
