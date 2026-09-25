# Compare a captured mathematical case

The studio's **Compare integer fields** instrument asks a precise finite question:
do both operands have exactly the declared keys, with equal integer values at
every key? It is available from a collection or arrangement's **Options** menu.
Select an incidence explicitly before comparing its retained occurrences.

## Declare the question

Choose the left value field and ordered key fields. Choose a right object, its
value field and corresponding keys, then an **Expected domain** and its keys.
The third choice is independent: it can name either operand when that is the
intended domain, or a separately constructed collection. Match components in the
same order. Geometric positions and equal labels never infer correspondence.

**Compare captured values** reads the current captures. It creates no arrangement,
preview, evaluation, or history entry. The last declaration stays in the browser
tab for reuse after a parameter change; the old verdict does not. **Save this
comparison** also exports the question and its captured case for later reopening. After **Cases →
Evaluate case → Apply**, reopen Compare and check the newly captured case.
Replay remains a presentation of an already recorded transformation.

| Outcome | Meaning and next inspection |
| --- | --- |
| Equal | Both values exist and the exact left-minus-right residual is zero |
| Different | Both values exist; inspect the nonzero residual and either occurrence |
| Missing | An expected key is absent on one or both sides; no residual is invented |
| Outside | An operand contains a key outside the declared domain; excluded from residuals and fails the domain claim |
| Could not compare | Duplicate keys, noninteger fields, unavailable captures, or incompatible declarations prevent the check |
| Empty expected domain | Explicitly reported; empty operands satisfy domain equality but assert no item equality |

Each key must identify one occurrence, even if duplicate values would agree.
Zero is a value with an occurrence and evidence. A key missing from both sides
still appears through the expected domain. Integers and residuals remain exact
beyond 64 bits; the browser receives decimal strings.

## Inspect a discrepancy

Filter keys by outcome and choose a witness. **View compared occurrences** opens
the existing paired capture views. Their labels show the *selected value fields*;
an occurrence's own `value` can be different. **Inspect left/right occurrence**
opens its receipt with a reminder of the compared field. Follow contributors,
weights, and captured reads as usual. **Back to comparison** restores the witness,
paired selection, and both cameras. An absent item has no inspection button;
**Inspect expected key** remains available for a key absent on both sides.

Fit, zoom, and directional pan buttons are shared by the main and paired views.
They work by tap or keyboard and change only the camera. On a narrow screen,
**Canvas** and **Controls and evidence** links move focus and scroll between the
two areas. These shorten navigation; they do not keep both areas visible at once.

## Two constructions and a broken assumption

Use the [parameterized Radon construction](PARAMETER_CASES.md): compare
`Radon recovered.recovered` by `(point_u, point_v)` with `Radon image.value` by
`(u, v)`, declaring `Radon image` by `(u, v)` as the expected domain. At `p = 3`,
all nine values agree. At `p = 4`, key `(0, 0)` has recovered value −1 and source
value 0. Division has remainder 0 there, but reconstruction is wrong. Its receipt
has occurrence value 56, the backprojection sum, distinct from recovered −1.
Inspecting the residual leads into the existing five-contributor evidence chain.

Transfer the same controls to the growing triangle. On the `(n+1) × (n+1)` grid,
count `i + j < n` by `i`. Independently construct a length-`n+1` grid with values
`n − i`. Compare their `value` fields by `i` over the formula grid. At `n = 4`,
the values are `[4, 3, 2, 1, 0]`; at `n = 0`, the retained zero still has a receipt.
Reordering or moving the formula source leaves correspondence unchanged.

As a domain counterexample, declare three expected keys with zero values, then
remove the middle occurrence from both operands. The two remaining zeros agree,
but the independent domain reports the key missing on both sides. Conversely,
restricting only the expected domain reports an outside key on each operand.

## Module decisions and boundaries

| Decision | Owner |
| --- | --- |
| Unique integer-key alignment, selected fields, exact residuals and domain failures | `kaleion.comparison`; extracted from the existing notebook helper |
| Bounded report with captured occurrence references | `examples/studio/comparison.py` and revision checks in `adapter.py` |
| Input choices, local status, outcome filter and selected witness | `web/comparison.js` |
| Captured views, independent cameras and evidence return navigation | Existing `evidence.js`, receipts, and studio composition |
| Shared tap/keyboard camera alternatives | `web/camera.js` |

`notebooks/snapshot_views.py` reexports the comparison helpers so lessons 04–05
keep their imports. Rectangular plotting remains notebook presentation support.
There is no new evaluator operation, runtime dependency, or saved-format change.
Reports remain read-only, and are not reusable residual arrangements. A separate
`kaleion-comparison` document now persists the question, exact workspace text,
three capture IDs and view. It adds no claim to the core workspace schema; Open
validates those IDs and checks the captured values again. Both successful and
failed comparisons can be saved. See [the quotient investigation](QUOTIENT_EQUALITY.md). Support, totals, isomorphism, and geometric
equality require separate contracts. This check does not prove a universal law.

## Verification and open questions

Seven adapter tests cover the two families, composite-modulus counterexample,
selected fields, missing/outside keys, duplicate keys, huge integers, empty and
unavailable inputs, read-only queries, stale revisions, preview preservation, and
saved inspection/undo/redo with evaluation disabled. Existing notebook adapter
tests remain unchanged. Run:

```sh
python3 -m unittest discover -s tests -p test_studio_comparison.py -v
python3 -m unittest discover -s tests -p test_snapshot_views.py -v
node docs/studies/check-construction-studio.cjs
```

The browser gate authors both constructions, returns through nested receipts,
checks missing-both/outside witnesses, retains a parked draft, and uses camera
buttons and mobile navigation without changing exported workspace data.
The [design study](UI_DESIGN_STUDY.md) records the current audit. Physical touch,
screen readers, and novice understanding of three key declarations remain open.
