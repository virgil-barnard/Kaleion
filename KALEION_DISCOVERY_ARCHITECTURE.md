# Kaleion Discovery Architecture

Revision 9 · September 19, 2026 · Notebook evidence and core refinement proposal

**Kaleion — Discover mathematics through motion.** Kaleion is the name of the project previously developed as the Icarus Python reference core. The v0.1.0 baseline uses the `kaleion` distribution and import namespace. Workspace exports use `kaleion-python`, schema 1; imports also accept legacy `icarus-python` schema 1 documents. Links to the original Icarus repository and the historical HTML prototype keep their actual names. This revision updates implementation evidence and links the proposed refactor; it does not change runtime contracts.

This document consolidates the capabilities and boundaries developed in the design discussion. It defines the intended behavior of the application and proposed initial implementation defaults. Prototype evidence is recorded in part 13; it does not establish implementation of every capability below. “Required” describes a contract to preserve; later capabilities are identified explicitly. The first implementation milestone is defined in part 12.

The executable Python reference core now has eight Jupyter investigations, optional Plotly viewers, and a separate 1D/2D video adapter. Its README, DESIGN, examples, and tests document the implemented subset. The single-HTML authoring prototype remains a separate application; its controls do not call the Python core. The [core refinement plan](docs/CORE_REFINEMENT_PLAN.md) reviews the current implementation and proposes the next small changes using Parnas's criterion.

**1. Product contract and scope.** Kaleion is a workspace for constructing mathematical arrangements, inspecting them, varying them, and preserving observations. Someone must be able to notice and record a pattern before expressing its formula. The output of an investigation—selected values, a count profile, a recorded transformation—can become the input to another construction.

The core scope includes customizable integer arrangements in one, two, or three spatial dimensions; user-defined rules; value, index, geometric, and structural lenses; reusable transformations; temporal sweeps; high-fidelity motion; and an observation notebook. Required examples include the confirmed spiral, modular relation matrices, quotient-region counts, periodic tiling, zero padding, and basic Young diagram/tableau investigations.

| Design decision | Required consequence |
| --- | --- |
| Exploration comes first | Executable or hand-authored constructions remain usable without a proof-system interpretation. |
| Results are reusable | A lens or measurement can produce a named collection or transformation, not only a picture. |
| Identity, indexing, and geometry are separate | Reindexing, moving objects, changing values, and moving the camera have explicit meanings. |
| Operations own mathematical behavior | Rendering and animation cannot silently redefine a relation, count, or boundary convention. |
| Evaluation is bounded | Open-ended definitions are evaluated in finite portions; coverage is visible. |
| Failures follow dependencies | A failed computation blocks its dependents while unrelated work and retained results remain usable. |
| Execution backends are replaceable | Saved operations and observations retain their meaning independently of CPU/GPU or autodiff support. |

Formal proof assistance, automatic discovery of rules from gestures, general polynomial fitting, full finite-field toolkits, GPU evaluation, and automatic differentiation are later capabilities. The current design preserves their integration points. Rich arbitrary region dissection is also deferred: the cut-and-reassemble example discussed here is a presentation of cyclic shifting.

The workspace should enable these overlapping families of observation:

| Family | Representative question |
| --- | --- |
| Membership and incidence | Which values or tuples satisfy this relation? |
| Spatial organization | Where do stripes, symmetry, gaps, or alignments appear? |
| Structural organization | What happens at a boundary or at the end of a construction stage? |
| Quantitative relationships | Do these counts, differences, or areas agree? |
| Correspondence and invariance | What changes or stays the same under this operation? |
| Behavior across a family | When does a feature appear, repeat, or accumulate? |
| Composition and equivalence | Do two sequences of operations produce corresponding results? |

**2. Canonical objects and terminology.** The six principal workspace concepts are fixed for this baseline.

| Object | Definition | Minimum retained information |
| --- | --- | --- |
| Collection | The items under investigation | Identities, values, domain, optional indices, order, attributes, structural relations |
| Construction | A reusable procedure that produces or transforms data or arrangements | Inputs, parameters, operations or custom definition, exposed outputs and stages |
| Arrangement | A placement of occurrences in 1D, 2D, or 3D | Collection reference, occurrence identities, coordinates, optional paths/cells/groups |
| Lens | A reusable inspection tool | Rule, input bindings, target and scope, coordinate convention, result display |
| Sweep | A specified family of parameter cases | Tracks, case domain, evaluation convention, accumulation settings |
| Observation | A saved moment or interval of an investigation | Annotations, selected references, revision, parameters, captured results and view |

A Workspace is the document container; a Canvas is a view of it. A Layer is a display group. A Notebook is the view of saved observations. These are interface terms.

An Operation is one named computation with inputs and outputs. A Rule is an executable definition, expressed through an expression, recipe, or custom code. A Transformation changes data or a representation. A Driver binds data from another result to a parameter or group of operations. A Reduction combines values over chosen indices; a Profile retains the remaining indices.

Use established mathematical terms literally. A predicate is a condition; a relation specifies admissible tuples; a map is single-valued on its declared domain. A permutation is a bijection of the indexed collection. A matrix is a rectangular indexed array. A Young diagram has a partition shape; its filling is a tableau, with standard or semistandard conditions selected when relevant. Generic ragged rows remain valid collections without being declared Young diagrams. [SageMath: Tableaux](https://doc.sagemath.org/html/en/reference/combinat/sage/combinat/tableau.html).

“Lens” is a UI metaphor. An incidence lens displays a specified relation, such as point–line membership. An incidence matrix is a representation of that relation. [SageMath: Incidence structures](https://doc.sagemath.org/html/en/reference/combinat/sage/combinat/designs/incidence_structures.html).

Reserve morphism, isomorphism, and functor for a declared category and the corresponding laws. Use Arrangement for general placement, which can allow overlap. Smooth display motion is an animation without an implied homotopy. [The Stacks Project: Categories](https://stacks.math.columbia.edu/tag/0013).

**3. Identity, indices, and change.** Each distinction below is part of the data model, not a display convention.

| Concept | Meaning |
| --- | --- |
| Item identity | Which source or derived entity this is, independently of its current value |
| Value | Its mathematical content; equal values do not imply equal identities |
| Occurrence identity | One appearance of an item in an arrangement or derived indexed result |
| Slot | A destination index in a specified representation; cyclic shifts change its contents |
| Position | Coordinates assigned to an occurrence |
| Construction role | A named role or event in a recipe, such as an endpoint of a repeated block |
| Lineage | References or an index map explaining where a result came from |
| Transition correspondence | The specified matching between occurrences in two displayed states |

Two tableau cells containing 3 remain distinct items. A tiled source can have several occurrences. A roll moves source content between destination slots. Camera changes affect none of these identities.

Built-in operations supply correspondence and lineage. The Python core preserves occurrence identity under changes of values or placement, including coincident placements, and through selection and stable ordering. Gather, Permute, Tile, and Concat create output occurrences linked to their sources; Roll preserves occurrence identity while reassigning contents to fixed slots. Output keys must be deterministic within the operation definition. Values and screen proximity must not be used as silent identity heuristics. A custom operation that supplies no reliable matching can use appearance/disappearance or cross-fading.

A selection explicitly follows item identities, occurrences, construction roles, or a recomputed predicate. Matching independently created collections by value or index requires a declared correspondence.

Initial editing defaults:

- A transform creates a derived result and retains its input. Editing its parameters creates a new document revision.
- Dragging with the placement tool changes coordinates. Editing a labeled value is a separate action.
- Editing a linked repeated occurrence requires choosing Edit source or Make independent; it cannot silently alter all copies.
- Editing relation membership creates an edited relation or explicit override. Inferring a polynomial or another generating rule is a separate future operation with a chosen model family; it can have a unique solution, several solutions, or no solution.
- A coordinate projection creates a derived arrangement. An XY camera view only changes presentation.

**4. Construction and operation contracts.** Construction supports three authoring routes: coordinate expressions, editable recipes, and custom code. A manual placement is valid without a generating rule. Presets expand into editable recipes.

Recipes support a seed state; Place next, Advance, Turn, Restart, Repeat, When, and Apply recipe; named parameters; and nested calls with explicit state. A repeated walk and recursive subdivision are both expressible. Built-in blocks can expose stage boundaries and their emitted prefixes. Opaque code exposes only the stages it actually supplies.

Every generator has a finite request range, depth, or work budget, even when its definition is open-ended. Rules need input compatibility and runtime error handling, not formal proofs. Ordinary expressions support named inputs, arithmetic, comparisons, Boolean combinations, and registered functions. They are evaluated outside the UI thread when work is substantial.

An operation record retains its versioned definition, named input references, parameters, axes, value domains, numerical representation, shape/extent rules, boundary conventions, and optional stage/lineage providers. Backend and derivative implementations are optional capabilities. Operations can return several named outputs.

| Canonical operation | Meaning and initial contract |
| --- | --- |
| Enumerate / Product / Map | Produce indexed items, indexed products, or derived values; retain input references and output keys. |
| Select / Group / Order | Form subsets or groups and explicit orderings. Group keys are independent of screen location. |
| Gather, shown as Reindex | Output j reads source g(j). Repeated or omitted source indices are allowed. |
| Permute | Gather with a checked bijection of the selected index domain. |
| Lookup, shown as Substitute values | Output j is S(x_j); retain the table/function and any address encoding. |
| Translate / Reflect / Shift groups | Change declared coordinates or indices; identify the target quantity and any driver. |
| Roll, shown as Cyclic shift | On a nonempty axis of length N, output j reads input (j−s) mod N. Positive s moves contents toward larger logical indices. |
| Tile | Repeat whole indexed blocks by nonnegative integer factors along named axes. |
| Concat, shown as Join along axis | Append compatible indexed blocks in a declared order. Other axes must agree or be explicitly aligned. |
| Pad | Extend a domain by stated widths with a constant fill; zero is the default. General filled blocks use Concat. |
| Slice / Prefix | Select explicit half-open ranges or construction prefixes. |
| Reduce | Count, Sum, or Any over named indices; retain the remaining keys, including zero counts. |
| Combine selections | Union, intersection, or complement in an explicit universe. |
| Compose relations / operators | Bind the intermediate domain and declare the composition law and arithmetic context. |
| Compare | Align by a declared key and compare selected values, membership, multiplicity, or coordinates. |

Gather is a transformation of indices; Lookup is a transformation of values. In the author's [bit.py](https://github.com/virgil-barnard/Dissertation/blob/main/utils/bit.py), these use the same gathering mechanism with the roles of data and addresses exchanged. The reviewed Git blob is 078694a74dafde63387ccadc63200a66be5e0439. This is a design precedent, not an implementation dependency.

Defaults and boundary rules are explicit:

- Index axes are zero-based unless a different index domain is declared; a positive-integer source starts at value 1.
- Gather and Lookup reject invalid or missing addresses by default. Wrapping or filling is a named policy, not inherited silently from a backend.
- Slice uses explicit ranges; out-of-domain requests require an explicit clipping policy.
- Roll on an empty axis returns the empty result. Tile by zero produces an empty extent; negative repeat factors or padding widths are invalid.
- Count and Sum of an empty group are zero; Any is false. Uncomputed or failed inputs are not empty groups.
- Complement requires its universe. AND/OR on predicates differs from relational composition.
- Multiplying zero–one matrices over integers, Booleans, or a finite field gives different operations; the context must be retained.
- Integer quotient and signed remainder conventions are named definitions. Residue rings are not silently treated as fields.
- Initial exact division and remainder operations reject a zero divisor/modulus. Real-modulus definitions and integer-modulus identities retain their different domains.

Tile repeats blocks: [a,b] tiled twice becomes [a,b,a,b]. This differs from repeating each item. Constant padding can be expressed through concatenation with constant blocks. [TensorFlow: Tile](https://www.tensorflow.org/api_docs/python/tf/tile), [TensorFlow: Pad](https://www.tensorflow.org/api_docs/python/tf/pad).

Tiled occurrences retain a tile key and source lineage. Padded zeroes are actual defined positions; they are neither absent nor pending data. Dense allocation is unnecessary when an index map or constant region can answer the request lazily.

**Driver bindings.** Shift groups specifies the target, grouping key, changed quantity, axis/direction, displacement source, matching keys, and boundary behavior. For group i with driver d(i), geometric displacement is p′=p+d(i)e along axis vector e. An index shift changes the declared index instead.

A scalar can broadcast. Collection drivers match by explicit keys; rearranging the driver's display does not change the binding. Missing matches remain unresolved unless a fill policy is selected. Duplicate driver keys require disambiguation. Positional zip is available only as an explicit choice.

This contract generalizes beyond rows or any rectangular domain. The Python syntax `B.bind(on=target_key, key=source_key, read=source_quantity)` declares a keyed read from B in the eventual target's context. The result can be used in a displacement vector, a new value expression, or an explicitly extracted singleton constructor argument. Matching by a residue class or an authored group works on a scattered 3D arrangement. Reading a driver's labels and reading its coordinates are distinct declarations.

The general transformation therefore has a target, a driver, a correspondence, and an operation on a declared quantity. Two arrangements alone do not determine that meaning. Arithmetic operators act on symbolic expressions; `A | Move(...)` applies a transform and `Values(...) >> Move(...)` composes transforms left to right. Arbitrary `A + B` or `A == B` would hide unresolved choices, so the first Python API does not assign those construction-level meanings. `same_definition` checks definition identity, not mathematical equality.

A measurement can drive a transform of its input stage. Feeding that result back into its own current definition requires an explicit recurrence and initial state. The scheduler does not interpret an accidental dependency cycle as time.

**5. Lens, relation, and measurement contracts.** A relation is independently reusable. A Lens combines its rule or measurement with bindings, scope, coordinate convention, and display. Dropping an unambiguous unary value predicate onto an arrangement creates a whole-target lens. Unbound or ambiguous arguments remain visible for assignment.

| Binding source | Example |
| --- | --- |
| Source value or attribute | Integer label, unreduced sum, residue, original row key |
| Current logical index | Sequence k, row i, column j |
| Arrangement coordinate | x, y, z |
| Lens-local coordinate | Position relative to a moved stencil |
| Construction stage or role | Named block endpoint, iteration, emitted prefix |

A binary relation binds two axes, two collections, tuple-valued items, or a collection and an anchor. Higher arity remains possible. Product-domain evaluation has explicit bounds.

The initial scope choices are Whole target, Selection, Window, and Construction stage. Whole-target counts do not change when the camera pans. A Window intentionally changes its inspected subset. A stage query identifies the relevant prefix or event independently of what remains visible in the finished picture. View slicing changes visibility unless a lens explicitly binds to that slice.

A value lens moves its inspection region without changing the arithmetic rule. A stencil using local coordinates changes its matches when translated or rotated. A structural lens can inspect construction history. The spiral's completed-cycle endpoint must not be replaced by an unspecified “corner” heuristic.

Evaluation distinguishes a true match, a false result, and unavailable computation. Errors and pending data must not be rendered as false. Logical behavior belongs to the declared rule; camera projection and pixel overlap do not establish incidence.

Lens outputs can become collections, profiles, measurements, relations, or reusable operations. Count specifies what is counted: occurrences, source identities, distinct indices, or occupied coordinates. Rows and other groups with zero matches remain present. Area or volume requires declared nonoverlapping cells and their measures; counting points alone is not area.

**Count-derived collections and arrangements.** For a finite evaluated input construction A, a Boolean relation R, an optional inspection-window predicate W, and a grouping function g, define

\[
c(t)=\left|\{p\in A:g(p)=t\land R(p)\land W(p)\}\right|.
\]

Whole-target scope takes W to be true. For grouping by observed keys, the key domain is g(A), including keys for which c(t)=0. For retained axes of a declared rectangular domain, use their full Cartesian key domain even if an eliminated axis is empty: a 3-by-0 matrix counted for each row produces [0,0,0]. These are empty fibers of a known domain, not missing evaluations. Holding row i fixed counts across the other indices; on a rectangular matrix this is the sum of the incidence indicator along j. Holding column j fixed instead sums along i. The prototype's “Count for each” control selects the retained key, not the eliminated axis.

The reduction produces a keyed integer collection. Arranging that collection is a separate operation. The collection owns its values, keys, source identities, and reduction reference; the arrangement owns its placement and construction events. Changing a line into a spiral does not redefine the counts. A new lens can inspect those integers, indices, coordinates, or original keys, and its reduction can supply another collection. This closes the construction–observation–construction loop without a special-purpose quotient widget.

| Count output contract | Meaning |
| --- | --- |
| key | Original grouping key t, independent of display order or the new arrangement's indices |
| value | Cardinality c(t); zero is an ordinary retained integer |
| source identity | Reduction identity and key; stable under placement changes and case updates while the key remains present |
| occurrence identity | Preserved when the measured collection receives another placement; explicit copying/index operations can create new occurrences linked to the measured source |
| derivation reference | The Count operation and key, leading to the input lens and construction |
| contributor correspondence | Matching input occurrence IDs and the population of the complete input group |

The implemented count convention is **occurrences**. Equal labels do not collapse to one member. Counting distinct source identities is a different future operation. A Window restricts membership while preserving the input's full key domain. An empty group and a failed computation remain different outcomes.

The prototype stores an optional `source: {kind: "profile", profile: id}` on an arrangement; its existing construction kind continues to select coordinate expressions, growth, or matrix placement. The linked source determines values and length. Coordinate expressions may use `key`, `index`, `value`, and `length`; matrix dimensions may use `length` and must multiply to the source size. The prototype refuses a mismatch rather than silently truncating or padding. Formula sources retain their previous behavior.

“Arrange on canvas” creates this binding from a count profile. The same binding is available in Construct → Integer source. A count-derived arrangement can supply a keyed row-shift driver; its original key matches destination row i regardless of placement. Driver evaluation uses its input collection, not animated screen positions. Reductions in this prototype also use the input construction before row transforms; choosing a transformed stage as a reduction input remains future work.

**Provenance and statements.** An evaluated result records a graph of Construct/Arrange, Incidence, Count, and Gather/Roll operations. Nodes contain definitions, input references, stage and scope conventions, and evaluation status; the graph records the parameter case. Construction nodes record generated extent and coverage. Count results retain group populations and contributor occurrence IDs; transformed occurrences retain their input occurrence references. A count point links to the corresponding reduction key rather than copying the entire upstream graph.

Selecting a count shows its finite cardinality definition and outlines its contributing input occurrences. The lineage is inspectable and is included with captured results and JSON exports. A displayed transformation can repeat or omit source occurrences: its screen outlines are a visualization of correspondence, not a fresh recount. Captures freeze the definitions, parameter case, results, and provenance together. Earlier captures lacking provenance retain their original evaluated results; the application does not invent retrospective contributor records.

This record is a basis for later statement construction. An equality must still specify the compared expressions, domain, parameter quantifiers, counted objects, and any required correspondence. A derivation record or agreement across tested cases does not establish a universally quantified equality. Formal proof translation and equality declaration controls are not implemented in this revision.

A hand-drawn annotation can be saved immediately. Turning it into a reusable selector lets the user choose identities, roles, or a predicate. Suggested interpretations, if added later, require previews on other cases. They are not prerequisites for recording an observation.

**6. Sweeps and motion.** Keep three notions separate: construction progress, the parameter case being evaluated, and playback time. A Track maps a sweep axis to one parameter. Several tracks can share an axis; the data model can also represent independent axes.

Integer parameters use discrete cases. Continuous parameters can be evaluated continuously when their operation has that meaning. Changing a recipe chooses a named definition or a declared conditional branch. View parameters can also be animated; they affect mathematics only through an explicit binding.

Let C_n be the selected identities in case n. Retaining matches through N means the union over cases 1 through N, regardless of which frames were visited. Jumping directly to N must evaluate missing cases or report incomplete coverage. Backward seeking changes the aggregate to the requested range. Accumulation retains a producing case or stage for each result. Union, intersection, frequency, and first occurrence are useful aggregations.

A Trail records positions. Accumulation records results across cases. Their matching keys are explicit.

Motion uses source/target snapshots and a correspondence. It must support reversible scrubbing, group motion, appearances/disappearances, stable anchors, and synchronized geometry, labels, and overlays. Default playback keeps origin and scale stable. Camera tracking is optional.

The described cut-and-reassemble motion is a presentation of Roll: translate the visible contents, wrap the displaced segment, then restore the fixed lattice with shifted contents. Item identity follows the contents; slot identity stays with the destination grid. Temporary display copies do not count twice, and the renderer must not apply the shift a second time at completion.

An animation between two integer arrangements does not create fractional integer cases. Intermediate positions may be retained as a mathematical construction only when an operation defining them has been supplied. Animation failure can fall back to the evaluated endpoint.

**Undo and reverse motion.** Every committed mathematical edit retains its prior and resulting states, plus the chosen motion path and correspondence. Undo restores the prior state and plays the original path at 1−t; it does not ask Gather, Reduce, or a value replacement to supply a mathematical inverse. Redo reuses the same captured forward transition. A new edit after Undo clears the redo branch. History retention is an explicit resource policy.

The Python `Transition` exposes exact start/end states; its `Frame` contains presentation coordinates, opacity, occurrence matches, before/after integer labels, and before/after Boolean membership. During reverse playback, endpoint pairs retain their original orientation and the original-path fraction decreases. Incidence highlights can therefore reverse without becoming fractional truth values. Repeated gathers may split tracks; reductions without one-to-one correspondence fade. These tracks are never extra mathematical occurrences.

The first headless journal covers construction creation/replacement/removal, parameter edits, and restoring observations. Captures themselves remain separately retained records; undoable notebook annotation edits and camera controls are future UI commands. Saving/reopening a workspace preserves snapshots, pending redo, and recorded paths without recomputing historical results.

**7. Extent, navigation, and performance.** Store separately the defined domain, requested finite extent, evaluated coverage, and visible viewport. Infinite scroll requests additional bounded work. It does not materialize infinity or guarantee constant-time access to an arbitrary recursive sequence.

| Navigation control | Contract |
| --- | --- |
| Pan / Zoom | View-only translation and pointer-centered zoom; two-finger pan and pinch on touch |
| Orbit | Explicit 3D mode; selection and object dragging remain distinguishable |
| XY / XZ / YZ / Isometric | Change perspective without deleting coordinates; orthographic is the default |
| Fit selection | Frame known selected positions |
| Fit generated | Frame the completed finite portion |
| Fit range | Frame a stated finite range when bounds are known; otherwise report the generated portion |
| Back view | Restore a previous viewpoint independently of mathematical Undo |
| Slice | Change visible depth and thickness; no implicit change to a whole-target measurement |
| Jump to index/stage | Request access subject to the generator's capabilities and budget |

Spatial dimension, source-index rank, and camera perspective are independent. A matrix can be arranged on a line; a planar arrangement can be viewed in 3D.

Evaluate chunks and cache checkpoints. Coordinate formulas may support direct access; sequential recurrences may require intermediate work. Recursive generators can supply conservative spatial bounds for pruning. Unknown bounds cannot justify assuming that unseen branches contain no relevant items.

The renderer can cull invisible data and replace subpixel details with identifiable aggregates. This does not change the domain of exact lens evaluation. Large exact coordinates can use camera-relative display buffers. Rendering approximation must not become arithmetic approximation.

Cancel obsolete jobs and prioritize current interaction. A computationally expensive case must leave navigation responsive. Performance targets will be measured on declared desktop and touch-device fixtures during the interaction prototype; arbitrary user programs receive no universal frame-rate guarantee.

**8. Runtime contracts and separation of concerns.** Develop the headless reference core independently of the browser workspace. A later front end issues the same construction and history commands, with isolated evaluation jobs where appropriate. The document model does not require separate services or an exposed node editor. Python with NumPy is selected for the initial executable contracts; rendering technology and reuse of existing Icarus modules remain separate implementation choices to resolve through repository review.

**Decomposition criterion.** Use Parnas's information-hiding criterion: identify difficult or changeable design decisions and assign each to a module whose interface protects its clients from that decision. His circular-shift example permits stored or computed shifts behind the same interface; his subsequent criticism of unnecessary output ordering is especially relevant to Kaleion. The reviewed source is the August 1971 technical-report version archived by Carnegie Mellon, preceding the cited 1972 ACM publication. [Parnas, archived report](https://kilthub.cmu.edu/articles/journal_contribution/On_the_criteria_to_be_used_in_decomposing_systems_into_modules/6607958).

The six product concepts and the sequence of a discovery session do not prescribe six implementation modules. Likewise, Gather and Roll are composable mathematical operations, but their names alone do not determine module boundaries. A single HTML distribution can retain these boundaries.

The [post-notebook core plan](docs/CORE_REFINEMENT_PLAN.md) applies this criterion to actual code: scoped incidence semantics, field evaluation, index/group maps, result ownership, contributor representation, and prepared motion tracks. It records the gaps as well as the working contracts. The service inventory below is not a prescription to split code by stages of a discovery session.

| Hidden decision | Owning responsibility | What clients may rely on |
| --- | --- | --- |
| Dense, sparse, tiled, or lazily computed storage | Collection access | Defined indices, values, identities, extent, and access status |
| Whether integers are authored directly or computed by a reduction | Source adapters and collection access | Keyed integer items and derivation references; placement does not reimplement counting |
| How an index transformation is represented or materialized | Index maps and lineage | Destination-to-source mapping, multiplicity, bounds, and declared ordering |
| Expression syntax, interpreter, or compiled evaluator | Rule evaluation | Explicit bindings, operation meaning, numerical convention, and bounded result/error behavior |
| Eager execution, caching, chunking, workers, or acceleration | Execution and scheduling | Requested revision/case, coverage, cancellation, and compatible published results |
| Drawing technology, camera projection, and paths of motion | Presentation | Evaluated snapshots, correspondence, view controls, and reversible presentation time |
| Capture encoding, storage location, and checkpoint mechanism | Observation and persistence adapters | Versioned captures, restore/export, and truthful save status |

These are Kaleion design decisions informed by the paper, rather than a decomposition supplied by Parnas. A driver binds to declared keys; profile display order must not become an accidental mathematical input. Source access must not assume a flat array's physical order. Intermediate arrays and their strides are not public contracts merely because the first evaluator uses them.

Review a proposed boundary by making a concrete change: replace materialized Roll with an index view; reverse a profile's display order; replace the renderer; or restore an observation without its evaluator. Identify exactly which clients must change. Information hiding and a dependency hierarchy are separate properties; failure isolation still requires explicit statuses and execution boundaries. The goal is a small, useful operation vocabulary with replaceable implementations, not the fewest possible functions.

| Component | Owns | Failure boundary |
| --- | --- | --- |
| Document and history | Definitions, references, parameters, transactional edits, revision history | Computation cannot mutate or erase the definition that requested it |
| Scheduler and cache | Dependency graph, priorities, cancellation, extent, result publication | Cancel or replace one job while retaining unrelated and cached results |
| Construction/transform evaluators | Values, indices, placements, stages, correspondences | Block only dependent work; retain prior states |
| Relation/reduction evaluators | Matches, profiles, measurements, comparisons | A failed lens leaves its arrangement and other lenses usable |
| Sweep controller | Case selection, track bindings, evaluation requests | Static construction and inspection remain usable without playback |
| Views and motion | Drawing, camera, picking, transitions | Recreate a view from retained snapshots or use another view |
| Observation notebook | Captures, annotations, references to specific revisions | Existing captures can open without recomputation |
| Persistence adapters | Durable checkpoints, portable export/import, optional sync | In-memory work continues with a clear unsaved state |

The saved graph is the source of definitions. Evaluators consume explicit inputs and publish new results. Views consume results. UI controls issue document commands. The renderer does not define arithmetic; the notebook does not force recomputation merely to display a saved observation.

Required conceptual interfaces:

| Record | Required contents |
| --- | --- |
| Operation definition | Operation/version, input references, parameters, domain and shape rules, boundary convention, optional stage/lineage and backend capabilities |
| Evaluation request | Definition revision, input result references, parameter case, requested extent, work budget, cancellation identity |
| Evaluation result | Definition/input revisions, case and extent, payload, status, coverage, stable keys, provenance/correspondence references |
| Observation capture | Document revision or frozen subgraph, parameters, selected identities/stages, results/coverage, annotation, view state |

Evaluation status distinguishes pending, ready, failed, and blocked. Coverage separately distinguishes complete, partial, and unknown with recorded ranges or bounds. A ready result can intentionally cover only a finite portion. A displayed previous result is marked as belonging to an earlier revision or case.

Publish compatible geometry and overlays together. Late jobs cannot replace newer cases. Streaming partial results are allowed only with explicit coverage. Retain the previous usable scene while an update is pending or fails. A failed upstream driver cannot supply a new valid downstream transform, even though its old result remains inspectable.

Use immutable chunks or explicit ownership; do not copy entire datasets merely to honor immutability. User-defined or expensive operations run outside the UI thread, with cancellation and replacement of a stuck job. Worker messaging, error events, and termination support this boundary. [MDN: Web Workers](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers).

Recursion lives inside an explicit construction with state. Graph dependencies between produced results remain inspectable and must not accidentally cycle. A reduction can drive a later transform, so runtime components do not impose a fixed linear pipeline.

The prototype now resolves source arrangements, input lenses, and count profiles by dependency rather than declaration order or a fixed pass sequence. It memoizes results within one evaluation and detects cycles before recursing indefinitely. A failed or removed count source blocks its derived arrangements and dependent drivers while unrelated constructions remain available. Removing a profile retains the dependent arrangement definition with an explicit unavailable-source state, so Undo or rebinding can recover it. The current bounded evaluator reports these dependent outcomes with `status: "failed"` and a “Blocked by” error; a separate blocked status remains part of the broader runtime contract. It does not yet provide incremental cross-case caching or a general graph editor.

Component isolation does not eliminate shared browser-process failure. Checkpointing and export provide recovery. Persistence failure must not be reported as a successful save.

**9. Tracing, numerical backends, and future differentiation.** Kaleion owns the operation meaning; compatible backends execute it. A reference evaluator supplies the initial required exact arithmetic. Supported GPU or TensorFlow/PyTorch adapters can follow without changing the saved operation vocabulary.

Retain five separate records where needed: the construction graph, execution trace, occurrence lineage, derivative tape, and motion presentation. A custom operation can expose external dependencies and outputs without an internal trace. Its unsupported introspection or derivative capabilities remain explicit.

Lineage can be queried lazily from index maps. Execution optimizations can fuse kernels while preserving named construction stages. Derivative tapes are temporary computation records, not substitutes for observations; discrete indices and branch decisions still matter when they have no gradient.

A backend declares supported operations, shapes, dtypes, numerical ranges, and boundary policies. Exact integers, fixed-width word arithmetic, residue/finite-field arithmetic, and floating-point geometry carry distinct conventions. Unsupported exact arithmetic falls back to a compatible evaluator or reports a limitation. It cannot silently become floating-point arithmetic.

Backend differences must be normalized at dispatch. TensorFlow's documented CPU/GPU difference for out-of-range gather indices illustrates why Kaleion owns validation and explicit wrap/fill policies. [TensorFlow: Gather](https://www.tensorflow.org/api_docs/python/tf/gather).

Differentiation is optional and specified per argument. For fixed index map g on continuous values:

\[
y_j=x_{g(j)},\qquad
\frac{\partial L}{\partial x_i}
=\sum_{j:g(j)=i}\frac{\partial L}{\partial y_j}.
\]

Thus g=[2,0,2] and a summed output give input gradient [1,0,2]. Reverse gathering accumulates contributions by scatter-add; a two-sided inverse exists in the permutation case.

Gather/Roll/Tile with fixed controls can differentiate continuous values. Lookup can differentiate continuous table entries selected by fixed addresses. Integer addresses, sizes, and repeat counts have no ordinary real-valued gradient. The linked bit.py's integer lookup is therefore distinct from its continuous-value gather path. [TensorFlow: Autodiff](https://www.tensorflow.org/guide/autodiff).

Derivative metadata distinguishes a derivative of the forward operation, a specified continuous relaxation, and a surrogate training rule. The source's custom backward rule for rounding motivates preserving that interpretation explicitly. Missing support, stopped gradients, unconnected inputs, and numerical zero gradients remain distinguishable. [TensorFlow: Custom gradients](https://www.tensorflow.org/api_docs/python/tf/custom_gradient).

Neither GPU execution nor smooth animation implies differentiability. A future soft incidence model is a separate rule; it does not replace exact membership. A failed derivative or acceleration adapter leaves forward snapshots and the document usable.

**Python reference implementation.** Immutable `Expr` and `Node` definitions are separate from evaluated `Snapshot` records and from motion. The evaluator currently uses NumPy CPU arrays and Python control flow. Exact integer contents use Python integers in object arrays, with a 4096-bit bound; integer arithmetic is not first performed in fixed-width arrays. `/` and geometry use floating-point arithmetic, while `//` and a positive-modulus `%` have explicit integer conventions. Coordinates and motion are finite `float64`, so geometric equalities do not inherit exact-integer guarantees.

Gather, Roll, Tile, Lookup, keyed driver reads, selection, and grouped reductions share address-map and segment-reduction mechanisms. The operation-level evaluation trace identifies relevant primitive families; it is not a record of every executed kernel or a derivative tape. The bounded spiral scan and key/lineage assembly include Python loops. No GPU adapter or general tensor compiler has been implemented. Supporting differentiable continuous contents will also require an explicit extension of the current integer value domain.

**10. Initial interaction surface and persistence.** Use a canvas, object list, contextual inspector, optional sweep strip, and observation drawer. Persistent actions are Add, Select, Lens, Transform, Measure, Capture, Undo/Redo, and navigation. Advanced dependency inspection is optional.

| Action | Initial behavior |
| --- | --- |
| Add sequence/arrangement | Proposed default: values 1–100, step 1, line placement; explicit 1D/2D/3D and extent choices |
| Change construction | Coordinates, Recipe, or Code; named parameters; next-step preview |
| Add relation | Name inputs and domains; enter a predicate; save independently of its views |
| Drop relation onto arrangement | Create a lens; auto-bind only unambiguous inputs; show remaining bindings |
| Transform | Select target quantity, operation, groups, driver, and boundary behavior; preview a derived result |
| Measure | Select scope, “For each” keys, reducer and counted quantity; create a named output |
| Add to sweep | Bind an exposed parameter to cases/range; set discrete or supported continuous behavior |
| Compare | Select two results, alignment keys, and comparison meaning; show linked differences |
| Capture | Save a frame or interval and annotations without demanding a conjecture |
| Save tool | Expose selected parameters and outputs of a reusable construction fragment |

A simple arrangement should not show every advanced control. Recipe state and nested calls appear when used. Basic selection, dragging, and orbiting have visible modes and touch equivalents. Spatial transforms can act in 3D even when the current camera view is planar.

An Observation captures a stable historical state. Rerunning it against current definitions is a separate action. Store definitions, input references, parameters, seeds, and dependency versions where applicable. Captured data or snapshots preserve externally supplied or opaque results that cannot otherwise be replayed.

Portable documents need a schema version and lossless encodings for supported exact values. Rebuildable caches are optional; referenced captures and indispensable source data must travel with the document or be identified as missing. Save/load must preserve rules, scope, identity, stage references, and conventions. Undo concerns document edits; camera Back view is separate.

**11. Reference workflows and acceptance scenarios.** These examples specify expected behavior without hard-coding their mathematical conclusions into the interface.

**W1 — Structural spiral discovery.** Start at 1 with no zero hole. Place an initial row of n integers; alternately add an outer row and column on opposite sides. After each complete growth cycle, the prefix is a filled rectangle with k rows and k+n−1 columns, k≥2.

The user creates the recipe, circles interesting endpoints, inspects their stages, and attaches a lens to the end of the complete growth block. They measure prefixes, sweep n, and accumulate selected integer identities. They do not enter a primality filter or the endpoint formula to obtain the selection.

| n | Expected completed-cycle endpoints |
| --- | --- |
| 1 | 4, 9, 16, 25, 36, … |
| 2 | 6, 12, 20, 30, 42, … |
| 3 | 8, 15, 24, 35, 48, … |

Path bends, cycle endpoints, and rectangle-completing prefixes are distinct. A generic rectangle-completion predicate can select intermediate values such as 6 and 12 for n=1. The lens must retain the intended cycle phase or an equivalent additional condition.

The explanatory identity is c=k(k+n−1). Every composite ab with 2≤a≤b occurs at k=a, n=b−a+1. Through B≥4, cases 1≤n≤floor(B/2)−1 cover all composites in that extent. For the acceptance fixture B=36, n=1–17 suffices. The value 1 is outside the prime/composite classification. These are reference expectations; the application records the observation and its evidence.

**W2 — Reindexing and quotient-driven cyclic shifts.** For positive integers a,b, start with the b-by-a table

\[
A[r,c]=r+bc,\qquad 0\le r<b,\quad 0\le c<a.
\]

Highlight multiples of a. Reorder the marked values into sequence, then shift each row to bring its mark into the first column. Record these actions as row-source and displacement sequences before comparing them with independent formulas.

With r_i=ai mod b and q_i=floor(ai/b), the result is

\[
B[i,j]=A[r_i,(j+q_i)\bmod a]=(ai+bj)\bmod(ab).
\]

For a=11,b=7, the source rows are [0,4,1,5,2,6,3], the left shifts are [0,1,3,4,6,7,9], and the first column becomes [0,11,22,33,44,55,66]. Roll uses signed shift −q_i. Slide-and-wrap and cut-and-reassemble presentations must reach this same result.

For a=6,b=4, the row map is [0,2,0,2]. Gather repeats and omits rows; Permute must identify the failure of bijectivity. Preserve original item lineage, source indices, and new slots. This workflow follows the [Modular Relation Matrix Presentation](https://github.com/virgil-barnard/Icarus/blob/main/docs/Modular%20Relation%20Matrix%20Presentation.pdf).

**W3 — Counting a quotient region and reusing the profile.** On 0≤i<b, 0≤j<a, retain the unreduced value ai+bj and define

\[
I(i,j)\iff ai+bj\ge ab.
\]

The user chooses Measure → For each row → Count matching columns → Create profile. Compare its output with an independently constructed quotient sequence:

\[
c(i)=\sum_{j=0}^{a-1}\mathbf 1_{I(i,j)}
=\left\lfloor\frac{ai}{b}\right\rfloor,\qquad
h(j)=\sum_{i=0}^{b-1}\mathbf 1_{I(i,j)}
=\left\lfloor\frac{bj}{a}\right\rfloor.
\]

For a=11,b=7, the row profile is [0,1,3,4,6,7,9] and the region contains 30 unit cells. Bind this profile as the shift driver in W2. The relation's zero–one indicator also equals floor((ai+bj)/(ab)) on the stated domain.

Counts, equal row profiles, and equal geometric coverage are distinct comparisons. Repacking selected cells into rows of lengths c(i) preserves their count and correspondence, without asserting preservation of all geometric relations. Preserve unreduced values: modular reduction alone discards the quotient information. This implements the counting mechanism in [Isomorphism with the Division Alogrithm](https://github.com/virgil-barnard/Icarus/blob/main/docs/Isomorphism%20with%20the%20Division%20Alogrithm.pdf). Signed conventions remain explicit as motivated by [Reduced Remainder Arithmetic](https://github.com/virgil-barnard/Icarus/blob/main/docs/Reduced%20Remainder%20Arithmetic.ArXiV.Final%202.pdf).

**W4 — Tile, Pad, and index extension.** Let E[b→a] be the b-by-a matrix with a one in column r mod a of row r.

| Case | Construction |
| --- | --- |
| b≤a | Concat the b-by-b identity with b-by-(a−b) zero columns |
| b>a | Tile the a-by-a identity vertically ceil(b/a) times; Slice the first b rows |

Check E[7→11], E[11→7], and E[7→7]. Preserve zero-valued positions and the lineage of periodic copies. Record the resulting maps as reusable operations and allow their matrix representations to participate in explicitly defined composition.

**W5 — Reuse beyond a matrix.** Reuse one value lens across a line, snake, growing broken rows, and a 3D arrangement. In a 4×4×4 lattice with each coordinate in {0,1,2,3}, a relation selecting x=0 matches 16 items; camera rotation preserves those identities. Change a Young shape and filling independently, including repeated values, and preserve cell identities. These are acceptance cases for dimensional and structural flexibility, not new special-purpose engines.

**W6 — Reliability and unprepared exploration.** Change a scope, jump forward/backward through a sweep, cancel generation, fail a lens, and save/reopen an observation. Verify coverage, result revisions, identities, and failure boundaries remain honest. Finally, ask someone to construct and record an observation the designers did not prepare. Their inability to express a reasonable action is evidence for revisiting the controls.

An additional operation-order experiment compares Lookup(S, Gather(x,g)) with Gather(Lookup(S,x),g). They agree for the same fixed g and defined pointwise S. Recomputing g from transformed values is a different experiment.

**12. Delivery sequence and the next decision.** The current concept set is sufficient to proceed to interaction validation. Add a new concept only when an actual walkthrough exposes a missing capability.

| Gate | Deliverable | Completion criterion |
| --- | --- | --- |
| Executable core contracts | Python classes, symbolic expressions, bounded tensor evaluator, lineage, reversible history, and portable examples | W1–W4 and selected 3D cases execute without a UI; lossy edits undo exactly; recorded paths reverse; definitions/results survive JSON round trips |
| Interaction validation | A compact storyboard or disposable interaction prototype for W1 and W2/W3 using shared controls | Each gesture, binding, intermediate state, and reusable output is identified; the user need not supply the discovered endpoint formula or quotient identity in advance |
| First executable milestone | One workspace supporting both the structural spiral loop and the quotient-profile-to-row-shift loop | Author inputs/rules, inspect stages, derive results, drive a transform, scrub, capture, save, and reopen; failed independent work does not disable the workspace |
| First usable discovery release | Extend the same core through W4–W6, basic 3D navigation, shape/filling operations, and measured interaction performance | The acceptance scenarios work without replacing the document model or introducing scenario-specific theorem tools |
| Later extensions | GPU/autodiff adapters, richer algebraic domains and fitting, optional formal reasoning | Each extension preserves the established operation, identity, scope, and evidence contracts |

The first executable milestone is deliberately paired: a structural spiral and an arithmetic matrix must share the core. A polished single-scenario demonstration does not establish that the architecture is general enough.

Repository review must account for the existing finite-field and interpolation behavior. Preserve useful modules and identify necessary migrations explicitly; this baseline does not assume a rewrite or removal of working features.

The remaining decisions are implementation questions with concrete resolution paths:

| Open decision | How to resolve it |
| --- | --- |
| Exact arrangement/rule-authoring gestures | Exercise the interaction prototype with incomplete observations and revise where authoring becomes tedious |
| Reuse versus replacement of existing Icarus modules | Review the repository against these contracts before choosing implementation boundaries |
| Browser integration and rendering library | Python/NumPy and the symbolic operation graph now provide reference semantics; choose a browser adapter or compatible evaluator and renderer through a focused integration spike |
| Performance budgets and device targets | Measure evaluation latency, cancellation, picking, and motion on declared desktop/touch workloads |
| Initial GPU or autodiff adapter | Select only when a concrete investigation justifies it; neither blocks the first milestone |

**13. Evidence and limits of this baseline.** Prior review read the three PDFs and the linked bit.py. Exact arithmetic checks covered the gather/roll result and both quotient profiles for all 841 pairs 2≤a,b≤30. Small NumPy checks covered duplicate-index gradient accumulation, Roll correspondence, fixed-map Lookup/Gather commutation, and the three Pad/Tile extension examples.

These checks support the reference examples. They do not validate an application implementation, every argument in the PDFs, interaction usability, or a GPU/autodiff backend. TensorFlow and PyTorch were not executed for those checks.

**Standalone interaction prototype.** `icarus-discovery-prototype.html` now exercises W1 and the combined W2/W3 loop through shared controls. It contains editable integer and coordinate expressions, a bounded growth recipe, whole-target/window lenses, profiles, count-derived integer arrangements, keyed profile/arrangement drivers, composed Gather/Roll index maps, scrubbable presentation, inspectable provenance, capture/reopen, and JSON export/import. It has no external runtime dependencies. A worker isolates evaluation where the browser permits it; a bounded local evaluator is the fallback.

Browser checks covered both workflows, live relation changes propagating into row displacements, failed-lens isolation, repeated gathers for non-coprime inputs, undo, skipped and backward sweep cases, captures, JSON round trips, blank-page authoring, window dragging, and playback. Visual checks included desktop, narrow-screen, and dark appearance. Source checks also reversed profile entry order and physical point storage order without changing the transformation, and checked 400 positive integers across cases 1–199 against the 321 composites in that extent.

Revision 6 source checks additionally cover zero counts and their populations, contributor identities, independent placement changes, chained counts, reversed dependency declaration order, live parameter propagation, keyed arrangement drivers under reversed storage order, Window scope, failed/cyclic/deleted-source isolation, exact matrix shape checks, retention across cases of a derived source, earlier JSON documents, and the original arithmetic fixtures. These are bounded reference-evaluator checks, not proofs about all possible expressions.

Browser checks exercised Count → Arrange → Lens → Count → Arrange through the actual controls, contributor inspection (including a zero group), reuse of a derived arrangement as the Gather/Roll driver's input, propagation from the original lens into both later arrangements, cycle detection, deletion/Undo recovery, frozen captured provenance, and current/legacy JSON imports. Desktop, 320px, and dark layouts were inspected. The offline sandboxed preview also passed its interaction and portable-export checks.

The HTML prototype supports bounded 2D scenes: at most 400 items per arrangement, four arrangements, six lenses, six profiles, and thirty observations. It is not the complete engine: a general graph editor, incremental scheduling, arbitrary recursion, 3D controls, Tile/Pad controls, Young tableaux controls, GPU/autodiff, and proof assistance remain unimplemented there. The implemented growth blocks are an initial authoring vocabulary, not a claim that arbitrary constructions are expressible. Browser checks establish these interactions and fixtures, not a universal performance guarantee or independent usability validation.

**Python reference core, Kaleion v0.1.0.** `kaleion` adds a headless executable model with expression operators; sequences, grids, partition-shaped fillings and rectangular spirals; independent 1D–3D placement; value/index/coordinate/structural predicates; explicit window scope; selection and keyed reductions; general arrangement bindings; Gather/Permute/Roll/Lookup/Tile/Concat/Pad; construction parameter binding; discrete sweeps; captured observations; and persistent undo/redo with reversible paths. It is a separate implementation, not an unannounced replacement for the original repository or HTML app.

The current suite includes 55 automated tests. The quotient/remainder fixture executes all 144 pairs 2≤a,b≤13, including non-coprime repeated/omitted source rows. Additional checks cover all three W4 extension matrices, Lookup/Gather commutation under a fixed map, a 4³ lattice plane with 16 matches, arbitrary scattered 3D points driven by keyed counts, count-driven values and constructor parameters, source-order independence, retained zero groups and empty fibers, contributor provenance, and exact integer arithmetic beyond 64-bit range. The notebook additions cover reciprocal floor sums, the three-incidence box, measured motion, finite Radon reconstruction, Young layers, additive energy, and Ehrhart counts; their evidence is in [notebooks/VALIDATION.md](notebooks/VALIDATION.md).

Spiral checks cover path contiguity, non-overlap, completed rectangular prefixes, and the B=36 composite sweep. History checks cover curved-path reversal, incidence-highlight endpoints, lossy operations, parameter changes, creation/removal, failed branches, redo invalidation, capture restoration, and JSON round trips with pending redo and contributors. A compatibility test checks that an Icarus Python workspace retains its history and paths when reopened and exported as Kaleion. Parameter-case isolation is checked so one local binding cannot contaminate a sibling evaluation. These finite checks are implementation evidence, not universal proofs or usability evidence.

The Python defaults are 10,000 occurrences per result, 2,000 nodes per evaluation, and 100 retained history edits. Optional viewers now consume snapshots and frames, with interactive 3D HTML and 1D/2D MP4 exports. A connected authoring GUI, asynchronous worker/cancellation system, lazy infinite extent, general recurrence language, standard/semistandard tableau validator, finite-field interpolation system, GPU/autodiff backend, and proof assistant remain future work. Young shapes and fillings are data, not automatically certified tableaux. The roll state is implemented; a specialized slide/wrap presentation remains a viewer extension. See the package's [VALIDATION.md](VALIDATION.md), the notebook validation notes, and [DESIGN.md](DESIGN.md) for implemented contracts and limits.

The core audit found a specific composition gap after `Incidence.with_params`, repeated motion-track preparation, unnecessary immutable-buffer copying, and a quadratic contributor-building loop. The [refinement plan](docs/CORE_REFINEMENT_PLAN.md) proposes repairs and migrations; they are not fixed by this documentation revision. It also distinguishes definition dependencies from per-target driver alignment evidence, which a general explanation view still needs.

The next evidence needed is whether the shared controls let a person construct, notice, and reuse something they did not already know how to express algebraically. New primitives should follow a demonstrated missing action. Revisit implementation boundaries when such an action exposes a leaked design decision.
