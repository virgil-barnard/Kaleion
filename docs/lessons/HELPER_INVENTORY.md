# Lesson helpers and authoring work

This inventory records what it currently takes to author each investigation.
Use it alongside the [review notes](REVIEW_NOTES.md) and
[core refinement plan](../CORE_REFINEMENT_PLAN.md) when choosing the next
extraction. The individual lesson notes list every local function, the shared
functions used, inline scaffolding, and the assumptions a reusable version would
need to expose.

After extracting the snapshot adapters from lessons 04–05, there are **53 top-level
and five nested notebook functions**, plus **22 top-level functions, six
methods/property getters, and one nested helper in four shared lesson modules**.
The module count includes the comparison records and two private key validators
added after the initial adapter extraction. These counts describe source
organization, not mathematical complexity
or a proposed number of primitives. Lessons 01 and 06 have no local functions but
still require substantial authoring work.

The scope is the numbered notebooks and their four project helper modules.
Core APIs and third-party utilities are named where they clarify a responsibility;
this is not a catalog of every Python or Plotly call. Private and nested helpers
are included. Imports alone do not establish use.

## Find the work in each lesson

| Lesson inventory | Local functions: top-level + nested | Main custom responsibilities | Shared lesson modules used |
| --- | --- | --- | --- |
| [01 · Discovery workbench](01_discovery_workbench.md#functions-and-authoring-scaffolding) | 0 + 0 | Inline shapes, lenses, measurement bindings, retention, sampling, and persistence | None; public viewers |
| [02 · Floor sums](02_floor_sum_proof.md#functions-and-authoring-scaffolding) | 2 + 1 | Finite-case report, rectangular mask view; inline packing | None; public viewer and Plotly |
| [03 · Incidence box](03_three_incidence_box.md#functions-and-authoring-scaffolding) | 9 + 2 | Finite-case report, voxels, slices, membership displays, playback | None; Plotly |
| [04 · Measured motion](04_measured_motion.md#functions-and-authoring-scaffolding) | 5 + 1 | Plane edges, discrepancy report, formatted measurement explanation | `snapshot_views`; public `Inspection`, viewer, and Plotly |
| [05 · Finite Radon](05_finite_radon.md#functions-and-authoring-scaffolding) | 4 + 0 | Reconstruction check, linked highlights, formatted binding/contributor explanation | `snapshot_views`; public `Inspection`, viewer, and Plotly |
| [06 · Young layers](06_young_layers.md#functions-and-authoring-scaffolding) | 0 + 0 | Inline conjugation, prefix declaration and dense reference, paths, nested receipts, and replay assembly | Public `Grouping.prefix_sums`, `Inspection`; `lesson_views` |
| [07 · Additive structure](07_additive_structure.md#functions-and-authoring-scaffolding) | 2 + 0 | Product and bin recipes; inline ranks, energy checks, and lens sweep | `lesson_views` |
| [08 · Ehrhart counts](08_ehrhart_counts.md#functions-and-authoring-scaffolding) | 2 + 0 | Measured case family and finite difference; inline evidence and probes | `lesson_views` |
| [09 · Norm fibers](09_norm_fibers.md#functions-and-authoring-scaffolding) | 3 + 0 | Arithmetic/phase recipes, placement, orbit validation, frame projection | `lesson_views`, `quadratic_coordinates` |
| [10 · Hermitian partitions](10_hermitian_partitions.md#functions-and-authoring-scaffolding) | 4 + 0 | Canonical representatives, incidence, guarded owners, ordered packing | `lesson_views`, `quadratic_coordinates` |
| [11 · Cyclic code and plane](11_cyclic_code_plane.md#functions-and-authoring-scaffolding) | 22 + 1 | Binary arithmetic, product/reduction recipes, field dictionary, paths, coordinated replay | `lesson_views`, `code_views` |

## Keep different responsibilities visible

Sixteen [saved studio examples and one blank canvas](../../examples/canvases/README.md)
adapt lessons 02–07 and the introductory triangle for exploration with Open.
Their generator, [save_canvases.py](../../examples/save_canvases.py), has seventeen
registered builders, two local shared construction recipes, and one export entry point.
`triangle_parts()` supplies a common domain, incidence, counts and independent
formula to first motion and packing. `ownership_regions()` supplies the box and
three predicates to the original box, cell-ownership comparison and planar lifts.
`measured_plane()` records three paired value/position changes; `cell_coverage()`
compares singleton measurements to a separately derived unit field, and
`tied_coverage()` selects the assumption-breaking parameters. `triangle_packing()`
composes selected cells, ranks and measured prefixes. These remain ordinary core
operations and captures; the tutorial adds no lesson-specific evaluator behavior.
Export losslessly compacts schema-1 JSON. Inspection, preview/apply and rendering
remain shared studio responsibilities. `studio/catalog.py` owns trusted example
choices and descriptions, while `web/learning.js` owns non-executing instructions.
These functions are outside the unchanged notebook/helper counts above.

The [division investigation's inventory](../DIVISION_MOTION.md#functions-and-authoring-scaffolding)
adds eight functions in `examples/division_relations.py`: a shared `division_parts`
recipe, `division_motion`, `relation_matrices`, `euclidean_step`, and the next-case
wrapper `euclidean_next`, shared `periodic_factor`, `periodic_extension`, and
`guarded_remainder_addresses`. Six builders are registered with the same exporter.
They compose existing Count/Sum/Bind/Move/Roll/Arrange and explicit domains;
there is no local matrix kernel or renderer. Singleton counts let composition
read actual incidence-derived 0/1 fields instead of duplicating predicates.
Shared transform/notation controls belong to the studio, not to those recipes.
The copying sheet and `studio.reindexing.reindex` separately own declaration
choices and lowering; copied identities and lineage remain core responsibilities.
The existing guarded `studio.coverage.unique_assignment` recipe is reused directly.
There is no lesson-local inverse calculation, copying kernel or receipt renderer.

| Responsibility | Typical input → output | Boundary to preserve |
| --- | --- | --- |
| Construction recipe | Parameters, expressions, collections → definitions | Compose existing operations; evaluation stays explicit. Width, domain, and key choices belong here. |
| Input validation or finite check | Declared input or captured results → accepted case, report, or witness | State what was checked and on which domain. A finite enumeration is not a proof for all parameters. |
| Captured-data adapter or explanation | Snapshots and scoped keys/IDs → matrix, correspondence, or contributor receipt | Read results without inventing a new mathematical input or deriving correspondence from screen proximity. |
| Placement and motion description | Definitions → placed definitions; captured endpoints → a path | Exact actions and their interpolated presentation have separate meanings. |
| Replay orchestration | Workspace edits/transitions → ordered samples, captions, and coordinated views | History owns edits and undo; the renderer consumes captures. Sampling policy does not change the mathematical cases. |
| Rendering and persistence | Captured data → figures or saved files | Chart style, projection, routing, video timing, and file effects must not own incidence or arithmetic. |

Several functions currently span boundaries: 09's `phase_atlas` validates an orbit
and builds definitions; 10's `projective_points` decodes coordinates and places
them; 10's `hermitian_partition` selects, measures, orders, and places;
11's `compact_workspace` writes a file and deserializes the same in-memory payload.
The inventory names those
combinations rather than treating every existing function as an ideal module.

## Shared functions already in use

“Direct” means called in notebook source, including inside a local function.
“Indirect” means reached through another helper. Colors and other constants are
not counted as functions.

### Captured integer-key adapters and comparison

Sources: [kaleion/comparison.py](../../src/kaleion/comparison.py) owns keyed
lookup/comparison; [notebooks/snapshot_views.py](../../notebooks/snapshot_views.py)
reexports the original names and owns rectangular presentation.
All three functions are used directly in 04–05; the two adapters replace four
local definitions. They do not import Plotly, evaluate definitions, or modify
captured evidence.

| Function | Input → result and required choices |
| --- | --- |
| `keyed_values` | Snapshot, explicit key-field names and optional value field → a detached tuple-keyed dictionary in occurrence order. Require unique exact integer keys, preserving integer values and zeros. |
| `rectangular_values` | Snapshot and explicit x/y field names → ascending axis labels and rows indexed by y, columns by x. Uses `keyed_values`; require a complete product of observed labels, without filling holes. |
| `compare_keyed_values` | Two snapshots, explicit key fields, optional selected value fields and an optional ordered expected domain → exact left-minus-right residuals plus missing and unexpected keys on each side. Without an expected domain it reports only the union of observed keys. |
| `keyed_indices`, `keyed_items` | Shared occurrence lookup for studio witnesses: unique integer-key indices, or indices paired with a selected integer value; the domain's labels are not compared. |
| `_context`, `_field_names`, `_key_tuple` | Private stored/intrinsic-field context and validation for declared field names and exact integer key tuples; placement never supplies keys. |
| `KeyedDifference.to_dict`; `KeyedComparison.nonzero`, `same_domain`, `values_equal_on_common`, `holds`, `to_dict` | Detached witness serialization and report predicates. `KeyedComparison.to_dict.keys` converts tuple keys to lists. |

Empty input with valid key fields yields an empty map or three empty lists. A
one-dimensional lookup retains one-tuple keys. Neither coordinates nor shape
metadata supplies implicit keys or absent axis labels. Comparison makes the expected
domain an independent input when absent labels matter. This is not a new core
operation or proof/evidence API; returned containers carry no measurement claim,
and equality is only for the captured finite case.
The studio requires an explicit domain and wraps the report with scoped receipts;
the shared Python helper retains its optional-domain behavior for existing clients.

### Captured binding and measurement inspection

Public source: [inspection.py](../../src/kaleion/inspection.py). Lessons 04–05 use
`Inspection.find`, `item`, `bindings`, and `measurement`. The adapter hides captured
scope resolution and contributor joins, reusing existing key/expression semantics.
It returns immutable records with detached `to_dict()` exports and executes no
graph operations. It handles retained zero groups, weighted sums, ordered ranks and prefixes,
copied measurements, and local parameter cases. The
[workflow document](../EXPLORATION_WORKFLOW.md) states supported operations and limits.

The local explanation functions remain: they choose narrative stages, coordinates,
and the reconstruction formula. This extraction removes manual correspondence
logic, not the mathematical explanation or necessarily lines of notebook code.
The public adapter is not part of the four lesson-module function counts above.

### Named product roles

Public source: [products.py](../../src/kaleion/products.py). Lessons 05 and 07 use
`Product(...).domain` and `.read(role, field)` for point–line, left–right,
pair–bin, and pair-of-pairs domains. It composes existing definitions without
evaluation. Slot addressing, factor order, new tuple identity, retained empty-axis
groups, and dense product cost have explicit contracts. Semantic keys and fields
are read separately. No local lesson function is removed; their mathematical
construction becomes more readable. This public recipe is outside the shared
lesson-module function counts above.

The bounded [touch study exporter](../../examples/touch_study.py) has two functions:
`investigation` constructs/checks the finite examples and captures receipts/paths;
`main` chooses the two study cases and writes the presentation template with its
data. The [template](../studies/touch-pairs.template.html) owns controls, drawing,
and local preview/history. Neither is a numbered lesson helper or a general UI
bridge. Their responsibilities are intentionally documented separately.

### Presentation helpers

Source: [notebooks/lesson_views.py](../../notebooks/lesson_views.py).
All six functions are lesson support, separate from the core construction API.

| Function | Input → result and responsibility | Current use |
| --- | --- | --- |
| `style` | Figure and title → themed figure | Direct: 09–10. Indirect: panels/profiles in 06–10 and code views in 11. |
| `xy_cells` | Placed snapshot or incidence → square-marker trace with explicit xy projection | Indirect: `cell_panels` in 06–07; `binary_panels` in 11. Requires at least two placement coordinates. |
| `cell_panels` | Captured snapshots and titles → comparable cell panels | Direct: 06–07. Uses `xy_cells` and `style`. |
| `profiles` | Snapshots, key-field names, titles → bar profiles | Direct: 06–10. Uses `style`; reads existing measurements. |
| `replay` | Captured samples, labels, optional ID colors → animation | Direct: 06–11. Wraps the public `animation_figure`; callers still assemble samples and labels. |
| `save_figures` | Directory and named figures → self-contained HTML files | Direct: 06–11. Explicit filesystem effect; no construction or evaluation. |

### Quadratic coordinate formulas

Source: [notebooks/quadratic_coordinates.py](../../notebooks/quadratic_coordinates.py).
The convention is the coefficient code `a + p*b` for `a + b*i`, with `i² = -1`.
The arithmetic functions compose integers or Kaleion expressions. The quotient
is a field for the supported prime cases congruent to 3 modulo 4; lesson 09 also
uses a reducible case as a counterexample. These functions are not a general
finite-field value type.

| Function | Responsibility | Current use |
| --- | --- | --- |
| `field_multiply` | Multiply two coefficient codes in the declared quadratic quotient | Direct: 09–10; also inside `hermitian_pair`. |
| `field_sum` | Add coefficients separately modulo p | Indirect: 10 through `hermitian_pair`. Imported but not called in 09. |
| `field_conjugate` | Negate the second coefficient | Direct: 10; also inside `hermitian_pair`. Imported but not called in 09. |
| `field_norm` | Compute the scalar norm from the coefficients | Direct: 09–10. |
| `hermitian_pair` | Check equal tuple lengths, then sum products with conjugated right coordinates | Direct: 10. Imported but not called in 09. |
| `element_label` | Render an integer coefficient code as readable text | Direct: 09–10. Presentation only. |

### Code and projective-chart viewers

Source: [notebooks/code_views.py](../../notebooks/code_views.py).
All five functions serve lesson 11 and consume captured data.

| Function | Responsibility and dependencies |
| --- | --- |
| `binary_panels` | Coefficient snapshots → labeled matrix panels, using `xy_cells` and `style`. |
| `_captured_lines` | Group selected captured support vectors by line rank. Private; used by both projective views. |
| `_line_path` | Route a captured triple in the fixed triangle-and-circle chart. Private; a circle/segment convention, not an incidence test. |
| `fano_gallery` | Display seven support masks and their dual complements using captured lines and chart routing. |
| `linked_field_motion` | Combine equally sampled ring and plane frames, identity colors, static line paths, and one scrubber. Uses the public animation viewer; does not commit a workspace action. |

## Opportunities supported by multiple lessons

The snapshot adapter, keyed comparison, and direct keyed-read inspector are delivered;
the table distinguishes those contracts from remaining work.
Each proposal should first shorten an actual lesson while preserving its evidence.

| Recurring work | Evidence to compare | Smallest useful boundary and required choices |
| --- | --- | --- |
| Keyed snapshot lookup and pivot · delivered | 04–05 now share `keyed_values`/`rectangular_values`; contrast 02–03's ordered reshapes | Explicit integer keys and x/y axes; reject duplicates and holes; ascending observed axes. This does not replace a check against an independently declared domain. |
| Named products · delivered in 05/07 | Public `Product` serves point/line pairs and 07's pair, bin, and energy domains; challenge with 10 `hermitian_incidence` and 11 parity recipes next | Declare factor roles and current-slot reads; preserve semantic keys separately. Relation, retained reductions, expected bins, and dense product cost stay explicit. |
| Guarded assignment | 10 measured owners; 11 quotient, inverse, and syndrome candidates | Reuse existing `coverage`, `on_keys`, `exactly`, `unique`, and `require`. Clarify the expected domain and failure witnesses; do not infer uniqueness from matching totals. |
| Captured explanation · direct keyed reads delivered | 04 `explain_column`; 05 `explain_pixel` now share `Inspection`; compare inline receipts in 06–11 | Follow captured scopes and actual input keys to matched drivers, then measurement origins/contributors/weights. Scalar extraction, positional reads, nested binding keys/reads, and recursive graph explanations remain separate work. |
| Finite comparison report · keyed values delivered | 04–05 use `compare_keyed_values`; 02–03, 08, and 11 still use specialized assertions | The delivered boundary compares exact integer values on declared keys and reports domain failures and residuals. Subsets, occurrences, totals, and declared incidence correspondences remain distinct future comparison kinds. |
| Staged and coordinated replay | Inline sampling throughout; 11 `sampled`; 03/04/05 custom views; 11 `linked_field_motion` | Compose recorded transitions with explicit times, endpoint holds, captions, projection, and ID colors. Keep discrete case selection separate; synchronized views do not imply atomic multi-root history. |
| Measured case family | 08 `measured_family`; compare parameter sweeps in 01 and 10 | A finite case-keyed construction with parameter bindings and retained per-case measurement references. Do not substitute sampled frames for a mathematical family or lose evidence at concatenation. |
| Weighted exclusive prefix · delivered | 06's level packing and dense reference; quotient-column packing in core/studio checks; compare unit-weight ranks in 07 and 10 | `Grouping.prefix_sums` declares strict order, optional groups, globally unique item keys and integer weights. The version-1 operation shares Rank's compact contributor ranges; `Inspection` reconstructs captured weights and reads. |
| Arithmetic and coordinate recipes | 09–10 quadratic formulas; 11 binary polynomial formulas and coordinate dictionary | Separate modulus/basis/encoding, exact arithmetic, and chart placement. First demonstrate a shared contract across models; a packed integer alone does not identify its arithmetic. |

The keyed snapshot adapter and finite keyed-value report in 04–05 are completed
lesson-support extractions from this inventory. Sampling/caption assembly is
another contained authoring improvement. Weighted prefixes now have a shared
ordered-range evidence contract; measured families still need theirs. The inspector does not manufacture a
measurement claim for a concatenated family or a transformed count. These needs
agree with the remaining work in the
[core refinement plan](../CORE_REFINEMENT_PLAN.md).

## Modules, objects, and inheritance

The experimental [construction studio](../CONSTRUCTION_STUDIO.md) adds an authoring
client, not another notebook helper or a lesson superclass. Its scaffolding is
partitioned by changeable decisions: `context.js` selects semantic actions;
`expressions.js` owns compact syntax editing and keyed-read field contexts;
`groups.js` supplies one ordered field-key control for selection, retained keys,
and member order. `drafts.js` owns one unfinished editor's lifetime and original
context across browsing; it retains actual controls and their local undo without
joining mathematical history. `groups.py` queries captured membership and lowers
a chosen group key to an ordinary lens. It shares axis-domain policy and key grouping
with `indexing.py`; it performs no graph execution. `studio.js` composes these
controls with gesture recognition and snapshot/frame drawing. `adapter.py` owns
explicit intent lowering, decimal-integer transport, revisioned previews, and
captured inspection; `server.py` owns the local transport.
`coverage.py` adds a captured expected-key report and a separate Count/Sum/Bind/
Require/Annotate assignment recipe. `web/coverage.js` owns its choices and witness
display, reusing `groups.js`. Assigned fields preserve expected labels and keys;
ordinary binding receipts expose the weighted reduction. The same path is tested
against quotient, modular, additive, and restricted Hermitian constructions.
No existing notebook function inventory or core operation changes in this increment.

The [linked-view instrument](../LINKED_EVIDENCE_VIEWS.md) adds `studio/views.py`
for bounded capture descriptions and complete measurement evidence, including
the zero-contributor source universe. `web/views.js` shares projection policy;
`web/evidence.js` owns two-card selection and independent cameras. Coverage and
receipt controllers supply explicit scoped links, with no lesson branching.
These are studio adapters; no notebook helper count or core class changes.
The [weighted-evidence follow-up](../WEIGHTED_EVIDENCE.md) extracts receipt
presentation/navigation into `web/receipts.js`, keeping contribution weights,
weight-expression reads, and source-field reads distinct. `evidence.js` adds
view-state recall and forwards opaque selection context; `expressions.js` edits
ordered tuples lowered to existing vector expressions. Radon reconstruction and
signed sums share these controls; notebook function counts remain unchanged.

The [parameter-case instrument](../PARAMETER_CASES.md) adds `web/cases.js`
(`caseFields`, `caseLabel`, `caseReport`) for exact declarations and case reports,
plus `web/replay.js::replayControls` for presentation samples with no requests.
`adapter.py::preview_case` validates proposed integer bindings and delegates
evaluation to existing `State.evaluate`; one-use commit/history reuse captured
states. Expression and grid controls emit parameter references, not evaluated
literals. Inline browser work parameterizes Radon and constructs a growing
triangle through the same choices; the weighted test fixture can lower a literal
or a parameterized modulus. Notebooks 05/08 and their function counts are unchanged.

Use the Parnas guidepost in [DESIGN.md](../../DESIGN.md): isolate decisions likely
to change, rather than turning each stage of a lesson into a module. A viewer can
change its routing without changing incidence; an arithmetic recipe can change
its coefficient representation without changing history; an evidence query can
change storage without forcing a lesson to reconstruct contributor joins.

Composition is the initial fit for most repeated recipes. A descriptor for a
coefficient convention or a finite family may eventually give useful names to
related data and operations. Require two concrete consumers before deciding
which behavior that object should own.

Inheritance needs a stronger contract than a shared mathematical theme. A
`CodeArrangement` subtype, for example, would need to define what ordinary
selection, arbitrary value replacement, or reduction does to its promise of
being a linear code. A code recipe that returns generic arrangements and named
evidence avoids silently carrying that promise through invalidating operations.
Subclassing is appropriate when implementations can be substituted under a
stable contract; separate viewer or evaluation implementations may eventually
justify it. The present inventories establish opportunities to investigate, not
a commitment to a hierarchy.

## Maintaining the inventory

When a lesson changes, update its **Functions and authoring scaffolding** section
in the same PR:

1. List every local function, including qualified nested names. State its inputs,
   result, responsibility, and consequential domain or ordering assumptions.
2. Name project helpers actually called, distinguishing direct and indirect use.
   Link their source modules; do not count an unused import as a requirement.
3. Describe substantial inline work: declarations, checks, joins, sampling,
   coordinated edits, and exports. Zero function definitions does not mean zero
   scaffolding.
4. Link a concrete overlap or state the limitation that prevents safe extraction.
   Say whether existing primitives suffice, a recipe would help, or a new
   operation/evidence contract is needed.
5. Update this index's counts, shared consumers, and cross-lesson evidence when
   they change. Keep future proposals separate from delivered APIs.

For an inventory-only edit, check notebook definitions and helper call sites
against the documentation, then check local links and the diff. Notebook execution
and runtime regression tests belong to changes in executable behavior; recorded
lesson validation remains in [notebooks/VALIDATION.md](../../notebooks/VALIDATION.md).
