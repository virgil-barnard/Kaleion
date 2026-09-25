# A shared interaction grammar, tested from a blank canvas

**Current interface:** see [One canvas, fewer decisions](CONTINUOUS_CANVAS.md).
The continuous-canvas refactor replaces Focus and the earlier menu/tool layout.
The contracts and dated implementation record below remain useful; use the new
guide for current control names and the current browser gate.

[Division in motion](DIVISION_MOTION.md) now transfers the same interface to the
two Icarus papers. Arrange / move chooses coordinates, displacement or cyclic
contents; Combine → Drive a transformation supplies a keyed read to that editor.
Arithmetic notation is shared with named fields and weights. Four loadable
investigations include from-blank construction, factor composition, explicit
Euclidean extensions and non-coprime counterexamples.
Two further investigations now exercise Reindex / extend: repeat, ordered address
lists with optional bijection, and explicit joins. Scalar editing also assigns
contents through keyed reads; copied occurrences have inspectable source links.


**Status:** working experimental authoring study. It composes new finite
constructions in the Python core; it does not choose from prerecorded lessons.
It is deliberately outside the installed core API. The latest
[weighted-evidence investigation](WEIGHTED_EVIDENCE.md) constructs a finite Radon
reconstruction through the shared controls and follows its nested measurements. All eleven lessons remain
the coverage target, not a claim about what this first editor can author.

[Parameter cases](PARAMETER_CASES.md) now declare exact integers once, use them
in formulas and grid extents, and explicitly preview/apply a changed assumption.
Case restoration and replay of a captured construction remain separate controls.
[Keyed comparison](KEYED_COMPARISON.md) now checks selected integer fields over
an independent expected domain. Residuals and missing/outside keys lead into
the same evidence views; zero and absence remain distinct.
[Ordered accumulation](ORDERED_PREFIX.md) now adds **Prefix sum · before each item**
to Measure. Explicit groups, order, unique item keys and weights derive offsets
from measured sizes without constructing every predecessor pair.

The [spatial workspace](SPATIAL_WORKSPACE.md) now opens with all named objects
visible together. Move their name handles, inspect definition connections, or
drag a source name to a destination in Connections to propose a product or keyed
placement. Focus preserves the existing single-object tools and captured evidence.

The [relation workbench](RELATION_WORKBENCH.md) adds canvas-side **Lens…** pattern
starters, **Reuse lens…** with explicit field mappings and captured constants, and
**Total…** over selected logical axes or retained measurement keys. Exact previews
appear in the scene; applied results retain contributor inspection and ordinary
save/history behavior. The detailed formula and Measure editors remain available.

The [shared scene](SHARED_SCENE.md) now replaces independent preview scales with
one camera, local axes and view offsets. Cells/Points, explicit logical/placement
charts, 3D orbit and slices consume captures. A Sequence sheet lowers finite
length/start/step to the existing builder. Scene choices can now be saved.

[Construction inspection](CONSTRUCTION_INSPECTION.md) now opens on selection.
Read the constructor, expressions, ordered inputs and parameter case; follow an
input to its actual definition and return with selection and camera restored.
Earlier and local inputs retain their own captured scope. View captured result
connects the declaration to the existing occurrence evidence.

The design hypothesis is that a person chooses **what they are acting on**, then
**what quantity or relationship they want to change**. Lesson names should never
determine the available tools. A count, a rank, and an ordinary integer source can
all be used as inputs to another construction.

The [UI design study](UI_DESIGN_STUDY.md) connects this hypothesis to HCI research,
audits the current controls, and defines cross-lesson and human-observation tasks.
Its first improvement preserves an unfinished idea while its author inspects
something else.

[Linked evidence views](LINKED_EVIDENCE_VIEWS.md) now keep coverage domains,
measurements, and actual driver versions visible in pairs. They use the same
capture descriptions and scoped references across investigations.

## Run the study

For an example to inspect before building, use the five
[saved canvases and first-five-minutes guide](../examples/canvases/README.md).
They open through **Open**. Choose Workspace for the overview or Focus for the
selected object's occurrences and construction tools.

From the repository root, use the existing environment:

```sh
source .venv/bin/activate
python3 -m examples.studio
```

Open **http://127.0.0.1:8765** on that computer. Stop the host with Ctrl+C.
Use `--port 8766` if necessary. First-time setup is in the
[README](../README.md#run-it). NumPy is the only runtime dependency; this study
does not require Jupyter, Node, Plotly, a CDN, or a web framework.

This is a local development host bound to loopback, not a deployed service or
a single-file offline viewer. It has one workspace shared by its local tabs.
Opening it in two tabs can produce a stale revision; refresh the older tab before
editing. Host and origin checks refuse cross-origin edits.

**Save → Canvas and view** stores the captured workspace and the shared scene's
offsets, charts, slices, selection and camera in a versioned studio document.
**Save → Mathematics only** exports the ordinary workspace for Python (schema 2 when it contains tuple-only domains).
**Open** accepts both without evaluating the graph. Evidence navigation,
group selection and unfinished drafts remain temporary view state.
The current editor admits 60 objects, 2000 occurrences per
evaluated operation, and 40 recorded history steps. The existing 32 MiB capture
import budget still applies; these limits do not promise every combination fits.

## Selection scope comes before the tool

Workspace name handles select objects; cells and points inspect occurrences.
**Move objects** changes view offsets; **Connections** shows named input/read
paths and proposes composition.
**Combine…** offers source/destination selectors as a tap and keyboard alternative.
Double-click an object, press Enter on it, or choose **Focus** for the selectors
below. Arrow keys move a focused object's view; camera buttons pan/zoom the
overview. Touch hold opens object options, and releasing that hold does not
activate a tool underneath the finger.

| Selector | Tap or hold target | Contextual actions | What stays unchanged |
| --- | --- | --- | --- |
| Objects | Selected object in the canvas | Define a field, create a relation, measure, check coverage, compare integer fields, arrange, form a product; a relation offers measurement, coverage, and explicit selection | A hold itself changes no definition |
| Occurrences | A captured occurrence, or an entry in its accessible list | Explain its fields, measurement contributors, and direct keyed reads; follow a read to its captured driver | Equal values and coincident positions do not merge identities |
| Groups | A group chosen by declared field keys, from a point or the group list | Choose group keys, create a group lens, measure all groups, check coverage | Browsing changes neither the universe nor history; group membership does not specify member order |
| View | Canvas | Fit/zoom/directional-pan buttons; drag to pan, pinch/wheel to zoom | Camera changes do not change mathematical extent or placement |
| Objects, empty canvas | Blank canvas | Add integers, a finite sequence or a grid | No implicit source is inferred from a gesture |

A hold opens after 480 ms. Moving beyond the threshold, another pointer, pointer
cancellation, or losing focus cancels the pending hold. The visible **Options**
button and Shift+F10 on the canvas invoke the same action resolver. Commands use
labeled buttons rather than a gesture-only radial menu. Object tabs select a
construction; hold the canvas to act on it. The menu is a sheet in this study;
its eventual position and radial/list presentation can change independently.

Main and paired views share camera buttons for tap and keyboard use. On narrow
screens, **Canvas** and **Construction and evidence** links move focus and scroll to
the relevant area. Both areas still require vertical space; this is a navigation
improvement pending the [real-device layout trial](UI_DESIGN_STUDY.md).

Occurrence selection uses captured `(node, occurrence)` references. A nearby hit
is provisional; an explicit list reaches every coincident item. An occurrence
does not automatically mean its row, fiber, or geometric neighborhood. The
Group selector first names its grouping fields. A future lasso will mean a finite
selection unless the user separately declares and checks a predicate.

### Select a group without measuring it

Choose **Groups**, add one or more fields, and choose **Browse groups**. The group
list and canvas use the same captured membership. Tap a point to choose its group;
use the list for coincident points or a group with no members. Key chips are also
used for retained measurement keys and Rank's ordered list of fields.

The selector reports both the candidate population and the incident subset: a
group can have **0 incident occurrences out of 3 candidates**. Outlined candidates
remain visible even when none satisfy the relation. A plain source has every
member incident. This is a read-only query over the current capture, not a new
measurement arrangement or a graph evaluation.

The domain follows the existing reduction contract. Direct rectangular axis
fields retain the declared Cartesian domain, including empty fibers; other fields
use observed keys. No fields means one whole-domain group, including on empty
input. Listing order is not mathematical member order. An absent observed key
does not become a zero group. Queries are bounded to 2000 groups independently of
the occurrence budget, including when a zero-length axis leaves no candidates.

**Create a group lens** explicitly adds a relation for the chosen key, intersected
with any existing incidence. It preserves the original universe. **Measure all
groups** retains the chosen grouping fields over the original object; highlighting
one fiber does not silently restrict the measurement to it. To measure that
fiber's incidence, first create its lens and then measure the lens. To change the
universe itself, use **Keep matching occurrences** as a separate action.

Selection is scoped to the capture, chosen fields, and group ordinal in that
query. Applying a construction, undoing, or reopening clears it. The adapter
recovers native key values from the capture; it never parses a displayed key or
guesses membership from pixels. A derived lens saves as an ordinary construction.

## Small controls compose different investigations

Expressions appear as compact, parenthesized formulas. Tap a field, number,
operator, or keyed read to open one inspector for that part. **Edit whole
expression** selects the root. **Done** closes the inspector; **Undo expression
edit** reverses draft edits separately from workspace undo. For example,
`(((j − i) mod 3) = 0)` stays visible while its modulus is edited.

The six expression kinds are **Field**, **Number**, **Parameter**, **Operation**,
**Key tuple**, and **Keyed read**.
Replacing a part with an operation wraps its current value as the first operand.
“Keep left/right operand” removes an operation without rebuilding the retained
part. A read labels its source and target keys separately; its source key and
value expressions offer the driver's fields, while its target key offers the
receiving object's fields. Changing a driver preserves the existing expressions
and marks unavailable fields for correction. Numbers travel as decimal strings;
the editor manipulates syntax and never calculates incidence or measurements.
Positions and view projections remain floating point.

The examples below describe choices in the editor, not buttons named after a
lesson. **Preview** evaluates a draft. **Apply** retains that exact capture as one
history action. **Cancel** discards it. You can revisit any earlier object.

### Inspect without losing an unfinished idea

Selecting another object or selector mode parks the current draft. Inspect a
group or follow an occurrence's contributors, then choose **Resume draft**. Its
original target, name, fields, grouping choices, and local expression undo return.
Parking invalidates its preview; use **Preview** again before applying. Feedback
beside the actions reports editing, checking, ready, or failed, and changes as
soon as an input changes.

There is one draft per tab. While it exists, new constructions, workspace
undo/redo, and Open are unavailable; the draft tray explains how to resume or
discard it. Save still exports applied work. Reloading loses the draft. This
first design supports browsing a dependency mid-edit, but not constructing a
new dependency without first finishing or discarding the draft.

Enter on a formula token focuses its editor; **Done** or Escape returns focus
to that token. Escape outside the formula inspector parks the construction.
**Cancel** or **Discard draft** explicitly removes it. Removing a group-key chip
focuses the next chip or the field picker. These keyboard behaviors supplement
the visible touch controls.

### Equal sums and measured stacks

| Step | Control and choices | Observation |
| --- | --- | --- |
| 1 | Add integers `A = [0,1,3]`, `B = [0,2]` | Each entry is an occurrence; repeated labels would remain separate |
| 2 | Select A; Form a product. Roles `left` from A, `right` from B; copy `value` from both. Name it Pairs | Six pairs with fields `left_value`, `right_value`; role indices are current source slots |
| 3 | Define a field named `total = left_value + right_value`; name the result Sums | Totals are `[0,2,1,3,3,5]` |
| 4 | Arrange Sums with `x = total`, `y = 0` | Two occurrences coincide at 3. Use “Label points with” to show total or key |
| 5 | Measure Sums: Rank, retain `total`, member order `index`, unique item key `key`. Name it Ranks | One strict predecessor at total 3; the other ranks are zero |
| 6 | Return to Sums; Arrange `x = total`, `y = Keyed read` from Ranks, matching target `key` to source `key`, reading `value` | The same six occurrences separate; one moves to height 1 |
| 7 | Select Occurrences; choose the point with index 4; Explain → Follow keyed read | The rank receipt identifies its predecessor. Undo restores the captured placement |

Now choose Groups, retain `total`, and browse `total = 3`: two occurrences are
selected by the same declared key even after placement separates them. Create a
group lens to retain their incidence over all six candidates. For an order
counterexample, use **Measure all groups → Rank**, remove `index`, and add `value`:
the equal values tie, so Preview fails without adding history. Add `key` as the
second order field to declare a strict lexicographic order. Group listing and
storage order supply no hidden tie breaker.

For representation counts, measure Sums with Count retaining `total`. These are
the **observed sum groups**. To include empty sums, explicitly construct bins,
form pairs × bins, relate each total to its bin, and count retaining the bin role.
The tests include an empty factor whose three declared bins retain three zeros.
Selecting the empty incidence first removes that declared rectangular universe;
the later observed groups are empty. That is a useful counterexample, not a
reason for the renderer to invent zero measurements.

### Modular incidence with the same tools

Add a `3 × 3` grid with axes `i,j` and constant value 1. Create a relation
`(j - i) % 3 = 0`. Measure with Count retaining `i`. The three row counts are
`[1,1,1]`. Change the retained key to `j` in a new measurement to view the other
direction. A relation `value = 0` on this grid instead produces three retained
zero counts; an occurrence explanation has no contributors.

In Groups, choose `i` and browse: each diagonal group has one incident member
among three candidates. The same selector also distinguishes missing/overlapping
assignment candidates. On the original grid define `(i > 0) and (j < i)` and
group by `i`: the counts are `[0,1,2]`, with three candidates per group. The zero
group remains selectable, and its group lens retains all nine source occurrences
with no hits. **Check coverage** now tests this fixture against independently
declared keys and preserves the missing obligation after selecting the survivors.
Its [walkthrough](COVERAGE_INSTRUMENT.md) continues to a valid assignment and
measurement-driven motion; the complete Hermitian source-constructor UI remains open.

The backend contract test goes further: a `3 × 3 × 3` domain with axes `u,v,m`,
field `t = (v - m*u) % 3`, and relation `t = 0` uses the same commands to count
modular lines and their point coverage. No “Radon tool” is introduced.

### Check a relation before using it as an assignment

Choose **Check coverage**, declare source group keys, select an expected domain,
and choose equally many expected key fields in matching order. The expected keys
must identify its occurrences uniquely. The check requires one incident match
per expected key and no incident keys outside that domain. Browsing and checking
use captures only; neither creates an object or changes history.

Filter to missing, multiple, or outside keys. Show a candidate group or inspect
an expected occurrence/match, then return with **Back to coverage**. An absent
source key has no source point to highlight, but its expected occurrence remains
inspectable. Another draft can stay parked during these queries.

**Use unique matches…** is available after a passing check when no other draft
is active. Choose the supplied integer expression and a fresh field name.
Preview/Apply adds that field to a derived copy of the expected items, preserving
their labels, keys, identities, and placement. Graph requirements check the
claim again and remain active during future evaluation. The value's keyed-read
receipt leads to its weighted reduction and contributors. Even an assigned zero
has one contributor; it is not a missing assignment.

### Quotient counts become placement on another source

The independent adapter fixture builds a `7 × 11` grid with
`value = 11*i + 7*j`, relates `value ≥ 77`, and counts retaining `i`. It obtains
`[0,1,3,4,6,7,9]`. A separate seven-point source binds its `i` to the count's `i`
and uses the read value as height. This exercises the same structured expressions,
group choices, placement operation, and explanation route as the other cases.
It is checked programmatically through semantic commands; the browser gate
constructs the additive and modular examples through controls.

## The boundary between a gesture and mathematics

For example, an Arrange sheet produces a language-neutral intent:

```json
{
  "action": "place",
  "name": "Sums",
  "args": {
    "source": "Sums",
    "coordinates": [
      {"field": "total"},
      {"read": {
        "object": "Ranks", "on": {"field": "key"},
        "key": {"field": "key"}, "value": {"field": "value"}
      }}
    ]
  }
}
```

The browser never invokes Python methods or evaluates Python text. The adapter
lowers this record to existing builders. Expression operations are allowlisted
and compile into existing symbolic expressions, so their exact arithmetic and
budget checks remain in Kaleion. This is an experimental transport vocabulary,
not a stable public language or a replacement for the operation graph.

| Changeable decision | Owner | Stable boundary for this experiment |
| --- | --- | --- |
| Which actions apply to a selection scope | [context.js](../examples/studio/web/context.js) | Mode + target kind/status + captured selection → action names; no lesson IDs |
| How an unfinished editor survives navigation | [drafts.js](../examples/studio/web/drafts.js) | One tab-local draft, original context, park/resume/discard; no evaluation, network, or saved-schema policy |
| How formula parts are selected and edited | [expressions.js](../examples/studio/web/expressions.js) | Structured expression in/out; no mathematical evaluation or workspace history |
| How a person chooses field keys and their order | [groups.js](../examples/studio/web/groups.js) | Ordered field names; no membership queries or numerical grouping |
| How captured groups expose candidates and incidence | [groups.py](../examples/studio/groups.py) | Captured data + field keys → scoped members; no graph evaluation or rendering |
| How expected keys expose coverage failures | [coverage.py](../examples/studio/coverage.py) | Captured alignment and witnesses; a separate recipe builds ordinary live guards and assigned fields |
| How to choose and inspect a coverage claim | [coverage.js](../examples/studio/web/coverage.js) | Shared key selectors and semantic callbacks; no arithmetic or history |
| How gestures, editors, and the canvas work together | [studio.js](../examples/studio/web/studio.js), HTML/CSS | An explicit intent record and captured selection; no arithmetic or Python method calls |
| How intents become existing definitions | [adapter.py](../examples/studio/adapter.py), `build` and `expression` | Source names, fields, keys, group/order choices; no gestures or pixels |
| Which preview can commit | `Studio` in the same adapter | Revision + one-use token → exact retained state; obsolete or failed previews cannot apply |
| How requests reach a session | [server.py](../examples/studio/server.py) | Small loopback JSON endpoints; no lesson construction logic |
| Numerical execution, evidence, identity, and recorded paths | Existing Kaleion modules | Existing contracts in [DESIGN.md](../DESIGN.md); no new evaluator opcode |

The grouping query and reducer share `indexing.retained_axes_shape` and
`indexing.group_keys`. The axis-domain decision has one owner; the browser does
not duplicate it. This is a small internal extraction, not a new grouping
primitive. Existing Python declarations and saved workspaces need no migration;
the experimental web client now also sends `group_lens` intents referencing a
current capture.

Apply uses the existing captured-state restoration boundary. It does not execute
the preview again. Undo/redo use retained states; sampled linear motion comes
from `Transition`, including its recorded correspondence. Twenty-five samples
are presentation data only. Floating reverse samples agree within rounding;
the restored mathematical endpoints and identities are exact.

Every newly derived object retains immutable input definitions. **Arrange** edits
one named object's placement; earlier derived objects keep their earlier inputs.
This is not a reactive source editor that silently rewrites downstream definitions.
That larger edit contract needs revisioned dependencies, explicit failure handling,
and atomic capture decisions before it becomes a UI promise.

Failed previews report an error beside Preview/Apply and above the **committed**
canvas. They do not add zero results or pretend that the preceding picture is
the failed result. Inspection is a separate read-only request. A receipt can
follow an earlier captured driver even if a current root with the same name has
a different placement.

## All lessons are the target: remaining composition coverage

These are gaps in this editor unless explicitly identified as backend gaps.
Most existing mathematics is already expressible in the Python core.

| Lessons | Shared controls exercised here | What is still needed to recreate the full investigation |
| --- | --- | --- |
| 01 · Discovery workbench | Integer/sequence/grid sources, relations, grouped counts, driver placement/displacement, rectangular cyclic shifts, axis/flat gather, repeat, explicit joins/padding, inspect/undo, exact parameter cases | Spiral/Young constructor sheets, structural-field vocabulary, independent per-fiber maps |
| 02–03 · Reciprocal incidences | Finite grid, arithmetic predicates, grouped measurements, shared 3D capture camera and view slices | Composite Boolean lens authoring, union/intersection/coverage comparisons, 3D placement editing, packed placement and explanatory annotations |
| 04 · Measured motion | Quotient fixture, independent driver placement, zero/contributor inspection, shared integer case editor; generic keyed comparison available | Three-component placements and complete notebook composition through controls |
| 05 · Finite Radon | Parameterized prime/composite reconstruction through products, sums, ordered tuple reads, remainder fields, driven placement, nested evidence and exact keyed comparison | Explicit arithmetic assumptions and complete notebook parity |
| 06 · Young layers | Filtered grids, layer counts, ordered weighted offsets, keyed strip placement, nested evidence and undo | Young constructor and conjugation controls, 3D editing and complete notebook composition |
| 07 · Additive structure | Constructed from blank inputs, including group selection, strict ranks, and compact expressions | Bin-domain convenience, equal-sum quadruples and energy narration |
| 08 · Ehrhart counts | Parameterized triangle growth, retained zero row counts, and comparison with an independent formula | Reusable measured case families and their evidence remain a **backend contract gap**; finite differences and full lesson composition |
| 09 · Norm fibers | Groups, explicit order, source reads, placement | Arithmetic-domain/basis recipes, lookup tables, modular power and trig expressions; orbit/case controls |
| 10 · Hermitian partitions | Product/read/group/rank and guarded coverage; adapter tested on a restricted seven-block family with canonical keys | Projective/field constructor controls, full support beyond the study budget, and complete lesson composition |
| 11 · Cyclic code/plane | Integer arithmetic, incidence, measurement and explanations | Polynomial/binary-field recipes, coordinate dictionaries, distinct comparison contracts, coordinated replay across charts |

No lesson-specific menu or source subclass was necessary for the delivered
constructions. Most controls compose existing operations. The new `prefix_sum`
operation addresses a concrete efficiency gap: layer offsets previously required
a dense predecessor product. It shares strict ordering and compact evidence with
Rank. This is the standard for adding an operation, not a claim that the complete
vocabulary has been found.

## Limits and next experiment

The study has one construction canvas, a rail of objects, and a temporary pair
of linked evidence views. It is not yet a free multi-view art workspace. Geometry editing is 2D; 3D imported placements receive an explicitly
labeled XY projection. Values remain exact; table projections and geometry do not.
Huge labels may be shortened on the canvas but stay complete in the inspector.
Group selection uses named fields, including composite keys. To group by an
expression, define a field first. Lasso and viewport-independent spatial queries
remain future work.

Count and Sum support multiple retained field keys. Rank and Prefix sum offer
multiple member-order fields in chosen order and one unique item key. Prefix sum
also uses the shared weight editor: the current item is excluded and each group's
first result is zero. Zero/negative weights retain their contributors. Keyed reads accept structured
expressions in target-key, source-key, and value contexts. **Key tuple** edits
2–8 ordered scalar components for composite reads. Long formulas wrap rather than introduce a new row of
controls at every nesting level, but named subexpressions and reusable formulas
are still absent. The declaration drawer retains the exact transport record.
No user trial or physical tablet test has established novice usability.

The [paired-view experiment](LINKED_EVIDENCE_VIEWS.md) now keeps an expected item
visible with no candidate beside it, and a quotient measurement visible with its
source and contributors. Captured keyed reads can refer to earlier versions.
The [Radon transfer](WEIGHTED_EVIDENCE.md) now adds weight-read and copied-field
navigation with a return path, plus composite key editing. [Exact parameter cases](PARAMETER_CASES.md)
now change the modulus and grow a lattice arrangement. Replay samples captured
construction edits without requests. [Keyed comparison](KEYED_COMPARISON.md) now
compares recovered/source fields and lattice counts/formulas, then follows their
witnesses into those views. **Next useful experiment:** observe whether people can
declare a domain, interpret a missing zero, and return from a discrepancy to their
question. Named formulas, measured families, and a saved-case browser remain
separate work; the updated [UI audit](UI_DESIGN_STUDY.md) records priorities.

## Validation and reproduction

```sh
python3 -m unittest discover -s tests -p test_studio.py -v
python3 -m unittest discover -s tests -p test_studio_groups.py -v
python3 -m unittest discover -s tests -p test_studio_coverage.py -v
python3 -m unittest discover -s tests -p test_studio_views.py -v
python3 -m unittest discover -s tests -p test_studio_weighted.py -v
python3 -m unittest discover -s tests -p test_studio_cases.py -v
python3 -m unittest discover -s tests -p test_studio_comparison.py -v
python3 -m unittest discover -s tests -p test_prefix_sums.py -v
python3 -m unittest discover -s tests -p test_studio_prefix.py -v
python3 -m unittest discover -s tests -p test_studio_construction.py -v
python3 -m unittest discover -s tests -v
python3 examples/discovery.py --out build/example-output
```

The nine adapter tests use independent finite enumerations for quotient counts,
modular incidence, additive multiplicities, and energy. They cover empty groups,
signed cancelling weights, integers beyond 64 bits, ambiguous keys, failed/stale
previews, exact capture commitment, and saved undo/redo/inspection with graph
execution disabled. Seven additional group tests cover additive/modular fibers,
empty declared versus observed domains, zero incidence, composite and native
typed keys, ties, stale captures, query budgets, scoped incidence composition,
and undo/reopen. Group browsing succeeds with graph execution disabled and
leaves workspace JSON unchanged. Finite fixtures are not universal proofs.
Seven coverage tests add independent expected domains, zero/absent/multiple/outside
witnesses, live assignment guards, exact/composite keys, expected identity,
keyed reuse, and the Hermitian missing-polar case. Inspection and saved assignment
receipts work with graph execution disabled.
The complete required suite passes **219 tests**, and the discovery example
retains its expected counts, driver results, sieve, and history exports.

With a separately installed Node/Playwright and Chromium:

```sh
node docs/studies/check-continuous-canvas.cjs
node docs/studies/check-scene-model.mjs
```

The optional gate starts its own fresh Python host. `KALEION_PYTHON` can select
another environment's interpreter. `KALEION_PLAYWRIGHT_MODULE` and
`KALEION_BROWSER_OPTIONS` can select an existing browser installation, as in the
[earlier touch study](TOUCH_WORKSPACE.md). Neither is a project dependency.
Screenshots and the report go to ignored `build/continuous-canvas-check/`.

On September 22, 2026, Chromium 153 passed the two constructions through actual
controls, preview cancellation/failure, keyed rank placement and contributor
inspection, sum/modular/zero group selection, tied-order rejection and an explicit
tie breaker, formula-part editing and local undo, undo/redo, save/open,
exact-integer transport, hold/drag/cancel/multi-touch, keyboard/context menus,
same-origin rejection, and layouts at 1250/736/360/320 pixels. The 320-pixel check
also edits a compound formula and selects a group by a canvas tap. Touch was
emulated. The expanded gate parks relation and measurement drafts, inspects a
different object, resumes the original declaration and local undo, and verifies
that browsing leaves saved data unchanged. It checks local failed/ready/edited
status, keyboard focus recovery, and the first object click after input blur.
Physical Safari/tablet and screen-reader testing
remains open. The browser host and browser run in one local process tree because
this execution environment isolates loopback across separate shell calls.
The comparison helper now lives in the installed package with compatible notebook
reexports; notebook cell sources and video exports are unchanged.

The coverage extension passes actual controls for the balanced `[0,1,2]` failure,
an absent group after selection, per-match receipts and return focus, a parked
assignment draft, a zero-valued owner, keyed placement with undo, an additive
transfer with outside matches, and save/reopen. Its choices/witnesses fit the
320-pixel layout without horizontal overflow; vertical scrolling remains necessary.

Five view-query tests and the same browser gate now cover linked coverage and
quotient evidence, absent candidates, zero contributors, exact weights, earlier
driver versions, independent cameras, pan cancellation, keyboard inspection, and
read-only history. See the [linked-view guide](LINKED_EVIDENCE_VIEWS.md) for the
construction, module decisions, validation evidence, and remaining layout limits.

Four weighted-evidence contracts now check prime Radon cases, a composite-modulus
counterexample, exact ordered keys, transformed signed weights, and a reopened
measurement/weight/source-field inspection chain without graph execution. The
expanded Chromium gate constructs the size-three reconstruction through controls,
checks division remainders, drives reversible placement, follows nested evidence,
restores camera/selection on return, and transfers to signed weights. Ordered
key failure, parked tuple edits, keyboard navigation, and phone layout also pass.

Six parameter-case contracts add one graph evaluated at prime/composite moduli,
lattice growth, locally bound case isolation, failed dependent branches, exact
large parameters, preview token replacement, and saved case/evidence restoration
with graph execution disabled. The browser gate also changes these parameters
through controls, checks wrong recovery despite exact division, parks/resumes case
drafts, and verifies replay makes no requests or saved-state changes. Reduced-motion
preference, explicit playback, keyboard controls, and 320-pixel layout are exercised.
The [case guide](PARAMETER_CASES.md) records the recipes, boundaries, and open limits.

Seven comparison tests add selected integer fields, independent domains, missing
keys on both sides, outside keys, exact residuals, reordered drivers, ambiguity,
empty inputs, and read-only restored evidence. The expanded browser gate checks
prime/composite Radon and lattice equality, retains declarations across cases,
returns through nested receipts to the same witness/cameras, preserves a parked
draft, and checks phone jump links and tap/keyboard camera controls. Reports
distinguish comparison values from occurrence values. See the
[comparison guide](KEYED_COMPARISON.md) for reproduction and remaining boundaries.

Eight core prefix tests and three studio contracts add exact exclusive offsets,
group/order/key separation, signed/zero weights, compact evidence, local cases,
failed-branch isolation, and restored inspection/history. The browser gate creates
Young layers and quotient-column packings through the same Measure/Arrange
controls, recovers from tied order, parks a prefix draft, follows offsets through
layer counts to cells, and returns to the same selected contributor and camera.
It also compares offsets with an independent finite list and follows a transformed
weight read. Desktop and 320px screenshots were inspected. The
[ordered-prefix brief](ORDERED_PREFIX.md) records the next development sequence.
