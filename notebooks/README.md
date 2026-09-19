# Kaleion notebooks

Start with [01_discovery_workbench.ipynb](01_discovery_workbench.ipynb). It is an editable walkthrough of the module, with interactive 2D/3D plots, parameter-case scrubbers, recorded motion and undo, and two embedded MP4 videos. It uses finite constructions and no external datasets.

[02_floor_sum_proof.ipynb](02_floor_sum_proof.ipynb) is a self-contained construction page for reciprocal floor sums. It places readable notation beside two incidences on a shared integer rectangle, checks their grouped counts and union/intersection, and animates packing and undo. The written argument proves the identity for all positive coprime parameters greater than one; exact finite examples also expose the `gcd(a, b) - 1` overlap correction. "Area" here counts unit cells, with explicit integer summation bounds. This notebook uses the existing symbolic Python API and does not introduce a text-language parser or proof assistant.

[03_three_incidence_box.ipynb](03_three_incidence_box.ipynb) constructs the three-dimensional analogue. The incidence with the greatest normalized coordinate owns each point of a shared integer box. For pairwise coprime parameters, rectangular cross-sections produce products of two floor quotients and the three volumes add to the box volume. Interactive voxel views, exact slice controls, and recorded packing/undo make the three pieces inspectable. Counterexamples distinguish pairwise coprimality from merely having a joint gcd of 1 and demonstrate triple-intersection accounting.

[04_measured_motion.ipynb](04_measured_motion.ipynb) derives three column-count arrangements and uses them as keyed motion drivers for an independent plane. Heatmaps, a 78-frame lift/undo animation, a discrepancy view, and contributor inspection connect a flat endpoint to a pointwise equality. The `(6,4,5)` counterexample exposes double-counting as a bump. All definitions are included, so the notebook can run independently of lesson 03.

[05_finite_radon.ipynb](05_finite_radon.ipynb) asks whether measurements determine an image. It starts with ambiguous row/column projections, builds modular lines over a prime field, and reconstructs every pixel from line counts. A line-selection scrubber and staged 3D reconstruction/undo demonstrate measured fields driving other arrangements. A source edit propagates through the computation; an altered line count produces exact-division witnesses. The default 5×5 case has 30 line measurements and a 144-frame reconstruction/undo animation.

The [lesson guide](../docs/lessons/README.md) contains educational notes for every existing notebook and [detailed plans](../docs/lessons/FUTURE_LESSONS.md) for the next investigations. The notes separate a lesson's construction, visual question, general explanation, finite evidence, and remaining design questions.

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

The second notebook writes to `build/notebooks/floor-sum/`: `partition.html`, `packing.html` (for coprime parameters), and `noncoprime.html` are standalone interactive views; `floor-sum-workspace.json` preserves the definitions, results, and capture; `floor-sum-cases.json` records the finite checks. Its packing animation uses the same captured transition for forward playback and undo.

The third notebook writes to `build/notebooks/three-incidences/`: `solids.html`, `sections.html`, `packing.html`, and `overlap.html` are standalone Plotly views; workspace JSON files retain the constructions, captures, and packing history; `cases.json` records the checks and `preview.json` contains evaluated centers and membership codes. Section and packing views are produced for disjoint cases. The voxel helper is local to the notebook and consumes evaluated snapshots/frames. It displays every cell and limits the chosen box to 1500 occurrences; use small parameters for smooth 3D playback. `SLICE_AXIS` chooses `x`, `y`, or `z` for the section view. Mesh gaps are styling, while volume counts unit cells.

The fourth writes to `build/notebooks/measured-motion/`: `height-maps.html`, `lift-and-undo.html`, `discrepancy.html`, and `column-explanation.html`; measurement and motion workspaces; `cases.json`; and `column-explanation.json`. Edit `COLUMN` to inspect another key in the counterexample. The saved explanation links the target occurrence, measured driver occurrences, and original contributors. Grid edges between target points are presentation guides. The box is limited to 1500 occurrences for these fully displayed views.

The fifth writes to `build/notebooks/finite-radon/`: `ambiguous-projections.html`, `line-measurements.html`, `reconstruction-and-undo.html`, `recovered-image.html`, and `corrupted-measurement.html`; reconstruction, motion, and corrupted-measurement workspaces; `cases.json`; and `pixel-explanation.json`. Edit `PIXEL` to inspect a reconstruction and `image_x` to move the source's selected column. Use prime `p` in `{2,3,5,7}` and keep `0 <= image_x < p`. The displayed pair domain has `p^3(p+1)` occurrences and is not an optimized imaging backend. All arithmetic reconstruction uses exact integer values; the general prime-field argument is written separately from the finite checks.

Both new notebooks use the existing optional dependencies. Their 3D playback exports are interactive HTML, not MP4 files. Construction code remains visible; longer presentation helpers can be expanded in Jupyter when their source is initially folded. A normal notebook execution needs no browser, but displaying interactive figures does.

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
```

The committed source notebooks have no outputs. Execution creates populated copies with plots and, in the first notebook, embedded videos. Per-figure HTML exports are the fully offline viewing option; the full nbconvert document may retain template links such as math-rendering assets.

For a quick separate encoder check:

```sh
python3 notebooks/check_video.py
```

Core and optional Plotly unit tests remain under `tests/` and run with `python3 -m unittest discover -s tests -v`. The notebook itself exercises the end-to-end examples; no web server or browser is needed for headless execution or the encoder check.

References: [Plotly animation frames](https://plotly.com/python/animations/), [interactive HTML export](https://plotly.com/python/interactive-html-export/), [renderer selection](https://plotly.com/python/renderers/), [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg).
