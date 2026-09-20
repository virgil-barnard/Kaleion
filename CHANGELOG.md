# Changelog

## Unreleased

- Add lesson 11: cyclic generator polynomials and matrices, a derived dual, Fano-plane supports, and an explicit incidence correspondence with the eight-element field constructed from the same cubic. Synchronize a Singer cycle in cyclic and projective charts, with captured undo, a measured single-error correction, and assumption-breaking witnesses.
- Add seven independent-oracle lesson tests, educational/UI notes, two MP4 exports, and README previews for lesson 11. All constructions use existing core operations and dependencies.

- Make grouping, strict member order, scoped coverage, and named measurement-driven coordinates explicit authoring choices. Add `Grouping` and `Coverage`, plus an executable guide and core-only example.
- Add version-1 `rank` and `require` operations. Ranks sort within groups and retain linear-size ordered-prefix evidence; requirements guard reuse while leaving independent witnesses inspectable. Updated code reads old captures; new operations and contributor-prefix version 1 need the updated implementation.
- Refactor lessons 07 and 10 to use these choices, preserving their motion endpoints. Complete the Hermitian pencil with its tangent singleton so all 28 keys have exactly one owner. Keep captured evidence queryable after save/reopen and reverse motion.
- Preserve a retained field named `key` in composite reductions and ranks instead of replacing it with an ordinal. Cover declared order, composite keys, zero groups, ambiguity, failed coverage, history, and evidence with public-contract regressions.
- Add norm-fiber and Hermitian-geometry lessons using existing primitives: finite-field cyclic motion, projective classes, polar lenses, measured partitions, counterexamples, captured undo, and two MP4 exports.
- Add educational notes, concrete UI discovery choices, and future briefs for Burnside counting, syndrome fibers, and Hermitian block exchanges. Extend the README gallery to ten lessons.
- Check finite arithmetic, projective incidence, keyed coverage/rank drivers, contributors, and restored motion with eight independent-oracle lesson tests. The initial lesson addition required no core operation, dependency, or saved schema changes.
- Added a README gallery from all eight lessons, with notebook links and a figure exporter for regenerating the static previews.

- Share unchanged validated snapshot buffers and frozen metadata during internal derivation; public constructors still copy caller data. Seal identity/lineage containers and reject mutable field elements.
- Normalize NumPy integer scalars and integer attributes before arithmetic, closing fixed-width overflow paths in captured data.
- Centralize key/group rules and rectangular address generation in `indexing.py`; keep named-operation identity policies and saved formats unchanged. Roll uses flat strides and reuses fixed placement.
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
