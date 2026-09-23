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

## Functions and authoring scaffolding

The [notebook](../../notebooks/03_three_incidence_box.ipynb) defines nine top-level
functions and two nested functions. Most support presentation rather than the
mathematical construction. See the [cross-lesson inventory](HELPER_INVENTORY.md).

| Local function | Responsibility and assumptions |
| --- | --- |
| `inspect_box(state)` | Check a captured box against section-count formulas, shared identities, full coverage, and inclusion–exclusion; report the tested parameters and intersections. |
| `membership_codes(state)`; `membership_name(code)` | Encode membership in X/Y/Z as display bit flags and readable intersection labels. These are derived display data. |
| `mesh_vertices(positions)`; `voxel_trace(positions, centers, code)` | Build slightly inset unit-cell meshes and a Plotly trace. Gaps improve visibility; they do not change the counted volume. |
| `box_outline(extents)` | Draw the declared box boundary. |
| `volume_figure(state, positions=None, controls=True)` | Combine captured membership, voxel traces, filtering controls, bounds, and camera settings. Optional positions allow the same view to present a motion frame. |
| `slice_figure(state, axis)` | Present a rectangular section scrubber with captured counts. This particular view requires disjoint X/Y/Z membership and the notebook's known box ordering. |
| `slice_figure.slice_data(t)`; `slice_figure.title(t)` | Nested section extraction and caption helpers: select one array slice and read its measured count. |
| `motion_figure(state, samples, labels)` | Match captured occurrence identities to moving voxel positions and build multi-trace Plotly playback with stable colors and bounds. |

**Shared functions used.** No lesson helper module is used. The custom voxel and
slice figures use Plotly directly; core snapshots, motion, and workspace history
supply their data.

**Saved-canvas adaptation.** `incidence_box()` in
[save_canvases.py](../../examples/save_canvases.py) adds a focused ordinary
[workspace file](../../examples/canvases/03_incidence_box.json) with the box,
X/Y/Z regions, X sections, three volumes and shared-cell incidence. It uses
`(11,7,5)` and captures the initial results without motion. The shared studio
scene supplies cell/point marks, camera orbit and view slices; this helper owns
only the construction. It does not replace the notebook's proof, full comparison
cases or packing animation, and does not change the notebook function counts.

**Inline scaffolding.** Box construction, the three inequalities, intersections,
section counts, and displacement targets remain visible declarations. The lesson
also assembles staged edits, undo and sampling loops, alternative parameter
cases, and saved figures/workspaces.

**Abstraction evidence.** Reusable voxel and section adapters could shorten this
lesson without adding a new mathematical operation. A coordinated frame viewer
also overlaps with 04, 05, and 11. Rectangular indexing, disjoint membership, and
identity matching are separate contracts; none should become an implicit
restriction on all arrangements.
