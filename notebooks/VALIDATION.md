# Notebook viewer validation

## Lesson 11 · Cyclic code, field, and projective plane

September 20, 2026; Python 3.12.14, NumPy 2.3.5, Plotly 6.9.0.

- All 21 code cells execute in fresh in-process IPython sessions for the default
  `(generator,message,error_mask)=(11,5,4)` and alternative `(13,9,3)`. Mathematical,
  contributor, capture, undo, and video assertions pass. The host still prohibits
  live Jupyter kernel sockets, so this does not claim a live JupyterLab session.
  The source validates as nbformat 4, parses, and has cleared outputs.
- The full core suite passes **101 tests**, including seven new lesson tests that
  load the actual tagged construction cells without Plotly or a notebook kernel.
  Independent bitwise polynomial multiplication/division checks both cubics,
  their generators, reciprocal quotients, code/dual spans, all 128 parity masks,
  and cyclic closure. `examples/discovery.py --out build/example-output` passes.
- The default code has 16 words with weights `{0:1,3:7,4:7,7:1}`; its dual has
  eight words with weights `{0:1,4:7}`. Every G/H cross-parity is zero. Every one
  of the 21 point pairs belongs to exactly one weight-three support, and all
  seven complements match nonzero dual words. Reordered matrices, words, weights,
  and column drivers preserve results through explicit keys.
- For each cubic, all 64 field products match an independent remainder oracle;
  nonzero inverse coverage is one. The coordinate dictionary is bijective and
  preserves all 64 additions. All 49 trace incidences reproduce the code's lines;
  multiplication by alpha carries each line to another and has a seven-step cycle.
- All 128 zero/single-error transmissions per cubic decode to their source. All
  336 two-error transmissions per cubic decode to a different codeword. The
  zero correction retains its sole contributor. A cancelled coefficient retains
  its two integer contributors, while its derived parity makes no cardinality
  claim. A failed quotient/inverse requirement leaves independent witnesses usable.
- Captured generator and field motion replays and reverses with evaluation
  disabled. The seven notebook workspace exports reopen with their evaluated
  dependencies and pending redo; the cycle capture is about 4.35 MiB. JSON exports
  preserve the quotient contributor and explicit field/H-column dictionary.
- Chromium loads all seven standalone figures and the converted notebook with
  HTTP(S) blocked. The notebook contains seven figures, the coordinate table, and
  two embedded videos. The 75-frame generator, 82-frame support, and 136-frame
  synchronized field sequences reach the checked endpoints and undo targets.
  The two field charts agree at all checked action boundaries; a full cycle returns
  to the initial positions and colors. A changed 3D camera persists across frames.
- Play, Pause, and Restart work. The previously observed Plotly 6.9.0 `undefined`
  cancellation event occurs on active Pause, with no other page errors. Screenshots
  at 1100 and 700 pixels were inspected. Both 960×600 gallery previews export
  offline without errors and were inspected.
- Both H.264 videos decode all frames (82 and 136) at 1000×620, 20 fps. Decoded
  start/intermediate/end frames were inspected. The field video's captions spell
  `alpha` because the portable default raster font does not provide the Greek
  glyph. Video points and incidence colors come from the captured frames; the
  interactive field figure additionally draws the projective incidence strokes.

These finite checks support the specified seven-slot lesson. The written linear
algebra and field arguments explain the correspondence. No runtime, schema,
dependency, or general polynomial/field implementation changes are included.

## Explicit choice refinement

- Changed lessons 07 and 10 execute their 7 and 12 code cells in fresh in-process
  IPython sessions, including all mathematical, contributor, saved-state, motion,
  and video assertions. Source notebooks validate with cleared outputs. The same
  host restriction on live Jupyter kernel sockets applies; this is not a live
  JupyterLab session. The core suite passes **94 tests**.
- Sum-stack ranks now use explicit grouping and strict member order. The dense
  pair-of-pairs domain remains only for the independent energy count. Both ways
  of measuring the default energy still give 44; sum-stack endpoints are unchanged.
- The Hermitian pencil now includes the tangent's singleton block. Its coverage
  and the spread's coverage are both one at all 28 retained point keys. Guarded
  owner assignments and compact predecessor ranks drive the same nine-triple-plus-
  singleton and seven-quadruple placements. The missing-polar witnesses remain
  `[85,86,88,89]`. Point explanations now include rank predecessor keys.
- All nine workspace exports reopen, and every saved rank prefix in their current
  evaluated states can be queried with the evaluator disabled. The full Hermitian
  motion capture is 11,942,367 bytes (11.39 MiB), down from about 18.3 MiB before
  replacing dense rank domains. It retains the captured states, evaluated
  dependencies, contributor evidence, observations, and pending redo.
- Chromium loads all 12 standalone HTML figures and both converted notebooks
  with HTTP(S) blocked. The converted notebooks contain five/seven figures and
  one embedded video each. The 84-frame sum-stack, 50-frame projective quotient,
  and 100-frame partition motions reach their checked endpoints, retain identity
  colors, and restore their coordinates exactly. Play, Pause, and Restart work;
  the 3D quotient retains its changed camera.
- The known Plotly 6.9.0 `undefined` cancellation event occurs once for each active
  Pause; no other page errors occur. Motion screenshots at 1100 and 700 pixels
  were generated and the changed stack/partition views inspected. Both MP4s decode
  every frame (84 and 100) at 960×640 and 24 fps; sampled decoded frames were checked.

Viewer implementation, dependencies, and gallery PNGs are unchanged. Existing
gallery selections still show the same mathematical endpoints. Other lessons and
the full polar-case sweep were not rechecked in the browser for this refinement;
their earlier evidence below remains separately identified. New rank/require
definitions and contributor-prefix queries require the updated Kaleion code;
old schema-1 captures remain supported.

## Norm fibers and Hermitian partitions

- Lessons 09 and 10 execute all 23 code cells in fresh in-process IPython sessions,
  including saved-state, contributor, motion, and MP4 assertions. Lesson 09 also
  executes fully at `P=11`. Source notebooks validate with cleared outputs. The
  previously documented local-kernel socket restriction applies; this is not a
  live JupyterLab session.
- **82 unit tests pass.** Eight new tests load the actual tagged construction
  cells without a notebook kernel or Plotly. Independent polynomial arithmetic
  and finite set oracles check products, conjugation, norm fibers, generators,
  all projective classes, all polar incidences, both partitions, sparse retained
  keys, reversed driver storage, infinity-chart poles, contributors, saved reverse
  paths, and invalid-pole failure isolation. The reference example is unchanged.
- At `p=7`, norm counts are `[1,8,8,8,8,8,8]`. Multiplication changes the exact
  labels along a cyclic path; a generator change preserves values and identity.
  At `p=5`, the displayed quotient has nine zero-norm elements and nonzero zero
  divisors. The general norm-fiber argument is written separately in the lesson.
- The `F_9` investigation starts with 728 representatives of 91 classes, eight
  contributors each. Its curve has 28 points, 28 tangents, and 63 four-point
  secants. Every curve point has ten line incidences; each pair shares one secant.
  Measured owners and ranks give nine triples plus the focus, and seven quadruples.
  Removing the default external polar leaves exactly keys `[85,86,88,89]` uncovered.
- Offline Chromium checks load all 13 standalone HTML views and both converted
  notebooks, with HTTP(S) requests blocked. The converted notebooks contain six
  and seven interactive figures and one embedded video each. Every one of the 91
  polar frames selects exactly its measured incidence row.
- The 150-frame norm motion, 50-frame generator change, 50-frame projective
  normalization, and 100-frame partition motion reach their checked endpoints,
  preserve occurrence colors, reverse exactly, and respond to Play/Pause/Restart.
  The 3D views retain a changed camera. The known Plotly 6.9.0 `undefined` promise
  cancellation appears once for each active Pause; playback stops and Restart
  works. No other page errors occurred.
- Screenshots at 1100 and 700 pixels were inspected for the motion sequences,
  along with coefficient/fiber views, the incidence matrix, polars, and missing
  points. Both MP4 files decode all 100 frames at 960×640 and 24 fps. Sampled
  decoded frames were inspected; the norm video's labels use `beta` so the
  raster adapter's available font displays them correctly. The videos use the
  raster adapter's own styling, not the Plotly identity-color palette.
- Both new 960×600 gallery images export offline without browser errors and
  total about 129 KiB. The Hermitian preview fits its selected frame and labels
  group order and within-group rank with independent screen scales.

The partition lesson restricts products to the declared support (91×28 incidence,
28×28 rank comparisons). All ten new workspace files reopen with their complete
evidence. Compact JSON removes whitespace only: the default partition motion is
about 18.3 MiB, compared with 37.0 MiB indented, and retains its pending redo path.
The 32 MiB import budget, saved schema, core operations, and dependencies are
unchanged. Sharing evaluated dependencies across saved states remains future work.
These finite checks do not prove the general unital theorems; their source and
scope are identified separately in the lesson.

## Snapshot ownership and indexing regression check

All eight notebooks rerun successfully in fresh in-process IPython sessions: 77
code cells, including construction, contributor, motion, undo, saved-state, and
MP4-export assertions. Their source cells and cleared-output state are unchanged.
The core suite now passes 74 tests. The same kernel-socket limitation applies.

The committed baseline and new example captures reproduce every saved result
exactly under reevaluation. This pass changes snapshot storage and numerical
address rules; viewer code is unchanged. Browser interaction checks were not
repeated; the preceding playback evidence below remains separately identified.

The README's eight static lesson previews were separately exported through
Plotly.js in Chromium, with network requests blocked and no page errors. Their
selected frames and visual framing were inspected. The generator consumes saved
Plotly outputs rather than reimplementing lesson constructions; no source
notebook outputs were committed. The optional Kaleido export route was not run.

## First core refinement regression check

- All eight source notebooks run in fresh in-process IPython sessions: 77 code
  cells complete with their mathematical, provenance, motion, and persistence
  assertions. MP4 exports are regenerated. The source notebooks remain unchanged
  with cleared outputs; executed copies stay under `build/notebooks/`.
- The 65-test suite and reference example pass. New tests exercise parameter-bound
  incidence composition and reuse of prepared tracks during playback and undo.
- Offline browser checks reload all 14 standalone figures and the three converted
  notebooks from lessons 06–08. Their 84-, 84-, and 102-frame motion sequences
  reach the expected endpoints, restore coordinates and identity colors, and
  respond to Play/Pause/Restart. The 3D Young view retains its adjusted camera.
  Every equal-sum and dilation frame has the expected selected coordinates.
- The existing Plotly 6.9.0 `undefined` cancellation event still occurs when pausing
  active playback; pause and restart work, with no other page errors in this check.

The local-kernel socket restriction still applies: these are fresh sequential
IPython executions and exported-browser checks, not a live JupyterLab session.
Earlier checks below describe the original lesson additions.

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
