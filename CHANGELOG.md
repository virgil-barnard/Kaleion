# Changelog

## Unreleased

- Fix Boolean composition and selection after incidence parameter binding, including nested scopes. Add `Incidence.universe` to expose the inspected collection or arrangement.
- Separate field interpretation into `expressions.py`, shared by construction evaluation and captured motion.
- Build reduction contributors in one pass; prepare motion correspondence and incidence membership once per captured root, shared by playback and undo.
- Preserve schema-1 and legacy imports. New scoped Boolean compositions use `incidence_boolean` version 1; executing that operation requires this evaluator.
- Extend the floor-sum construction to a 3D box with three incidences, voxel plots, exact cross-sections, packing/undo, and pairwise-coprimality and intersection proofs.
- Add a reciprocal floor-sum construction notebook with two incidences, grouped counts, interactive partition/overlap views, packing and undo, and a general proof including the noncoprime correction.
- Add an optional `notebooks` dependency group with JupyterLab, Plotly, and portable MP4 rendering.
- Add a programmatic discovery walkthrough covering arrangements, lenses, counts and contributors, quotient/remainder transforms, 3D drivers, structural sweeps, and history.
- Add snapshot/frame Plotly adapters and a separate 1D/2D video adapter; the mathematical evaluator and saved formats are unchanged.

## 0.1.0 · Kaleion baseline · September 19, 2026

**Discover mathematics through motion.**

This is the renamed distribution of the Icarus Python v0.1.0 baseline. The mathematical operation vocabulary and behavior are unchanged.

- Project, repository directory, Python distribution, and import namespace: `kaleion`.
- Source package: `src/kaleion/`.
- Updated README, design contracts, architecture, example imports, and tests.
- New workspace exports use `kaleion-python`, schema 1. Existing `icarus-python` schema 1 workspaces remain loadable, including captures, provenance, and undo/redo paths.
- Regenerated sample exports under the Kaleion name.
- Retained the original 29 tests and added one compatibility test for legacy Python workspaces.

To update an existing script, change its imports from `icarus` to `kaleion`. The old Python import namespace is not included. No published package or GitHub repository is assumed; install from this source checkout.

The original Icarus repository URLs and HTML prototype filename remain accurate historical references. The HTML prototype is a separate application and is not included in this Python package.
