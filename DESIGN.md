# Design contracts

## Decompose by decisions that may change

The module boundary is chosen around a hidden decision: expression representation, numerical execution, item correspondence, state retention, or motion presentation. This follows the information-hiding approach in [Parnas, “On the Criteria To Be Used in Decomposing Systems into Modules”](https://kilthub.cmu.edu/articles/journal_contribution/On_the_criteria_to_be_used_in_decomposing_systems_into_modules/6607958). It is our application of that principle, not a claim that the paper prescribes these particular classes.

| Module | Owns | Contract exposed to clients |
| --- | --- | --- |
| `ir.py` | Immutable expression/operation definitions, definition identity, graph encoding | Versioned definitions with explicit dependencies; no rendering or numerical execution |
| `api.py` | Typed construction vocabulary and operator syntax | Pure builders returning new definitions |
| `tensor.py` | Exact integer rules, array validation, elementary numerical kernels | Checked numerical conventions, gathering, grouping, and segment reduction |
| `model.py` | Evaluated data, occurrence/source identity, lineage, snapshot encoding | Immutable finite snapshots independent of reevaluation |
| `evaluate.py` | CPU evaluation, dependency ordering, parameter cases, bounded work | A result or an explicit error for each requested root |
| `motion.py` | Correspondence tracks, paths, reverse sampling | Presentation frames derived from captured states; no changes to mathematical results |
| `history.py` | Workspace commands, exact retained states, captures, persistence | Undo/redo, independent observations, portable historical results |
| `sweep.py` | Parameter-case selection and retention | Explicit coverage through a case, independent of playback sampling |

The evaluator currently uses NumPy directly as well as the kernel helpers. There is no interchangeable backend interface pretending to be complete. A future GPU evaluator can consume the same operation definitions while implementing supported operations and numerical types. Some reference algorithms—key factorization, lineage assembly, and the spiral scan—are Python control flow today.

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
| Driver binding | Key alignment → Gather selected source field | Unique source keys; complete requested matches |
| Spiral | Bounded stateful scan → positions and structural fields | Special reference constructor, not a general recursive language |

For grouping key g, mask m, and integer values v, the implemented reductions are:

\[
\operatorname{count}_t = \sum_{p:g(p)=t} \mathbf 1_{m(p)},
\qquad
\operatorname{sum}_t = \sum_{p:g(p)=t} \mathbf 1_{m(p)}v(p).
\]

The output key domain comes from the source before masking. If the grouping consists of retained axes of a declared rectangular domain, use their Cartesian domain even when an eliminated axis is empty. For other expressions, use observed source keys in first-appearance order. A total reduction returns one item, with sum/count zero on an empty universe. `any` returns an integer indicator 0 or 1.

Counts here measure occurrences. Distinct-source or geometric-area measures must be expressed separately; they are not implicit aliases for count. The graph, key, relation, source extent, and contributor identities remain available for later analytical statements.

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

## Numerical contracts

- Integer operations start with Python integers in NumPy object arrays, before any fixed-width kernel could overflow. Values and intermediate integer results are bounded to 4096 bits. Exponentiation also checks its work budget before computing an excessive result.
- Integer contents reject Boolean and floating-point results. Use `choose(predicate, 1, 0)` for an indicator. `floor` and `ceil` explicitly produce integers and preserve already-exact integers.
- `//` is floor quotient. `%` requires a positive integer modulus and returns a least nonnegative residue. `/`, trigonometry, coordinates, and paths use floating arithmetic.
- Coordinates are finite `float64`; exact-integer labels do not imply exact geometric distances. Comparing geometry is a numerical operation under that convention.
- `choose` evaluates both branches. Domain errors in an unselected branch are still errors. Short-circuit or masked evaluation would be an explicit future expression feature.

## Evaluation and failures

Definitions are immutable. Calling `.evaluate()` creates a bounded evaluator. Each root resolves its dependencies, and one evaluation invocation caches common nodes. Local parameter cases get distinct runtime identities and separate caches: evaluating one graph at n=4 must not substitute its result into a sibling evaluated at n=2.

The execution record contains operation status, runtime case ID, parameters, finite extent, and a catalog of relevant primitive families. This is an operation-level trace, not kernel instrumentation or an autodiff tape.

An invalid rule marks that branch failed. An unrelated root can still succeed. Workspace edits record failed definitions so that they can be corrected or undone. A presentation may retain the previous geometry, marked as retained after failure. Missing or failed data never becomes a zero count automatically.

This isolation is within one process. The reference evaluator has finite size/depth budgets but no worker termination, interruptible jobs, asynchronous scheduler, or process-failure recovery. Those are separate runtime responsibilities.

## Undo is a history operation

Each committed edit retains its exact before/after state and motion definition. The mathematical state changes immediately when the command is committed; the renderer may display a transition while keeping calculations tied to the selected exact state.

For a forward transition path P(t), undo samples P(1−t). It restores the prior snapshot instead of calculating an inverse. This works for both bijective and lossy operations, subject to the configured history retention limit.

Correspondence is built from identity first, then explicit motion lineage. A duplicated gather can split into several tracks; omitted items fade. Reduction contributors do not imply a one-to-one trajectory. Changes of dimension require an explicit common projection/embedding before a motion is constructed.

Frame labels and incidence masks retain original before/after values. A reversed frame carries the same endpoint pairs and a reversed fraction. Presentation opacity may vary continuously, but mathematical membership remains Boolean. The frame type cannot be passed into a construction as an arrangement.

Custom motion paths use captured start/end coordinates and a `time` parameter. They must agree with the endpoints. External drivers are evaluated in the construction before motion is captured, so later driver edits cannot change an old undo path. Endpoint validation is not a proof that an arbitrary custom path is defined at every intermediate time; a sampling failure is a presentation error.

JSON persistence retains snapshots, histories, pending redo, motion expressions, observations, and definitions. Reopening a capture does not require an evaluator or source recomputation. The first version intentionally stores materialized states; compression, structural sharing on disk, and incremental checkpointing can replace that strategy without changing the command contract.

## Extension points to exercise next

1. Let someone author an unfamiliar arrangement and reuse its counts without editing the evaluator. Record which missing operation actually blocked them.
2. Add a renderer consuming `Snapshot` and `Frame`, then controls that emit the same definitions and commands.
3. Extract a general bounded scan/recurrence construction once several authored recipes establish the needed state and emission contracts.
4. Introduce additional numerical domains or backends with explicit capabilities. Continuous-value differentiation will require a value-domain extension; present contents are integers.
5. Build finite comparison statements from declared key alignment and provenance before attempting proof assistance.

The core establishes executable examples and boundaries. It does not establish that this vocabulary can express every future mathematical observation.
