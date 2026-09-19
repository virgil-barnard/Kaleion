# Notebook viewer validation

Checked with Python 3.12.14, NumPy 2.3.5, Plotly 6.9.0, JupyterLab 4.6.3,
IPython 9.17.1, Pillow 12.3.0, and imageio-ffmpeg 0.6.0.

- Editable installation with `.[notebooks]` succeeded. A fresh core import does not load Plotly.
- `python3 -m unittest discover -s tests -v`: 38 tests passed, including eight presentation tests for exact labels, incidence states, zero-opacity creation, reversed labels, fixed motion bounds, empty/3D views, and failed evaluation visibility.
- `python3 examples/discovery.py --out build/example-output`: reference results unchanged.
- `python3 notebooks/check_video.py`: six H.264 frames decoded at 480×320, 6 fps.
- Wheel build succeeded; notebook source validates as nbformat 4 and has cleared outputs.
- All 15 notebook code cells ran sequentially in a fresh IPython process. The default examples produced counts `[0, 1, 3, 4, 6, 7, 9]`, first column `[0, 11, 22, 33, 44, 55, 66]`, and 24 retained structural hits through 36. Save/reopen and forward/undo assertions passed.
- The generated notebook converted to HTML with 15 interactive figures and two embedded videos. Browser inspection covered the full document and all three standalone exports, with HTTP(S) requests blocked to check local figure operation. The 3D camera was changed and remained in place after advancing animation frames.
- Both MP4 exports decoded at 960×640 and 24 fps: roll/undo has 98 frames (about 4.08 seconds), and the spiral has 204 frames (8.5 seconds). Representative video frames and Plotly screenshots were visually inspected.

## Limits of this check

This execution host prohibits local socket binding, so a normal `nbconvert --execute`
kernel could not start over either TCP or IPC. Cell execution was verified using
IPython's in-process shell and captured rich outputs, not a live JupyterLab kernel
session. The README retains the standard local Jupyter/nbconvert commands.

With Plotly 6.9.0, pressing Pause during active playback emitted an undefined rejected
animation promise in the headless browser console. Pause stopped playback and Restart
returned to the first frame. These cancellation events were recorded rather than
silenced; loading and inspecting the figures succeeded. The initial viewer does not
guarantee a particular 3D playback frame rate or export 3D MP4 video.

Execution and rendering checks concern finite examples. Any general mathematical
claim needs a separate argument, such as the partition proof in the second notebook.

## Reciprocal floor-sum construction

Checked with the same environment listed above:

- All nine code cells in `02_floor_sum_proof.ipynb` ran in order in a fresh IPython process, with captured rich outputs. The same local-kernel socket limitation applies.
- For `(a, b) = (11, 7)`, the original counts are exactly `[0, 1, 3, 4, 6, 7, 9]`. The new incidences have cardinalities 30 and 30, cover all 60 occurrences of the shared domain, and have empty intersection.
- For `(a, b) = (12, 8)`, cardinalities are 40 and 40, the union has 77 occurrences, and the intersection contains precisely `(2, 3)`, `(4, 6)`, and `(6, 9)`.
- `python3 -m unittest discover -s tests -v`: 40 tests passed. Two new tests cover exact floor-sum incidence counts/coverage/overlap, including the smallest allowed parameters and retained zero groups, and reorientation of the earlier quotient region without changing occurrence identity or membership.
- `python3 examples/discovery.py --out build/example-output`: reference results unchanged.
- Browser checks with HTTP(S) requests blocked loaded all three standalone exports and the converted notebook. The P/Q/Both/Overlap buttons produced the expected cell counts in both parameter cases. The 82-frame packing/undo sequence retained colors by identity, filled 60 distinct integer positions at its packed endpoint, and restored its starting positions exactly. No page errors occurred during these checks.
- Screenshots were inspected at widths 1100 and 700 pixels. Both source notebooks validate as nbformat 4 and have cleared outputs; the user's existing kernel and cell metadata in the first notebook are preserved.

The general proof is written in the notebook: coverage follows from ordering, and
coprimality excludes shared interior lattice points. For arbitrary positive integer
parameters greater than one, inclusion–exclusion gives the correction
`gcd(a, b) - 1`. The notebook distinguishes this deduction from finite assertions
and does not claim an automated proof certificate.

## Three incidences in a box

- All 11 code cells in `03_three_incidence_box.ipynb` execute in order in a fresh IPython process, under the same local-kernel socket limitation described above. The converted notebook has four interactive figures.
- The `(11, 7, 5)` case gives volumes `[86, 80, 74]`, covering 240 distinct occurrences with no pairwise overlap. Captured cross-section areas agree with products of floor quotients, including zero sections.
- The `(6, 4, 5)` case has joint gcd 1 but a pairwise gcd of 2: the first two incidences share `(3, 2, 1)` and `(3, 2, 2)`, and `23 + 19 + 20 - 2 = 60`.
- The `(4, 6, 8)` case exercises a triple intersection: `118 - 4 - 8 - 2 + 1 = 105`.
- `python3 -m unittest discover -s tests -v`: 42 tests pass. The new construction tests compare integer cross-product predicates with independent exact rational maxima, check cross-section products and contributors, and exercise pair/triple inclusion–exclusion, including the smallest box.
- `python3 examples/discovery.py --out build/example-output`: reference results unchanged.
- Browser checks with HTTP(S) requests blocked loaded the four standalone exports and the converted notebook. All/X/Y/Z/Shared controls show the expected cell counts. All ten x-slices match the captured X areas; separate data checks verify all y- and z-slices too.
- The 62-frame voxel motion retains 240 cells and 2880 mesh triangles, fills 240 distinct integer centers at its packed endpoint, restores its initial coordinates exactly, and retains a changed camera orientation across frames. No page errors occurred during these checks.
- Solid, isolated-piece, overlap, and motion screenshots were visually inspected, including the solid view at 680 pixels wide. Notebook source validates with cleared outputs. The written largest-coordinate argument establishes the general identity for pairwise coprime integers; these numerical and rendering checks concern finite cases.
