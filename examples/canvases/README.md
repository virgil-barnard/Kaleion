# Open a worked canvas

Run the construction studio in your existing environment:

```sh
source .venv/bin/activate
python3 -m examples.studio
```

Open http://127.0.0.1:8765. **Open** lists seventeen worked examples and a blank canvas.
Choose a title to read what it demonstrates, then **Load example**. Loading replaces
the current workspace, so save work you want to keep first. **Choose a file** still
opens your own JSON. These committed files need no generation step. The older
`build/touch-study.html` is a separate bounded sketch and cannot open them.

For a guided construction, choose **Open → Start walkthrough**. It begins with
a blank canvas, builds a triangular relation, counts its columns, moves independent
markers using those counts, follows contributors and compares a formula. The
[full tutorial](../../docs/CANVAS_TUTORIAL.md) extends this to ordered packing,
3D motion and the quotient-box equality with an assumption-breaking case.
The guide's Next/Previous buttons only change instructions; use the ordinary
controls to do the work.

## Starting points

| Title in Open | File | What to try |
| --- | --- | --- |
| Blank canvas | [00_blank.json](00_blank.json) | An empty workspace for your own construction or the walkthrough. |
| Remainder fibers and hidden carries | [12_residue_fibers.json](12_residue_fibers.json) | Fold 24 integers, separate them by measured ranks, cycle within fibers by measured period. Compare zeros/twos with a unit field; try `(7,5)`. [Lesson and from-blank instructions](../../docs/lessons/12_residue_fibers.md). |
| Repeat, truncate and pad | [12_periodic_extension.json](12_periodic_extension.json) | Moving factor copies one measured period, then truncates by an explicit address list. Padded R joins declared zeros. |
| A relation supplies addresses | [12_guarded_addresses.json](12_guarded_addresses.json) | Inverse remainder addresses reorder unrelated identical labels in 3D. Try `a=14`; guarded consumers fail while the source relation remains. |
| Division in motion | [12_division_motion.json](12_division_motion.json) | Carry counts displace fibers, which wrap and take their derived remainder positions. Undo/Redo three stages on Moving table. |
| Quotient and remainder relations | [12_relation_matrices.json](12_relation_matrices.json) | Weighted extraction drives a cyclic shift. Compare composed/direct Q by `(n,q)`; `(12,8)` produces 36 extra matches. |
| Euclidean step · 3 and 4 become 7 and 4 | [12_euclidean_step.json](12_euclidean_step.json) | An explicit domain extension, shear and reassembly; 28 exact values agree by declared destination keys. |
| Euclidean step · 4 and 7 become 11 and 7 | [12_euclidean_next.json](12_euclidean_next.json) | The same two stages after exchanging generator roles. Try `q=2`. |
| First motion · counts become heights | [00_first_motion.json](00_first_motion.json) | Counts `[4,3,2,1,0]` move five zero-labeled Markers. Undo, Redo, inspect a height's contributors. |
| Pack a triangle | [01_triangle_packing.json](01_triangle_packing.json) | Ten selected cells pack into a strip using ranks and offsets `[0,4,7,9,10]`. Follow an offset to earlier measured counts. |
| Three measurements lift a plane | [04_measured_plane.json](04_measured_plane.json) | Three saved lifts bring 12 points to height two. Undo three times, then Redo each lift. Change to `(6,4,5)` and compare the nonflat result with Expected height. |
| A box of ones | [03_cell_coverage.json](03_cell_coverage.json) | Compare Cell owners with One per cell on Box, all keyed by `(i,j,k)`: 24 equal values. A static comparison canvas. |
| When two regions claim a cell | [03_tied_coverage.json](03_tied_coverage.json) | The same comparison at `(6,4,5)` exposes two double-counted cells: 62 counted versus volume 60. Joint gcd one is insufficient. |
| Two regions fill a rectangle | [02_floor_sums.json](02_floor_sums.json) | Select Pieces and Undo/Redo its reassembly. Lower and Upper total are 30 each. Change Parameters to `a=12,b=8`: totals 40 and 40 include three shared cells in a 77-cell rectangle. |
| Explore the larger incidence box | [03_incidence_box.json](03_incidence_box.json) | The original 240-cell `(11,7,5)` case. X/Y/Z volumes are 86, 80, 74. Static 3D regions and measurements, with no recorded movement. |
| Recover an image from line sums | [05_radon_reconstruction.json](05_radon_reconstruction.json) | Nine image values become heights. Follow Backprojection weights through measured line sums to source pixels. |
| Turn and pack Young layers | [06_young_layers.json](06_young_layers.json) | Layers `[3,3,2,1,1]` produce offsets `[0,3,6,8,9]`. Two saved moves turn and pack Cells. |
| Gather pairs by their sums | [07_equal_sums.json](07_equal_sums.json) | Sixteen Moving pairs gather then stack. Counts `[1,2,3,4,3,2,1,0,0]` retain zero bins; Energy is 44. |

## Motion and evidence

The chooser selects the movement target for each of the fourteen motion examples.
Use **Undo**, then **Redo** to expose **Replay saved movement**. Young layers and
Equal sums have two saved edits; Measured plane has three. Select their target
before traversing those edits. History is workspace-wide, not a separate stack
for each object. Object names are results, not chronological steps.

**Details → How this is made** shows the actual construction and earlier inputs.
Tap an item, or use **Appearance → Choose an item** to reach coincident/hidden
occurrences. Follow a keyed read, then **View measurement and contributors**.
Inspect a zero count as well as a nonzero count. Details, evidence and the main
canvas retain their distinct meanings.

To make your own motion, choose **Details → Arrange / move**, or use **Combine → Drive a
transformation** with explicit matching keys. Choose coordinates, displacement
or a cyclic shift; [Division in motion](../../docs/DIVISION_MOTION.md) builds
these from a blank canvas. Dragging an object
name only moves its view. **Parameters** evaluates a new mathematical case; the
playback scrubber interpolates an already recorded path and never supplies inputs.
The [continuous-canvas guide](../../docs/CONTINUOUS_CANVAS.md) describes these controls.

## Compare and vary

In the box-ownership canvases, compare **Cell owners.value** with
**One per cell.value**, using `(i,j,k)` on both sides and **Box** as expected domain.
The pointwise all-ones statement is stronger than matching volume totals. Its
sum is the volume; the scalar volume is not itself an all-ones object.

In the plane canvas, compare **Lifted plane.value** with **Expected height.value**
by `(i,j)`, expected domain **Footprint** by `(i,j)`. The small coprime case is
flat. At `(6,4,5)`, logical column `(2,1)` has height six versus four.

In Radon, compare **Recovered fields.recovered** with **Image.value** by `(u,v)`
and expected domain **Pixel domain** by `(u,v)`. The size-three case agrees.
Change **Parameters → p** to `4`, **Preview results → Keep results**. At `(0,0)`,
the recovered value is −1, the source value is zero, and the division remainder
is still zero. Exact division alone does not establish reconstruction.

For 3D cases, **View → 3D** sets a camera angle; **View → Selected** centers the
selected object. **Appearance → Points** and **Chart and slice** offer lighter
views. For a placed box use **Slice z**; logical charts use their chosen indices.
The small plane/box captures are easier starting cases than the 240-cell example.
These choices are not an established orbit-performance improvement.

## What is saved

Each file contains definitions, captured results, contributor evidence and any
recorded undo/redo paths. Opening and inspecting them does not evaluate the graph.
New constructions and parameter changes use the same Preview/Apply controls as
a blank canvas. **Save → Canvas and view** also retains appearance, selection,
offsets and camera; **Mathematics only** exports a core workspace for Python.
Drafts, guide progress and comparison reports remain temporary UI state.

The existing replay strip appears after an edit or Undo/Redo and is cleared when
switching objects or opening a file. This is not yet a browsable timeline of all
previous movements. These integer examples remain schema 1; adding tuple-only
objects makes the next mathematical export schema 2.

The examples are focused adaptations of lessons 02–07 and a new introductory
triangle. They do not reproduce every notebook stage or the finite-field code
lessons. Shared UI primitives should eventually make those investigations
constructible too. Captures use limits of 2,000 occurrences per evaluated operation
and 40 retained history edits.

## Reproduce or customize

[save_canvases.py](../save_canvases.py) and [division_relations.py](../division_relations.py)
contain the ordinary construction recipes.
There is no viewer-specific operation or saved-format addition. Generate copies
without overwriting the committed examples:

```sh
python3 examples/save_canvases.py --out build/canvases
python3 examples/save_canvases.py --out build/canvases --only 00_first_motion 04_measured_plane
python3 -m unittest discover -s tests -p test_saved_canvases.py -v
node docs/studies/check-canvas-tutorial.cjs
```

Regeneration creates fresh source identities; compare mathematical results and
recorded endpoints, not bytes from independent builds. The offline tests inspect
the committed captures, zero groups, exact comparisons, contributor references,
reverse paths and continued authoring. The current browser gate recreates the
tutorial with public controls and opens every catalog entry. Earlier saved-canvas
scripts document older UI generations.

The browser gate is optional and uses an existing Playwright/Chromium installation
with the environment options in the
[studio validation guide](../../docs/CONSTRUCTION_STUDIO.md#validation-and-reproduction).
