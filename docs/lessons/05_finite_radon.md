# 05 · Can line counts recover an image?

**Status:** available. [Open the notebook](../../notebooks/05_finite_radon.ipynb).

**Question:** Which measurements determine every value of a picture?

**Background:** modular arithmetic, a prime modulus, integer grids, and summation.
The notebook introduces the finite affine lines it needs.

## Construction

Use a binary image on the `p × p` grid over integers modulo prime p. Lines satisfy
`y - m*x = t (mod p)`, with a further vertical family `x=t`. The p+1 families
contain p lines each. Construct the finite point/line pair domain and measure the
incidence of illuminated points by retained `(m,t)` keys.

Treat these line counts as an arrangement. Bind each measured value onto its incident
pixels and reduce again to obtain `B(P)`. The total `T` comes from the line measurements
in a single parallel family. Then

\[
B(P)=p f(P)+T,\qquad f(P)=\frac{B(P)-T}{p}.
\]

Every other pixel shares exactly one line with P, while P itself lies on p+1 lines.
This proves the formula. Multiplicative inverses of nonzero coordinate differences
are where primality enters the argument.

## Narrative

1. Compare diagonal and opposite-diagonal 2×2 patterns: identical row/column counts
   fail to identify the selected subset.
2. Add modular directions. Scrub all lines and view each measured count alongside
   the highlighted source points. Wrapped lines are incidences, not Euclidean segments.
3. Build backprojection and derive the exact inverse by counting multiplicities.
4. Use each direction's derived contribution field to lift a second arrangement.
   Subtract T and divide by p to expose the image as heights. Undo the captured steps.
5. Compare original and recovered values at every key; show the residual arrangement.
6. Inspect one reconstructed pixel's measured lines and their exact contributors.
7. Edit the source and verify propagation. Then corrupt one line count: its p incident
   pixels become witnesses where the reconstruction numerator is not divisible by p.
8. Delete a complete recovered row. An explicit pixel domain reports the missing
   keys—including missing zero values—separately from numerical residuals.

## Experiments and limits

- Try prime sizes 2, 3, 5, and 7 and a different binary image expression.
- Use `sum(value=F.weight)` for weighted integer images. The same proof applies to
   signed values as well; a cardinality count alone would discard those weights.
- Remove a direction and ask which information remains. The displayed exact inverse
   requires all direction families and consistent measurements.
- A nonzero division remainder is evidence of failure. Zero remainders alone do not
   establish consistency for arbitrary corrupted data; remeasurement is another check.
- Modulo a composite integer is not the required prime field. Prime-power fields
   need their own field operations, not merely a different integer modulus.

The dense pair domain has `p^3(p+1)` occurrences. Large scenes need a more economical
execution strategy. Reconstruction recovers **values on a declared domain**, not the
source's occurrence identities. The second arrangement has its own persistent points.

The standard construction is a finite Radon transform; its prime-grid inverse is
described in the [scikit-image documentation](https://scikit-image.org/docs/stable/api/skimage.transform.html#skimage.transform.frt2),
which also cites Kingston and Svalbe's work on periodic image arrays. Kaleion uses
its own explicit direction convention and no external inversion dependency.

Exports go to `build/notebooks/finite-radon/`: five offline HTML figures, construction,
motion, corrupted-measurement, and missing-domain workspaces, finite checks, and
`pixel-explanation.json`.

## Transfer to the construction studio

The [weighted-evidence investigation](../WEIGHTED_EVIDENCE.md) constructs a
size-three, integer-valued variant through the shared UI. Ordered tuple keys
connect line sums and backprojection; recovered/remainder attributes keep exact
checks visible. A measurement-driven placement uses those recovered values, and
receipt navigation follows a weighted contribution through its actual line sum
and the copied image-field read. Returning preserves selection and camera.

The accompanying offline case modulo four also shows a wrong reconstructed
value with zero division remainder. Integrality alone does not certify the
reconstruction; the required incidence structure remains an assumption. This
transfer does not change the notebook or claim full UI parity with its case
editing, staged 3D animation, comparisons, and corruption investigation.

## Functions and authoring scaffolding

The [notebook](../../notebooks/05_finite_radon.ipynb) defines four top-level functions.
See the [cross-lesson inventory](HELPER_INVENTORY.md) for related recipes.

| Local function | Responsibility and assumptions |
| --- | --- |
| `heatmap(snapshot, names, maximum)` | Render that matrix with shared scales and labels. |
| `check_reconstruction(captured)` | Check the binary source, line sizes and counts, direction coverage, exact divisibility, and finite keyed equality of recovered and source values on the declared pixel domain. |
| `line_explorer(captured)` | Build synchronized image/measurement panels. Frames highlight captured point–line incidences and the corresponding measured count; they do not reevaluate a relation. |
| `explain_pixel(captured, key)` | Use `Inspection` to follow backprojection weights to line measurements, then sampling bindings to image pixels; retain the lesson's exact inverse arithmetic and format its explanation. |

**Shared functions used.** [snapshot_views.py](../../notebooks/snapshot_views.py)
reexports lookup/comparison from `kaleion.comparison` for compatibility and keeps
rectangular presentation locally. The same exact comparison serves the studio. It
provides `keyed_values` with explicit `keys=("u", "v")` or `keys=("m", "t")`, and
`rectangular_values` with explicitly chosen x/y field names, and
`compare_keyed_values` with an explicitly declared pixel domain. Keys must be unique
exact integers; rectangular output requires all pairs of the observed axis labels.
Zero values remain zeros, absent cells fail, and axes are sorted independently of
storage or placement. Comparison keeps missing and unexpected keys separate on
both sides and computes exact residuals only for shared keys. The public
`animation_figure` presents the measured lifts; custom heatmaps and line
exploration use Plotly directly. Public `Inspection.find`, `measurement`,
`bindings`, and `item` supply the saved joins. A backprojection contributor's
weight is the line count it read, distinct from that pair occurrence's label.

**Studio scaffolding, separate from notebook counts.** `web/expressions.js` edits
composite keys; the adapter lowers them to `vector`; `web/receipts.js` presents
weight and field-read receipts; `web/evidence.js` presents/restores paired views.
All numerical evidence comes from the existing captured inspector. The browser
investigation needs no Radon-specific UI function or core subclass.

The [parameter-case follow-up](../PARAMETER_CASES.md) adds `web/cases.js` for
named integer inputs and per-object case reports, and `web/replay.js` for captured
presentation samples. The adapter's `preview_case` uses the existing evaluation
contract; committing and restoring use existing captures. Inline browser work
declares `p`, builds symbolic image/line extents, and reuses `$p` in incidence and
inverse arithmetic. It changes 3 to 4, observes wrong recovery with zero remainder,
and follows five line contributions. This is separate from the unchanged notebook's
four local functions; no parameter-specific Radon helper is added to the application.

**Inline scaffolding.** The notebook defines the binary image, a point–line
product domain using `Product(point=pixels, line=lines)` and its source-field
reads, incidence, counts, backprojection, exact quotient/remainder, and
residual. Direction-by-direction displacement, captures, reverse sampling,
source edits, deliberately corrupted counts, a deliberately deleted recovered row,
and exports are assembled in cells.
The dense sampling domain has `p^3(p+1)` occurrences, so product construction also
carries a real execution cost.

**Abstraction evidence.** The former `field`/`matrix` pair now shares a strict,
read-only adapter contract with 04, without hiding the incidence or reconstruction.
`check_reconstruction` supplies the independently declared full key domain to the
shared comparison report: an observed-domain pivot cannot discover an entirely
missing row or column. The missing-row counterexample demonstrates the difference
between an absent occurrence, a retained zero, and a nonzero residual. The
product-domain recipe is now shared with 07 through `Product`; 10 and 11 remain
candidate consumers. It hides ordinal grid/binding assembly while exposing source
roles, multiplicity, and cost. Pixel and line keys stay explicit attributes. The shared captured inspector
now removes the manual point/line/pixel joins from `explain_pixel`; its output also
retains read expressions and scoped driver references. The inverse formula and
division checks remain visible mathematical choices. The
[exploration workflow](../EXPLORATION_WORKFLOW.md) compares this with 04 and states
the query limits; a generic automatic theorem explanation is not provided.
