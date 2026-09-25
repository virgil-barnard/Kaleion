# Kaleion core refinement plan

The later [residue-fiber investigation](lessons/12_residue_fibers.md) reuses
existing primitives to expose quotient groups and carries. Its concrete UI gap
is the difference between a scalar constructor argument and a read per occurrence.
Repeat now accepts a measured singleton through existing `scalar()`, with live
arity checks. This does not justify another evaluator operation. Standalone
ordering and scalar-constructor inspection remain explicit follow-up contracts.

September 19, 2026 · Accepted plan following lessons 01–08; stages A–B delivered, C–D started

**Recommendation:** retain the public mathematical vocabulary and refactor the
implementation around field evaluation, index/group maps, and captured evidence.
Start with a composability defect and three avoidable execution costs. Then make
the repeated notebook constructions easier to express. A wholesale rewrite or an
immediate TensorFlow/PyTorch dependency is not justified by the current evidence.

The original review below concerns baseline `e7a88c1` and the
[lesson review notes](lessons/REVIEW_NOTES.md). [DESIGN.md](../DESIGN.md) remains the
current contract. The [diagnostic script](../examples/core_design_probe.py) and
[baseline results](reviews/2026-09-core-design-probes.json) preserve the audit evidence.

## Delivery status

- **Division and modular relation transfer:** the [paper investigation](DIVISION_MOTION.md)
  exposes existing Move and Roll through a shared transform instrument, and
  shares arithmetic text/term editing with coordinates and weights. Counted
  quotients drive a shear, a wrap and remainder placement; singleton incidence
  measurements compose two relations into a quotient with inspectable witnesses.
  Euclidean shears declare enlarged domains explicitly. Coprimality failures
  separate correct counts from bijective placement and unique composition.
  Reindex / extend now exposes Tile/Gather/Concat and a checked address order;
  unique assignment derives inverse addresses for unrelated 3D occurrences.
  The periodic factor uses actual copies of measured cells, while zero padding
  joins an explicit zero grid. No new evaluator operation is justified. Next test
  Euclidean raw-value extension, modulus changes and per-fiber maps; keep these
  decisions separate from copied domains and presentation paths.

- **UI contract experiment:** the [construction studio](CONSTRUCTION_STUDIO.md)
  constructs additive and modular investigations from blank inputs with one
  contextual action model and a language-neutral adapter. It retains exact previews
  using existing captured history. Shared group selection now distinguishes
  candidates from incident members; compact formulas edit one part at a time.
  One internal axis-domain helper is shared by captured queries and reductions;
  no evaluator primitive or public API change is needed. The
  [UI design study](UI_DESIGN_STUDY.md) adds a research-backed review rubric and
  a tested edit–inspect–return loop: tab-local drafts retain their source and
  local undo, with current feedback and focus recovery. The
  [coverage instrument](COVERAGE_INSTRUMENT.md) now adds independent expected keys,
  captured witnesses, and guarded assignment as a field using existing primitives.
  Simple/additive browser tasks and a restricted Hermitian adapter case exercise
  the same contract. [Linked evidence views](LINKED_EVIDENCE_VIEWS.md) now keep
  coverage witnesses, keyed drivers, and measurement contributors together through
  explicit scoped references. Coverage and quotient browser tasks exercise the
  same renderer, with zero sources and earlier inputs intact. [Weighted evidence
  navigation](WEIGHTED_EVIDENCE.md) now adds ordered key tuples and follows Radon
  contributions through weight and source-field reads, retaining return views.
  [Explicit parameter cases](PARAMETER_CASES.md) now reuse declared integers in
  formulas and extents, preserve evaluated failures, and distinguish case endpoints
  from captured replay. Radon modulus and triangle growth exercise the same controls.
  Measured case families, full-lesson coverage, and reactive source edits remain open.
  [Short relation notation](RELATION_NOTATION.md) now lowers comparisons and
  Boolean combinations to the same expression protocol, with reversible syntax
  views and exact previews. The [comparable-workspaces survey](COMPARABLE_WORKSPACES.md)
  prioritizes visible expression scope and measurement reuse before new primitives.
  The [field guide](FIELD_GUIDE.md) now links field terms and grouping controls
  to captured fibers on that same canvas, including zero-match candidates and
  driver context. It reuses the group endpoint; no core primitive is required.
  The [deferred conjecture workflow](PROVENANCE_CONJECTURES.md) preserves the
  longer-term proof goal while keeping statement/proof policy outside evaluation.

- **Stage A delivered:** bound and nested-case incidences compose and select with
  their original scopes. `Incidence.universe` exposes the inspected collection or
  arrangement. The field interpreter now lives in `expressions.py`; motion has no
  import from graph execution.
- **Stage B delivered:** contributor grouping takes one pass over the
  selected items. Correspondence, occurrence indexes, ancestry, and membership are
  prepared once per captured motion root and reused for playback and undo.
  Internal derivation now shares unchanged validated buffers; public construction
  copies inputs and seals identity, lineage, scalar attributes, and metadata.
- **Stage C started:** `indexing.py` owns keys, alignment, group domains, and
  rectangular address rules. Named operations retain explicit identity and placement
  policies. The evaluator still owns both scheduling and operation dispatch.
- **Stage D started:** explicit grouping, strict member order, coverage with
  witnesses and guarded assignment, and named coordinates simplify lessons 07 and
  10. Ordered ranks replace dense predecessor products and retain compact evidence.
  `grouping.py` owns authoring choices; `measurements.py` hides contributor storage.
  The [authoring guide](AUTHORING.md) states the implemented contracts.
- **Captured inspection delivered:** `Inspection(state)` follows pointwise keyed
  reads and preserved measurements using saved scopes and inputs. Lessons 04–05
  use it for their column/pixel explanations, including weights and original
  contributors. No new operation or capture schema is needed. See the cross-lesson
  [workflow and query limits](EXPLORATION_WORKFLOW.md).
- **Named products delivered:** `Product` names factor roles and source reads in
  lessons 05 and 07. It lowers to existing operations, preserves multiplicity and
  empty-axis zero groups, and states the slot-identity and dense-cost limits.
  The [touch study](TOUCH_WORKSPACE.md) tests how the shared choices might become
  controls; it is a bounded captured demonstration, not a general editor.
- **Delivered weighted prefixes:** exact exclusive accumulation now shares the
  strict order plan and compact contributor ranges with Rank. Lesson 06 uses it
  for layer offsets; the studio transfers it to quotient-column packing. Nested
  receipts retain the earlier measured layers and their original contributors.
- **Next:** measured case families,
  and comparison kinds beyond exact keyed integer values. Separate operation
  execution from session scheduling when that reduces concrete coupling. The public
  `Coverage` helper is scoped to an existing reduction domain, so it does not complete the general
  comparison work.

A contained lesson-support extraction now shares strict integer-key lookup,
rectangular snapshot projection, and finite keyed-value comparison between lessons
04–05. It replaces four local helpers with two read-only adapters and adds a report
over captured snapshots, without adding a core operation. The report distinguishes
missing and unexpected keys on both sides from exact residuals on common keys;
its optional expected domain is an independent authoring choice. The
[helper inventory](lessons/HELPER_INVENTORY.md) records this boundary. Comparisons
of subsets, occurrences, totals, and declared correspondences remain separate work.

The studio now exercises that same finite comparison contract for Radon and
lattice counts. Integer-key lookup and comparison live in `kaleion.comparison`;
the notebook helper retains compatible reexports and its rectangular projection.
Value-field selection is explicit, while the studio requires the independent
expected-domain choice and attaches captured references for inspection. This
extraction serves two clients without moving rendering or evaluator policy into
the comparison module. See [the comparison guide](KEYED_COMPARISON.md).

The [canvas walkthrough](CANVAS_TUTORIAL.md) now makes the complete introductory
loop reproducible through those controls and exposes a placement-visibility bug:
new coordinates must actually become the displayed chart. Five additional
worked captures cover first motion, measured packing, three planar lifts and
per-cell box ownership with a failed assumption. The tutorial and catalog remain
presentation modules; the existing comparison and measurement contracts suffice.
The same construction exposed placement discoverability rather than a missing
primitive: **Arrange / move** now opens the existing coordinate editor directly
from a selected collection, without duplicating it in More tools.

The [first implementation results](reviews/2026-09-core-refactor-probes.json) record
the tested working tree with a core-source digest. For 2,000 one-item groups, the
diagnostic fell from roughly 0.50 s to 0.027 s on this host. Its motion fixture now
prepares tracks once at capture and performs no new preparation for 21 forward and
21 reverse samples; the baseline rebuilt tracks for each forward frame. That first
report still exposes snapshot copying and missing per-target driver references.
These timings are bounded observations, not a general performance guarantee.

The [ownership/indexing comparison](reviews/2026-09-ownership-indexing-probes.json)
checks the same 2,000-item, 24-move graph against merged revision `0b7d61c`. Across
26 retained snapshots, value buffers fall from 26 to one, and unchanged attribute
buffers from 52 to two. Their array storage falls from 1,248,000 to 48,000 bytes;
total traced peak memory falls from about 8.2 to 6.9 MB. Median evaluation time on
this host falls from about 54 to 42 ms. Changed placement still requires 25 distinct
buffers. Cross-case caching, disk deduplication, and per-target driver explanations
remain separate work.

The [ordered-group comparison](reviews/2026-09-grouping-probes.json) runs the old
dense predecessor recipe and new rank operation in the same current evaluator.
For 96 items in six groups, the largest intermediate falls from 9,216 to 96 items,
and compact captured JSON from 6,357,997 to 80,962 bytes. The rank stores 96 ordered
occurrences and 96 prefix ranges instead of enumerating all 720 predecessor entries.
Core-source digests identify the tested implementation; timings and traced memory
are observations on one host. Reproduce with
`python3 examples/grouping_probe.py --out build/grouping-probe.json`.

From the repository root, with the documented virtual environment active:

```sh
mkdir -p build
python3 examples/core_design_probe.py > build/core-design-probes.json
```

The diagnostic reports observed failures rather than treating them as successful
contract tests. Its internal probes belong to this audit and should evolve with the refactor.

## 1. Apply Parnas to actual change decisions

Parnas's circular-shift example hides whether shifts are stored, indexed, or computed
on demand. He also identifies unnecessary ordering promises as a restriction on
future implementations. Module interfaces need not become repeated runtime calls;
the implementation can combine work efficiently. These are the relevant lessons
from the [archived 1971 report](https://kilthub.cmu.edu/articles/journal_contribution/On_the_criteria_to_be_used_in_decomposing_systems_into_modules/6607958),
preceding the [1972 ACM paper](https://doi.org/10.1145/361598.361623).

Our application: assign each changeable decision one owner, expose its mathematical
contract, and measure the compiled or interpreted work separately. Module count and
operator count are poor targets for minimization. An interface with fewer hidden
assumptions is simpler even when it lives in another small file.

Preserve deliberately declared order: sequence order, stable sorting, and the existing
first-appearance grouping convention. Key matching must remain independent of storage.
An ordered scan needs a declared order; a driver binding does not need positional zip.

## 2. What the reviewed baseline does well—and where it leaks

The 2,610-line core, excluding optional viewers, is still small. Keep its separation
of definitions, explicit evaluation, retained snapshots, motion, and viewers. Preserve
integer exactness, occurrence/source distinctions, zero groups, failed-branch isolation,
and undo by retained state. The notebooks establish useful examples of those contracts;
they do not establish arbitrary composition, large-scale performance, or usability.

| Finding in the reviewed source | Consequence | Recommended response |
| --- | --- | --- |
| `Incidence._combine`, `__invert__`, and `select` inspect the immediate node's attributes/input kind | After `with_params`, evaluation works but Boolean composition fails and selection has the wrong symbolic type | Centralize the incidence's scoped universe and result-kind semantics; stop assuming every incidence node is a direct `where` |
| `evaluate.py` combines scheduling, expression interpretation, address construction, grouping policy, and lineage assembly | Adding a constructor or changing evidence storage reaches the same evaluator machinery | Extract pure expression evaluation and map/group helpers; separate named-operation execution from session scheduling |
| `_reduce` scans selected items again for every output group's parents | Contributor assembly costs O(KM) for K groups and M selected items, despite a linear segment-sum kernel | Bucket contributors once, retaining group order and empty groups |
| `Snapshot.__post_init__` copies unchanged buffers during `replace`; `Evaluator.get` uses `replace` to assign runtime node identity | Even a node-name change copies values, fields, and positions | Introduce an internal validated construction path with explicit buffer ownership |
| `Transition.frame` rebuilds tracks on every sample and ancestry lookup uses tuple searches | Fixed correspondence work repeats during playback | Prepare immutable tracks and occurrence lookup indexes once per captured transition |
| Binding expressions record graph dependencies, but derived snapshots' direct parents identify only the target items | A generic per-target explanation cannot obtain matched driver items from `parents` alone | Record/query binding alignment separately from target continuity and motion correspondence |
| Concatenation drops active reduction metadata; lesson 08 retains case roots manually | A measured family is reusable but awkward to explain | Add a case-family recipe and a provenance query over scoped result references |
| `Sweep` depends on history's state factory; workspace edits create fresh evaluators; JSON expands materialized results repeatedly | Case execution, caching, and storage choices are not fully hidden | Delegate case requests to one evaluation service; stage cache/storage work after ownership is sound |

The parameter-case defect has a small reproduction:

```python
from kaleion import Collection, F, param

A = Collection.sequence(4).arrange(F.value, 0)
I = A.where(F.value > param("n")).with_params(n=2)
I.evaluate().cardinality       # 2, correct in the reviewed baseline
# (~I).evaluate()              # baseline raised KeyError('rule'); now works
# (I & I).evaluate()           # baseline raised KeyError('rule'); now works
# I.select().arrange(F.value, 0)  # baseline mistyped selection; now works
```

This was a correctness problem, not a request for a more permissive universe rule.
Parameter binding can change a source domain. The repair must retain lexical scope
and reject combinations of different declared universes unless alignment is explicit.
Equal array lengths or equal coordinates are insufficient.
A focused semantic query for an incidence's source and scope is the first step;
this defect does not justify introducing a general type-inference framework.

The bounded diagnostic also found:

- Changing only a 200-item snapshot's node label invokes one exact-value conversion
  and five read-only-copy calls. None of its value, position, or three field buffers
  is shared with the original.
- Sampling 21 frames of one captured 200-item transition constructs its tracks 21 times.
- A two-item keyed displacement has the driver in its definition dependencies and
  produces the correct positions, but has zero direct driver-parent references.
- For 2,000 selected items, a total count took about 5 ms, while one group per item
  took about 0.5 s on this host. The nested contributor loop explains an avoidable
  cost. These are baseline timings, not measurements of an implemented speedup.

## 3. A small mathematical substrate

Use a finite **occurrence domain** D with typed fields on it: integer contents,
attributes, logical keys, optional coordinates, and Boolean incidence. Identity
remains protected bookkeeping; it is not an ordinary editable label.

Two maps explain much of the current behavior:

- An index map `u: E → D` transports a field by `f'(e) = f(u(e))`. Gather, indexed
  lookup, roll, tiling, and keyed reads can share this numerical mechanism.
- A grouping map `g: D → K` combines selected field values over each fiber:

  \[
  S(k)=\sum_{d\in D:\,g(d)=k}\mathbf1_{R(d)}\,w(d).
  \]

  Count uses weight one. Sum uses an integer-valued expression. K must be declared
  or derived under an explicit policy, so empty fibers and unavailable inputs differ.

The implementation needs the following families; this is a useful working basis,
not a claim of universal mathematical minimality.

| Family | Responsibility | Existing or anticipated uses |
| --- | --- | --- |
| Finite domains | Enumerate occurrences, products, disjoint unions, and declared keys | Sequence, Grid, paired domains, Concat, case families |
| Field expressions | Evaluate typed arithmetic, predicates, and coordinates | Values, Annotate, Place, Move, Lens |
| Index maps | Transport fields with checked addresses | Gather, Lookup, Roll, Tile, Select, keyed binding |
| Grouped reduction | Combine selected weights over a specified key domain | Count, Sum, Any, convolution, finite-line measurements |
| Ordered scan | Accumulate along explicit order, optionally within groups | Exclusive weighted prefixes and predecessor ranks delivered; arbitrary scans/recurrences remain separate |
| Bounded recurrence | Carry state and emit occurrences/roles under a work limit | General authored spirals, stair steps, and 3D paths; later extension |

Count is a readable operation even if its kernel is a masked sum. Roll is a readable
operation even if its kernel is gather. **Shared kernels do not imply identical
operation semantics.** Today's Gather creates fresh occurrences and drops placement;
Roll preserves occurrence identity while moving contents between fixed slots;
Select preserves selected identities and, when present, placement. Retain those
policies when sharing address computation. Likewise, Pad needs explicit fill keys,
attribute fills, and source identities; naive concatenation is not a compatibility proof.

Keep named operations in the saved construction graph. An internal execution plan
may fuse or specialize them without erasing their names, parameters, or evidence.
Do not expand every efficient operation into a large product merely to reduce the
number of opcodes. In particular, dense matrices are optional representations of
relations, not the required representation of an index map or a reduction.
An associative prefix scan and an arbitrary stateful recurrence have different
scheduling guarantees; arbitrary authored steps do not imply a parallel algorithm.

## 4. Boundaries worth making explicit

These are ownership boundaries, not a mandate to create a class for every row.
Extract a small function or record first; preserve public imports and method names.

| Owner | Decision hidden | Small contract |
| --- | --- | --- |
| Definitions: `ir.py` / `api.py` | Expression encoding, scoping, output kinds, named operation meaning | Immutable definitions; scoped universe information; dependencies; versioned graph compatibility |
| Field evaluator: proposed `expressions.py` | Interpretation of scalar/field expressions | Rule + field context + parameters + injected source resolver → value or explicit error |
| Indexing: proposed `indexing.py` | Key representation, alignment, address generation, grouping/order plans | Checked index maps and grouping maps with explicit domains, multiplicity, and order |
| Numerical kernels: `tensor.py` | Exact-integer representation and implementation of bulk arithmetic | Checked field operations, gather, segment reduction; explicit numerical limits |
| Results and evidence: `model.py`, with focused lineage helpers | Buffer ownership, occurrence-reference encoding, contributor storage | Immutable results; distinct identity/causal/motion references; bounded explanation queries |
| Evaluation session and operation handlers | When work executes versus how a named operation is carried out | Session owns scope, cache, budgets, and root outcomes; handlers consume resolved inputs and return results/evidence |
| Motion: `motion.py` | Matching captured occurrences and sampling their path | Prepared tracks + path + progress → Frame, independent of source reevaluation |
| History and codecs | Retention, restoration, and on-disk sharing | Captured states and commands; compatible import/export without source execution |
| Viewers and later notation | Plot technology and mathematical presentation | Consume captured results or semantic definition views; never invent arithmetic or proof status |

`motion.py` should import the small field evaluator rather than the graph evaluator.
History and Sweep should request captured results through the same evaluation entry
point. Separate handlers can share the indexing and result-building functions;
introducing a plugin registry or inheritance framework is unnecessary for this step.

Three pieces of evidence must remain distinct: **operation dependencies**, **which
items contributed or were read**, and **which occurrence continues through motion**.
A later derivative tape is another record. Putting all four in one generic edge list
would make the system shorter to describe but harder to interpret correctly.

## 5. Enrich the authoring language with proven recipes

The table is the original recipe agenda. Strict ranks and weighted prefixes are now
implemented as `source.group_by(...).order_by(...).ranks(key=...)` and
`.prefix_sums(key=..., value=...)`, along with scoped coverage and
named placement. Captured keyed-read/measurement inspection is now implemented,
as is the lesson-support report for exact keyed integer values. The remaining
rows and broader forms of these queries are proposals, not API signatures.

| Recipe or view | Required choices and result | First demonstrations |
| --- | --- | --- |
| Paired domain | Two finite sources, distinct field namespaces, both source references; full domain versus selected relation remains explicit | Finite Radon measurement; equal-sum pairs |
| Exclusive prefix sum | Source order and optional groups; one result per source key; first result zero | Young layer offsets; packing measured quotient columns |
| Rank within groups | Group key and unique order key, or an explicit tie policy; one rank per input occurrence | Equal-sum stacks; packing unordered height layers |
| Measured case family | Finite case keys, named parameter bindings, retained measurement references; compound case/group keys for grouped outputs | Ehrhart counts; quotient profiles as parameters vary |
| Explanation query | Scoped target reference → matched driver → measurement/contributors; include weight/read expression and coverage | Existing column, pixel, layer, sum, and dilation explanations |
| Finite comparison | Both key domains, declared meaning, residuals and witnesses; missing keys stay explicit | Quotient partition, reconstruction, reciprocity |

A prefix or rank should use an ordered scan or stable grouping/sorting, not materialize
all predecessor pairs. If sorting is necessary, its cost is normally O(N log N);
an already ordered grouped scan can be linear. Explicitly listing every prefix's
contributors still takes quadratic space. Store a compact order/range derivation
and expand the requested explanation, rather than promising free full provenance.

Case families must preserve the parameter environment of each measurement, including
zeros and variable group domains. Neither concatenated storage order nor one unscoped
key should become the identity of a case. The current single-case roots remain valid
inputs to the explanation adapter during migration.

Add a notation renderer once the semantic views are reliable. It should display
named sets, predicates, grouped sums, parameter cases, and equality scope beside
the plots, with aliases separate from definition identity. Unknown/custom operations
remain named operations with stated inputs. They must not acquire invented formulas.
This advances the intended Euclid-like reading experience before a new parser or GUI.

## 6. Preserve the path to future capabilities

| Future capability | Boundary it exercises | Constraint to retain |
| --- | --- | --- |
| Authored recurrences and scattered 3D arrangements | Finite-domain generation and bounded recurrence | Explicit initial state, step/emission rule, stop/budget behavior, stable occurrence keys, structural roles, and checkpoint state |
| Larger logical products | Domain/indexing | Logical rank is independent of display dimension; today's 1–3-axis Grid limit is an API restriction, not a mathematical requirement |
| Infinite-scroll presentation | Evaluation requests and result coverage | Request finite extents; camera visibility does not redefine the mathematical domain or a whole-domain count |
| GPU execution | Kernels and operation execution plans | Exact arithmetic cannot silently become floating point; fixed-width kernels require checked range assumptions and a compatible fallback or explicit refusal |
| Differentiation | Numerical domains and optional derivative rules | Fixed-index gather on continuous fields has a scatter-add adjoint; integer addresses, predicates, sorting choices, and cardinalities do not acquire gradients by being animated |
| Finite fields or continuous weights | Explicit numerical-domain extensions | Residue fields, integers, floats, and geometric tolerances have different laws; integer-weight Sum does not already support arbitrary real weights |
| Proof assistance | Definitions, explanations, and finite comparisons | A checked finite equality and a universal theorem are different claims; exploratory/custom operations may remain opaque to a prover |

Continuous coordinates and some attributes already exist. Differentiating that
continuous subgraph need not first turn all contents into floats. Continuous contents
or weighted real reductions would need their own explicit value-domain extension.
Keep these experiments independent of exact integer discovery and of motion replay.

Changing the NumPy import in `tensor.py` would not provide a device backend:
expression evaluation, snapshots, and motion also materialize NumPy buffers. First
accelerate one contained execution segment and make transfer to the existing CPU
snapshot explicit. Avoid a host/device transfer at every operation. Device-resident
results would later require a result-access boundary as well as numerical kernels.

Do not require every future construction to lower to the small built-in vocabulary.
When a concrete authored rule needs an extension, require bounded inputs/outputs,
versions, declared capabilities, and an explicit identity policy. An opaque operation
may support forward snapshots without supporting compilation, inspection, or proof.
Portable captures must remain inspectable when its implementation is unavailable.

## 7. Deliver in small, reviewable stages

| Stage | Work | Acceptance gate |
| --- | --- | --- |
| A · Repair composition | Add regressions for bound/nested-case incidence Boolean operations and selection; centralize scoped universe/result-kind interpretation; extract the pure field evaluator | Existing lessons still run; new compositions succeed; incompatible universes fail intentionally; motion no longer imports graph execution |
| B · Remove repeated work | One-pass contributor grouping; prepared motion tracks and lookup indexes; internal owned-buffer construction | Same values, identities, ordered contributors, zero groups, errors, and reverse paths; linear contributor assembly; one track preparation per immutable endpoint pair; unchanged buffers reused safely |
| C · Establish the shared mechanisms | Extract index/group plans and evidence-building helpers; separate session scheduling from operation handlers; retain named definitions | Roll, Gather, Tile, Lookup, Select, and reductions use the shared mechanisms while preserving their different policies and v1 import behavior |
| D · Shorten two real investigations | Introduce prefix/rank and case-family recipes, a bounded explanation query, and explicit keyed comparisons; rewrite small sections of lessons 06–08 alongside their reference constructions | Two independent uses per convenience; numerical equivalence, key coverage, contributor explanations, and undo checked; no dense predecessor expansion |
| E · Test one new reach | Express the rectangular spiral and a restart-and-grow stair step through one bounded recurrence; then choose either a windowed evaluator or one accelerated continuous-field example | Preserve spiral prefix/role fixtures; declare coverage and work bounds; supported results match reference; unsupported capabilities fail without losing captures |

Stages A–C refine contracts and internals. Stage D should deliver an observable
improvement in reading and composing mathematics. Start the touch-interface design
after that comparison. Full GPU support, general proof automation, and a broad custom
language should remain separate projects driven by actual investigations.

Efficiency gates need declared fixtures and measured outcomes. Alongside the eight
lessons, use many small reduction groups, repeated-gather ancestry, a long sequence
of placement-only edits, and a reordered parameter family. Compare operation work,
peak memory, capture size, and sample latency against the recorded baseline. Do not
set a universal frame-rate or speedup promise from one host's microbenchmark.

Refactoring must also preserve eager expression error behavior (`choose` currently
evaluates both branches), checked address bounds, and existing budget failures in
compatibility mode. New streaming/work budgets require a declared contract. Cache
reuse must respect definition, parameter scope, extent, numerical policy, and applicable
budgets; a stale or failed result cannot become a zero or masquerade as a current case.

At external boundaries, continue copying/validating caller-owned mutable arrays.
Internal sharing needs an ownership contract; NumPy's read-only flag alone does not
establish exclusive ownership. Retain schema-1 loading and legacy Icarus envelopes.
If compressed evidence or storage needs a new format, version it explicitly and test
reopening old captures without executing sources. Do not migrate history silently.

**Implementation completed:** Stages A–B, the index/group-rule portion of C, and
the ordered-rank/coverage portion of D exercised in lessons 07 and 10. Weighted
prefixes now serve lesson 06 and quotient-column packing through the studio.
Stage D is not complete: case families, broader comparison meanings,
and explanation of scalar/positional or nested driver reads remain. Direct keyed
bindings and captured measurement receipts now serve lessons 04–05. The next
refinements should address those concrete gaps before adding another layer of notation.

## Original review validation

The baseline's 55 tests and `python3 examples/discovery.py --out build/example-output`
pass. The diagnostic reproduces the recorded non-timing findings; its known-failure
reports reveal cases the existing suite does not cover. Local document links resolve.
This proposal changes documentation and adds the diagnostic, without implementing
the planned repairs or claiming a measured improvement. Notebook rendering checks
were not repeated for a documentation review; their existing evidence remains in
[notebooks/VALIDATION.md](../notebooks/VALIDATION.md).

The ownership/indexing implementation passed 74 tests and all eight notebooks.
Later deliveries and their current checks are recorded in
[VALIDATION.md](../VALIDATION.md); the same host limitation on live Jupyter kernel
sockets applies. See
[DESIGN.md](../DESIGN.md) for new-operation compatibility and track-memory costs.
