# 11 · A code becomes a projective plane

**Status:** available. [Open the notebook](../../notebooks/11_cyclic_code_plane.ipynb).

**Question:** Can one seven-bit pattern explain a code, its dual, and a moving
finite projective plane?

**Background:** binary vectors and polynomial coefficients. The notebook introduces
generator/check matrices, Hamming weight, dual codes, projective points and lines,
an extension field, trace, and a Singer cycle as explicit finite constructions.
Lessons 09–10 offer another route into fields and projective geometry, but are not
required to execute or follow this lesson.

## Construction and narrative

1. Choose `g=1+x+x^3`, encoded by 11. Keep seven coefficient slots, including
   zeros. Make four copies, shift copy `r` cyclically by `r`, and unfold the rings
   into the generator matrix G. The 3D path preserves all 28 copied occurrences.
2. Enumerate the 16 messages. On the message/row/degree product, select terms where
   both the message bit and G entry equal one. Count retaining message and degree;
   reduce those integer counts modulo two to obtain output coefficients. Inspect
   two contributions whose parity is zero, and a zero group with no contributors.
3. Search all 32 possible degree-at-most-four quotients. Unique coverage selects
   `h=(x^7+1)/g`; reverse its coefficients and shift them to form H. Check every
   G/H row overlap, then all 128 masks: `ker(H)=span(G)` and `ker(G)=span(H)`.
   The code has weight distribution `1,7,7,1` at weights `0,3,4,7`; the dual has
   one zero word and seven weight-four words.
4. Read H's columns as the seven nonzero vectors of `F_2^3`. Count each codeword's
   support, retain the seven triples, and rank them by packed word label. Those
   measured ranks place the support copies in seven projective charts. Every point
   pair lies on exactly one triple; complements are exactly the nonzero dual words.
5. Use the same cubic to construct `K=F_2[t]/(g)`. Explicit bounded long division
   supplies multiplication and powers; inverse coverage checks the nonzero elements.
   A displayed linear coordinate dictionary sends `alpha^j` to column `H_j`.
   This constructs an incidence isomorphism with the plane formed from K as an
   `F_2` vector space.
6. Form `Tr(z)=z+z^2+z^4`. The seven conditions `Tr(a*z)=0`, for nonzero a,
   reproduce the seven line masks, while their complements reproduce the dual.
   Watch multiplication by alpha in synchronized exponent and projective charts.
   A seven-step Singer cycle returns the points, values, and identities; undo
   retraces the seventh step from captured state.
7. Derive the one-error correction mask by syndrome coverage. Zero syndrome has
   an explicit no-error candidate. Display sent, received, and decoded coefficients.
   The complete covering/coset-motion and spectral lessons remain future work.

## Names and equality scopes

| Object | Meaning of its labels | Relation being preserved |
| --- | --- | --- |
| Seven-slot code ring | Coefficients in `F_2[x]/(x^7-1)`; packed into `0,...,127` | Binary linear combinations and cyclic shifts |
| Code C and dual | Subspaces of `F_2^7` | Dot-product orthogonality |
| Column coordinates | Nonzero vectors of `F_2^3`; packed into `1,...,7` | A line has three vectors summing to zero |
| Field K | Coefficients of `1,alpha,alpha^2`; packed into `0,...,7` | Field addition and multiplication modulo g |
| Projective chart | Screen locations assigned to column keys | Logical point/line incidence, independent of distance |

Packing changes notation, not arithmetic. The plane is not a field. Its points
are one-dimensional subspaces of K over `F_2`; here each contains exactly one
nonzero representative. Its lines are two-dimensional subspaces with zero removed.
Code duality and projective point/line duality are also different concepts.

The dictionary T maps the polynomial basis `(1,alpha,alpha^2)` to the first three
columns of H, with binary linear extension. Checking `T(alpha^j)=H_j` gives
`H*c^T=T(c(alpha))`. Thus the polynomial-root and matrix-check descriptions agree.
For three distinct supported points, their zero sum gives their projective line.
Multiplication by alpha is invertible and `F_2`-linear, so it preserves these lines;
on exponents it becomes a cyclic shift. Smooth intermediate coordinates merely
present this discrete collineation.

## Experiments and witnesses

- Replace 11 by 13, encoding `1+x^2+x^3`; restart and rerun. Both offered cubic
  models are checked. Compare their coordinate dictionaries and identify what
  changes under relabeling.
- Pick two projective points and predict the third, first in H coordinates and
  then in field coordinates using the dictionary. This transfers the construction
  beyond replaying its default animation.
- Use h without taking its reciprocal. The notebook records every odd overlap;
  the default includes G row 0 and the erroneous H row 2.
- Use the noncyclic stencil 15. Its span contains word 68 but lacks its cyclic
  shift 9. The failed quotient root does not invalidate the independent span.
- Change two bits on the zero word. The one-error rule returns a different
  codeword. A decoder does not have access to undo's captured history.
- Use `t^3+1` as a field modulus. Inverse coverage fails for nonzero elements;
  the inverse-count witness remains available.
- Reorder generator, check, or measured-column occurrences. Bindings use the
  declared row/degree or field-element keys, rather than storage order.

## What this teaches the software design

The minimal recipe remains a named finite product, incidence, retained-axis
measurement, keyed binding, and placement. `span`, `parity_checks`, and
`field_model` are visible, bounded lesson recipes. This is not a general coding
library or a new field/polynomial class in the evaluator.

Following Parnas, the arithmetic convention belongs with the construction; chart
coordinates belong with placement; strokes, colors, and synchronized playback
belong with the viewer. `code_views.py` consumes captured data only. The two field
charts are two recorded workspace updates shown at the same progress, not a new
atomic multi-root history operation. A future coordinated-view authoring feature
should make that choice explicit without making a renderer own the action.

The coefficient convention and coordinate dictionary are useful future UI objects:
a novice should be able to ask what a label means and which relation a relabeling
preserves. The kernel/span and trace/code comparisons also strengthen the need for
an explicit finite comparison report with domains and witnesses. Today these are
visible assertions on captured results; no proof-assistant integration is claimed.

The notebook exports seven self-contained Plotly HTML figures, two MP4s, seven
captured workspaces, and contributor/dictionary explanations. The source remains
cleared. Mathematical and rendering evidence is recorded in
[VALIDATION.md](../../notebooks/VALIDATION.md).

## Sources and continuation

- [MIT: polynomial Hamming codes](https://math.mit.edu/~djk/18.310/Lecture-Notes/polynomial_hamming_codes_2007.html)
- [MIT: matrix Hamming codes](https://math.mit.edu/~djk/18.310/Lecture-Notes/matrix_hamming_codes_2007.html)
- [Sage: cyclic-code construction](https://doc.sagemath.org/html/en/reference/coding/sage/coding/cyclic_code.html)
- [Sage: Singer difference sets from extension fields](https://doc.sagemath.org/html/en/reference/combinat/sage/combinat/designs/difference_family.html#sage.combinat.designs.difference_family.singer_difference_set)

Continue with the [syndrome covering and spectral cancellation briefs](CODES_AND_DISCOVERY_PATHS.md).
A later extension can construct `PG(2,3)` from one-dimensional `F_3` subspaces of
`F_27`: 26 nonzero representatives become 13 projective points. Unlike the binary
case, scalar equivalence is visible and must be measured before taking the quotient.
