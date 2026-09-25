# 04 · Three measurements lift a plane

**Status:** available. [Open the notebook](../../notebooks/04_measured_motion.ipynb).

**Question:** Can counts from three solids make a separate plane become flat?

**Background:** lesson 03, or its largest-normalized-coordinate rule introduced in
this notebook. No new Kaleion primitives are required.

## Construction and pointwise statement

For each `(x,y)` in the common footprint, count selected z coordinates:

\[
h_X(x,y)=\#\{z:(x,y,z)\in X\},\qquad h_Y,h_Z\text{ similarly}.
\]

Construct an independent plane at height zero and move it in three stages by
`h_X`, `h_Y`, and `h_Z`, aligned by the retained `(x,y)` keys. For pairwise coprime
parameters, every column contains exactly `c-1` singly counted points, hence

\[
h_X+h_Y+h_Z=c-1\quad\text{at every retained key}.
\]

## Narrative

1. Read the incidence definitions and the three measured heatmaps.
2. Predict what three successive lifts will do to a new plane.
3. Scrub intermediate surfaces, reach a flat endpoint, and undo every step.
4. Explain flatness by partitioning each column; connect the upper surface to
   `c-1-max(floor(cx/a), floor(cy/b))`.
5. Change to `(6,4,5)` and inspect the discrepancy field. A bump at `(3,2)` reaches
   height six instead of four.
6. Follow that target point to driver values `(2,2,2)`, then to original contributors.
   Both X and Y counted z coordinates 1 and 2.
7. Reopen the saved workspaces and verify that contributor identities and pending
   redo survived.

## Experiments

- Choose another pairwise coprime triple. Predict the reference height first.
- Change the retained keys or reduce along another common axis.
- Inspect a zero-count column; its displacement should be zero, not unavailable.
- Change a relation and examine the exact integer discrepancy before proposing an equality.

## Software implications

The mathematical sequence is a pushforward of counting measure onto a key domain,
followed by a pullback through the target's keys and a displacement operation.
Measured values and motion remain separate: every calculation reads exact endpoints,
while frames interpolate a recorded path.

The notebook includes an explicit contributor explanation keyed by `COLUMN`.
`Inspection` now follows each actual captured move's keyed read to its measurement
and original contributors. Clickable cross-highlighting remains future presentation work.
The example does not infer an inverse from a cardinality, and it does not assert
that equal counts establish identical source occurrences.

Exports go to `build/notebooks/measured-motion/`: four offline HTML figures,
measurement and motion workspaces, finite-case reports, and `column-explanation.json`.
The 3D animation is interactive HTML, not an MP4 recording.

## Functions and authoring scaffolding

The [notebook](../../notebooks/04_measured_motion.ipynb) defines five top-level
functions and one nested function. See the [cross-lesson inventory](HELPER_INVENTORY.md).

| Local function | Responsibility and assumptions |
| --- | --- |
| `height_maps(captured)` | Show the three measured height fields with a common color scale. |
| `plane_motion(captured, frames, captions)` | Extend the public animation viewer with logical-neighbor edges and a reference plane; keep the vertical range fixed over playback. |
| `plane_motion.grid(frame)` | Nested renderer: locate each logical edge's endpoints by occurrence identity. This path assumes identities persist through the move. |
| `inspect_case(captured)` | Compare the measured total with an independent constant-height snapshot on the declared footprint; check formulas, placement/value agreement, and identity preservation; return exact residual witnesses for the finite case. |
| `discrepancy_figure(captured)` | Pair the lifted endpoint with an exact excess heatmap. Some reference labels and bounds are specific to the chosen counterexample. |
| `explain_column(captured, key)` | Walk the three move/value-update stages using `Inspection`; format their matched driver measurements and source coordinates for this lesson. The stage names and presentation remain local. |

**Shared functions used.** [snapshot_views.py](../../notebooks/snapshot_views.py)
provides `keyed_values(snapshot, keys=("u", "v"))`,
`rectangular_values(snapshot, x="u", y="v")`, and `compare_keyed_values`.
Lookup/comparison are now compatible reexports from `kaleion.comparison`, shared
with the studio; rectangular presentation remains beside the notebooks.
The lookup rejects duplicate or
noninteger keys; the rectangular adapter requires a complete product of observed
axis labels and returns ascending axes with rows indexed by y, columns by x. Neither reads
placement nor fills missing cells with zero. Comparison aligns the measured and
reference snapshots on an independently declared finite domain and reports exact
left-minus-right residual witnesses. `plane_motion` wraps the public
`animation_figure`; the other views use Plotly directly. Public
`Inspection.find`, `bindings`, `measurement`, and `item` replace the local key/ID
joins. Receipts include the actual target input, matched key, driver reference,
and field read; they do not reconstruct correspondence from the displayed plane.

**Inline scaffolding.** Three incidences are reduced while retaining `(u, v)`;
explicit keyed bindings lift an independently constructed plane. The notebook
registers the roots needed for explanations, stages the displacements and undo,
samples captions/frames, and captures alternative cases and exports.

**Abstraction evidence.** The former `keyed`/`field_matrix` pair and 05's
`field`/`matrix` now share read-only captured-data adapters. Key and rectangular-domain
validation is independent of Plotly and is covered by adversarial tests. An
entirely absent axis label cannot be inferred from observed keys; `inspect_case`
therefore supplies the full expected key domain to the finite comparison report.
`explain_column` now obtains driver alignment through the shared captured query.
It still knows this construction has three paired value-update/move stages, so it
is a lesson narrative adapter, not an automatic explanation of any graph.
The [exploration workflow](../EXPLORATION_WORKFLOW.md) compares this boundary with
05's weighted backprojection and names the remaining unsupported read kinds.

**Saved-canvas adaptation.** `measured_plane()` in
[save_canvases.py](../../examples/save_canvases.py) reuses `ownership_regions()`
from the lesson-03 adaptation, reduces X/Y/Z along `k` retaining `(i,j)`, and
records three lifts of an independent footprint. It uses `(5,4,3)` to keep the
interactive case small: twelve points reach height two. **Expected height** and
**Footprint** supply independent value/domain inputs to the existing comparison
instrument. Changing to `(6,4,5)` exposes a residual two at logical key `(2,1)`.
The [walkthrough](../CANVAS_TUTORIAL.md) connects this to singleton ownership;
the shared studio supplies the 3D scene, captured reverse paths and receipts.
This adds no notebook functions, video export helper, or new backend primitive.
