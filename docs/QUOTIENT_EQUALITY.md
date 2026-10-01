# Two quotient fields make one

Open **Two quotient fields make one**. This is a small canvas investigation
using the same construction, measurement, motion and comparison controls as the
other lessons. Its authoring source is [quotient_equality.py](../examples/quotient_equality.py).
No new evaluator operation or proof engine is introduced.

The two inputs start independently. Lower domain enumerates `(i,j)` in that
order. Upper domain enumerates `(j,i)` in the opposite storage order. Their
incidences become singleton counts, with zero groups retained. Explicit keyed
reads add those fields onto a third, initially zero grid. A fourth independently
constructed grid supplies the comparison's ones. None of these alignments uses
screen coordinates or storage position.

## Explore the exact claim

1. With **Moving cover** selected, Undo twice and Redo twice. Each step is a lift
   driven by a measured field. The coprime `(a,b)=(7,5)` case finishes at height 1.
2. In **Appearance → Color**, choose Integer field, `value`, Ocean and Fixed
   min–max 0–2. Apply colors. Set the same palette and limits on **Independent
   ones**. A constant automatic range uses the midpoint; fixed limits also make
   subsequent cases comparable.
3. From Moving cover, open **Details → More tools → Compare exact fields**.
   Compare its `value` with **Independent ones.value**, using `(i,j)` in that
   order on both sides. Choose Independent ones, also by `(i,j)`, as the
   expected domain. All 24 values agree.
4. The **Declared finite equality** states `dom(L)=dom(R)=D` and
   `∀ k ∈ D, L(k)=R(k)`, with L, R and D explicitly defined by the selected
   object fields and ordered keys. Give the record a title and **Save this
   comparison**. This saves the question together with its captured workspace
   and view. Open it later to check the same finite question again.
5. Change Parameters to `(6,4)` and Apply. Compare again. The key `(i,j)=(1,2)`
   has left value 2, right value 1, residual 1. The other 14 keys agree. The fixed
   color scale shows one different cell. Follow **Inspect left occurrence** to
   its read from Upper cells; inspect both singleton measurements at that key.
   Each has one contributing source point. Save this failed comparison too.
6. Open the earlier comparison file. Its parameters are still `(7,5)`, and its
   finite equality still holds. This does not overwrite the later file or attach
   an old verdict to a new case. Compare Counted area with Rectangle area by
   `key` if you want the scalar claim as well.

A plain **Canvas and view** save stores presentation and mathematics, but not
an open comparison question. Use **Save this comparison** to preserve that
question. Neither comparison saving nor checking creates an undo action.
The records are individual portable observations, not a workspace-wide statement
library. Their titles are labels, not interpreted hypotheses.

## Build it from blank with the existing controls

Declare positive integer parameters `a=7`, `b=5`. All formulas below use the
zero-based indices shown in the fields menu.

| Object | Construction choices |
| --- | --- |
| Lower domain | Grid sizes `b-1`, `a-1`; contents `1` |
| Lower incidence | Relation on Lower domain: `b*(j+1) <= a*(i+1)` |
| Lower cells | More tools → Measure with keys and order: Count; group keys `i`, then `j` |
| Upper domain | A new Grid; advanced axis names `j`, `i`, sizes `a-1`, `b-1`; contents `1` |
| Upper incidence | Relation on Upper domain: `a*(i+1) <= b*(j+1)` |
| Upper cells | Count; group keys `j`, then `i`, retaining the different storage order |
| Independent ones | A new Grid sizes `b-1`, `a-1`; contents `1` |
| Moving cover | A new Grid of those sizes, contents `0`; Arrange / move to `(i+1,j+1,0)` |

Use **More tools → Set values from a formula** on Moving cover. In the structured expression
editor choose a keyed read from Lower cells, receiver key `(i,j)`, source key
`(i,j)`, source field `value`. Keep the result name Moving cover. Arrange / move
to `(i+1,j+1,value)`. Next set its contents to `value +` a keyed read from Upper
cells with the same declared keys, and arrange again. Separate value assignment
and placement create separate history steps in the UI; the Python recipe groups
each assignment and its placement into a single captured command. Both build
the same definitions and measured endpoints. Arithmetic text handles the ordinary
terms; keyed reads currently use **Use controls**.

For a quotient profile, count Lower incidence by `i` only, and Upper incidence
by `j` only. For a discrepancy object, set a new copy of Moving cover's values to
its value minus the matching read from Independent ones. This is an ordinary
constructed residual with provenance. The comparison report remains read-only
and never silently manufactures that arrangement.

## What the picture suggests, and why it is true

Write `u=i+1`, `v=j+1`. On
`D = {1,…,b−1} × {1,…,a−1}`, the measured values are

\[
L(u,v)=\mathbf 1_{bv\le au},\qquad
U(u,v)=\mathbf 1_{au\le bv}.
\]

Every pair of integers is ordered, so at least one inequality holds. Both hold
exactly on `au=bv`. Consequently the stronger identity, without coprimality, is

\[
L(u,v)+U(u,v)=1+\mathbf 1_{au=bv}.
\]

Let `d=gcd(a,b)`. After dividing the equality by d, the coprime reduced factors
force `u=t b/d`, `v=t a/d`, with `t=1,…,d−1` in the stated rectangle. There are
exactly `d−1` double-owned cells. Thus the field is all ones when `d=1`, and
summing the independently measured quotient profiles gives

\[
\sum_{u=1}^{b-1}\left\lfloor\frac{au}{b}\right\rfloor+
\sum_{v=1}^{a-1}\left\lfloor\frac{bv}{a}\right\rfloor
=(a-1)(b-1)+\gcd(a,b)-1.
\]

These paragraphs supply a mathematical argument. **Expand construction** now
derives the actual two indicators and their bounded total sums from the graph,
with both starting domains and key order preserved. Authors can vary `a,b` and
declare `a > 1 and b > 1` and their coprimality. The software does not infer those
hypotheses, perform the floor-sum/gcd rewrite above, or attempt a universal proof.
The [statement guide](ALGEBRAIC_STATEMENTS.md) gives the controls and contracts.
The stronger correction identity is the next proof target because it explains
the failed case rather than discarding it.

## Scaffolding, ownership and limits

| Function or component | Responsibility |
| --- | --- |
| `quotient_equality(a,b)` | Authoring recipe: four independent domains, two predicates, singleton/axis/total reductions, keyed sums, residual and two captured lifts |
| `comparisonInspector` and the existing Python comparator | Explicit finite question, exact residuals, coverage failures and contributor navigation |
| `comparison-record.js` | Versioned portable question, selected fields/keys, three capture identifiers and generic finite notation; no arithmetic or proof status |
| `document.js` | Lossless original workspace text plus view and question; accepts existing canvas versions |
| `colors.js` / `color-controls.js` | Palette, exact limits and presentation controls, independently of construction/equality |
| `examples/statements/terms.py` / `expansion.py` | Shared typed integer translation, scoped substitution, retained domains, sums and obligations; also used for 3D ownership |
| `studio/statements.py` / `web/statement.js` | Explicit generalization/assumptions, versioned statement identity and shared controls; no theorem solver |

The portable format is `kaleion-comparison`, version 1. The complete existing
workspace JSON is carried as original text. The question's kind is
`keyed-integer-equality`, version 1 for a finite-only question or version 2 with
parameter/assumption choices and a pinned translator identifier. Both are readable;
older readers reject version 2. All three capture identifiers must match the
named roots on reopen; a mismatch prevents a verdict. Saving also checks the
server revision atomically, so a newer case cannot be paired with an old question. A saved verdict is not
trusted or even stored: the existing comparator checks the restored captures
again without executing their graphs. Historical definitions and contributors
remain available even if the live authoring logic later changes. This is an
inspectable local record, not a tamper-evident proof certificate.

The study retains the 2000-item intermediate budget. Large field displays still
have finite pixel resolution. No arbitrary set equality, isomorphism, unrestricted
symbolic translation or proof integration is implied. Unsupported construction
operators block expansion explicitly while finite comparison stays usable. Next
check an indicator lemma and keyed-read domain obligation through a separate
proof adapter before widening the supported translation rules.
