# 09 · A field changes its clothes

**Status:** available. [Open the notebook](../../notebooks/09_norm_fibers.ipynb).

**Question:** Can multiplication become a simple turn after rearranging the same elements?

**Background:** modular arithmetic and counting. The lesson introduces quadratic
fields, conjugation, norm fibers, cyclic groups, and a choice of phase coordinates.
It adapts the grid-to-fibers and finite-rotation experiments in
[Finite-Hermitian-Geometry](https://github.com/virgil-barnard/Finite-Hermitian-Geometry).
It covers one quadratic field; the source project's product rings and CRT remain separate.

## Construction and narrative

1. Declare `K = F_p[i]`, with `i² = -1` and prime `p ≡ 3 (mod 4)`. A stored
   integer `a + p*b` labels `a + bi`; arithmetic on those codes is coefficient
   arithmetic, not arithmetic modulo `p²`.
2. Arrange all elements on a coefficient grid. Measure the fibers of
   `N(a+bi) = a²+b² mod p`, retaining zero and all their contributors.
3. Choose a norm-one element β of order `p+1`. Construct its powers symbolically
   and select a representative of each nonzero norm fiber. These choices supply
   an order within each fiber; counts alone cannot do so.
4. Bind each element to its phase and measured fiber size. Move the nonzero
   elements from the grid onto rings. Multiplication by β changes values and
   advances one phase, following a recorded circular path.
5. Lift the rings to separate levels in 3D, then undo all three actions. The
   same 48 occurrences survive the default `p=7` construction.
6. Change β to another generator. This changes phase coordinates while preserving
   values and occurrence identity. Compare it with actual multiplication.
7. Break the field assumption at `p=5`: nine elements have norm zero, including
   nonzero factors whose product is zero. Inspect a measured fiber's contributors.

The notebook accepts teaching models `p=3,7,11` and validates the generator.
At `p=7`, the counts are `[1,8,8,8,8,8,8]`. The main motion has 150 sampled
frames; the separate generator change and undo have 50. Its 100-frame MP4 is an
explicit 2D projection of grouping, multiplication, and reversal. It omits the
vertical separation; use Plotly to inspect that in 3D.

## Explanation and limits

The nonzero field elements form a cyclic group of order `p²−1`. Its norm map
`z ↦ z^(p+1)` is onto `F_p*`, with a kernel of size `p+1`. Each nonzero fiber is
a coset of that kernel. This proves `p² = 1 + (p−1)(p+1)` and explains the turn:
`β(r_n β^k) = r_n β^(k+1)`. See
[Conrad, *Finite Fields*, Theorem 5.7 and the cyclicity appendix](https://kconrad.math.uconn.edu/blurbs/galoistheory/finitefields.pdf).

Drawing radii and angles do not make this a Euclidean field embedding. Even for
`p=7`, square roots of least norm residues violate the triangle inequality in the
displayed example. Smooth frames are presentation, not additional field elements.

The small [coordinate helper](../../notebooks/quadratic_coordinates.py) composes
existing integer expressions. It is a lesson recipe, not a new numerical domain.
Generator validation, exact arithmetic, grouping, and rendering remain separate.
This is a concrete use case for declaring an invariant, choosing group order,
and assigning measured values to placement in the future interface.

Exports in `build/notebooks/norm-fibers/` include six offline HTML views, an MP4,
four workspace files, `checks.json`, and `fiber-explanation.json`.

## Functions and authoring scaffolding

The [notebook](../../notebooks/09_norm_fibers.ipynb) defines three top-level functions.
See the [cross-lesson inventory](HELPER_INVENTORY.md).

| Local function | Responsibility and assumptions |
| --- | --- |
| `norm_fibers(p)` | Validate the supported primes 3, 7, and 11; construct coefficient-coded elements, annotate their norm, place the coefficient grid, and count by norm. Arithmetic assumptions and the initial chart are currently combined in this recipe. |
| `phase_atlas(points, p, beta)` | Check that the chosen norm-one generator has order `p+1`; unroll symbolic products; choose the least-coded element of each nonzero norm fiber as its anchor; bind anchors and powers into a keyed phase atlas. The finite Python orbit check validates the input choice. |
| `in_norm_fibers(source, atlas, counts, cylinder=False)` | Bind phase and measured fiber size into placement formulas for rings or a cylinder. The source's norm annotation must correspond to its current values. |

**Shared functions used.** From
[quadratic_coordinates.py](../../notebooks/quadratic_coordinates.py), this lesson
calls `field_multiply`, `field_norm`, and `element_label`. The additional imported
`field_sum`, `field_conjugate`, and `hermitian_pair` are not called here.
[lesson_views.py](../../notebooks/lesson_views.py) supplies `style`, `profiles`,
`replay`, and `save_figures`; public `snapshot_figure` and `write_mp4` also serve
the views.

**Inline scaffolding.** The cells construct multiplication actions, compare them
with a change of phase coordinates, and stage paths and undo. They assemble
fiber figures, identity colors, explicit two-dimensional projections of captured
frames for video, zero-divisor and misleading-distance witnesses, contributor
explanations, and saved workspaces/figures.

**Abstraction evidence.** An orbit/coordinate-atlas recipe could separate the
chosen representatives and phase keys from ring geometry. The shared quadratic
arithmetic also supports 10; 11 uses a different coefficient model. Any later
common arithmetic abstraction must state its basis and modulus. Packed integer
labels and screen distance do not determine the field operations.
