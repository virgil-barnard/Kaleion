# A touch workspace for composing investigations

**Status:** interface hypothesis, with a bounded working interaction study and a
new [blank-canvas construction studio](CONSTRUCTION_STUDIO.md). The studio adds
real authoring through a separate semantic-command adapter and context-sensitive
hold menus. Its guide states the implemented subset and all-lesson coverage gaps.
The shared `Product` recipe is implemented in lessons 05 and 07. The study uses
real captured Kaleion results and paths; it is not a general editor or a browser
implementation of the evaluator. Its two source choices are deliberately finite.
See the [cross-lesson audit](EXPLORATION_WORKFLOW.md) for the mathematical basis.
The [UI design study](UI_DESIGN_STUDY.md) adds research, an audit rubric, and a
formative testing protocol. Draft retention, coverage, linked evidence, exact
parameter cases, and [keyed comparison](KEYED_COMPARISON.md) now compose in the
studio. The older two-source demonstration described below remains a bounded
gesture study. Human touch trials remain to be conducted.

### Progress against this proposal · September 23, 2026

| Proposed experience | Current studio evidence | Still open |
| --- | --- | --- |
| Compose tools on objects | Contextual relations, measurements including ordered prefixes, keyed placement and comparison; one recoverable draft | Full lesson vocabulary, reusable recipes, novice transfer |
| Inspect how a result was made | Paired captured views; contributor, weight and source navigation; return restores cameras/selection | Free pinning and a usable layout for many simultaneous views |
| Change assumptions | Exact integer cases preview/apply a new evaluation; replay uses recorded motion separately | Saved-case browsing and measured case families |
| Declare a comparison | Selected integer fields, ordered keys and an independent expected domain; missing-both and outside witnesses | Distinct support, totals and structural-correspondence contracts |
| Reach tools without a gesture requirement | Visible menus, occurrence lists, shared Fit/zoom/pan buttons; phone links move between canvas and controls | Physical-device reach, screen-reader review, simultaneous picture/control visibility |

The [updated UI study](UI_DESIGN_STUDY.md#4-initial-audit-and-current-disposition)
records which findings these changes address. Deterministic browser transfer
between Radon and lattice comparisons does not establish human discovery or
comfortable touch use.

## The experience to aim for

Let a person compose a scene: put down a source, shape it, move a lens over it,
pull out a measurement, and use that new object to reshape something else. Keep
the picture large and the response immediate. Each action should also leave a
readable declaration that can be inspected, adjusted, saved, and undone.

The canvas holds **objects**, not a compulsory sequence of lesson steps. A count
profile can become a driver, another source for a relation, or something to compare.
Several views can show one construction. A dependency outline is available in
Explain; it need not occupy the working canvas or become the primary interface.

The artistic quality comes from easy variation, continuity of motion, visible
consequences, and reversible composition. Mathematical meaning still requires
choices: which occurrences, which relation, which keys, and which quantity changes.
Put those choices close to the object receiving the action, using progressive
disclosure rather than a single panel of all possible controls.

## The first control vocabulary

These are editor controls over existing definitions, not new mathematical classes.
Names in the first column are proposed user-facing labels.

| Control | Small initial interaction | Mathematical declaration and advanced choices |
| --- | --- | --- |
| **Add** | Choose Sequence, Grid, Spiral, Young diagram, or an existing object | Source values and finite extent. Choose logical axes separately from 1D/2D/3D placement. Arithmetic convention stays visible. |
| **Pair** | Select two sources; name their roles, then choose “Every pair” | `Product(left=A, right=B)` declares occurrence tuples. Show factor sizes and total product size before applying. It is different from matching keys or combining collections. |
| **Fields** | Tap named value/index/attribute chips to compose an expression | `annotate` or `with_values`. Chips carry their source context; `left.value`, a retained key, and a displayed x coordinate are different inputs. |
| **Relate** | Choose field, comparison, argument; place the resulting lens on an object | `where(predicate)` keeps its universe. Dragging a handle changes an explicit parameter. Compose AND/OR/complement within that universe. |
| **Measure** | Choose Count, Sum, Presence, Rank, or Prefix sum; pull the result into the scene | Declare groups and expected coverage. Sum asks for a weight; Rank asks for strict member order and item key; Prefix sum combines those choices. Distinguish retained zero groups from an item's empty prefix. |
| **Arrange** | Assign fields or measurements to x/y/z; preview a built-in layout | `arrange`/`place` changes positions. `move` adds displacements. Values, occurrence identity, and arithmetic remain separate. |
| **Use measurement** | Select a measurement, then a destination such as “height” | Show target key ↔ driver key, quantity read, and quantity changed before committing `bind` plus the destination operation. Equal lengths do not imply alignment. |
| **Transform** | Choose Shift, Gather, Tile, or Join from an object menu | Expose whether the change moves contents in fixed slots, changes placement, creates copies, or selects occurrences. Boundary/wrap and axis choices belong to the operation. |
| **Explain** | Tap an occurrence, a zero bin, or a warning | Scoped captured reference → fields, actual keyed reads, measurement receipt, then contributors. Expand a bounded number at a time. |
| **Compare** | Select two results and choose what to compare | Initially, exact values on declared keys and an independently declared domain. Equality of totals, support equality, and isomorphism need different contracts. |
| **Cases / Replay** | Choose an exact case, or scrub a recorded action | Two visibly separate modes: integer parameter cases request evaluation; playback samples stored motion. Undo restores the captured state and reverses the recorded path. |

Count and Rank should not share a vague “height” button. Lesson 07 needs the number
of earlier **members** to stack points; lesson 06 needs the total **weight** of
earlier layers to pack them. The [ordered-prefix operation](ORDERED_PREFIX.md) now
supplies that weighted accumulation. Its control says **before each item**, shows
the weight expression, and requires explicit order and a unique item key. Similar
pictures do not justify concealing the difference between counts and weights.

Keep rare options in an “Edit declaration” sheet. A readable symbolic expression
is a parallel representation of the same definition, not an unrelated script
hidden behind a simplified picture. Round-trip editing between chips and arbitrary
Python is **not implemented**; a future editor must state which expression subset
it can edit and preserve unsupported definitions without silently rewriting them.

## A canvas, a contextual tool shelf, and an inspectable declaration

The proposed shell has a canvas, a small Add/Undo/Redo bar, and a tool shelf for
the selected object. On a wide screen the declaration/inspection sheet sits at
the side; on a phone it opens below the canvas. Use visible labels, native menus,
and tap alternatives for every drag. Essential actions cannot require hovering,
memorizing a gesture, or accurate selection of a single dense marker.

| Input | Proposed default | Necessary distinction |
| --- | --- | --- |
| Tap object/occurrence | Select; open relevant tools or Explain | A dense/coincident hit opens an occurrence chooser. Equal coordinates do not merge items. |
| Drag a labeled tool handle | Preview that handle's declared parameter or placement change | A free drag of the picture must not silently modify values or indices. Show the destination and current expression. |
| Drag a result toward a destination chip | Propose a binding, then show key/read choices | Offer the same path as “Use on…” in a menu. A driver follows its derivation; an explicit freeze command would make a literal copy. |
| Drag empty space in View mode; pinch | Pan/zoom the camera | Camera changes do not alter domain bounds or become mathematical construction edits. |
| Choose Orbit in a 3D view; drag | Rotate the camera | Coordinate changes live in Arrange. Provide view presets and named planes for selections. |
| Lasso / paint occurrences | Create a finite selection by scoped identity | It is not automatically a general predicate. A separate “Describe with a rule” action must expose and check any proposed generalization. |
| Release a preview; Cancel/Escape | Commit one semantic edit; or restore the starting state | Do not add a history action per pointer sample. An abandoned preview leaves no construction change. |

The studio now uses hold-to-open options selected by object/occurrence/view scope,
with the same actions on a visible Options button and a keyboard route. Menu
placement and radial versus list presentation can change independently of the
commands. Long-press is a first-class shortcut, not the only way to reach a tool.
Start with roughly 44-pixel control targets and test on
actual tablets; dense points also need the occurrence chooser and an accessible list.

Zooming out fits the **declared domain**. Panning beyond it may offer “Extend to…”
with explicit new bounds; it must not silently change a finite theorem's universe.
Visual culling, level of detail, and loading windows belong to the viewer. An
unbounded symbolic domain, if added, would require a separate evaluation contract.

The Spiral and Young choices are initial recipes. A general path/recurrence
editor remains a later experiment: initial state, step rule, turn/break rule, and
termination/bounds must be explicit. Structural fields such as a spiral corner
come from that constructor, not recognition of a corner on the screen. A free
spatial gesture alone cannot supply that recursive meaning.

## Work through three different constructions

### Equal sums: relate, measure, then compose a new placement

1. Add two integer arrangements. Pair them with roles `left` and `right`.
2. Put `left.value + right.value = s` in a lens. Move its integer handle and see
   which pairs are incident. Touch and a slider should select the same exact cases.
3. Choose Measure → Count, retaining an explicit sum-bin domain. Pull the count
   profile into the scene. Tap a zero bin and see an empty contributor list.
4. Choose Arrange → x = sum. Coincidences preserve the pairs. To separate them,
   choose Rank grouped by sum, ordered by pair key; use that measured rank as y.
5. Inspect one stack point, follow its rank receipt to its predecessors, then Undo.
   Change the source from `[0,1,2,3]` to `[0,1,3,7]` and repeat.

The two cases both have 16 ordered pairs but additive energies 44 and 28. Equal
population does not determine the distribution. The study uses two extra empty
outer bins in addition to any internal gaps, making zero coverage visible.

The [study exporter](../examples/touch_study.py) implements this bounded scenario:

```sh
python3 examples/touch_study.py --out build/touch-study.html
```

Open the generated HTML locally. Sources, Relate, Measure, Arrange, and Inspect
have working menus. A pointer drag previews the lens; release commits it. Choose
the three placements, inspect rank contributors, and undo/redo. Reduced-motion
settings skip replay while preserving the same endpoint. “Read the construction”
shows executable symbolic Python. The browser only selects captured results;
the Study's local command history is not a serialization bridge to `Workspace`.

The Python exporter checks counts against an independent `Counter` enumeration,
obtains explanation references from `Inspection`, and samples actual forward/undo
paths. The browser does not reconstruct incidence from its drawn diagonal or count
SVG marks. The [template](studies/touch-pairs.template.html) owns presentation and
input handling; the exporter owns the finite study cases. Generated data stays in
`build/`, outside commits. Neither file introduces a general UI command framework.

An optional [browser regression check](studies/check-touch-study.cjs) exercises
pointer, keyboard, emulated touch, cancellation, zero bins, identity-preserving
placement, and responsive layouts. With an existing Node/Playwright installation:

```sh
node docs/studies/check-touch-study.cjs build/touch-study.html
```

It writes its report and screenshots to `build/touch-check/`. A tool installation
outside the project can be selected with `KALEION_PLAYWRIGHT_MODULE` (module path);
`KALEION_BROWSER_OPTIONS` optionally supplies a JSON Playwright launch-options
object. Neither is a Kaleion runtime dependency. The
[validation record](../notebooks/VALIDATION.md) distinguishes emulation from
physical touch testing. The drawing uses a persistent hit surface and owns its
native touch gesture; unrelated controls stay stable during redraws. This avoids
losing the gesture target or interference with the next menu tap.

### Image reconstruction: the same controls, a different relation

Select pixels and lines; Pair names their roles. Relate builds the modular line
predicate; Measure counts lit pixels retaining line keys `(m,t)`. Use those line
counts as weights on the point–line incidence and Sum retaining pixel keys `(u,v)`.
An independent probe plane uses those measurements as heights. Explain follows a
probe → line-count read → contributing pixels using the captured inspector.

The user must be able to revisit Measure more than once and work on a derived
object. A linear creation wizard would obstruct this construction. Remove an
entire reconstructed row: Compare must expose missing keys against the declared
pixel domain, including missing zeros, rather than displaying a false agreement.

### Hermitian partitions: a failed construction is useful material

Pair poles with curve points. Relate defines field orthogonality; Measure counts
coverage of every expected curve point. “Use unique owner” is available only after
checking exactly one match per key. Removing a candidate owner leaves uncovered
points available to inspect while the owner-dependent packing fails explicitly.

The [coverage adapter test](COVERAGE_INSTRUMENT.md) now challenges `Product` with
a restricted seven-block family and reversed canonical point storage. The full
lesson's `Product` migration remains separate work. Lesson 10's canonical point
codes currently align with a particular storage convention. A named role is a
**current source slot**, not automatically the project's canonical code. Reorder
and filter representatives, retain both quantities under separate fields, and
check the owner domain before migrating that lesson. Do not make screen order,
storage order, or equal integer labels silently stand in for a correspondence.

## Preview, commit, history, and failure

A future controller should own the transaction boundary. A gesture changes a
draft declaration. It may request an exact preview case; rapid obsolete requests
can be coalesced or cancelled. Every reply needs a request/revision identity so
an old result cannot replace the current preview. Release commits one accepted
definition/capture; cancel discards the draft. Scheduling/cancellation is proposed,
not added by this study.

Undo is semantic: restoring a lossy gather or reduction requires the earlier
capture. Reverse playback uses the recorded path; it does not guess the inverse
operation. Changing camera or selecting a point needs separate view state. An
unsupported explanation should leave the current picture usable. A failed
evaluation may leave the previous picture available only with an explicit stale
indicator, never relabeled as the new result. Independent ready objects continue
to work.

Display these outcomes distinctly: ready zero, missing expected key, ambiguous
key/coverage, failed evaluation, pending preview, and unavailable explanation.
They invite different next actions. Do not render all of them as an empty scene.

Selection carries a scoped captured reference. During replay, an inspector must
choose a before or after endpoint, or pause there. A moving marker's interpolated
position is not a mathematical key. A graph root name alone is insufficient once
sources are edited or parameter cases change.

## Boundaries by changeable decision

This applies the Parnas criterion in [DESIGN.md](../DESIGN.md). A menu item is not
automatically a module; touch, keyboard, and programmatic authoring should issue
the same semantic declarations.

| Decision that may change | Owner | Boundary to preserve |
| --- | --- | --- |
| Touch recognition, hit testing, gestures versus menus | Input/view adapter | Semantic intentions and captured selections; no arithmetic implementation |
| Which source role/address convention a recipe uses | `products.py` and other small authoring recipes | Ordinary definitions; explicit reads and identity policy; no evaluation |
| Which fields, groups, order, and destination an edit declares | Declaration editor | Typed definitions or a validation message; no screen-derived correspondence |
| When to evaluate, cancel, bound work, or accept a preview | Future evaluation controller | Revision-tagged results/errors; exact evaluation stays in existing modules |
| What one undoable edit contains | History/controller boundary | Captured endpoints and recorded paths; no per-frame graph inputs |
| How dense geometry is projected, culled, and animated | Renderer/camera | Snapshots and motion samples; no implicit domain edits |
| How saved reads and measurements become explanations | `Inspection` plus a narrative adapter | Read-only scoped receipts; independent failure and bounded expansion |

There is no justification yet for a `TouchArrangement` subclass, one class per
lesson, or a new evaluator primitive for every tool. `Product` already demonstrates
a smaller boundary: named factors lower to existing Grid/Count/Bind operations.
Its implementation and dense cost can be examined independently of the UI.

## What to test next

Have a new user perform the five equal-sum steps without entering Python. Record
where they cannot predict a control's effect, confuse a parameter case with replay,
lose track of source identity, or cannot find a zero/coincident occurrence. Then
have them make a new relation rather than repeat a scripted demonstration.
The current two-case study cannot establish this general authoring usability.

The [construction studio](CONSTRUCTION_STUDIO.md) now connects a bounded real
declaration editor to Kaleion, with save/reopen, cancellation, failure recovery,
and two constructions through the same controls. Its shared Group selector now
browses sum and modular-line fibers, retaining zero groups and separating
candidate membership from incidence. Compact formulas open one selected part for
editing; grouping, measurement, and member order reuse a field-key control.
The [coverage instrument](COVERAGE_INSTRUMENT.md) now checks independent expected
keys and attaches guarded assigned fields. Simple/additive browser tasks and a
restricted Hermitian adapter test cover its witnesses and keyed reuse. Paired
views now cover absent items, measured dependencies, and nested Radon weights.
Comparison follows exact residuals into those receipts, while case controls expose
the prime/composite assumption. Next observe whether new users can choose an
independent domain, distinguish a compared field from an occurrence's value,
and return to their original question. Compare the current phone jump links with
a bottom-sheet prototype on real devices. Weighted prefixes in lesson 06 now
establish the ordered-measurement contract, with a dense reference and transfer
to quotient-column packing. The shared Measure control follows that contract;
its first zero, retained zero-weight items, signed sums and tied orders have
automated checks. Measured case families remain a separate backend gap.
