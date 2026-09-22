# A shared interaction grammar, tested from a blank canvas

**Status:** working experimental authoring study. It composes new finite
constructions in the Python core; it does not choose from prerecorded lessons.
It is deliberately outside the installed core API. All eleven lessons remain
the coverage target, not a claim about what this first editor can author.

The design hypothesis is that a person chooses **what they are acting on**, then
**what quantity or relationship they want to change**. Lesson names should never
determine the available tools. A count, a rank, and an ordinary integer source can
all be used as inputs to another construction.

## Run the study

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

**Save** downloads an ordinary Kaleion schema-1 workspace, including definitions,
captured evidence, and pending undo/redo. **Open** restores those captures without
evaluating the graph. Camera, point selection, and unfinished drafts are view state
and are not saved. The current editor admits 60 objects, 2000 occurrences per
evaluated operation, and 40 recorded history steps. The existing 32 MiB capture
import budget still applies; these limits do not promise every combination fits.

## Selection scope comes before the tool

| Selector | Tap or hold target | Contextual actions | What stays unchanged |
| --- | --- | --- | --- |
| Objects | Selected object in the canvas | Define a field, create a relation, measure, arrange, form a product; a relation instead offers measurement and explicit selection | A hold itself changes no definition |
| Occurrences | A captured occurrence, or an entry in its accessible list | Explain its fields, measurement contributors, and direct keyed reads; follow a read to its captured driver | Equal values and coincident positions do not merge identities |
| View | Canvas | Fit; drag to pan, pinch/wheel to zoom | Camera changes do not change mathematical extent or placement |
| Objects, empty canvas | Blank canvas | Add integers or a grid | No implicit source is inferred from a gesture |

A hold opens after 480 ms. Moving beyond the threshold, another pointer, pointer
cancellation, or losing focus cancels the pending hold. The visible **Options**
button and Shift+F10 on the canvas invoke the same action resolver. Commands use
labeled buttons rather than a gesture-only radial menu. Object tabs select a
construction; hold the canvas to act on it. The menu is a sheet in this study;
its eventual position and radial/list presentation can change independently.

Occurrence selection uses captured `(node, occurrence)` references. A nearby hit
is provisional; an explicit list reaches every coincident item. An occurrence
does not automatically mean its row, fiber, or geometric neighborhood. A future
Group selector must first name its grouping rule. A lasso will mean a finite
selection unless the user separately declares and checks a predicate.

## Small controls compose different investigations

Expressions use four editable card types: **Field**, **Number**, **Operation**,
and **Keyed read**. A read asks separately for the source, target key, source key,
and field to read. Numbers travel as decimal strings; JavaScript never calculates
incidence or measurements. Positions and view projections remain floating point.

The examples below describe choices in the editor, not buttons named after a
lesson. **Preview** evaluates a draft. **Apply** retains that exact capture as one
history action. **Cancel** discards it. You can revisit any earlier object.

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

The backend contract test goes further: a `3 × 3 × 3` domain with axes `u,v,m`,
field `t = (v - m*u) % 3`, and relation `t = 0` uses the same commands to count
modular lines and their point coverage. No “Radon tool” is introduced.

### Quotient counts become placement on another source

The independent adapter fixture builds a `7 × 11` grid with
`value = 11*i + 7*j`, relates `value ≥ 77`, and counts retaining `i`. It obtains
`[0,1,3,4,6,7,9]`. A separate seven-point source binds its `i` to the count's `i`
and uses the read value as height. This exercises the same expression cards,
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
| How a person edits a declaration or opens a menu | [studio.js](../examples/studio/web/studio.js), HTML/CSS | An explicit intent record; no arithmetic or Python method calls |
| How intents become existing definitions | [adapter.py](../examples/studio/adapter.py), `build` and `expression` | Source names, fields, keys, group/order choices; no gestures or pixels |
| Which preview can commit | `Studio` in the same adapter | Revision + one-use token → exact retained state; obsolete or failed previews cannot apply |
| How requests reach a session | [server.py](../examples/studio/server.py) | Small loopback JSON endpoints; no lesson construction logic |
| Numerical execution, evidence, identity, and recorded paths | Existing Kaleion modules | Existing contracts in [DESIGN.md](../DESIGN.md); no new evaluator opcode |

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

Failed previews report an error above the **committed** canvas. They do not add
zero results or pretend that the preceding picture is the failed result. Inspection
is a separate read-only request. A receipt can follow an earlier captured driver
even if a current root with the same name has a different placement.

## All lessons are the target: remaining composition coverage

These are gaps in this editor unless explicitly identified as backend gaps.
Most existing mathematics is already expressible in the Python core.

| Lessons | Shared controls exercised here | What is still needed to recreate the full investigation |
| --- | --- | --- |
| 01 · Discovery workbench | Sources, relations, grouped counts, driver placement, inspect/undo | Spiral/Young/sequence constructor sheets, constructor binding, structural-field vocabulary, roll/gather/tile/pad, exact case controls |
| 02–03 · Reciprocal incidences | Finite grid, arithmetic predicates, grouped measurements | Composite Boolean lenses, union/intersection/coverage comparisons, 3D editor/camera, packed placement and explanatory annotations |
| 04 · Measured motion | Quotient fixture, independent driver placement, zero/contributor inspection | Three-component placements and parameter-case editing; keyed comparisons with independent expected domains |
| 05 · Finite Radon | Modular incidence, products, sums and keyed reads | Composite-key read editor, finite-field/residue assumptions, inverse checks, reconstruction comparison |
| 06 · Young layers | Sources can be filtered grids; count/rank/read/placement | Young constructor and conjugation controls; efficient weighted prefix remains a **backend contract gap** |
| 07 · Additive structure | Constructed through browser controls from blank inputs, including ranks | Bin-domain convenience, composite expression readability, equal-sum quadruples and energy narration |
| 08 · Ehrhart counts | Finite sources, predicates, count and measurement-driven positions | Exact case-family editor; measured-family evidence remains a **backend contract gap** |
| 09 · Norm fibers | Groups, explicit order, source reads, placement | Arithmetic-domain/basis recipes, lookup tables, modular power and trig cards; orbit/case controls |
| 10 · Hermitian partitions | Product/read/group/rank mechanisms | Projective representative recipes, explicit unique-coverage adoption and witnesses, canonical-code versus slot selection |
| 11 · Cyclic code/plane | Integer arithmetic, incidence, measurement and explanations | Polynomial/binary-field recipes, coordinate dictionaries, distinct comparison contracts, coordinated replay across charts |

No lesson-specific menu, source subclass, or evaluator primitive was necessary
for the delivered constructions. That does not show that the complete vocabulary
has been found. The standard for a new primitive remains an actual construction
whose contract cannot be expressed clearly or efficiently with existing ones.

## Limits and next experiment

The study has one focused canvas and a rail of objects, not a free multi-view art
workspace. Geometry editing is 2D; 3D imported placements receive an explicitly
labeled XY projection. Values remain exact; table projections and geometry do not.
Huge labels may be shortened on the canvas but stay complete in the inspector.
The current occurrence picker and whole-object scope cannot yet express a fiber
selection, a lasso, or a viewport-independent spatial query.

Count and Sum support multiple retained field keys. Rank's sheet currently offers
one member-order field and one item key. Keyed-read cards offer an expression for
the target key and a single source key/read field; the core supports more. Nested
cards become long even for modest formulas. The declaration drawer shows the
structured intent, not yet the readable Euclid-like mathematical notation we want.
No user trial or physical tablet test has established novice usability.

**Next useful experiment:** add a declared Group selector and a compact readable
expression surface. Recreate both sum fibers and modular-line fibers with the
same selection control, including a zero group and tied order. Then add coverage
witnesses from the Hermitian lesson: removing an owner must expose missing groups,
not silently change the universe. This should establish the next UI contract
before adding a new lesson preset or broadening the evaluator vocabulary.

## Validation and reproduction

```sh
python3 -m unittest discover -s tests -p test_studio.py -v
python3 -m unittest discover -s tests -v
python3 examples/discovery.py --out build/example-output
```

The nine adapter tests use independent finite enumerations for quotient counts,
modular incidence, additive multiplicities, and energy. They cover empty groups,
signed cancelling weights, integers beyond 64 bits, ambiguous keys, failed/stale
previews, exact capture commitment, and saved undo/redo/inspection with graph
execution disabled. Finite fixtures are not universal proofs.
The complete required suite passes **137 tests**, and the discovery example
retains its expected counts, driver results, sieve, and history exports.

With a separately installed Node/Playwright and Chromium:

```sh
node docs/studies/check-construction-studio.cjs
```

The optional gate starts its own fresh Python host. `KALEION_PYTHON` can select
another environment's interpreter. `KALEION_PLAYWRIGHT_MODULE` and
`KALEION_BROWSER_OPTIONS` can select an existing browser installation, as in the
[earlier touch study](TOUCH_WORKSPACE.md). Neither is a project dependency.
Screenshots and the report go to ignored `build/studio-check/`.

On September 22, 2026, Chromium 153 passed the two constructions through actual
controls, preview cancellation/failure, keyed rank placement and contributor
inspection, zero groups, undo/redo, save/open, exact-integer transport, hold/drag/
cancel/multi-touch, keyboard/context menus, same-origin rejection, and layouts
at 1250/736/360/320 pixels. Touch was emulated; physical Safari/tablet testing
remains open. The browser host and browser run in one local process tree because
this execution environment isolates loopback across separate shell calls.
No notebook source or core API changes are included, and no video export is added.
