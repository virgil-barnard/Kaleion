# Discovery choices the interface should make legible

Lessons [09](09_norm_fibers.md) and [10](10_hermitian_partitions.md) extend the
[earlier review evidence](REVIEW_NOTES.md). These are tested authoring needs and
proposed UI capabilities, not a new core API or a prescribed set of touch gestures.

## Two construction stories

**Turn multiplication into motion:** declare coefficient arithmetic → arrange
elements → group by norm → count → choose a representative and phase generator →
bind phases and sizes → place fibers → apply multiplication → inspect and undo.

**Gather a curve by incidence:** form projective classes → select isotropic
points → choose a pole → inspect its polar and pencil → count coverage → assign
unique owners → measure order within groups → use owner and rank for placement →
compare another partition → inspect missing points and undo.

These stories reuse existing operations. Their repeated decisions suggest a small
declarative vocabulary before any commitment to menus or gestures:

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
| How keyed products, ranks, and reductions execute | Evaluator and indexing policy | Exact results, zero groups, failures, and contributors |
| How states and evidence are stored | Snapshots and history | Stable captures and replay without reevaluation |
| How a transition is sampled | Motion | Recorded correspondence and validated endpoints |
| Camera, colors, projection, and controls | Viewer | Snapshots and frames as read-only inputs |

The notebook coordinate helper changes no evaluator opcode. A different camera
does not change the domain. A failed relation does not become zero coverage.
Animated frames never become mathematical source arrangements.

## Gaps to investigate before adding primitives

- **Products and ordered groups.** Current pair-domain definitions are correct but
  verbose. Compare a small named-role recipe across lessons 05, 07, and 10 before
  proposing a core product or rank operation. Preserve source keys and order.
- **Coverage and comparisons.** Return witnesses with the compared domains, rather
  than treating equality of totals as a correspondence. Lesson 10 checks coverage
  explicitly before using the summed owner key.
- **Explanation across bindings.** The notebook can follow named intermediate
  measurements. A general inspector still needs captured driver-alignment evidence;
  direct snapshot parents alone do not identify every matched driver occurrence.
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
