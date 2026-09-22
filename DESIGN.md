# Design contracts

## Decompose by decisions that may change

The module boundary is chosen around a hidden decision: expression representation, numerical execution, item correspondence, state retention, or motion presentation. This follows the information-hiding approach in [Parnas, “On the Criteria To Be Used in Decomposing Systems into Modules”](https://kilthub.cmu.edu/articles/journal_contribution/On_the_criteria_to_be_used_in_decomposing_systems_into_modules/6607958). It is our application of that principle, not a claim that the paper prescribes these particular classes.

| Module | Owns | Contract exposed to clients |
| --- | --- | --- |
| `ir.py` | Immutable expression/operation definitions, definition identity, graph encoding | Versioned definitions with explicit dependencies; no rendering or numerical execution |
| `api.py` | Typed construction vocabulary and operator syntax | Pure builders returning new definitions |
| `grouping.py` | Grouping, member-order, and coverage declarations | Small immutable records; recipes build definitions without evaluation |
| `products.py` | Named factors and current-slot addressing for finite products | Lazy Grid/Count/Bind recipe; explicit source reads, multiplicity, and new tuple occurrences |
| `expressions.py` | Scalar/field interpretation, including explicit driver reads | Context, parameters, and an injected resolver produce a value or an error; no graph scheduling |
| `tensor.py` | Exact integer rules, array validation, elementary numerical kernels | Checked arithmetic, broadcasting, gathering, and segment reduction |
| `indexing.py` | Key representation, alignment, group domains, member ordering, rectangular address maps | Checked keys and addresses; no occurrence identity or placement policy |
| `model.py` | Buffer ownership, evaluated data, occurrence/source identity, lineage, snapshot encoding | Validated finite snapshots; unchanged owned buffers may be shared |
| `measurements.py` | Captured contributor representation and queries | Enumerated contributors or versioned ordered prefixes; no evaluator or viewer dependency |
| `inspection.py` | Scoped navigation of captured items, measurement origins, and declared keyed reads | Read-only receipts from saved inputs; no graph execution, history edits, or plotting |
| `evaluate.py` | CPU evaluation, dependency ordering, parameter cases, bounded work | A result or an explicit error for each requested root |
| `motion.py` | Correspondence tracks, paths, reverse sampling | Presentation frames derived from captured states; no changes to mathematical results |
| `history.py` | Workspace commands, exact retained states, captures, persistence | Undo/redo, independent observations, portable historical results |
| `sweep.py` | Parameter-case selection and retention | Explicit coverage through a case, independent of playback sampling |
| `viewers/` | Optional plotting, playback controls, and video encoding | Consume snapshots/frames; never evaluate definitions or mutate mathematical state |

The evaluator currently uses NumPy directly as well as the kernel helpers. There is no interchangeable backend interface pretending to be complete. A future GPU evaluator can consume the same operation definitions while implementing supported operations and numerical types. Some reference algorithms—key factorization, lineage assembly, and the spiral scan—are Python control flow today.

The [core refinement plan](docs/CORE_REFINEMENT_PLAN.md) audits these boundaries
against lessons 01–08. Its first delivered changes centralize incidence-universe
semantics in `ir.py`, separate field interpretation from evaluation sessions, group
contributors in one pass, and prepare motion correspondence once. Snapshot ownership
and shared indexing rules are now implemented too. Explicit grouping, strict ranks,
coverage guards, and named placement shorten lessons 07 and 10. Operation-handler
separation, weighted prefix sums, and case families remain planned. The
[exploration workflow](docs/EXPLORATION_WORKFLOW.md) audits all eleven lessons;
captured measurement and keyed-read inspection now serves lessons 04–05.
Named products now serve 05 and 07. The [touch workspace study](docs/TOUCH_WORKSPACE.md)
maps these choices to proposed controls, separating input gestures, semantic edits,
exact previews, captured history, and rendering.

The experimental [construction studio](docs/CONSTRUCTION_STUDIO.md) now tests a
language-neutral command boundary outside the installed core. Its action resolver
depends on selector scope and target capabilities; its adapter lowers explicit
declarations to existing builders. Preview tokens refer to captured states, and
commit retains the accepted capture without reevaluation. Gesture policy,
declaration editing, numerical execution, and history remain separate decisions.
No public core signature, evaluator opcode, or saved schema changes are required.

Its group selector queries captured candidates and incidence separately, without
graph evaluation. The query shares the reducer's retained-axis domain policy in
`indexing.retained_axes_shape`: declared axis fibers survive empty input; other
keys are observed. Captured group selection is view state, not a measurement or
an ordering rule. Creating a lens lowers the selected native key to an existing
predicate while preserving the original universe. Formula editing owns syntax
and context choices separately from compilation and numerical execution.

The client now isolates unfinished-editor lifetime in `drafts.js`: browsing can
park and resume the same controls without changing their source or losing local
undo. A draft is tab-local view state; only the existing revisioned preview/apply
boundary changes captured history. The [UI design study](docs/UI_DESIGN_STUDY.md)
provides evidence-based review questions and testable interaction hypotheses;
these presentation decisions introduce no core primitive or saved-format change.

## Four different things an arrangement contains

For an evaluated arrangement with N items:

| Quantity | Representation | Meaning |
| --- | --- | --- |
| Contents | `values[N]` | Exact integer labels |
| Occurrences | `ids[N]` | Distinct appearances, including repeated copies |
| Logical addressing | Named fields and optional rectangular `shape` | An explicitly declared indexed domain |
| Placement | `positions[N, d]`, 1 ≤ d ≤ 3 | Coordinates independent of storage and labels |

`sources[N]` records underlying source identity. `parents[N]` records direct causal input references. `motion_parents[N]` supplies a single correspondence when one exists. A count can have several causal parents and no single motion parent.

Independent source constructors receive independent namespaces. Deriving placements or labels preserves item identity when appropriate. Gather/Tile/Concat can create new occurrence IDs while preserving source identities. Source identities must not be inferred from equal labels or coincident coordinates.

Rectangular logical indices are destination slots after an axis gather or roll. To retain an original index as data, annotate it under a separate name before the operation. `F.index` is the current flat ordinal, not a persistent identity. Keyed bindings use explicit source/target keys rather than physical order.

## Named products are authoring recipes

`Product(point=points, line=lines)` supplies `.domain` and `.read(role, field)`.
It composes existing Grid, total Count, Scalar, and Bind expressions. No evaluator
operation or saved schema is added. Graph serialization retains the lowered
definitions, names, and dependencies; the Python wrapper is not serialized.

Factors are two or three collections/arrangements in declared order. The last
role varies fastest. The domain has a new occurrence for each tuple of **current
source slots**, unit values, named logical axes, and no inherited placement.
Role names cannot shadow built-in fields. Reads align a role axis with source
`F.index`; repeated labels and retained keys do not merge occurrences. Retain
semantic keys/fields explicitly with `annotate` before reindexing or overwriting
role axes. Reordering a factor changes the values read at each slot; it does not
promise continuity of source-pair identity across that edit. An application needing
that continuity must declare and preserve a different correspondence.

An empty factor gives an empty rectangular product; the other role's declared
axis still supplies zero groups for a reduction. Factors are not implicitly
filtered incidences: call `select()` deliberately. Geometry, predicates, weights,
retained measurement keys, and expected bins remain separate choices.

Product cost remains the product of factor sizes, bounded by the existing
evaluator item limit. Source total counts establish symbolic extents and retain
ordinary evidence; this is not a sparse join or a faster tensor kernel. A future
size/shape query or product execution strategy needs its own demonstrated contract.
The [authoring guide](docs/AUTHORING.md) records migration and examples.

## Snapshot ownership

Public snapshot construction copies and validates incoming buffers, even if a
caller marks an array read-only. Identity, shape, axis, and lineage containers are
converted to immutable tuples. Attribute elements must be finite immutable scalars;
mutable objects inside an object array are refused. Exact integer contents and
integer attributes normalize NumPy integer scalars to Python integers before
arithmetic, so object dtype cannot conceal fixed-width overflow.

The evaluator uses a private update path on already validated snapshots. It shares
only unchanged owned buffers and frozen metadata members; new or changed inputs
are copied and validated. Runtime identity changes therefore allocate no new data
buffers. Placement changes retain the contents and attributes; annotation copies
new fields while retaining the others. A public `dataclasses.replace` still uses
the copying constructor. Read-only flags are a use contract; clients needing
writable data should make their own copies.

Sharing is local to retained snapshots in an evaluation. Workspace edits and
parameter cases still use separate evaluators; this change does not introduce a
cross-case cache or deduplicate arrays on disk. Schema-1 captures remain materialized
and reopen independently of the original process.

## Tensor interpretation

These operations form the reference implementation vocabulary; the table describes semantics, not a fully compiled tensor IR.

| User operation | Core computation | Important policy |
| --- | --- | --- |
| Sequence | `start + step * arange(N)` | Integer contents; explicit finite length |
| Grid | Cartesian logical indices → elementwise value expression | 1–3 declared axes; placement is separate |
| Placement | Stack coordinate expressions into N × d | Finite `float64` geometry |
| Move | `P' = P + D` | Broadcast one vector or provide one per occurrence |
| Value transform | `v' = f(v, fields, parameters, bindings)` | Output must be integer-valued |
| Incidence | Elementwise Boolean predicate `m` | Invalid computation is an error, not false |
| Select | `nonzero(m)` → Gather | The selected collection has a new finite universe |
| Gather | `out[j] = input[address[j]]` | Repetition and omission allowed; address bounds checked |
| Permute | Gather plus bijectivity validation | Same index set, exactly one use per source slot |
| Roll | Subtract shift → positive modulus → Gather | One displacement per shifted fiber; placement stays in its slots |
| Tile | Repeat address sequence → Gather | Copies are distinct occurrences |
| Lookup | Gather table values by declared integer addresses | Content substitution, distinct from reindexing the source |
| Concat / Pad | Concatenate data and lineage; Pad creates explicit fill items | Shape/attribute compatibility checked |
| Count / Sum | Factorize keys → masked weights → segment sum | Initialize all declared groups, including zero groups |
| Group rank | Factorize keys → lexicographic sort → predecessor count | Unique item keys and strict member order; compact prefix evidence |
| Require | Check all incidence entries → pass through items | Failed checks block this dependency; witnesses remain inspectable |
| Driver binding | Key alignment → Gather selected source field | Unique source keys; complete requested matches |
| Spiral | Bounded stateful scan → positions and structural fields | Special reference constructor, not a general recursive language |

`indexing.py` owns first-appearance grouping, declared Cartesian group domains,
unique-key alignment, address bounds, and rectangular Gather/Tile/Roll/Concat maps.
Roll reduces exact shifts modulo the axis extent before using flat strides, avoiding
full coordinate grids. The evaluator's indexing adapter names placement policy as
`drop`, `gather`, or `fixed`; it also owns occurrence and lineage policy. Sharing an
address calculation does not make Gather and Roll the same mathematical operation.
The former `tensor.key_rows`, `factorize`, and `align` entry points delegate to the
new module for compatibility.

For grouping key g, mask m, and integer values v, the implemented reductions are:

\[
\operatorname{count}_t = \sum_{p:g(p)=t} \mathbf 1_{m(p)},
\qquad
\operatorname{sum}_t = \sum_{p:g(p)=t} \mathbf 1_{m(p)}v(p).
\]

The output key domain comes from the source before masking. If the grouping consists of retained axes of a declared rectangular domain, use their Cartesian domain even when an eliminated axis is empty. For other expressions, use observed source keys in first-appearance order. A total reduction returns one item, with sum/count zero on an empty universe. `any` returns an integer indicator 0 or 1.

Contributor assembly visits each selected occurrence once and freezes one ordered
bucket per output key: O(M + K) work for M selected occurrences and K groups.
Zero and negative weights still have contributors; their arithmetic contribution
does not determine whether they belonged to the incidence.

Counts here measure occurrences. Distinct-source or geometric-area measures must be expressed separately; they are not implicit aliases for count. The graph, key, relation, source extent, and contributor identities remain available for later analytical statements.

### Grouping and ordering are independent

`items.group_by(...)` declares retained keys. Its `count` and `sum` methods build
the existing reductions. `groups.order_by(...)` declares lexicographic **member**
order; `groups.order_by(...).ranks(key=...)` produces a measurement for each selected
item. Output item keys must be globally unique, and member-order tuples must be
unique within a group. Ties fail instead of silently adopting storage order.
An incidence ranks only selected occurrences; a count retains its pre-mask domain.
The storage order of resulting groups is chosen separately with
`counts.order_by(...)`.

Retained fields keep their declared names. `F.key` aliases the sole retained key,
or supplies an ordinal for a composite key only when `key` is not itself a retained
field. `groups.key` reads the complete scalar/composite key from a grouped result.
This corrects an earlier edge case where a retained field named `key` was overwritten.

Rank execution takes O(N log N) worst-case time and stores O(N) evidence: one ordered
roster of source occurrence IDs per group, and one `(group, stop)` prefix range per
result. `Snapshot.contributor_ids(key)` finds that retained key and expands only its
prefix. Requesting every prefix can still produce quadratic total output. Rank
parents anchor the item being ranked; its counted predecessors are recorded
separately, with the evaluated source identified by metadata `universe`.
Reindexing and placement preserve this evidence. Value transformations remove the
active measurement claim and retain its derivation.

`groups.coverage()` is a recipe around counts. It exposes missing and multiply
covered groups, finite `exactly(...)` checks, and `on_keys(...)` in the grouped-count
context. `unique(value=...)` guards a weighted sum with coverage exactly one before
using it as an assignment. Equal-valued duplicate matches still fail. This checks
the existing reduction domain; it does not compare arbitrary external key universes.
See the [authoring guide](docs/AUTHORING.md) for executable examples.

NumPy's [take](https://numpy.org/doc/stable/reference/generated/numpy.take.html) and [ufunc.at](https://numpy.org/doc/stable/reference/generated/numpy.ufunc.at.html) provide useful implementation primitives. Kaleion validates its own address rules before calling a kernel. Repeated-index accumulation uses `add.at`, rather than buffered indexed assignment that could lose repeated contributions.

## Explicit binary binding

An arrangement-driven transformation needs more information than two arrangement operands:

1. A target result and a driver result.
2. The target key expression `on` and driver key expression `key`.
3. The quantity read from the driver.
4. The operation and target quantity being changed.

The syntax retains those choices:

```python
driver_values = B.bind(on=F.value % 7, key=F.key, read=F.value)
moved = A.move(vector(driver_values, 0, -driver_values))
changed = A.with_values(F.value + driver_values)
```

This avoids giving `A + B` an arbitrary meaning among displacement, label addition, superposition, and concatenation. Operator overloads are used where the meaning is declared: scalar expression arithmetic, predicate composition, pipeline application, and pipeline composition. Python's [numeric emulation model](https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types) supplies the syntax hooks; it does not determine our mathematical semantics.

Bindings can read coordinates as well as labels. Constructor bindings use explicit singleton extraction to distinguish one parameter value from a per-item field. All binding sources become graph dependencies, so failures and provenance follow them.

Placement accepts `arrange(x=..., y=..., z=...)` and `place(...)` with the same
named coordinates. Declare x, x/y, or x/y/z, with no gaps or mixing of positional
and named arguments. Positional placement remains supported. A bound count or rank
is an ordinary coordinate expression; no row-specific driver object is needed.

## Captured inspection

`Inspection(state)` resolves scoped references against a captured state's graph,
execution contexts, and saved results. It can inspect one pointwise operation's
keyed reads and follow preserved measurement evidence to its original Count, Sum,
Any, or Rank. It reuses the field interpreter with a captured-only resolver; it
never invokes operation execution. Direct parents, matched driver references,
contributors, and motion correspondence retain their separate meanings.
Receipts carry exact weights separately from source labels and report truncation.
The contributor limit bounds expanded records, not stored parent references or
weight-field work. Scalar/positional reads and nested bindings within binding
keys/reads remain unsupported. The [query contract](docs/EXPLORATION_WORKFLOW.md#delivered-follow-a-measurement-through-its-actual-binding)
lists the migration and limits. This adds no operation version or saved schema.

## Numerical contracts

- Integer operations start with Python integers in NumPy object arrays, before any fixed-width kernel could overflow. Values and intermediate integer results are bounded to 4096 bits. Exponentiation also checks its work budget before computing an excessive result.
- Integer contents reject Boolean and floating-point results. Use `choose(predicate, 1, 0)` for an indicator. `floor` and `ceil` explicitly produce integers and preserve already-exact integers.
- `//` is floor quotient. `%` requires a positive integer modulus and returns a least nonnegative residue. `/`, trigonometry, coordinates, and paths use floating arithmetic.
- Coordinates are finite `float64`; exact-integer labels do not imply exact geometric distances. Comparing geometry is a numerical operation under that convention.
- `choose` evaluates both branches. Domain errors in an unselected branch are still errors. Short-circuit or masked evaluation would be an explicit future expression feature.

## Evaluation and failures

Definitions are immutable. Calling `.evaluate()` creates a bounded evaluator. Each root resolves its dependencies, and one evaluation invocation caches common nodes. Local parameter cases get distinct runtime identities and separate caches: evaluating one graph at n=4 must not substitute its result into a sibling evaluated at n=2.

`Incidence.universe` exposes its collection or arrangement definition with the same
nested parameter cases. Selection derives its result kind from that universe and
retains selected identities and placement. Boolean operations compare declared
universe definitions, including case order and binding expressions. They do not infer
equivalence from equal evaluated arrays, or discard apparently unused bindings.

Binding applies to the whole wrapped definition. For example,
`A.where(F.value < param("n")).with_params(n=4)` evaluates the predicate with n=4;
`A.with_params(n=4).where(F.value < param("n"))` evaluates the new predicate with the
surrounding n. Those incidences can share a declared universe while retaining
different predicate scopes. Composition evaluates both predicates in their own
scopes, then combines their masks. Failed predicates remain errors, even if a
different predicate is true everywhere.

The execution record contains operation status, runtime case ID, parameters, finite extent, and a catalog of relevant primitive families. This is an operation-level trace, not kernel instrumentation or an autodiff tape.

An invalid rule marks that branch failed. An unrelated root can still succeed. Workspace edits record failed definitions so that they can be corrected or undone. A presentation may retain the previous geometry, marked as retained after failure. Missing or failed data never becomes a zero count automatically.

`items.require(checks, message=...)` is an explicit graph dependency. All entries of
the supplied incidence must be true before its items are evaluated and passed
through unchanged. Empty check domains pass vacuously. A failure reports witness
keys; callers can retain the checks and their measurements as independent roots.

This isolation is within one process. The reference evaluator has finite size/depth budgets but no worker termination, interruptible jobs, asynchronous scheduler, or process-failure recovery. Those are separate runtime responsibilities.

## Undo is a history operation

Each committed edit retains its exact before/after state and motion definition. The mathematical state changes immediately when the command is committed; the renderer may display a transition while keeping calculations tied to the selected exact state.

For a forward transition path P(t), undo samples P(1−t). It restores the prior snapshot instead of calculating an inverse. This works for both bijective and lossy operations, subject to the configured history retention limit.

Correspondence is built from identity first, then explicit motion lineage. A duplicated gather can split into several tracks; omitted items fade. Reduction contributors do not imply a one-to-one trajectory. Changes of dimension require an explicit common projection/embedding before a motion is constructed.

Each captured transition prepares correspondence and membership once per displayed
root, during validation or first sampling. Occurrence lookup indexes and memoized
ancestry avoid repeated linear searches. Prepared tracks are private, immutable
data shared with the reversed transition; playback changes only progress along the
path. The transition owns a frozen copy of the motion mapping and each path's
expression sequence. This retains O(T) track data for T display correspondences
per root until the transition is released.

Frame labels and incidence masks retain original before/after values. A reversed frame carries the same endpoint pairs and a reversed fraction. Presentation opacity may vary continuously, but mathematical membership remains Boolean. The frame type cannot be passed into a construction as an arrangement.

Custom motion paths use captured start/end coordinates and a `time` parameter. They must agree with the endpoints. External drivers are evaluated in the construction before motion is captured, so later driver edits cannot change an old undo path. Endpoint validation is not a proof that an arbitrary custom path is defined at every intermediate time; a sampling failure is a presentation error.

JSON persistence retains snapshots, histories, pending redo, motion expressions, observations, and definitions. Reopening a capture does not require an evaluator or source recomputation. The first version intentionally stores materialized states; compression, structural sharing on disk, and incremental checkpointing can replace that strategy without changing the command contract.

Schema 1 and legacy Icarus envelopes remain readable. Existing direct-incidence
Boolean constructions retain their definitions. Compositions that preserve nested
scope use the new `incidence_boolean` operation, version 1 (`and`, `or`, or `not`).
Older evaluators cannot execute that new operation; its captured results remain
ordinary schema-1 snapshots. Prepared motion tracks are not serialized: reopening
reconstructs them from retained snapshots, without evaluating source definitions.

Grouping adds `rank` and `require` operations, version 1. Older evaluators cannot
execute these definitions. Ordered-rank snapshots store contributor-prefix format
version 1 inside schema-1 metadata; the updated query implementation is needed to
read that evidence. Older captures with enumerated contributors still load and
remain queryable. The new compact prefix record does not deduplicate snapshots
across history states or change capture restoration semantics.

## Extension points to exercise next

1. Let someone author an unfamiliar arrangement and reuse its counts without editing the evaluator. Record which missing operation actually blocked them.
2. Exercise the optional Plotly notebook viewer, which consumes `Snapshot` and `Frame`, before adding authoring controls that emit the same definitions and commands.
3. Extract a general bounded scan/recurrence construction once several authored recipes establish the needed state and emission contracts.
4. Introduce additional numerical domains or backends with explicit capabilities. Continuous-value differentiation will require a value-domain extension; present contents are integers.
5. Build finite comparison statements from declared key alignment and provenance before attempting proof assistance.

The core establishes executable examples and boundaries. It does not establish that this vocabulary can express every future mathematical observation.
