# 10 · One curve, two ways to gather it

**Status:** available. [Open the notebook](../../notebooks/10_hermitian_partitions.ipynb).

**Question:** Can different incidence measurements organize the same 28 points
into one point plus nine triples, and then seven quadruples?

**Background:** lesson 09's coefficient arithmetic and norms. Projective points,
Hermitian orthogonality, polars, pencils, and a finite block design are introduced
as constructions. This fully enumerated lesson uses `F_9`; larger fields are not
enabled by changing a parameter.

## Construction and narrative

1. Begin with all 728 nonzero triples over `F_9`. Normalize the first nonzero
   coordinate to one. Moving to normalized coordinates leaves 728 occurrences
   at 91 shared positions. Count by the canonical key to form 91 new projective
   classes, each with eight original representatives as contributors.
2. Select the isotropic classes for `h(x,y) = Σ x_j conjugate(y_j)`:
   `h(x,x)=0`. There are 28. The visible code chart and infinity strip locate
   their labels; projective lines need not look straight in that chart.
3. Construct the incidence on **91 line poles × 28 curve points**. Retaining the
   line key produces 28 counts of one and 63 counts of four. Retaining the curve
   point key produces 28 counts of ten. Both totals are 280.
4. Scrub the 91 poles. Each pole becomes a relation argument selecting its polar
   intersection with the curve. A curve point selects its tangent; an external
   point selects a four-point secant.
5. Through a chosen curve point, select its nine secants and omit their common
   point from those blocks. Its tangent supplies the singleton block. Declare
   coverage on all 28 point keys, then use `coverage.unique(value=F.i)` to derive
   owners only after every key has exactly one match. Order the blocks separately
   from their members; measured strict ranks supply their placement slots.
6. Use those measurements to gather the 28 points into one point plus nine triples.
   Choose an external pole, take its six secants, and add its polar. The resulting
   measured correspondence gathers the same points into seven quadruples.
7. Remove that polar: four points become uncovered. Inspect their keys and trace
   one assigned point through its incidence contributor to its eight projective
   representatives. Inspect its rank's predecessor evidence too. Reverse both
   motions from recorded history.

The default poles are key `4`, representing `[1:0:1+i]`, and external key `0`,
representing `[1:0:0]`. The notebook marks the permitted choices. Tests also use
points on the infinity strip and reversed storage order. Keys, rather than row
positions, determine every correspondence and contributor query.

## Explanation and limits

Nonzero scalar multiplication acts freely on nonzero triples, so each projective
class has eight representatives and `728/8=91`. Norm-fiber sizes `1,4,4` give 24
isotropic points in the chart `(1,a,b)` and four more at infinity.

The Hermitian unital's secants form a `2-(28,4,1)` design: every pair of curve
points shares exactly one secant. A curve point therefore yields `27/3=9` triples.
The external-pole construction yields a regular spread, whose seven disjoint
four-point blocks cover the curve. These are established finite-geometric
constructions, not new theorems inferred from animation. See
[Dover, *A Search for Spreads of Hermitian Unitals*, §1](https://arxiv.org/pdf/1702.01297).
The notebook checks every line, every point pair, and both coverage functions.

The quotient and its 50-frame normalization/undo distinguish coincident
representatives from reduced classes. The 100-frame partition motion preserves
all 28 curve occurrences and their original group colors, making the mixing
between partitions visible. Norms and polars are exact algebraic relations;
the diagram is not a Euclidean metric model. Background on Hermitian forms:
[Greaves et al., *Frames over finite fields*](https://arxiv.org/abs/2012.12977).

## What this teaches us about Kaleion

The [explicit authoring choices](../AUTHORING.md) now express grouping, member
order, coverage, and named measurement-driven placement. A future interface
needs explicit domain roles, selection-as-relation-argument, coverage witnesses,
ordered groups, and a distinction between quotienting and moving points together.
A sum of owner keys is meaningful only after coverage is one; zero alone is
ambiguous. The [UI notes](UI_DISCOVERY_NOTES.md) make these choices concrete.

The later [coverage instrument](../COVERAGE_INSTRUMENT.md) tests the same contract
on a restricted seven-block family through the studio adapter, using named product
roles and reversed canonical point storage. An independently chosen 28-point
domain still exposes four missing keys after the polar is removed and survivors
are selected. This adds a separate adapter fixture, not new notebook helpers;
the complete lesson's source-constructor UI and larger support remain future work.

Pair domains also expose a practical limit. Incidence still uses the declared
91×28 support. Ranks now sort within groups and store compact predecessor prefixes,
removing the old `28×28` rank domain. With all definitions, evaluated dependencies,
contributors, observations, and pending redo retained, the default motion capture
is about 11.4 MiB in compact JSON, down from 18.3 MiB before this refinement.
The 32 MiB import budget is unchanged. Complete snapshots still repeat across saved
states; shared capture storage remains separate future work.

Exports in `build/notebooks/hermitian-partitions/` include seven offline views,
an MP4, six workspace files, `checks.json`, and `point-explanation.json`.

## Functions and authoring scaffolding

The [notebook](../../notebooks/10_hermitian_partitions.ipynb) defines four top-level
functions. See the [cross-lesson inventory](HELPER_INVENTORY.md).

| Local function | Responsibility and assumptions |
| --- | --- |
| `projective_quotient(p=3)` | Construct nonzero triples, normalize the first nonzero coordinate, encode representative keys, and count the classes. This bounded recipe uses `p=3`; moving 728 representatives together is distinct from reducing them to 91 classes. |
| `projective_points(p=3, labels=None)` | Decode canonical point labels into coordinates, annotate self-pairing, and assign an affine chart plus an infinity strip. Coordinate decoding and display placement are currently coupled. |
| `hermitian_incidence(points, p=3)` | Build the point/curve product, bind both coordinate triples by their declared indices or keys, apply the Hermitian pairing, and count hits. The right-hand domain is the 28-point curve, not all 91 points. |
| `hermitian_partition(points, incidence, line_counts, focus, p=3, external=False)` | Select the relevant secants or polar, measure per-point coverage, guard the owner assignment with unique coverage, declare block/member order, and bind measured ranks into packing. Return named intermediate stages so coverage and ownership remain inspectable. |

**Shared functions used.**
[quadratic_coordinates.py](../../notebooks/quadratic_coordinates.py) supplies direct
calls to `field_multiply`, `field_conjugate`, `field_norm`, `hermitian_pair`, and
`element_label`; `hermitian_pair` also calls `field_sum` internally.
[lesson_views.py](../../notebooks/lesson_views.py) provides `style`, `profiles`,
`replay`, and `save_figures`; the public `snapshot_figure` and `write_mp4` support
additional presentations.

**Inline scaffolding.** Polar exploration builds its own multi-trace frame family.
Normalization and partition edits, reverse playback, color assignment, an omitted
line's coverage witness, and export loops are inline. Explanations manually join
owners to incidence pairs and point classes, and inspect rank predecessors.

**Abstraction evidence.** Coordinate decoding, canonicalization, incidence, and
packing have different reasons to change; they need not become one projective
arrangement subclass. Guarded assignments recur in 11's quotient, inverse, and
syndrome constructions. Coverage, strict ranks, and named placement are already
public capabilities; the opportunity is to compose them readably and explain
the bindings, while keeping failed coverage visible.
