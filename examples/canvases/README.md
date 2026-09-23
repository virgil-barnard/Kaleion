# Open a worked canvas

Start with **[07_equal_sums.json](07_equal_sums.json)**. It opens with sixteen
ordered pairs already stacked by their sums, plus their sources, counts and ranks.
You can inspect everything and continue constructing with the existing tools.

These are ordinary saved Kaleion workspaces. Use the **construction studio**:

```sh
source .venv/bin/activate
python3 -m examples.studio
```

Open http://127.0.0.1:8765 on your computer. Save any current work you want to keep,
then click **Open** and choose a JSON file in this folder. There is no generation
step required. The older `build/touch-study.html` is a separate bounded sketch;
it cannot open these files.

## Your first five minutes

1. Open **07_equal_sums.json**. Select **Moving pairs → Details**. Its source
   objects stay visible. **How this is made** shows the coordinates and keyed
   read from Ranks. Follow that input, then **Back to Moving pairs**.
2. Close Details. Click **Undo**, then **Redo**. Ranks separate the sixteen pairs
   into stacks. Scrub **Replay saved movement** below the canvas; **Show result**
   returns to the saved picture. Other objects stay on the board.
3. Tap a cell to inspect its value. To reach a coincident or hidden item, use
   **Appearance → Choose an item**. Follow a keyed read, then **View measurement
   and contributors**. The evidence opens beside the working canvas.
4. Select **Counts** and inspect item **8 · value 0**. The declared bin exists
   even though no pair sums to 8, and its receipt has no contributors.
5. Try **Details → Relation**. Choose one input `value`, Even numbers, Preview,
   then Apply. Or open **03_incidence_box.json**, select **X region → Details →
   Sum / count**, and count along `k` to make a reusable plane of counts.

**Connect** exposes named definition paths and reviewed combination proposals.
**Parameters** explicitly evaluates new mathematical results. **Create** makes a
Vector, Grid or Cube, with tuple-only locations or values from an index formula.
[The continuous-canvas guide](../../docs/CONTINUOUS_CANVAS.md) describes the current
controls and the distinction between changing mathematics, appearance and replay.

**Save → Canvas and view** retains appearance, selection and camera with the exact
workspace. **Mathematics only** exports for Python. Drafts stay in the current tab.
These five existing integer lesson files remain schema 1. Adding tuple-only
objects will make the next mathematical export schema 2.

## Five starting points

| Canvas | Loaded arrangement | What to inspect next |
| --- | --- | --- |
| [07 · Equal sums](07_equal_sums.json) | Sixteen pairs stacked by sum and rank | **Counts** are `[1,2,3,4,3,2,1,0,0]`; **Energy** is 44. Two saved moves gather and stack the same pairs. |
| [06 · Young layers](06_young_layers.json) | Ten original cells packed into one row | **Layers** are `[3,3,2,1,1]`; **Offsets** are `[0,3,6,8,9]`. Inspect offset 8, then one of its three measured layer contributors, then that layer's cells. Two saved moves turn and pack the cells. |
| [02 · Floor sums](02_floor_sums.json) | Two separated pieces reassembled into a rectangle | **Lower total** and **Upper total** are both 30; **Overlap total** is 0. Select **Overlap**, then try **Cases** with `a=12`, `b=8`: the totals become 40 and 40 with 3 overlapping cells in a 77-cell rectangle. |
| [03 · Incidence box](03_incidence_box.json) | A 240-cell box with three 3D relation regions | Select **X region**, choose **Selected**, then **3D**. Under **Chart and slice**, choose **Slice z → 2**. Volumes are 86, 80 and 74; **Shared cells** has zero matches. This file starts with captured results and no motion edits. |
| [05 · Radon reconstruction](05_radon_reconstruction.json) | Reconstructed image values displayed as nine heights | **Backprojection** is a weighted measurement. Inspect one value, a contributor, its weight read, and then the line sum's contributing pixels. **Recovered fields** retains both `recovered` and `remainder`. |

For the four motion examples, the last object tab is the movement target: **Moving pairs**,
**Cells**, **Pieces**, or **Image heights**. Select it before Undo/Redo to see its
motion. Two Undo clicks in the sum and Young canvases reach the original layout;
Redo walks forward again. Object tabs are named results, not chronological steps.

In the Radon canvas, compare **Recovered fields.recovered** with **Image.value**
using keys `(u,v)` and **Pixel domain** as the expected domain. The size-three
case agrees. Change `p` to `4` through **Cases → Evaluate case → Apply case**:
at `(u,v)=(0,0)`, the recovered value is −1, the source value is 0, and the division
remainder is still 0. Exact division alone does not establish reconstruction.
These integer cases are distinct from replaying a recorded placement.

## What is saved, and what is still awkward

Each file contains definitions, captured results, contributor evidence and
recorded undo/redo paths. Opening and inspecting them does not evaluate the graph.
Ordinary new constructions and parameter changes use the same Preview/Apply
controls as a blank canvas. Save/Open preserves the mathematical work and history.

The existing scrubber appears only after an action or Undo/Redo and is cleared
when switching objects or opening a file. The **Undo, Redo** sequence above makes
it available again. The [shared scene](../../docs/SHARED_SCENE.md) adds cells,
points, 3D orbit, slices and saved scene choices; it does not change replay.
Focus/evidence navigation and unfinished drafts remain temporary view state.

These are focused prototypes of lessons 02, 03, 05, 06 and 07. Lesson 03 adds an
actual three-coordinate placement; the other four use explicit 2D placements.
The Young turn is planar; Radon uses a small weighted image and a flattened
height profile. They do not reproduce all notebook stages or all eleven lessons.
The files stay within the current studio
limits of 2000 occurrences per evaluated operation and 40 retained history edits.

## Reproduce or customize the prototypes

The five small recipes and the four examples' motion edits are visible in
[save_canvases.py](../save_canvases.py). No viewer-specific operation or new saved
format is involved. To generate another copy without overwriting these examples:

```sh
python3 examples/save_canvases.py --out build/canvases
```

Regeneration creates new source identities. Compare mathematical results and
recorded endpoints, not byte-for-byte equality with an independently built file.

The tests check the committed files against independent finite expectations,
including saved evidence, reversed motion and continued authoring. Browser checks
open these same files through the existing controls.

```sh
python3 -m unittest discover -s tests -p test_saved_canvases.py -v
node docs/studies/check-saved-canvases.cjs
```

The browser check is optional and uses an existing Playwright/Chromium installation
with the same environment options as the
[studio browser gate](../../docs/CONSTRUCTION_STUDIO.md#validation-and-reproduction).
