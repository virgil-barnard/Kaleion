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

1. Open **07_equal_sums.json**. The selected object is **Moving pairs**. Workspace
   shows its sources and measurements together; Connections exposes their named
   definition paths. Choose Focus to inspect the selected object alone.
2. Click **Undo** once: equal sums collapse onto seven positions, retaining all
   sixteen pairs. Click **Redo**: ranks separate them into the stacks again.
3. Below the canvas, drag **Replay captured transformation** slowly from left to
   right and back. **Play replay** runs it; **Return to result** restores the
   applied picture. Scrubbing changes the presentation, not the mathematics.
4. Choose **Occurrences**, then the occurrence-list entry **12 · value 3**. Follow
   its keyed read of **3** to the measured rank. Choose **View measurement and
   contributors** to see the three earlier pairs in that sum. Close the paired
   view when finished.
5. Select **Counts**, then choose occurrence **8 · value 0**. Its count is zero
   with no contributors. The declared bin exists even though no pair sums to 8.

To make one small change yourself: choose **Objects**, select **Moving pairs**,
then **Options → Create a relation**. Name it `My sum four`. In the initial
`value = 0` formula, click `0` and change it to `4`, then finish that formula edit.
Choose **Preview**, then **Apply**. Three pairs should be highlighted. **Save**
downloads your extended workspace; the source file in this folder is unchanged.

To compose by connecting objects, see the [shared workspace walkthrough](../../docs/SPATIAL_WORKSPACE.md#try-this-increment).
View-panel layout is temporary; Save retains the mathematical workspace and its history.

## Four starting points

| Canvas | Loaded arrangement | What to inspect next |
| --- | --- | --- |
| [07 · Equal sums](07_equal_sums.json) | Sixteen pairs stacked by sum and rank | **Counts** are `[1,2,3,4,3,2,1,0,0]`; **Energy** is 44. Two saved moves gather and stack the same pairs. |
| [06 · Young layers](06_young_layers.json) | Ten original cells packed into one row | **Layers** are `[3,3,2,1,1]`; **Offsets** are `[0,3,6,8,9]`. Inspect offset 8, then one of its three measured layer contributors, then that layer's cells. Two saved moves turn and pack the cells. |
| [02 · Floor sums](02_floor_sums.json) | Two separated pieces reassembled into a rectangle | **Lower total** and **Upper total** are both 30; **Overlap total** is 0. Select **Overlap**, then try **Cases** with `a=12`, `b=8`: the totals become 40 and 40 with 3 overlapping cells in a 77-cell rectangle. |
| [05 · Radon reconstruction](05_radon_reconstruction.json) | Reconstructed image values displayed as nine heights | **Backprojection** is a weighted measurement. Inspect one value, a contributor, its weight read, and then the line sum's contributing pixels. **Recovered fields** retains both `recovered` and `remainder`. |

For each file, the last object tab is the movement target: **Moving pairs**,
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
it available again. This increment adds no controls or playback changes. Camera,
selection and unfinished drafts remain temporary view state.

These are focused prototypes of lessons 02, 05, 06 and 07, with explicit 2D
placements for this viewer. The Young turn is planar; Radon uses a small weighted
image and a flattened height profile. They do not reproduce all notebook stages,
3D presentation, or all eleven lessons. The files stay within the current studio
limits of 2000 occurrences per evaluated operation and 40 retained history edits.

## Reproduce or customize the prototypes

The four small recipes and their motion edits are visible in
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
