# Follow the weight, then return to the question

September 22, 2026 · Radon reconstruction through shared studio controls

A sum has three distinct quantities: the source item's value, its contribution
weight, and any driver value read to calculate that weight. The studio now makes
each inspectable. This extends the [linked-view instrument](LINKED_EVIDENCE_VIEWS.md)
with ordered key tuples and a return path through nested measurements.

The same controls build the investigation below and the unrelated signed-weight
example at the end. There is no Radon menu or new evaluator operation.

## Two reusable interactions

**Key tuple** is a new expression-editor choice. Tap its components to choose
fields or formulas; Add component and Remove last component change its arity.
A tuple has 2–8 ordered scalar components. Single-field keys still use Field.
For a read, target components belong to the receiving object; source components
belong to the driver. Choosing `(m,t)` is different from choosing `(t,m)`.
Local expression undo and parked drafts retain the tuple and its field contexts.
The adapter lowers this syntax to the existing `vector` expression; normal
binding checks still reject missing or ambiguous keys. Nested tuple components
are not supported. No automatic key encoding or correspondence inference occurs.

**Inspect selected occurrence** in a contributor view now retains the surrounding
measurement context. The receipt shows source value, exact weight, measured
result, retained key, and weight formula. **Follow weight read** follows a keyed
read in that formula. If a weight uses a copied field, its source occurrence's
ordinary **Follow keyed read** controls expose the field's earlier reads. Each
read is labeled by its site so equal-valued reads remain distinguishable.

**Back to contribution**, **Back to measurement**, and **Back to read origin**
restore the previous receipt and paired views, including selected occurrences
and independent cameras. These are tab-local inspection actions, separate from
mathematical Undo. They do not change a construction, apply a draft, or add a
history step. Starting another investigation or changing the workspace leaves
this temporary navigation path behind.

## Build an image from its line sums

Use the existing environment and `python3 -m examples.studio`. This is a small,
weighted variant of [lesson 05](lessons/05_finite_radon.md), constructed through
the ordinary controls. Its image is `I(u,v) = u*(v+1)` for `u,v` in `0,1,2`.

| Object | Construction choices |
| --- | --- |
| Image | Grid `3,3`, axes `u,v`, value `u*(v+1)`; arrange `x=u, y=v` |
| Lines | Grid `4,3`, axes `m,t`, value `0`; `m=3` denotes vertical lines |
| Pairs | Product with roles `point=Image`, `line=Lines`; copy `u,v,value` from point and `m,t` from line |
| Incidence | Relation `(line_m < 3 and (point_v-line_m*point_u-line_t) mod 3 = 0) or (line_m = 3 and point_u = line_t)` |
| Counts | Sum Incidence, retain `line_m,line_t`, weight `point_value`; arrange with those two keys as coordinates |
| Backprojection | Sum Incidence, retain `point_u,point_v`; weight is a keyed read of Counts.value, target `(line_m,line_t)`, source `(line_m,line_t)` |
| Family | Relation on Counts: `line_m = 0` |
| Total | Sum Family with no retained keys and weight `value` |
| Recovered | Add field `recovered` to Backprojection: `(value - read Total.value at target key 0, source key key) div 3` |
| Division check | Add field `remainder` to Backprojection using the same numerator `mod 3` |

Names are choices, not special identifiers. In the editor, `div` is floor integer
division. Keep the remainder check explicit; floor division always returns an
integer, even when an intended exact division has failed. `Recovered` is a new
attribute: the original backprojection values and their measurement evidence
remain intact. Select `recovered` in the point-label control to display it.

The image, indexed by `u` first, is:

| u \ v | 0 | 1 | 2 |
| --- | ---: | ---: | ---: |
| 0 | 0 | 0 | 0 |
| 1 | 1 | 2 | 3 |
| 2 | 2 | 4 | 6 |

Line sums in `(m,t)` order are `[3,6,9,8,5,5,7,7,4,0,6,12]`, and Total is `18`.
Backprojection is `[18,18,18,21,24,27,24,30,36]`. Subtracting 18 and dividing by
three recovers the image, with nine zero remainders. These expected results are
checked independently by enumerating points on each line.

To reuse the measurement as motion, arrange Image with `x=u` and
`y=v + read Recovered.recovered`, matching target `(u,v)` to source
`(point_u,point_v)`. Preview and Apply produce a measured displacement; Undo/Redo
restore its captured endpoints. The image's labels remain unchanged. Earlier
products retain their original image input, so inspecting their field reads
still shows that captured image even after its named view has moved.

## What the evidence chain reveals

Inspect Backprojection at `(0,0)`, and open its contributors. There are four
point–line occurrences. Their product values are all one, while their weights
are `3,8,7,0`: four line sums read by `(m,t)`.

Choose the contributor for `(m,t)=(3,0)`. Its source value is **1**, its weight is
**0**, and its weight read points to a real line measurement with value **0**.
Follow that read, then open the line measurement's contributors. All three
pixels on `u=0` contributed weights zero. This is not an empty reduction.

Those contributors are still point–line occurrences. Their weights came from
the copied `point_value` field. Follow the ordinary read labeled `point_value`
to see the actual captured image pixel in its original 2D placement. The UI
preserves the difference between a product occurrence, its copied attribute,
and the source occurrence that supplied it. Return controls recover each stage.

The general identity used in the notebook is `B(x)=p*I(x)+T`: over the prime
plane, a point lies on `p+1` lines and each different point shares exactly one
line with it. Summing all lines through x counts its own image value `p+1` times
and every other image value once. This explanation depends on the incidence
structure, not on the smoothness or appearance of the animation.

## Break an assumption

Changing only the target tuple to `(line_t,line_m)` makes the vertical-family
read unavailable. Preview fails, Apply stays disabled, and local expression Undo
can restore the declared key order. This is a binding failure, not a zero weight.

More subtly, rebuild the same recipe modulo **4**, using a `4 × 4` image and five
line families. The prime-plane reconstruction identity no longer applies.
For the same formula `u*(v+1)`, Total is `60`. At `(0,0)` backprojection is `56`,
so the reconstructed value is **-1** rather than **0**, even though its division
remainder is zero. Other pixels have nonzero remainders. Thus exact divisibility
at a point does not by itself establish correct reconstruction. The offline
counterexample checks the whole finite case independently. This does not construct
the field of four elements; that requires different arithmetic.

A second transfer case separates a weight from the value it reads. Create source
values `[99,99,99]`, a driver `[0,2,5]`, and sum weights `2*read(driver)-4`, aligned
by `index`. The weights are `[-4,0,6]` and the total is `2`. Inspecting the middle
contributor shows source value **99**, weight **0**, and driver read **2**. Each
number has a different role. Negative and zero contributions remain inspectable.

## Information hiding and evidence

| Changeable decision | Owner | Contract |
| --- | --- | --- |
| How to write ordered keys | `web/expressions.js` | Structured tuple parts, source/target field contexts, local undo; no arithmetic |
| How that syntax enters a construction | `studio/adapter.py::expression` | Bounded tuple syntax becomes an existing vector expression |
| How a weight and its reads are explained | `web/receipts.js` | Existing captured receipts, named read sites, semantic navigation callbacks |
| How a view returns to its earlier focus | `web/evidence.js` | Temporary link selection and per-card camera snapshots; opaque selection context |
| How weights and bindings are obtained | Existing `Inspection` and studio queries | Captured inputs, scoped references, exact weights; no graph execution |

Receipt presentation is extracted from `studio.js`; no new core class or
inheritance hierarchy is needed. The generic view renderer forwards selection
context without knowing the meaning of a contribution. Public Python APIs,
operation/history schemas, dependencies, and notebooks are unchanged. Existing
captures need no migration. Clients using the experimental declaration protocol
can now supply `{"tuple":[{"field":"m"},{"field":"t"}]}` wherever an ordered key
expression is appropriate; invalid vector-valued uses still fail normal evaluation.

Four new offline tests cover prime cases 2, 3, and 5; the composite-modulus failure;
ordered and huge exact keys; invalid tuple forms; signed/zero transformed weights;
and a reopened measurement → weight read → source-field read chain with graph
execution disabled. The required suite passes **160 tests** and the discovery
example retains its expected outputs. The browser gate constructs the size-three
case from blank inputs, checks reconstruction and exact remainders, uses the
result for reversible placement, traverses and returns through the receipts,
and transfers to transformed signed weights. It also checks tuple drafts/undo,
failed key order, desktop/320-pixel layout, and unchanged saved data during browsing.

Run `python3 -m unittest discover -s tests -p test_studio_weighted.py -v` for the
focused contracts. Full validation commands and separate Playwright setup are
in the [studio guide](CONSTRUCTION_STUDIO.md#validation-and-reproduction).
No notebook or video export changed. Touch is emulated; physical-device,
screen-reader, Safari, and novice usability testing remain open. Cards still
require substantial vertical scrolling on phones. Scalar/positional reads and
bindings nested inside another binding's key or read remain outside the existing
inspector contract. This increment does not claim full lesson-05 UI parity.

**Next experiment:** exact case controls for the prime-to-composite change, clearly
separated from replay time. The repeated modulus currently has to be entered in
several expressions. A shared parameter declaration could make changing that
assumption both easier and explicit, while preserving each measured case and its
evidence. Test it on this investigation and a growing lattice-point arrangement
before introducing a broader reactive editing mechanism.
