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
The general graph records the driver dependency, but a generic per-target binding
inspector and clickable cross-highlighting remain future presentation work.
The example does not infer an inverse from a cardinality, and it does not assert
that equal counts establish identical source occurrences.

Exports go to `build/notebooks/measured-motion/`: four offline HTML figures,
measurement and motion workspaces, finite-case reports, and `column-explanation.json`.
The 3D animation is interactive HTML, not an MP4 recording.
