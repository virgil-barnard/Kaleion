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

## Functions and authoring scaffolding

The [notebook](../../notebooks/11_cyclic_code_plane.ipynb) defines 22 top-level
functions and one nested function. They cover several different responsibilities;
their count is not a proposed count of core operations or classes. See the
[cross-lesson inventory](HELPER_INVENTORY.md).

| Local function | Responsibility and assumptions |
| --- | --- |
| `bit(word, degree)`; `binary_sum(left, right, width)` | Compose exact arithmetic for packed binary coefficients and their componentwise sum. Width is explicit; ordinary integer addition is different. |
| `polynomial_product(left, right, left_width, right_width)` | Build bounded binary coefficient convolution. This is a visible expression recipe, not a general polynomial engine. |
| `coefficients(packed)` | Expand a packed expression into seven coefficient slots, including zeros. |
| `cubic_remainder(items, modulus, highest_degree)` | Unroll a declared number of binary long-division steps, each a symbolic value transformation. Degree-three modulus and bounded input degree are part of the recipe. |
| `generator_rows(polynomial, dimension)` | Copy coefficient slots and assign each copy its cyclically shifted degree; return the copies and resulting matrix. |
| `generator_placements(copies, matrix)`; `generator_placements.rings(items, degree)` | Choose ring and matrix placements. The nested ring helper owns radius, angle, and height conventions. |
| `generator_turn()`; `support_turn()` | Describe custom presentation paths for generator-row turns and support rotation. The paths interpolate captured positions. |
| `span(matrix, dimension)` | Declare message/row/degree products, count selected contributions, take parity, and derive packed words and weights. Return intermediate definitions for inspection. |
| `dual_polynomial(polynomial)` | Enumerate bounded quotient candidates, require unique factor coverage, and reverse the five quotient coefficients into seven slots. |
| `cross_parities(left, right, left_dimension, right_dimension)` | Count row-pair overlaps and reduce them modulo two. |
| `parity_checks(matrix, dimension)` | Construct all 128 words' row checks, syndrome values, and zero-syndrome kernel; retain the intermediate counts. |
| `fano_supports(code, check_matrix)` | Pack check-matrix columns, select weight-three words, measure their order, and bind those words and columns onto a support product. |
| `fano_chart()`; `support_placements(supports, chart)` | Declare the seven chart positions and the ring, shifted-ring, and ranked-panel placements. Drawn geometry does not define incidence. |
| `field_model(polynomial, columns)` | Construct the bounded multiplication table, inverse-coverage guard, powers, coordinate dictionary, trace, and trace incidences. Return their definitions separately. |
| `multiply_by_alpha(points, field)` | Apply the exact field multiplication binding, then update exponent and column-coordinate annotations. This is the mathematical action presented by the motion. |
| `field_placements(points, chart)` | Put the same labeled points in exponent-ring and projective-chart coordinates. |
| `single_error_rule(syndromes)` | Declare no-error and single-bit candidates; require a unique candidate for each syndrome and measure the correction mask. |
| `sampled(transition, name, label, steps=25)` | Sample one captured transition and attach captions. This helper assembles presentation data. |
| `compact_workspace(workspace, filename)` | Write compact workspace JSON under the notebook's output directory and reconstruct a workspace from the same in-memory payload. This combines a file effect and a deserialization check; it does not read the saved file back. |

**Shared functions used.** [code_views.py](../../notebooks/code_views.py) provides
`binary_panels`, `fano_gallery`, and `linked_field_motion`. Its private
`_captured_lines` groups captured supports and `_line_path` chooses chart strokes;
neither constructs projective incidence. Those viewers use `xy_cells` and `style`
from [lesson_views.py](../../notebooks/lesson_views.py); the notebook directly uses
that module's `replay` and `save_figures` as well. The public `animation_figure`
and `write_mp4` handle further captured playback/export.

**Inline scaffolding.** Workspace registration, generator edits, seven cycle
steps, undo, identity colors, finite kernel/span and trace/support comparisons,
dictionary display, four counterexamples, and contributor explanations remain in
cells. Coordinated field playback pairs two recorded workspace edits at the same
progress; it is not an atomic multi-root action. HTML, video, and evidence exports
also require orchestration beyond the named recipes.

**Abstraction evidence.** `span`, `cross_parities`, and `parity_checks` repeat a
named-product → incidence → retained-count → parity construction. Quotient,
inverse, and syndrome selection repeat guarded assignment. These are candidates
for small composable recipes, with widths, keys, and coverage exposed. Playback
coordination, coefficient arithmetic, finite comparisons, and chart routing each
hide different decisions and should remain independently replaceable. A code
subclass would not automatically remove those four kinds of authoring work.
