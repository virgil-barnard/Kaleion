# Kaleion notebooks

Start with [01_discovery_workbench.ipynb](01_discovery_workbench.ipynb). It is an editable walkthrough of the module, with interactive 2D/3D plots, parameter-case scrubbers, recorded motion and undo, and two embedded MP4 videos. It uses finite constructions and no external datasets.

[02_floor_sum_proof.ipynb](02_floor_sum_proof.ipynb) is a self-contained construction page for reciprocal floor sums. It places readable notation beside two incidences on a shared integer rectangle, checks their grouped counts and union/intersection, and animates packing and undo. The written argument proves the identity for all positive coprime parameters greater than one; exact finite examples also expose the `gcd(a, b) - 1` overlap correction. "Area" here counts unit cells, with explicit integer summation bounds. This notebook uses the existing symbolic Python API and does not introduce a text-language parser or proof assistant.

[03_three_incidence_box.ipynb](03_three_incidence_box.ipynb) constructs the three-dimensional analogue. The incidence with the greatest normalized coordinate owns each point of a shared integer box. For pairwise coprime parameters, rectangular cross-sections produce products of two floor quotients and the three volumes add to the box volume. Interactive voxel views, exact slice controls, and recorded packing/undo make the three pieces inspectable. Counterexamples distinguish pairwise coprimality from merely having a joint gcd of 1 and demonstrate triple-intersection accounting.

[04_measured_motion.ipynb](04_measured_motion.ipynb) derives three column-count arrangements and uses them as keyed motion drivers for an independent plane. Heatmaps, a 78-frame lift/undo animation, a discrepancy view, and contributor inspection connect a flat endpoint to a pointwise equality. The `(6,4,5)` counterexample exposes double-counting as a bump. All definitions are included, so the notebook can run independently of lesson 03.

[05_finite_radon.ipynb](05_finite_radon.ipynb) asks whether measurements determine an image. It starts with ambiguous row/column projections, builds modular lines over a prime field, and reconstructs every pixel from line counts. A line-selection scrubber and staged 3D reconstruction/undo demonstrate measured fields driving other arrangements. A source edit propagates through the computation; an altered line count produces exact-division witnesses. Removing a complete result row shows why missing keys, zero values, and residuals need separate reports. The default 5×5 case has 30 line measurements and a 144-frame reconstruction/undo animation.

[06_young_layers.ipynb](06_young_layers.ipynb) counts a Young diagram by columns and layers, constructs its conjugate, and turns the original cells through 3D. Measured prefix offsets pack the cells into a strip; an ordering counterexample shows what the counts forget. The default ten-cell example has 84 turn/pack/undo frames.

[07_additive_structure.ipynb](07_additive_structure.ipynb) measures how many ordered pairs give each integer sum. It introduces convolution, uses measured predecessor counts to stack equal-sum pairs, and derives additive energy in three ways. The default progression has energy 44; a scattered four-element set has energy 28. Its 84-frame stack/undo sequence also exports as an embedded 2D MP4.

[08_ehrhart_counts.ipynb](08_ehrhart_counts.ipynb) counts integer dilations of a triangle, keeps those cases as symbolic inputs to a measured family, and derives finite differences. The measurements drive independent probes in a 102-frame sequence. Interior/boundary comparisons explain reciprocity; a rational triangle demonstrates a period-two quasipolynomial. A separate embedded MP4 holds the exact dilation cases.

[09_norm_fibers.ipynb](09_norm_fibers.ipynb) constructs a quadratic finite field with coefficient formulas, counts norm fibers, and chooses a phase generator. Measured sizes determine angular spacing; multiplication becomes one cyclic turn. A 150-frame grid/rings/cylinder/undo sequence and a separate coordinate-change animation distinguish changing values from changing their arrangement. A reducible quotient and a triangle-inequality counterexample expose the domain assumptions.

[10_hermitian_partitions.ipynb](10_hermitian_partitions.ipynb) normalizes 728 nonzero triples into 91 projective classes, then selects a 28-point Hermitian curve. Inspect all 91 polar lenses and derive line owners and ranks from incidences. A 100-frame sequence gathers the same points into nine triples plus one point, then seven quadruples, and reverses both actions. Removing a polar line exposes four uncovered points.

[11_cyclic_code_plane.ipynb](11_cyclic_code_plane.ipynb) unfolds cyclic coefficient patterns into a generator matrix, derives its dual, and discovers the Fano plane in the code's seven weight-three supports. The same cubic constructs an eight-element field; an explicit coordinate dictionary identifies its projective incidences with the code's. Synchronized cyclic and projective views show a Singer cycle and captured undo. Seven interactive figures, two MP4s, a syndrome-correction coda, and four counterexamples accompany the visible recipes. Both offered irreducible cubics run independently.

The [lesson guide](../docs/lessons/README.md) contains educational notes for every existing notebook and [detailed plans](../docs/lessons/FUTURE_LESSONS.md) for the next investigations. The notes separate a lesson's construction, visual question, general explanation, finite evidence, and remaining design questions. [Review notes](../docs/lessons/REVIEW_NOTES.md) collect architectural evidence. [UI discovery notes](../docs/lessons/UI_DISCOVERY_NOTES.md) connect the constructions to declarative choices and separate module responsibilities.

Lessons 07 and 10 now use explicit `group_by`, member `order_by`, and `ranks`
declarations, with keyed bindings supplying named placement coordinates. Lesson 10
also uses coverage checks before adopting owners; its tangent supplies the singleton
block, so both partitions cover every one of the 28 point keys exactly once.
The [authoring guide](../docs/AUTHORING.md) explains these choices in a smaller
example. Restart the kernel after updating Kaleion: the new rank and requirement
operations need the updated evaluator and contributor queries.

Lessons 04–05 now use public `Inspection` queries for their contributor explanations.
They follow actual captured binding inputs to measurements and source contributors;
the lesson keeps its own mathematical formula and display choices. The
[exploration workflow](../docs/EXPLORATION_WORKFLOW.md) maps this to choices shared
across all eleven lessons and states the query limits. After updating, restart the
kernel so `from kaleion import Inspection` uses the new module.

## Install and launch

From the repository root on WSL/Linux/macOS:

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e '.[notebooks]'
python3 -m ipykernel install --sys-prefix --name kaleion --display-name "Kaleion"
python3 -m jupyterlab notebooks/01_discovery_workbench.ipynb
```

Reuse an existing environment if already installed. Choose the **Kaleion** kernel, then **Restart Kernel and Run All Cells**. The first notebook prints the kernel executable so you can confirm it belongs to `.venv`. In VS Code, open the repository in WSL, open the notebook, and choose that environment or the Kaleion kernel. If WSL does not open a browser automatically, copy JupyterLab's local URL from the terminal into your Windows browser. Open any of the other notebooks in the same session, or substitute its filename in the launch command above.

Notebook dependencies are optional: `python3 -m pip install -e .` still installs only the core. Installing `.[notebooks]` adds JupyterLab, the kernel/conversion tools, Plotly, Pillow, and imageio-ffmpeg. Plotly is imported only when its adapter is used. The FFmpeg wheels include an encoder on common platforms; if yours does not, install FFmpeg and point `IMAGEIO_FFMPEG_EXE` to its executable.

## What to try

| Section | Capability |
| --- | --- |
| Alternative placements | The same integer occurrences on a line, snake, and 3D helix |
| Lenses | Rules on values, indices, geometry, and moving spatial windows |
| Quotient region | Cardinalities become a new arrangement, with retained zero groups and contributors |
| Remainder table | Gather and keyed cyclic shifts driven by those cardinalities |
| Scattered 3D cloud | One driver changes either coordinates or integer contents |
| Rectangular spiral | Structural cycle-end incidence, exact parameter cases, retained hits |
| Tensor operations | Gather, substitution, tile, padding, Young diagram, and 3D grid incidence |
| Captures and replay | Undo follows a recorded path; workspace JSON preserves observations |

Edit the parameter or construction cells, then rerun downstream cells. Plot controls change presentation only. They do not implicitly reevaluate the kernel. Figure hover labels preserve exact integers as strings, including values beyond JavaScript's safe integer range. Floating coordinates still have ordinary numerical limits.

## Animations and videos

`snapshot_figure`, `animation_figure`, and `transition_figure` live in `kaleion.viewers.plotly`. They accept evaluated results, hold axes fixed across playback, and show exact before/after labels rather than fractional integers. The 3D camera remains interactive. An incidence's false points stay visible; an evaluation failure remains visibly identified if a motion retains old geometry.

Exact sweep cases are discrete. Smooth paths are sampled from Kaleion's recorded transitions. Plotly is not asked to infer a construction between two cases. Large scenes or many 3D frames can play below the requested rate; this preliminary viewer targets small investigations rather than streaming or GPU-scale data. `connect=True` explicitly draws storage order and should only be used when that order represents the path you want to see.

`kaleion.viewers.video.write_mp4` is a separate Pillow/FFmpeg raster adapter for 1D/2D samples. It writes an H.264 MP4, then checks the encoded frame count. It needs no browser or Kaleido, and consumes the same snapshot/frame inputs as the Plotly adapter. It is not a pixel-identical recording of Plotly. For 3D, use the interactive HTML export or explicitly project an arrangement into 2D before capturing its motion.

Run All writes these generated outputs into `build/notebooks/`:

- `roll-and-undo.mp4`, `spiral-cases.mp4`: videos embedded into the executed notebook.
- `roll-and-undo.html`, `spiral.html`, `cloud-3d.html`: standalone interactive views with Plotly.js embedded and no CDN dependency.
- `investigation.json`, `construction-graph.json`: captured state/history and symbolic definitions.

GitHub's notebook preview does not run interactive JavaScript. Run the notebook locally or open its generated HTML views in a browser. Newly executed local cells are trusted by Jupyter; only trust saved notebook outputs if you trust their source. Clearing outputs before committing keeps embedded Plotly.js, videos, generated IDs, and execution counts out of reviews.

The main README includes [static previews from all ten lessons](../README.md#a-glimpse-of-the-lessons). [Gallery regeneration](../docs/images/lessons/README.md) extracts those figures from executed notebooks without rerunning their constructions. PNG previews stay small and work directly on GitHub; full interactive outputs remain under `build/`.

The second notebook writes to `build/notebooks/floor-sum/`: `partition.html`, `packing.html` (for coprime parameters), and `noncoprime.html` are standalone interactive views; `floor-sum-workspace.json` preserves the definitions, results, and capture; `floor-sum-cases.json` records the finite checks. Its packing animation uses the same captured transition for forward playback and undo.

The third notebook writes to `build/notebooks/three-incidences/`: `solids.html`, `sections.html`, `packing.html`, and `overlap.html` are standalone Plotly views; workspace JSON files retain the constructions, captures, and packing history; `cases.json` records the checks and `preview.json` contains evaluated centers and membership codes. Section and packing views are produced for disjoint cases. The voxel helper is local to the notebook and consumes evaluated snapshots/frames. It displays every cell and limits the chosen box to 1500 occurrences; use small parameters for smooth 3D playback. `SLICE_AXIS` chooses `x`, `y`, or `z` for the section view. Mesh gaps are styling, while volume counts unit cells.

The fourth writes to `build/notebooks/measured-motion/`: `height-maps.html`, `lift-and-undo.html`, `discrepancy.html`, and `column-explanation.html`; measurement and motion workspaces; `cases.json`; and `column-explanation.json`. Edit `COLUMN` to inspect another key in the counterexample. The saved explanation links the target occurrence, measured driver occurrences, and original contributors. Grid edges between target points are presentation guides. The box is limited to 1500 occurrences for these fully displayed views.

The fifth writes to `build/notebooks/finite-radon/`: `ambiguous-projections.html`, `line-measurements.html`, `reconstruction-and-undo.html`, `recovered-image.html`, and `corrupted-measurement.html`; reconstruction, motion, corrupted-measurement, and missing-domain workspaces; `cases.json`; and `pixel-explanation.json`. Edit `PIXEL` to inspect a reconstruction and `image_x` to move the source's selected column. Use prime `p` in `{2,3,5,7}` and keep `0 <= image_x < p`. The displayed pair domain has `p^3(p+1)` occurrences and is not an optimized imaging backend. All arithmetic reconstruction uses exact integer values; the general prime-field argument is written separately from the finite checks.

The sixth writes to `build/notebooks/young-layers/`: four HTML figures (`diagrams`, `measurements`, `turn-pack-undo`, `lost-order`), three workspaces, `checks.json`, and `layer-explanation.json`. Edit `HEIGHTS` and `LAYER`. Heights must be nonnegative and nonincreasing for the main packing construction; trailing zeros and the empty list are supported. The fixed unordered example is separate. The 3D motion uses interactive HTML.

The seventh writes to `build/notebooks/additive-structure/`: five HTML figures (`representation-counts`, `sum-lens`, `sum-stacks`, `energy-squares`, `structure-comparison`), three workspaces, `checks.json`, `sum-explanation.json`, and `sum-stacks.mp4`. Edit `A_VALUES`, `B_VALUES`, and `SUM`. Input labels are distinct integers, at most six per set, with a displayed sum interval of at most 31 bins. Ranks use compact ordered-prefix evidence; dense pair domains remain for the independent energy count and explicit bin domain. This is not an optimized convolution backend.

The eighth writes to `build/notebooks/ehrhart-counts/`: five HTML figures (`integer-dilations`, `count-differences`, `measured-difference-motion`, `interior-boundary`, `rational-periodicity`), two workspaces, `checks.json`, `case-explanation.json`, and `integer-dilations.mp4`. Use `4 <= MAX_N <= 12`. `INSPECT_N` selects a case whose original point contributors are shown. The default video has nine held integer cases, not interpolated counts.

The ninth writes to `build/notebooks/norm-fibers/`: six HTML figures (`coefficient-grid`, `fiber-counts`, `grid-fibers-turn`, `fiber-cylinder`, `generator-change`, `reducible-counterexample`), four workspaces, `checks.json`, `fiber-explanation.json`, and `fiber-turn-and-undo.mp4`. Use `P` in `{3,7,11}` and a norm-one `BETA` of order `P+1`. `INSPECT_NORM` selects a retained key. The video explicitly projects the planar stages of the 3D motion into 2D.

The tenth writes to `build/notebooks/hermitian-partitions/`: seven HTML figures (`projective-quotient`, `hermitian-curve`, `incidence-matrix`, `line-counts`, `polar-lens`, `two-partitions`, `missing-polar`), six workspaces, `checks.json`, `point-explanation.json`, and `two-partitions-and-undo.mp4`. This model uses `P=3`, giving the field `F_9`. Choose `FOCUS` on the curve and `EXTERNAL` outside it, then rerun downstream cells. The polar scrubber selects previously evaluated cases. Capture files use compact JSON with all evidence retained; the default partition-motion file is about 11.4 MiB, below the existing 32 MiB import budget. This is a small enumerated investigation, not a scalable finite-geometry backend.

All notebooks use the existing optional dependencies. Lessons 06–10 share [lesson_views.py](lesson_views.py), a presentation-only helper beside the notebooks; their mathematical constructions remain visible. Lessons 09–10 also share [quadratic_coordinates.py](quadratic_coordinates.py), visible coefficient formulas composed from integer operations, without adding a core value domain. Longer presentation cells can be expanded in Jupyter when initially folded. A normal notebook execution needs no browser, but displaying interactive figures does.

Lessons 04–05 share [snapshot_views.py](snapshot_views.py), with no Plotly dependency:

```python
from snapshot_views import compare_keyed_values, keyed_values, rectangular_values

by_key = keyed_values(captured_counts, keys=("u", "v"))
xs, ys, rows = rectangular_values(captured_counts, x="u", y="v")
report = compare_keyed_values(left, right, left_keys=("u", "v"), domain=expected_keys)
```

The comparison report treats the supplied domain as authoritative: it lists
missing and unexpected keys on each side and exact `left - right` residuals on
shared keys. With no domain it can only compare the union of observed keys. It is
a detached check of captured finite data, not a universal proof or new arrangement.

Run from `notebooks/` or use the notebook's explicit path setup. These are
lesson-support functions, not imports from the installed `kaleion` API. They read
snapshots only; keep using symbolic bindings for construction and motion drivers.
Keys are unique exact integers; x/y select fields rather than screen coordinates.
Rows follow ascending y labels, columns ascending x labels. Missing cells fail,
zeros remain, and empty snapshots yield empty output. Entirely absent axis labels
cannot be inferred: retain separate checks of the expected mathematical domain.
The returned dictionaries/lists are detached inspection data, without provenance
claims. The original captured measurement and its contributors remain unchanged.

## Execute without the UI

With the environment activated and the kernel installed as above, run from the repository root:

```sh
python3 -m jupyter nbconvert --to notebook --execute notebooks/01_discovery_workbench.ipynb --output-dir build/notebooks --output 01_discovery_workbench.executed.ipynb --ExecutePreprocessor.timeout=180
python3 -m jupyter nbconvert --to html build/notebooks/01_discovery_workbench.executed.ipynb --output-dir build/notebooks
python3 -m jupyter nbconvert --to notebook --execute notebooks/02_floor_sum_proof.ipynb --output-dir build/notebooks --output 02_floor_sum_proof.executed.ipynb --ExecutePreprocessor.timeout=180
python3 -m jupyter nbconvert --to html build/notebooks/02_floor_sum_proof.executed.ipynb --output-dir build/notebooks
python3 -m jupyter nbconvert --to notebook --execute notebooks/03_three_incidence_box.ipynb --output-dir build/notebooks --output 03_three_incidence_box.executed.ipynb --ExecutePreprocessor.timeout=180
python3 -m jupyter nbconvert --to html build/notebooks/03_three_incidence_box.executed.ipynb --output-dir build/notebooks
python3 -m jupyter nbconvert --to notebook --execute notebooks/04_measured_motion.ipynb --output-dir build/notebooks --output 04_measured_motion.executed.ipynb --ExecutePreprocessor.timeout=180
python3 -m jupyter nbconvert --to html build/notebooks/04_measured_motion.executed.ipynb --output-dir build/notebooks
python3 -m jupyter nbconvert --to notebook --execute notebooks/05_finite_radon.ipynb --output-dir build/notebooks --output 05_finite_radon.executed.ipynb --ExecutePreprocessor.timeout=180
python3 -m jupyter nbconvert --to html build/notebooks/05_finite_radon.executed.ipynb --output-dir build/notebooks
python3 -m jupyter nbconvert --to notebook --execute notebooks/06_young_layers.ipynb --output-dir build/notebooks --output 06_young_layers.executed.ipynb --ExecutePreprocessor.timeout=180
python3 -m jupyter nbconvert --to html build/notebooks/06_young_layers.executed.ipynb --output-dir build/notebooks
python3 -m jupyter nbconvert --to notebook --execute notebooks/07_additive_structure.ipynb --output-dir build/notebooks --output 07_additive_structure.executed.ipynb --ExecutePreprocessor.timeout=180
python3 -m jupyter nbconvert --to html build/notebooks/07_additive_structure.executed.ipynb --output-dir build/notebooks
python3 -m jupyter nbconvert --to notebook --execute notebooks/08_ehrhart_counts.ipynb --output-dir build/notebooks --output 08_ehrhart_counts.executed.ipynb --ExecutePreprocessor.timeout=180
python3 -m jupyter nbconvert --to html build/notebooks/08_ehrhart_counts.executed.ipynb --output-dir build/notebooks
python3 -m jupyter nbconvert --to notebook --execute notebooks/09_norm_fibers.ipynb --output-dir build/notebooks --output 09_norm_fibers.executed.ipynb --ExecutePreprocessor.timeout=180
python3 -m jupyter nbconvert --to html build/notebooks/09_norm_fibers.executed.ipynb --output-dir build/notebooks
python3 -m jupyter nbconvert --to notebook --execute notebooks/10_hermitian_partitions.ipynb --output-dir build/notebooks --output 10_hermitian_partitions.executed.ipynb --ExecutePreprocessor.timeout=180
python3 -m jupyter nbconvert --to html build/notebooks/10_hermitian_partitions.executed.ipynb --output-dir build/notebooks
```

The committed source notebooks have no outputs. Execution creates populated copies with plots and, in lessons 01, 07, 08, 09, and 10, embedded videos. Per-figure HTML exports are the fully offline viewing option; the full nbconvert document may retain template links such as math-rendering assets.

For a quick separate encoder check:

```sh
python3 notebooks/check_video.py
```

Core and optional Plotly unit tests remain under `tests/` and run with `python3 -m unittest discover -s tests -v`. The notebook itself exercises the end-to-end examples; no web server or browser is needed for headless execution or the encoder check.

References: [Plotly animation frames](https://plotly.com/python/animations/), [interactive HTML export](https://plotly.com/python/interactive-html-export/), [renderer selection](https://plotly.com/python/renderers/), [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg).
