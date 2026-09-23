# Ordered accumulation: implementation brief and contract

## Next-PR brief

**Status:** implemented from merged `91a6e33`; validation is recorded below.

Close the weighted-prefix gap exposed by Young-layer packing. Add an exact,
exclusive prefix measurement with declared groups, member order, item keys and
weights. Preserve compact captured evidence. Expose it through the existing
Measure instrument and demonstrate transfer to quotient-column packing. Keep
construction, evaluation, inspection, history and presentation separately usable.

Acceptance requires two constructions and a broken assumption: derive Young
offsets `[0,3,6,8,9]`, derive offsets from quotient counts including their zero
column, and reject tied order or duplicate item keys without guessing. Check
signed/zero/large weights, empty input, scoped parameter cases, keyed reuse,
saved evidence and reversible placement. Do not expand all predecessor pairs.

This follows the [core plan](CORE_REFINEMENT_PLAN.md),
[UI design study](UI_DESIGN_STUDY.md), and [touch proposal](TOUCH_WORKSPACE.md).
The latter explicitly asks for the ordered-measurement contract to precede its
control. No lesson-specific menu or general recurrence editor is part of this PR.

## Mathematical contract

For item `a`, its exclusive prefix is the sum of weights of items in the same
group whose declared order tuple is strictly earlier than `a`'s. The current
item does not contribute. Each nonempty group's first result is zero.

- Declare member order explicitly, with no implicit tie breaker. Ties within a
  group fail even when weights agree. Group order itself is not member order.
- Declare globally unique output item keys; composite keys may include group
  identity. Duplicate labels or repeated gathers require an explicit new key.
- Return one measurement per selected item, in its input storage order. Keys
  align downstream bindings; sorting storage or changing placement is independent.
- Incidences first select their members. No prefix is invented for an absent
  item or empty group. A retained zero count is an actual item and participates.
- Weights are exact integers. Zero and negative weights remain contributors;
  arbitrary integer accumulation need not describe a nonoverlapping packing.
- Store each group's ordered source roster once and one prefix range per output.
  Expand only requested evidence; requesting all prefixes still has quadratic
  output size.

The public spelling is
`source.group_by(...).order_by(...).prefix_sums(key=..., value=...)`.
It needs a named `prefix_sum` operation because the existing dense recipe has
quadratic intermediate work and evidence. It uses the same strict ordering and
version-1 contributor ranges as Rank. It is an ordinary measured collection,
available to existing bindings, comparisons, captures and motion.

## Use the shared instrument

Choose **Measure → Prefix sum · before each item**. Declare optional group fields,
one or more order fields, a unique item key, and a weight expression. The weight
editor is the same one used by Sum; order/key choices are shared with Rank. The
form explains that the result has one measurement per selected item. Preview and
Apply retain their existing semantics; failed or tied order cannot be applied.

| Measurement | Output domain | Quantity |
| --- | --- | --- |
| Count | Retained group domain | Number of matching occurrences |
| Sum | Retained group domain | Total selected weights |
| Rank | Selected item keys | Number of earlier items in its group |
| Prefix sum | Selected item keys | Total weights of earlier items in its group |

For the Young example, add heights `[5,3,2,0]`, a `4 × 5` grid with fields `i,j`,
and a relation `j < read(heights, on=i, key=key, value=value)`. Count by `j` to get
`[3,3,2,1,1]`. On those counts, choose Prefix sum, no group fields, order `j`, item
key `j`, weight `value`. The result is `[0,3,6,8,9]`. Select the diagram's matching
cells and arrange them at `x = i + read(offsets, on=j, key=j, value=value), y = 0`.
These ten original occurrences occupy positions 0 through 9. Undo restores their
prior placement; replay samples the recorded path.

For quotient columns, start from `grid(7,11)` with values `11*i + 7*j` and retain
the relation `value >= 77`. Count by `i`, yielding `[0,1,3,4,6,7,9]`. Prefix sum by
order/item key `i` yields `[0,0,1,4,8,14,21]`. Rank selected cells within each `i`
group by `j`, keyed by their original `key`. Add the keyed rank to the keyed
offset to pack 30 cells. The second prefix has value zero **with one contributor**:
the zero count from column 0. Its own count receipt has no contributors.

An offset receipt identifies earlier measured layers or columns. Inspect one to
follow its own measurement to the original cells; return restores the selected
contributor and camera. A weight can instead contain a keyed read and a transform:
source values `[99,99,99]`, driver `[0,2,5]`, and weight `2*read − 4` produce
prefixes `[0,−4,−4]`. The zero weight reads 2 from its driver. This is valid
accumulation but does not describe packing nonnegative lengths.

## Implementation and compatibility

`Grouping` builds definitions; `indexing.ordered_groups` owns strict order and
key grouping; `tensor.exclusive_sum` normalizes integer inputs before accumulation.
The evaluator scatters ordered sums back to input order. `measurements` reuses
the existing version-1 contributor rosters/ranges; `Inspection` recovers weights
and declared reads from captured inputs. The studio only translates declarations
and presents those receipts.

The new operation is `prefix_sum`, version 1. Existing schema-1 workspaces and
enumerated/rank evidence remain readable. New definitions need the updated
evaluator, and their weight receipts need the updated inspector. Captured history
and motion still restore without executing definitions. There are no new runtime
dependencies, source subclasses, or changes to the outer saved schema.

## Validation

The required suite passes **184 tests**. Eight core prefix tests and three studio
tests cover both constructions, the dense Young reference, ambiguous order/key
failures, exact weights beyond 64 bits, integer budgets, empty/zero domains,
reordering, grouped/composite keys, weight reads, case isolation and saved
inspection/history with evaluation disabled. A 160-item prefix fits a 160-item
budget and stores 160 roster entries and 160 ranges; a predecessor product would
need 25,600 items. This is structural evidence, not a timing benchmark.

The discovery example and expanded Chromium 153 gate pass. Browser tasks use
actual controls for packing, prefix comparison, tied-order recovery, draft
retention, nested evidence/return, signed reads, keyboard access and 320px layout.
Inspected screenshots show usable controls without horizontal overflow; long
phone evidence sheets and physical touch/novice usability remain open.

Lesson 06's seven code cells run in separate fresh IPython processes for default
heights and empty heights. Its dense reference, all 84 motion frames, reversed
paths, saved workspaces and nested receipts pass. The host denies both TCP and
IPC Jupyter kernel sockets, so these are in-process notebook executions rather
than a live JupyterLab session. Source outputs stay cleared. See the
[notebook validation record](../notebooks/VALIDATION.md).

## Development sequence after this increment

1. Reuse an investigation's declarations across cases: saved comparison questions
   and named expressions need explicit context, invalidation and persistence
   contracts before adding shortcuts to their controls.
2. Continue filling lesson vocabulary through shared source and arrangement
   instruments. Measured case families remain a distinct backend evidence gap.
3. Run the proposed novice and physical-device tasks. Compare the current phone
   navigation with a compact sheet while recording lost context, occlusion,
   scrolling and mathematical misunderstandings. Automated transfer checks do
   not substitute for those observations.
