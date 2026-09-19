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

## Measured motion and finite Radon lessons

- `04_measured_motion.ipynb`: all 11 code cells run in order in a fresh IPython
  process, with captured rich outputs. The `(11,7,5)` count fields sum to height 4
  at every `(x,y)` key. The `(6,4,5)` case has exactly one discrepancy, +2 at `(3,2)`;
  its three driver counts are `(2,2,2)` and their original contributors are inspectable.
- Its 78-frame animation uses three captured moves followed by three undos. Target
  occurrence identities remain unchanged, reverse samples agree with the forward
  path, and workspace reopening preserves contributor IDs and pending redo.
- `05_finite_radon.ipynb`: all 10 code cells run in order in a fresh IPython process.
  The default binary 5×5 image has weight 10. All six direction families recover
  that total from their five measurements; the 30 line counts reconstruct every
  pixel exactly. The construction explicitly checks zero division remainders and
  equality over the complete pixel key domain.
- The Radon notebook's 144-frame animation accumulates six measured direction fields,
  subtracts the measured total, divides by 5, and undoes all eight moves. Its target
  uses independent occurrences. Editing the source column updates the counts and
  recovered values. Increasing the `(m,t)=(1,0)` measurement by one produces division
  remainder 1 at exactly the five pixels `(x,x)`; the notebook presents these as
  witnesses rather than silently rounding a reconstruction.
- `python3 -m unittest discover -s tests -v`: **48 tests passed**. Six new construction
  tests independently check column contributors with rational maxima, zero groups,
  reordered drivers, overlap and saved reverse motion, prime-grid binary image
  reconstruction (zero, impulse, and full images at p=2,3,5), signed weights beyond
  64-bit range, an altered measurement, and failure of the prime-field inverse at
  composite modulus 4.
- `python3 examples/discovery.py --out build/example-output`: reference outputs
  unchanged. No runtime operation, dependency, or saved-format change was needed.
- Both executed notebooks convert to HTML. All five source notebooks validate as
  nbformat 4 with cleared outputs and syntactically valid code. Local links in the
  new lesson guides, updated README files, and new notebooks resolve.
- Browser checks with external HTTP(S) requests blocked load all nine standalone
  figures and both converted notebooks. All 30 finite-line selections highlight
  exactly five incident pixels and agree with the displayed measurement. Both
  motion sequences reach their checked endpoints, undo exactly, retain a changed
  camera, and respond to Play/Pause/Restart. The discrepancy and corruption views
  contain exactly their expected witnesses.
- Screenshots of the measured surfaces, overlap witness, contributor view, finite
  lines, reconstruction endpoint, and recovered image were inspected, including
  700-pixel-wide views. Reconstruction colors read captured endpoint labels so the
  zero pattern remains visible with fixed motion bounds. Crowded line-view titles
  and playback controls were adjusted during inspection.
- The browser recorded the previously documented Plotly `undefined` cancellation
  event once when pausing each active 3D animation. Pause did stop playback; no
  other page errors occurred in these checks. These events are documented, not
  suppressed in the notebook or viewer.

The same host restriction on local kernel sockets described above applies: execution
uses a fresh in-process IPython shell, not a live JupyterLab kernel. The notebooks
retain normal Jupyter/nbconvert instructions for local use. Their mathematical proofs
are written separately from finite tests. Both new 3D animations export to interactive
HTML; no new 3D MP4 capability is claimed.

## Young layers, additive structure, and Ehrhart counts

- All seven code cells in each of `06_young_layers.ipynb`,
  `07_additive_structure.ipynb`, and `08_ehrhart_counts.ipynb` run in order in
  separate fresh IPython processes with captured rich outputs. The same local-kernel
  socket limitation described above applies. All three executed notebooks convert to HTML.
- Lesson 06 derives layers `[3,3,2,1,1]` from heights `[5,3,2,0]`, recovers those
  heights by double conjugation, and derives offsets `[0,3,6,8,9]`. Its 84-frame
  transpose/pack/undo animation packs ten distinct occurrences and restores them.
  Transposed originals and a newly built conjugate agree in occupied coordinates,
  while their occurrence identities remain distinct. The unordered counterexample
  loses column order as stated. A separate full execution with `HEIGHTS=[]` also passes.
- Lesson 07 derives representation counts `[1,2,3,4,3,2,1]`. Squared counts, a direct
  equal-sum quadruple incidence, and measured square cells all give 44. The scattered
  comparison gives 28 from the same 16 ordered pairs. Measured predecessor counts
  drive the 84-frame collapse/stack/undo sequence without dropping coincident
  occurrences. A separate full execution with an empty left set also passes,
  including zero-count provenance and video export.
- Lesson 08 gives closed counts `[1,3,6,10,15,21,28,36,45]`, first differences
  `[2,3,4,5,6,7,8,9]`, and seven second differences equal to one. These derived
  arrangements drive seven independent probes through 102 frames and back.
  Reciprocity residuals vanish for n=1,...,8. Rational-triangle counts are
  `[1,1,3,3,6,6,10,10,15]`; second differences with stride two are all one.
  The scale-four explanation links a family occurrence to its measured case and
  exactly 15 original point contributors, preserved on reopening.
- `python3 -m unittest discover -s tests -v`: **55 tests passed**. Seven new tests
  use independent counting oracles and invariants for empty/zero Young diagrams,
  measured packing, lost order, captured spatial transposition, sum multiplicities
  with negative values and reordered keys, equal-sum quadruples, reordered parameter
  families, case provenance, boundary counts, and rational periodicity. The only
  floating tolerance is `1e-12` for trigonometric endpoint roundoff; reverse samples
  of the same captured path are compared exactly.
- `python3 examples/discovery.py --out build/example-output`: reference outputs
  unchanged. No runtime operation, dependency, or saved-format change was needed.
- All eight source notebooks validate as nbformat 4, have cleared outputs, and have
  syntactically valid Python cells. Local links in the notebooks, lesson guides, and
  updated README files resolve. The shared `lesson_views.py` consumes captured
  snapshots/frames and does not evaluate mathematical definitions.
- Browser checks with external HTTP(S) requests blocked load all 14 new standalone
  figures and all three converted notebooks. The converted documents have 4, 5, and
  5 interactive figures, respectively; the last two each contain an embedded video.
  Every equal-sum and integer-dilation frame has exactly the expected selected
  coordinates and colors. All three motion sequences reach the checked endpoints,
  restore starting positions and identity colors, and respond to Play/Pause/Restart.
  The Young-diagram view retains a changed 3D camera across animation frames.
- Screenshots at 1100 and 700 pixels were checked for representative diagrams,
  counts, energy squares, comparison profiles, periodic differences, and motion.
  Crowded subplot titles were shortened and the energy comparison uses a shared
  vertical scale. Both MP4 files decode at 960×640: `sum-stacks.mp4` has 84 frames
  at 24 fps (3.5 seconds); `integer-dilations.mp4` has 72 frames at 12 fps (6 seconds).
  Representative decoded frames were inspected. The latter holds nine exact cases.
- Pausing each active animation produced the previously documented Plotly 6.9.0
  `undefined` cancellation event. Playback stopped, Restart worked, and no other
  page errors occurred. The events are recorded rather than suppressed.

These checks concern finite examples and presentation. The notebooks provide separate
elementary arguments for their general identities and distinguish the broader Ehrhart
theorems from the triangle case proved here. Parameter-family contributor inspection
currently retains named measured-case roots because concatenation does not provide
a merged reduction-metadata query; the review notes document that limitation.
