# Declare the choices behind a picture

An arrangement can look like a line, a grid, a spiral, or a scattered cloud.
Its logical groups and ordering need not follow the visible rows. These operations
make the author's choices explicit while keeping evaluation and motion separate.

Run the complete core-only example with an activated virtual environment:

```sh
python3 examples/grouping_choices.py
```

Lessons [07](../notebooks/07_additive_structure.ipynb) and
[10](../notebooks/10_hermitian_partitions.ipynb) use the same declarations beside
their interactive figures. Restart the notebook kernel after updating Kaleion.

## Name the roles in a product

```python
from kaleion import Collection, F, Product

left = Collection.literal([0, 1, 3])
right = Collection.literal([0, 2])
product = Product(left=left, right=right)
pairs = (product.domain
         .annotate(a=product.read("left"), b=product.read("right"))
         .annotate(total=F.a + F.b, pair_key=F.key)
         .with_values(F.total).arrange(F.a, F.b))
assert pairs.evaluate().values.tolist() == [0, 2, 1, 3, 3, 5]

bins = Collection.sequence(7, start=0)
measurement = Product(pair=pairs, bin=bins)
domain = measurement.domain.annotate(
    total=measurement.read("pair", F.total), s=measurement.read("bin"))
profile = domain.where(F.total == F.s).count(by=F.bin).arrange(F.bin, F.value)
assert profile.evaluate().values.tolist() == [1, 1, 1, 2, 0, 1, 0]
```

`Product` names two or three factor roles, then supplies a collection and source
reads. It does not choose a predicate, a chart, or a grouping. `read("left", F.key)`
would copy that source's retained key; the role field `F.left` is its **current
slot**. Duplicate labels and keys remain distinct product occurrences. The last
factor varies fastest, and products have unit values until replaced explicitly.
An empty input still permits zero counts for every declared bin in the other
factor. The product does not discover absent semantic bins: declare those yourself.

Reads use the role axes; copy needed fields before changing those axes or applying
a reindexing operation. Reordering factors' items changes which source item is in
each slot; preserving pair identity across that edit requires an explicit semantic
correspondence. Geometry is never adopted automatically from a factor.

**Migration:** replace a manually sized grid plus `source.bind(on=F.i, key=F.index)`
with `Product(role=source, ...)`, `.domain`, and `.read("role")`. Update retained
ordinal keys such as `by=F.j` to the corresponding role, such as `by=F.bin`.
Keep semantic keys such as `(m,t)` unchanged. If the old binding used a canonical
label instead of `F.index`, first establish that label's relationship to the slot;
it is not a mechanical substitution. Lessons 05 and 07 provide two working uses.

This is a lazy authoring recipe in `products.py`, not a new graph operation.
Dense products retain their full cost and existing item bounds. Saved definitions
use ordinary Grid/Count/Bind operations, so the capture schema is unchanged.

The [touch workspace hypothesis](TOUCH_WORKSPACE.md) maps these declarations to
controls. Try its bounded study with `python3 examples/touch_study.py` and open
`build/touch-study.html` locally.

## Group, order, measure, place

```python
from kaleion import Collection, F, Workspace

points = (Collection.grid(3, 4, values=F.i + F.j)
          .annotate(point=F.key).arrange(x=F.j, y=F.i))

groups = points.group_by(F.value)
counts = groups.count()
ranks = groups.order_by(F.point).ranks(key=F.point)

slot = ranks.bind(on=F.point, key=F.key)
stacks = points.arrange(x=F.value, y=slot)
```

The group sizes are `[1,2,3,3,2,1]`. A rank is the number of strictly earlier
members of the same group. It starts at zero and retains the point key supplied
to `ranks`. Moving the original points into stacks preserves their occurrence
identities; the rank collection is a new measurement with its own identities.

| Declaration | Context and meaning |
| --- | --- |
| `source.group_by(F.g)` | Retain the source's `g` keys for subsequent measurements |
| `source.group_by(F.g, F.h)` | Retain a composite key; `groups.key` reads it from a grouped result |
| `source.group_by()` | Treat the whole finite source as one group |
| `groups.count()` / `groups.sum(value=...)` | Existing exact reductions, with zero-group rules unchanged |
| `groups.order_by(F.a, F.b)` | Declare lexicographic member order within each group |
| `ordered.ranks(key=F.id)` | One zero-based predecessor count per unique item key |
| `counts.order_by(F.key)` | Separately choose the storage/display order of group measurements |
| `driver.bind(on=..., key=..., read=...)` | Match a target key to a unique driver key and read a quantity |
| `target.arrange(x=..., y=..., z=...)` | Assign coordinates explicitly; supply x, x/y, or x/y/z |

Member-order ties are an error. Add another field, such as a stable item key, to
resolve them. Storage order is never an automatic tiebreaker. To reverse a numeric
order, use `order_by(-F.value, F.id)`. Counts do not depend on the member order.
Ranking an incidence ranks its selected occurrences; an empty selection produces
no rank items. Its grouped count can still retain zero groups.
For composite keys, retained fields keep their names, including a field named
`key`; an ordinal `F.key` is supplied only when that name is otherwise unused.

## Check coverage before adopting an assignment

Select the first member of every sum group:

```python
first = points.where(slot == 0)
coverage = first.group_by(F.value).coverage()
representatives = coverage.unique(value=F.point)

state = Workspace({"counts": coverage.counts,
                   "missing": coverage.missing,
                   "overlaps": coverage.overlaps,
                   "representatives": representatives}).state
assert not state.errors
assert state.results["representatives"].values.tolist() == [0, 1, 2, 3, 7, 11]
```

Coverage counts **matching occurrences**. Two matches fail uniqueness even if their
values are equal. `unique` checks every retained key, then reads its sole
contributor through a guarded weighted reduction. Value zero is an ordinary valid
result. It never substitutes for missing coverage.

`coverage.exactly(1)` builds an incidence of checks. `coverage.missing` selects
zero counts; `coverage.overlaps` selects counts greater than one. When an assignment
fails, those measurements and witnesses remain usable as independent roots.
`coverage.on_keys(F.key > 0)` explicitly narrows the report before checking or
assigning. Its predicate sees the grouped-count context.

The example also constructs coverage `[0,1,2,1,1,1]`. Its total is still six, but
the assignment fails: sum zero is missing and sum two has two representatives.

**The domain matters.** Coverage uses the existing reduction domain before the
incidence mask: declared retained grid axes include empty fibers; other group keys
come from the source. It does not invent keys absent from that domain. A target
binding requesting an absent key still fails. This is a scoped finite coverage
check, not an equality/comparison engine for arbitrary unrelated key domains.

For another finite prerequisite, `items.require(checks, message="...")` passes
items through only when every check is true. Empty check domains pass vacuously;
state the intended universe explicitly. Failed evaluation remains an error.

## Use measurements on another arrangement

```python
probes = Collection.sequence(6, start=0).arrange(x=F.value, y=0, z=0)
height = counts.bind(on=F.value, key=F.key)
lifted = probes.place(x=F.x, y=F.y, z=height)
```

The independent probes read measured heights by sum key. Reordering the driver's
storage does not change the correspondence. `place` and `arrange` also retain
their positional forms, so existing code continues to work. The workspace's
recorded transition supplies animation and reverse playback.

## Inspect evidence without expanding every prefix

```python
rank_snapshot = ranks.evaluate()
earlier_occurrences = rank_snapshot.contributor_ids(6)
assert len(earlier_occurrences) == 1
```

Rank evaluation groups and sorts in O(N log N) worst-case time. Its stored evidence
contains each group's ordered occurrence IDs once, plus one prefix range per
result: O(N) space. This query locates the retained key and expands only its prefix;
requesting every prefix can still require quadratic total output. The snapshot's
`metadata["universe"]` identifies the evaluated source of these contributor IDs.
Direct rank parents anchor the item being ranked; they are distinct from the
counted predecessors.

Placement and reindexing preserve the evidence. Changing measured values removes
the active measurement claim while retaining the input derivation. Captured JSON
retains the compact representation, so explanations and undo work after reopening
without reevaluation.

## Follow a bound measurement

The independent probes above can explain their placement without manually joining
saved IDs. Inspection reads the captured inputs of the placement operation:

```python
from kaleion import Inspection, Workspace

workspace = Workspace({"lifted": lifted})
inspect = Inspection(workspace.state)
point = inspect.find("lifted", 3, by=("value",))
read, = inspect.bindings(point)
receipt = inspect.measurement(read.driver, limit=8)
assert read.key == (3,)
assert read.value == receipt.item.value
```

The [complete example](../examples/inspection_choices.py) includes zero groups,
reordered storage, failed keys, signed weights, and saved undo/redo. Use
`item(ref).parents` to navigate earlier steps; measurement values changed by
`with_values` no longer carry the original active measurement claim. The
[exploration workflow](EXPLORATION_WORKFLOW.md) states supported query kinds and
limits. Direct keyed reads are implemented; arbitrary recursive explanation,
scalar extraction, positional lookup, and nested binding keys/reads remain future work.

## Why these boundaries

`grouping.py` owns the declarations and small recipes. `indexing.py` owns member
ordering. `measurements.py` owns captured contributor representation and queries.
The evaluator schedules their execution; history and viewers retain their own
responsibilities. This applies the project's Parnas criterion to changeable
decisions rather than creating a class for each screen.

Two new version-1 operations are justified: `rank` avoids a dense predecessor
expansion, and `require` makes a finite prerequisite part of the dependency graph.
Coverage uses existing reductions, predicates, and bindings. Older schema-1
captures remain supported by the updated code. Executing the new operations and
reading contributor-prefix version 1 require this updated implementation.
