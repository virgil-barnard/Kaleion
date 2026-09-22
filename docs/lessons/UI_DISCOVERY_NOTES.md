# Discovery choices the interface should make legible

The new [construction studio](../CONSTRUCTION_STUDIO.md) tests these choices with
real authoring from a blank canvas. Hold options depend on selector scope and
target capabilities. The same declaration controls construct additive stacks
and modular incidences through a separate Python adapter. Its all-lesson matrix
keeps the general goal explicit; grouped selection, compact expressions, and
physical touch usability are the next experiments.

Lessons [09](09_norm_fibers.md) and [10](10_hermitian_partitions.md) extend the
[earlier review evidence](REVIEW_NOTES.md). These are tested authoring needs and
proposed UI capabilities. The first four authoring choices are now implemented
in Python. The [touch workspace hypothesis](../TOUCH_WORKSPACE.md) now proposes
concrete controls, gestures, and transaction boundaries, with a bounded working
equal-sum study. General authoring usability remains untested. See the
[authoring guide](../AUTHORING.md).

The [cross-lesson exploration workflow](../EXPLORATION_WORKFLOW.md) now maps all
eleven lessons to reusable choices, proposed editor groups, and concrete UI tasks.
Its implementations include the shared captured inspector in lessons 04–05 and
named product roles in 05/07. The study connects the common choices into a canvas
workflow: Relate → Measure → Arrange → Explain, with recorded reverse motion.

## Two construction stories

**Turn multiplication into motion:** declare coefficient arithmetic → arrange
elements → group by norm → count → choose a representative and phase generator →
bind phases and sizes → place fibers → apply multiplication → inspect and undo.

**Gather a curve by incidence:** form projective classes → select isotropic
points → choose a pole → inspect its polar and pencil → count coverage → assign
unique owners → measure order within groups → use owner and rank for placement →
compare another partition → inspect missing points and undo.

These stories motivated explicit grouping, member order, scoped coverage, and
named placement. Their remaining decisions guide the next refinements before
any commitment to menus or gestures:

| Author's choice | Evidence | Candidate interaction |
| --- | --- | --- |
| Which arithmetic do these labels represent? | `a+p*b` labels a field element; code addition is different | Show domain, basis, and formulas beside the arrangement |
| Which occurrences form the universe? | Line poles × curve points, with distinct roles | Choose explicit source collections and name each role |
| What stays constant? | Norm fibers; projective equivalence classes | Declare a grouping expression, inspect members, derive counts |
| What orders each group? | A generator, a representative, or predecessor counts | Choose an order separately from the grouping and size |
| Which object supplies a relation's arguments? | A selected point determines its polar | Bind named fields from a selected occurrence to relation parameters |
| Does a relation assign exactly one result? | Pencil coverage and the missing polar | Display uncovered and multiply covered keys before adopting owners |
| What changes? | Multiplication changes values; a new generator changes coordinates | Name the target quantity: contents, attributes, constructor, or placement |
| What does a measurement drive? | Fiber sizes set angular spacing; owners and ranks set placement | Declare target key, driver key, and quantity to read |
| Which identity is preserved? | 728 coincident representatives versus 91 reduced classes | Keep move, select, and reduce visibly distinct |
| Why is this point here? | Point → assigned line → incidence → eight representatives | Inspect captured derivation and contributors by retained key |
| What does time mean? | Exact poles, an algebraic step, or a sampled path | Distinguish a case scrubber from reversible presentation playback |

The first sketch should let a reader reproduce both stories with these choices.
Selecting the four uncovered points should reveal the omitted line. Selecting a
rotated element should reveal the unchanged norm and the changed field value.
Such concrete tasks will tell us whether the interface is understandable.

## Keep decisions in separate modules

Following [Parnas's information-hiding criterion](https://doi.org/10.1145/361598.361623),
decompose around decisions likely to change, not around the successive screens
or stages of one demonstration. The [core plan](../CORE_REFINEMENT_PLAN.md)
already applies that criterion. These lessons add the following evidence:

| Decision to hide | Owner | What other components may rely on |
| --- | --- | --- |
| Representation of field arithmetic | A local coordinate recipe today; a numerical domain only if later needed | Explicit exact formulas and domain restrictions |
| How a declaration becomes executable nodes | Authoring recipes and operation graph | Definitions, source identities, and declared keys |
| How measured predecessor evidence is represented | `measurements.py` | Query a retained key; expand its prefix without evaluating sources |
| How captured scopes, keyed reads, and contributors are navigated | `inspection.py` | Item descriptions and measurement receipts; no graph execution or renderer dependency |
| How keyed products, ranks, and reductions execute | Evaluator and indexing policy | Exact results, zero groups, failures, and contributors |
| How states and evidence are stored | Snapshots and history | Stable captures and replay without reevaluation |
| How a transition is sampled | Motion | Recorded correspondence and validated endpoints |
| Camera, colors, projection, and controls | Viewer | Snapshots and frames as read-only inputs |

The notebook coordinate helper changes no evaluator opcode. A different camera
does not change the domain. A failed relation does not become zero coverage.
Animated frames never become mathematical source arrangements.

## Delivered choices and remaining gaps

Lessons 07 and 10 now use `group_by(...).order_by(...).ranks(key=...)`.
Counts, member order, group display order, binding keys, and coordinates are
separate declarations. Lesson 10 completes its pencil with the tangent singleton;
`coverage.unique(...)` checks all 28 keys before adopting owners. Missing and
overlapping witnesses remain independent roots if a requirement fails.
Rank evidence stores ordered rosters and prefix ranges; playback still reads captures.

- **Products and prefixes.** Pair-domain definitions remain verbose. Compare a
  named-role recipe across lessons 05, 07, and 10. Ordered ranks are implemented;
  weighted exclusive prefix sums, needed for Young layer offsets, remain a gap.
- **Coverage and comparisons.** Current coverage checks an existing pre-mask
  reduction domain, including zero groups. Lessons 04–05 also have a finite
  keyed-value report with explicit expected domains and missing/unexpected keys.
  Subset and occurrence comparisons remain distinct future contracts. Equal totals
  alone never establish a correspondence.
- **Explanation across bindings.** `Inspection` now follows direct keyed reads
  in captured pointwise steps and weighted sums to matched driver occurrences.
  Lessons 04–05 use it without re-creating their joins. Scalar/positional reads,
  nested binding keys/reads, and automatic recursive explanations remain open.
- **Capture size.** Narrowing explicit support and compact JSON make this lesson
  portable. They do not deduplicate evaluated dependencies across states. Study
  shared capture storage separately from motion or the mathematical vocabulary.
- **Finite families of actions.** Cyclic multiplication and polar selection are
  concrete starting points for the orbit and coding lessons in
  [future lessons](FUTURE_LESSONS.md). General group-action notation should earn
  its place by simplifying more than one of them.

The next review can compare these declarations with the visible notebook code,
asking where the reader must still understand storage details. That is a more
useful target for simplification than reducing the number of Python classes alone.

## Lesson 11 · A coordinate dictionary connects two discoveries

The [code/field/plane lesson](11_cyclic_code_plane.md) adds an explicit bridge:
polynomial coefficient degree → a power of a field element → a parity-check
column → a projective point. None of these labels silently supplies another's
arithmetic. A future reader should be able to select a point and inspect this
dictionary, its direction, and the incidence it preserves.

Three further choices emerge. First, the integer overlap count and its parity
need separate names and inspectable evidence: two contributors may cancel.
Second, adopting a quotient, inverse, or error candidate requires a declared
coverage condition, with failed witnesses left available. Third, showing one
action in two charts needs coordinated presentation without duplicating the
mathematical occurrences or making the viewer evaluate that action.

The notebook uses existing products, counts, sums, ranks, bindings, and requirements.
Its bounded polynomial and field recipes remain visible; a helper owns only
captured-data plotting. Two root edits share a displayed progress value, with their
recorded undo paths retained separately. This is useful evidence for a later
coordinated-view authoring contract, not a reason to add code-specific evaluator
operations or to claim an atomic multi-root edit already exists.

The finite comparisons also distinguish equality from isomorphism. The code's
support masks equal the field-trace masks after choosing a dictionary and matching
line keys by their supports. The projective plane itself is not a field. Ask a
novice to predict a third point in both coordinate systems before designing the
controls for this correspondence.
