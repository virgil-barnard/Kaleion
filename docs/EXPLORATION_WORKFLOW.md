# From worked lessons to an exploration workspace

The eleven lessons suggest a common **way to compose choices**, not one universal
mathematical object. The reader chooses a domain, defines fields and relations,
measures fibers, reuses a measurement through declared keys, and inspects the
result. Any intermediate collection can begin another investigation. A new chart
or animation is a view of that work, not a new source of mathematical truth.

This is an authoring audit and a proposed UI contract. The captured inspector
below is implemented and used in lessons 04–05. Named products now serve 05 and
07; a bounded [touch interaction study](TOUCH_WORKSPACE.md) exercises the proposed
controls. A general touch authoring interface is not implemented.

## What actually repeats

| Lesson | Construction that can be reused | Decision that must remain visible |
| --- | --- | --- |
| 01 · Workbench | Place one sequence differently; apply value or structural predicates; retain hits across cases | Structural roles come from the constructor. A screen corner alone is not a predicate. |
| 02 · Floor sums | Count two incidences on a common rectangle; pack selected cells | Counts measure cells, not marker area. Overlap changes the identity. |
| 03 · Three solids | Partition a product domain; reduce onto slices | Pairwise coprimality, tie rules, and the retained axes are independent choices. |
| 04 · Measured motion | Reduce along z; bind three height fields to another plane | Composite keys establish correspondence; the target has independent occurrences. |
| 05 · Finite Radon | Form point–line pairs; count by line; sum those counts by point | Source roles, prime arithmetic, and integer summation weights cannot be inferred from a picture. |
| 06 · Young layers | Count cells by column/layer; use weighted predecessor sums as packing offsets | Counts do not determine member order. Weighted prefixes differ from ranks. |
| 07 · Additive structure | Form ordered pairs; group by sum; stack using measured ranks | Pair multiplicity survives overlapping positions. Include the desired empty bins explicitly. |
| 08 · Ehrhart counts | Measure exact parameter cases; form differences; move independent probes | Each measurement belongs to a parameter environment; a frame is not a case. |
| 09 · Norm fibers | Group by an invariant; choose a phase order; use sizes for angular spacing | Field arithmetic, generator choice, and coordinate placement have different meanings. |
| 10 · Hermitian partitions | Measure coverage; adopt unique owners; rank and place each block | Zero/multiple coverage are witnesses. Canonicalizing representatives changes the domain. |
| 11 · Code and plane | Build products and parity sums; guard assignments; compare through an explicit dictionary | Integer overlap and parity differ. A dictionary must name the correspondence it preserves. |

Four recurring connections do most of the work:

1. **Relate:** a predicate on a declared occurrence domain, sometimes a product
   with named source roles. A lens shows that incidence without deleting its universe.
2. **Measure:** retain grouping keys and reduce selected weights. Count, Sum,
   presence (`any`), and ordered rank expose different information.
3. **Reuse:** read a measured field by explicit target and driver keys, then change
   contents, attributes, placement, or a constructor argument. Binding is a read;
   it does not itself choose the transformation.
4. **Investigate:** compare a captured result under a declared meaning, inspect
   its derivation, change an assumption, and repeat. Record paths separately so an
   observation can be replayed or undone.

These connections are not a fixed wizard sequence. Radon uses Measure → Reuse →
Measure; a coverage check can gate Reuse; a changed lens restarts measurement.
The existing immutable graph already expresses these branches and dependencies.

## A small UI vocabulary, with explicit choices

These are candidate editor groups, not five new core classes. Each edit should
produce the same readable Python declaration shown beside the picture.

| Editor group | Choices the user declares | Result and failure behavior |
| --- | --- | --- |
| Sources and fields | Finite extent; arithmetic convention; source roles; value/attribute expressions; optional placement | A collection/arrangement definition. Camera visibility never silently changes the domain. |
| Relation and measurement | Predicate; retained keys; Count/Sum/Any or rank; weight expression; separate strict member order | An incidence or measured collection. Keep unselected groups as zeros under the declared grouping-domain policy. |
| Correspondence and change | Target; driver; target key; driver key; field to read; quantity to change | A binding and a named operation. Missing/ambiguous driver keys fail; coverage can guard an assignment. |
| Observation and explanation | Selected scoped occurrence; comparison kind and expected domain; contributor expansion limit | Read-only captured evidence. Missing keys, unequal values, absent evidence, and failed computation remain different outcomes. |
| Cases and replay | Exact parameter and discrete cases; recorded action/path; playback progress; camera | Case selection requests mathematics. Playback samples a captured path. Undo restores a state, including lossy edits. |

Progressive disclosure can keep the first view small: show source, relation, and
result, then open grouping or binding details when needed. A drag between results
can propose a binding but must expose its keys and read field before committing.
Equal storage lengths, labels, or screen proximity do not establish correspondence.

Selection should carry a scoped `Ref(node, occurrence)` from a captured endpoint.
Hovering a moving track must choose its before/after reference explicitly; an
interpolated coordinate cannot be used to identify a mathematical occurrence.
An inspection failure should leave the captured picture available. An evaluation
failure must remain visible even if presentation retains the preceding geometry.

## Delivered: follow a measurement through its actual binding

Previously, lesson 04 reconstructed the driver join using known root names;
lesson 05 reconstructed the point–line–pixel joins from its own incidence logic.
Both now use `Inspection(captured_state)` for the common work:

```python
from kaleion import Inspection

inspect = Inspection(workspace.state)
point = inspect.find("probes", 3, by=("key",))
read, = inspect.bindings(point)
receipt = inspect.measurement(read.driver, limit=8)

print(read.key, read.value)                 # the matched key and field read
print(receipt.item.value, receipt.reducer)  # the retained result and its meaning
for contributor in receipt.contributors:
    print(contributor.item.ref, contributor.item.value, contributor.weight)
```

Run the complete [example](../examples/inspection_choices.py) with
`python3 examples/inspection_choices.py`. It has reordered driver/target storage,
a retained zero group, a missing-key failure, a cancelling weighted sum, saved
inspection, and recorded reverse motion. A zero count has no selected contributors;
a zero weighted sum can have several, including one with weight zero.

| Query | Contract |
| --- | --- |
| `find(root, key, by=(...))` | Locate exactly one occurrence in a ready named result by declared fields. Duplicate/absent keys fail. Existing scoped references need no key lookup. |
| `item(ref)` | Read value, attributes, position, source identity, and direct scoped parents. These remain separate quantities. |
| `bindings(ref)` | Explain keyed reads at one Values/Annotate/Place/Move step, using its captured **input** fields and parameter scope. Return matched driver references, keys, read expressions, and read values. |
| `measurement(ref, limit=32)` | Follow preserved measurement evidence to Count/Sum/Any/Rank, returning its original reference, key, formula, population, contributor count, and expanded contributors. Sum entries retain their evaluated weights and keyed reads. |

Returned records are immutable descriptions and have detached `to_dict()` forms
for lesson exports. They are not arrangements or proof certificates. A changed
value no longer claims the original measurement; the caller can explicitly follow
its parents. Copies retain distinct references even when they share an original
measurement. Parameter cases resolve through captured scopes, never a guessed
runtime-ID format or the workspace's current global parameters.

Inspection reads the saved graph, execution contexts, and snapshots. It replays
declared field expressions over captured inputs using the existing expression
interpreter; it does **not** execute graph operations. No new evaluator operation
or persistence schema is needed, and reopened captures remain usable offline.
This is a reconstruction of declared reads, not a newly recorded execution event.

**Limits:** direct keyed reads are supported; scalar extraction, positional lookup,
and bindings nested inside another binding's key/read are not explained yet.
Unsupported queries fail explicitly. This is a one-step query, not automatic
recursive explanation of every operation. Following preserved measurement parents
has a depth budget of 100. The limit bounds expanded contributor records; stored
parent references, weight-field interpretation, and prefix expansion can still
scale with the captured domain. Do not call this per animation frame or promise
constant-time inspection. JavaScript clients will need an exact-integer transport
policy before consuming the Python records as JSON numbers.

## Parnas boundaries: hide decisions that can change

| Changeable decision | Owner today | What its client should need to know |
| --- | --- | --- |
| How declarations are encoded and scoped | `api.py`, `ir.py`, small authoring recipes | Typed immutable definitions and explicit dependencies |
| How keys align, groups form, and order resolves | `indexing.py`, `grouping.py` | Declared keys/order, exact results or explicit witnesses/errors |
| How arithmetic and predicates execute | `expressions.py`, `tensor.py`, evaluator | Numerical domain, supported operations, and evaluation outcome |
| How contributors and captured scopes are represented | `measurements.py`, `model.py`, history; query adapter in `inspection.py` | Scoped references, active claims, field reads, and contributor receipts |
| How edits are retained and undone | History | Captured before/after states and recorded actions |
| How paths are matched and sampled | Motion | Endpoint correspondence and presentation frames |
| How evidence becomes a picture, notation, or controls | Viewer and future UI | Read-only snapshots/receipts and explicit authoring commands |

The inspector owns interpretation of existing captured evidence; lesson code no
longer needs to know trace nesting or join stored IDs by hand. Evidence storage can
change behind that query boundary. It deliberately reuses expression and key
semantics rather than inventing a second alignment algorithm. Inspection remains
optional: a failed query cannot invalidate history, a result, or a renderer.

Do not introduce `CodeArrangement`, `RadonArrangement`, or a universal `Lesson`
superclass to unify these examples. Ordinary value replacement can invalidate a
code; a relation edit can invalidate an inverse. Compose generic definitions with
named recipes and separately checked claims. Sharing numerical mechanisms does
not erase the different identity policies of Gather, Roll, Select, and reduction.

## Next experiments, in order

1. **Named products delivered in 05 and 07; challenge them in 10 next.** `Product`
   owns named roles and current-slot reads using existing operations. Tests cover
   reordered inputs, repeated labels/keys, empty factors, exact values, and captured
   reads. The next probe must separate canonical point codes from source slots in
   Hermitian incidence after reordering/filtering. Dense cost and new tuple identity
   remain explicit; this extraction does not justify a core product operation.
2. **Weighted prefix in 06.** Compare layer offsets with unit-weight ranks in 07.
   Require explicit order, zero first offset, signed weights, independent groups,
   and contributor receipts. This may justify an efficient scan primitive because
   the existing all-predecessor construction expands quadratically.
3. **Case-family evidence in 08.** Give each measurement an explicit case key and
   parameter environment. Test variable key domains and reordered cases. Today
   `Inspection` can follow saved parent references, but concatenation does not
   create a unified measurement claim; a family recipe must specify that contract.
4. **Coordinated replay in 11.** Compose existing transitions, captions, holds, and
   chart projections without reevaluation. Keep shared presentation progress
   distinct from an atomic edit of multiple workspace roots, which is not provided.

The [blank-canvas studio](CONSTRUCTION_STUDIO.md) now implements a first command
adapter and contextual hold controls across additive and modular constructions.
Its coverage matrix keeps all eleven lessons as the acceptance target. Next test
group selection and a compact expression editor across unrelated fibers; do not
turn the first successful investigation into the UI's organizing structure.

Alongside those recipes, test the [touch control hypothesis](TOUCH_WORKSPACE.md)
against concrete tasks: rebuild the plane lift;
select a reconstruction pixel and follow its line counts; remove an owner from a
partition and locate uncovered points; distinguish a phase-coordinate change from
multiplication. Record where a learner needs to understand storage details. That
is evidence for simplification; fewer class names alone are not.
