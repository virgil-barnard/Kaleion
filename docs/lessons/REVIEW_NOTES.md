# Evidence for the next Kaleion review

The [division/modular relation transfer](../DIVISION_MOTION.md) adds a further
test of the interaction grammar: position, displacement and cyclic slot movement
are separate choices within one instrument. Count/Sum/Bind already express the
quotient and remainder drivers, including composition through incidence witnesses.
The Euclidean step exposes domain extension as a distinct decision. It does not
justify a new mathematical superclass or a general-purpose animation-as-input
mechanism. Nonunit parameters preserve valid quotient counts while breaking
the bijection and unique-factor assumptions; these failures should stay visible.

These are observations from [lessons 01–11](README.md). Their authoring code
shows where a clearer notation, reusable recipe, or faster evaluator might help.
The delivery note below distinguishes implemented changes from remaining ideas.

The subsequent [core refinement plan](../CORE_REFINEMENT_PLAN.md) checks these
observations against the implementation and Parnas's decomposition criteria. It
records a parameter-case composition defect, measured copying and playback costs,
and an ordered migration plan. The first implementation fixes that defect, isolates
field evaluation, and removes repeated contributor grouping and motion preparation.
The plan's delivery status distinguishes these changes from the remaining recipes
and explanation tools below.

The [UI design study](../UI_DESIGN_STUDY.md) adds a separate evidence layer:
primary HCI sources, a concrete studio audit, cross-lesson acceptance tasks, and
a proposed human-observation protocol. Its first delivered changes retain drafts
through inspection and repair stale feedback, disappearing focus, and swallowed
navigation clicks. These are browser-verified behaviors, not learner-study results.

The subsequent [coverage instrument](../COVERAGE_INSTRUMENT.md) declares expected
keys independently and distinguishes zero, absent, multiple, and outside matches.
A passing claim can attach the sole match's value as a new field, retaining labels
and keys for reuse. Saved graph requirements guard adoption; an inspection report
never becomes an unverified proof input. Browser checks transfer between modular
and additive examples; adapter tests also remove the Hermitian polar and reverse
canonical-key storage. Paired views are the next UI experiment.

## Delivered: explicit discovery choices

Lessons 07 and 10 now declare grouping, strict member order, coverage, and named
placement directly. The [authoring guide](../AUTHORING.md) gives their contracts.
Two new operations earn their place: `rank` avoids dense predecessor products,
and `require` makes checked coverage a prerequisite for adopting an assignment.
Coverage otherwise composes existing counts, predicates, sums, and bindings.

The [recorded probe](../reviews/2026-09-grouping-probes.json) compares both rank
recipes on the same 96-item fixture and evaluator, with a source digest. The new
operation preserves exact ranks and queryable contributors while keeping ordered
evidence linear in source size. A counterexample with coverage `[0,1,2,1,1,1]`
demonstrates why equal totals do not establish unique owners. Compact prefix
queries work from saved captures without source execution.

These choices simplify two independent constructions without changing their visible
endpoints. The later ordered-prefix increment below adds weighted sums. Measured
case families, broader comparison meanings, and inspection of every kind of
driver read remain separate work.

## Delivered: ordered weighted accumulation

Lesson 06 now declares `layers.group_by().order_by(F.j).prefix_sums(key=F.j)`
for its packing driver, retaining the old dense construction as a small independent
check. Prefix receipts identify earlier measured layers, whose receipts identify
the original cells. The same Measure controls pack quotient columns; a zero
column is a real zero-weight contributor to the following offset.

The new operation shares member-order planning and contributor-prefix format 1
with Rank. A 160-item test fits a 160-item evaluator budget, retains 160 roster
entries and 160 ranges, and never builds the 25,600-item predecessor product.
It checks exact values beyond 64 bits without claiming a general timing result.
Ties, duplicate keys, signed weights, local cases, saved inspection and history
have explicit tests. [The implementation brief](../ORDERED_PREFIX.md) records the
UI contract and next work; this is not a general recurrence or case-family API.

## Delivered: captured explanations and a common exploration workflow

The [workflow audit](../EXPLORATION_WORKFLOW.md) compares all eleven lessons and
defines candidate UI choices without a new lesson superclass or GUI framework.
`Inspection(state)` now hides captured scope and alignment details behind item,
binding, and measurement queries. Lessons 04–05 follow actual saved driver reads
instead of manually rebuilding their joins. Weighted-sum receipts distinguish
source labels, weights, and read values; zero contributions retain their origins.
Preserved measurements and pending undo/redo can be inspected after reopening.

This extraction changes responsibility more than notebook length: each lesson
still explains its mathematics and formats its own narrative. It adds no evaluator
operation or saved schema. Scalar/positional reads, nested binding keys/reads,
arbitrary recursive explanations, and efficient expansion of very large receipts
remain outside the delivered contract.

## What the examples establish

The first extraction from the [helper inventory](HELPER_INVENTORY.md) is now
delivered: 04–05 share `keyed_values` and `rectangular_values` in
[snapshot_views.py](../../notebooks/snapshot_views.py). Two pure functions replace
four local ones while leaving mathematical definitions, evidence, and plotting
choices separate. Duplicate keys and holes fail explicitly; zero counts remain
present. Axes are selected by name and sorted, not inferred from storage or position.
Completeness is relative to observed axis labels: detecting an entirely missing
row requires the independent expected-domain checks that both lessons retain.
The subsequent `compare_keyed_values` report adds explicit expected domains and
exact residuals. The captured inspector above addresses direct keyed reads; broader
comparison meanings and read kinds still need separate contracts.

| Repeated construction | Evidence | Question for the review |
| --- | --- | --- |
| Measure, bind by keys, change a target | 04's lifted plane, 05's reconstruction, 06's packing, 07's stacks, 08's probes | Can the author declare the target quantity and correspondence in one readable expression? |
| Pair domain, relation, reduction | Lines × pixels in 05; layers × layers in 06; pairs × bins and pairs × pairs in 07 | Would a paired-domain recipe expose source keys more clearly without hiding identity? |
| Ordered prefix and rank | 06's starting offsets; 07's equal-sum predecessor counts | Delivered with declared strict order and unique item keys. How should a novice resolve ties? |
| Exact case family | 08's measured dilations and finite differences | How should a family expose case parameters and measured contributors? |
| Keyed comparison with witnesses | 04's bump, 05's failed divisibility, 08's reciprocity residuals | Which equality is intended: totals, keyed values, subsets, or occurrences? |
| Contributor explanation | A column in 04, a pixel in 05, a layer in 06, a sum in 07, a dilation in 08 | Can a common inspector follow target → bound driver → original contributors? |
| Invariant and within-fiber order | 09's norm fibers, generators, and measured angular spacing | How do grouping, size, representative choice, and order remain separate declarations? |
| Quotient versus coincidence | 10's 728 representatives at 91 positions, followed by 91 measured classes | Can an interface make the change of occurrence domain unmistakable? |
| Relation becomes an owner assignment | 10's pencils and spreads, checked point by point | Can coverage witnesses accompany every proposed single-valued correspondence? |
| An object supplies relation arguments | 10's selected pole and polar lens | How are source roles and parameter bindings named when keys label both points and lines? |

The [UI discovery notes](UI_DISCOVERY_NOTES.md) develop these new cases into
concrete authoring choices, with Parnas-style separation of decisions. Lesson 10
also exposes saved-state size: explicit domain restriction and lossless compact
JSON keep its full motion capture below the existing import budget. Shared
persistent storage remains a separate execution/history problem.

## Distinctions the interface must preserve

**Size does not determine order.** Young layer counts agree for `[5,3,2]` and
`[2,5,3]`. Packing needs an explicit within-group order. Reassigning values at keys
changes the mathematical input; reordering storage while preserving keys does not.

**Coincidence does not erase multiplicity.** Several ordered pairs can share the
position `(a+b,0)`. Lesson 07 preserves their identities and separates them with
measured ranks. A renderer may visually overlap them without implying deletion.

**Zero needs a domain.** Declared grid axes retain empty groups. A reduction over
arbitrary observed keys cannot manufacture bins that were never present. The
pair × bin construction deliberately includes zero-multiplicity sums.

**A case is part of a measurement.** In lesson 08, each count depends on a particular
integer dilation. Concatenation preserves symbolic inputs and parent lineage but
does not merge their reduction metadata into one contributor-query interface.
Keeping named case roots makes inspection possible today. A family view should
make that relationship accessible, including for zero counts and reordered cases.

**A further derivation changes the claim.** A difference or squared count is derived
from measurements; it is not itself the original subset cardinality. The graph can
preserve the derivation without attaching misleading count metadata to a new value.

**Motion is not a theorem or another evaluated case.** A smooth transpose, packing,
or lift shows a captured path. Integer dilations are discrete evaluations. Every
general identity in these lessons has a separate argument with stated assumptions.

## Remaining experiments

1. Ordered prefixes now drive layer and quotient-column packing, with keyed
   comparison and contributor receipts. Named `Product` roles shorten pair-domain
   declarations in 05 and 07; next test reordered canonical representatives in 10.
   The strict-rank recipe is already exercised in sum stacking and Hermitian
   partitions. Preserve their keys and evidence.
2. Apply the delivered captured inspector to further contributor examples. The
   tests already include zero groups, signed weights, ranks, copied measurements,
   and local parameter cases; lesson 05 follows several derivation steps. Next
   expose the case-family boundary in 08. Keep receipts out of animation frames.
3. The initial finite keyed-value report is delivered in lessons 04–05: it takes an
   optional authoritative domain and separates missing/unexpected keys from exact
   residual witnesses. Test another semantic kind before generalizing it to subsets,
   occurrences, totals, or declared correspondences; do not hide them behind `==`.
4. Give a parameter-family recipe a case key and accessible per-case measurement.
   Compare it with lesson 08's current `with_params` plus concatenation construction.

These are candidates for review, not missing prerequisites for continuing lessons.
A convenience operation should first make at least two real constructions clearer.

The [touch workspace study](../TOUCH_WORKSPACE.md) makes the proposed UI choices
reviewable using captured equal-sum examples. It separates preview/commit, case
selection/replay, zeros/missing keys, and overlapping/distinct occurrences. Its
two-case menus do not establish general novice authoring. The new
[construction studio](../CONSTRUCTION_STUDIO.md) now composes fresh sources,
relations, grouped measurements, and keyed placements through one command adapter.
Browser checks construct additive and modular examples from a blank workspace,
then save/reopen captures. This establishes a shared mechanism, not novice
usability or complete lesson coverage. Shared group selection now uses captured
membership across additive/modular fibers and zero/one/two assignment witnesses.
It does not evaluate the graph or add measurements. Compact formulas edit one
subexpression at a time, with separate source/target contexts for keyed reads.
Seven group contracts and the browser gate exercise zero groups, tied order,
native keys, stale selection, and phone-width controls. Next expose explicit
coverage requirements with an independent expected domain and guarded adoption.

The core audit sharpens the explanation requirement: definition dependencies are
already recorded, but a driven snapshot's direct parents currently name the target
items, not its matched driver items. `Inspection` now reconstructs direct keyed
reads from saved inputs and scopes; this is not an instrumented execution tape.
Keep those reads separate from the single correspondence used for motion.

## Separation of responsibilities and practical limits

Definitions build the dependency graph; evaluation produces exact values; captured
states and transitions support replay; viewers consume those results. Lessons 06–08
share a small presentation-only [helper](../../notebooks/lesson_views.py), while their
mathematical definitions stay visible in the notebooks. The helper is not a new
runtime API or an authoring language.

Dense paired domains make the current small investigations explicit. They can grow
quadratically in the number of occurrences, and a pair-of-pairs domain grows as the
fourth power of the input-set size when both sets grow together. This is an execution
cost, not evidence that another mathematical object is necessary. Lazy pairs, sparse
reductions, scans, or accelerated backends should preserve the same exact contracts.

The current plots remain preliminary viewers. Plotly supplies interactive 3D;
the separate raster adapter supplies 1D/2D MP4. Neither establishes physical cell
area from marker size. Tests and [viewer validation](../../notebooks/VALIDATION.md)
record finite evidence and environment limitations.

For the review, start with 06's ordering counterexample, 07's collapse/stack motion,
and 08's measured family. They expose three different kinds of information the
future notation and interface must make visible before we choose touch gestures.
Then compare 09's coordinate change with actual multiplication, and 10's complete
partition with the missing-polar witnesses. They test whether an author can state
what changes and what a measured correspondence actually guarantees.
