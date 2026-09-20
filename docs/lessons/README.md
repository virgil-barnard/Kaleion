# Kaleion lesson guide

Kaleion develops through complete mathematical investigations: construct an object,
ask a visual question, measure something, reuse the measurement, and explain what
the result establishes. These notes give each notebook a narrative that can later
support an educational page or a touch interface.

## Available investigations

| Lesson | Guiding question | Reusable construction |
| --- | --- | --- |
| [01 · Discovery workbench](01_discovery_workbench.md) | What can we construct, observe, and change? | Arrangements, lenses, reductions, keyed drivers, and captured motion |
| [02 · Two incidences fill a rectangle](02_floor_sum_proof.md) | Why do two reciprocal floor sums fill a rectangle? | Shared universe, complementary inequalities, coverage and overlap |
| [03 · Three incidences fill a box](03_three_incidence_box.md) | What does the floor-sum argument become in three dimensions? | Largest normalized coordinate, cross-sections, products of quotients |
| [04 · Three measurements lift a plane](04_measured_motion.md) | Can measured column heights make another plane flat? | Incidence → count → keyed displacement → discrepancy |
| [05 · Can line counts recover an image?](05_finite_radon.md) | Which measurements determine a picture? | Finite affine incidence → line counts → backprojection → exact recovery |
| [06 · Turn a diagram; count its layers](06_young_layers.md) | What do layer counts preserve and forget? | Conjugation → measured prefix offsets → packing and lost order |
| [07 · How many ways can a sum occur?](07_additive_structure.md) | What does the distribution of equal sums reveal? | Convolution → measured ranks → stacks and additive energy |
| [08 · Count lattice points as a triangle grows](08_ehrhart_counts.md) | When are dilation counts polynomial? | Parameter families → finite differences → driven probes and reciprocity |
| [09 · A field changes its clothes](09_norm_fibers.md) | Can multiplication become a turn? | Norm fibers → counts → phase coordinates → cyclic action and undo |
| [10 · One curve, two ways to gather it](10_hermitian_partitions.md) | How can the same 28 points form different partitions? | Projective quotient → polars → coverage → measured owners and ranks |
| [11 · A code becomes a projective plane](11_cyclic_code_plane.md) | How does a cyclic code reveal a field and a moving plane? | Polynomial → generator/dual → Fano supports → field trace → Singer cycle |

Read 01 as a reference tour. The mathematical sequence is 02 → 03 → 04.
Lesson 05 opens a second path through finite geometry and imaging. Lessons 06 → 07
connect counting, order, and multiplicity; 08 introduces parameter families and
quasipolynomials. Lessons 09 → 10 develop finite-field motion and Hermitian geometry.
Lesson 11 connects coding theory to a projective plane through an explicit field
coordinate dictionary; it includes a first syndrome-correction construction.
Every notebook includes its own definitions and can run in a fresh kernel.

The [future lessons](FUTURE_LESSONS.md) preserve the original briefs and remaining
investigations, with delivery status made explicit. [Review notes](REVIEW_NOTES.md)
collect concrete findings from the notebooks for our next architecture and
notation discussion. [UI discovery notes](UI_DISCOVERY_NOTES.md) identify the
declarative choices behind the new constructions and their module responsibilities.
The [codes and discovery paths](CODES_AND_DISCOVERY_PATHS.md) expand the next
investigations into dual codes, spectral cancellation, topology, and local
combinatorial dynamics, with concrete motion designs and checked finite seeds.

## A common narrative

1. **Question.** Offer something observable before stating its explanation.
2. **Construction.** Put readable notation beside visible symbolic Python. State
   the domain, parameters, keys, and incidence convention.
3. **Measurement.** Say what is counted and which keys survive. Keep zero groups
   and contributor provenance.
4. **Action.** Reuse a derived arrangement as another construction's input when it
   serves the mathematical question. Identify the target quantity being changed.
5. **Explanation.** Separate an exact finite check from an argument covering a
   general family. A smooth transition supplies intuition, not extra mathematical states.
6. **Challenge.** Alter an assumption, find a discrepancy, and inspect a witness.
7. **Record.** Save definitions, measurements, captures, and explanation data.

Each lesson note records prerequisites, a suggested reading/teaching sequence,
experiments, and software implications. It should support both a reader following
the mathematics and a developer deciding whether a recurring task deserves a helper.

## Conventions that matter educationally

- `count(by=...)` names **retained** keys; the other indices are reduced away.
- Area and volume in these lessons count declared unit cells or occurrences.
  Mesh gaps, point sizes, and interpolated surfaces do not change that measure.
- Equal values, equal keyed measurements, equal selected subsets, and identical
  occurrences are different claims. Check key-domain coverage on both sides.
- Measurements retain their contributors. Giving measured values another placement
  preserves that interpretation; changing the values creates a further derivation.
- A driver binding declares a target key, source key, and quantity to read. Storage
  order and coincident coordinates never establish a correspondence implicitly.
- Undo restores captured state and reverses its recorded path. It does not assert
  that a reduction has a mathematical inverse.
- Keep rendering helpers separate from construction and evaluation. A plot can
  expose a result without owning the rule that produced it.

## Running and maintaining lessons

See [notebooks/README.md](../../notebooks/README.md) for the `python3`/venv setup,
Jupyter commands, exports, and viewer limits. Commit source notebooks with cleared
outputs; generated figures and executed notebooks belong under `build/notebooks/`.
Validation evidence is recorded in [notebooks/VALIDATION.md](../../notebooks/VALIDATION.md).

Before extracting a new primitive, record the actual obstacle. Distinguish a
plotting convenience, a readable construction recipe, an execution optimization,
and a missing mathematical operation. The lessons should inform the future UI by
revealing repeated choices, without committing us to gestures prematurely.
