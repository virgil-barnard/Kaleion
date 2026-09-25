# Browser study gates

For the current UI, run `node docs/studies/check-continuous-canvas.cjs` with
Playwright and Chromium available. It starts its own local Python host; optional
arguments are an existing origin and an output directory. `KALEION_PYTHON`,
`KALEION_PLAYWRIGHT_MODULE` and `KALEION_BROWSER_OPTIONS` support an existing local
runtime. Core tests do not require a browser.

`node docs/studies/check-relation-notation.cjs` is a second current-shell gate
for short rules and text/control conversion. It constructs modular, lattice and
binary projective incidences from a blank canvas, including invalid drafts and
delayed parse responses. It accepts the same optional runtime configuration.

`check-scene-model.mjs` checks pure geometry and lossless view documents offline.

`check-field-guide.cjs` checks current captured-field exploration and draft
retention. `check-canvas-tutorial.cjs` builds the introductory workflow and opens
the original eleven catalog entries. `check-division-motion.cjs` builds a measured
displacement, cyclic reindexing and Euclidean shear from blank, opens the four
division canvases, checks the modular composition counterexample, and exercises
replay, invalid drafts, syntax conversion and a narrow emulated-touch layout.
These current-shell gates use the same runtime options above.

The remaining `.cjs` scripts record earlier authoring, evidence and spatial UI
experiments. They target the controls at commit `19928e6`, including the now
removed Focus surface and mode toolbar. Use a checkout of that commit to reproduce
those historical results. They are not acceptance gates for the current shell.
Their mathematical contracts continue in Python tests; the current gate covers
creation, relations, totals, ordered measurement, comparison, coverage, captured
weighted evidence, lesson import, replay, view state and emulated touch.
