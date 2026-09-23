# UI design for mathematical discovery

September 22, 2026 · Research and initial audit

September 23, 2026 · Reevaluation through cases, comparison and ordered accumulation

September 23, 2026 · Icarus comparison and construction-inspection review after PR #29

September 23, 2026 · Readable construction inspection implemented after the PR #30 design

September 23, 2026 · Shared scene, cell/point charts, 3D slices and saved views after PR #31

**Recommendation:** build a workspace of reusable mathematical instruments, with
low-cost experimentation and visible consequences. Judge it by whether someone
can transfer an interaction to an unfamiliar construction, explain what changed,
and pursue their own question. Completing a scripted lesson is necessary evidence
of expressiveness, but insufficient evidence of discovery or novice usability.

This study reviews primary HCI research, authors' design guidance, and W3C
accessibility guidance. The initial audit used merged commit `1c35d358`, after
shared group selection and compact formula editing. The new review starts from
`bba8b19` (merged parameter-case PR #25) and records the comparison/navigation
changes below. [TOUCH_WORKSPACE.md](TOUCH_WORKSPACE.md) supplies the complementary
design constraints: nearby object tools, readable declarations, explicit domains,
and camera state separate from mathematics. Findings about the code and
browser are observations; proposed effects on learners are hypotheses. No human
participants were recruited and no accessibility conformance audit was performed.
The existing [all-lesson coverage matrix](CONSTRUCTION_STUDIO.md#all-lessons-are-the-target-remaining-composition-coverage)
remains the capability inventory. This document supplies the evaluation criteria.
The ordered-prefix increment starts from `91a6e33` (merged PR #26); it adds the
transfer evidence recorded below without claiming new human-study results.
The latest [unified canvas proposal](UNIFIED_CANVAS_DESIGN.md) reviews merged
PR #29 (`00d9202`) against Icarus and the maintainer's further desktop feedback.
It records design decisions and an implementation sequence. The first step,
[construction inspection](CONSTRUCTION_INSPECTION.md), now implements readable
declarations and scoped input navigation on top of merged PR #30 (`dfa8cb1`).
The [shared scene](SHARED_SCENE.md) now implements the next step on merged
PR #31 (`5740d63`). Captured transport, reusable rules and later steps remain proposals.

## 1. What the research contributes

The applications below are our design deductions, not prescriptions the cited
papers make about Kaleion. Full-text papers were inspected where available;
Kirsh–Maglio and Heer–Robertson are used at the scope of their publisher abstracts.
Sources and access details are listed at the end.

| Concept and source | Finding or design lens | Application to Kaleion | Important limit |
| --- | --- | --- | --- |
| Direct manipulation · [R1] | Keep relevant objects visible; support small reversible actions with visible effects. | Keep a construction visible while changing its rule. Distinguish Preview from Apply; retain the accepted capture for undo. | Direct manipulation includes labeled controls. It does not require every mathematical operation to be a drag. |
| Instrumental interaction · [R2] | Instruments mediate actions on domain objects. Reification makes an abstract action manipulable; polymorphism broadens its useful contexts; reuse carries work forward. | A relation lens, group selector, measurement, placement, and case controller should compose across lessons. A reusable measurement can become an input to another instrument. | Generality requires meaningful contracts, not an unrestricted menu on every object. A shared widget alone does not establish a shared meaning. |
| Cognitive dimensions of notation · [R3] | Examine change effort (viscosity), space consumption (diffuseness), visible dependencies, provisional work, and opportunities to check partial work. These are tradeoffs in an activity, not independent scores. | Evaluate the formula and its editor together. Test a small edit, an interruption, and returning to a half-built idea; inspect whether users can locate a driver's source. | A compact formula may reduce space yet increase selection difficulty. Fewer controls need not mean easier reasoning. |
| Epistemic action · [R4] | In the reported Tetris work, some rotations and translations help people obtain information rather than merely advance a final arrangement. | Treat rearranging, grouping, and replay as ways to think. Preserve an unfinished construction while its author examines another object. | The study does not establish learning benefits for mathematical animation; transfer to Kaleion needs investigation. |
| Heuristic evaluation · [R5] | Visibility, user control, recognition, and error recovery are useful inspection prompts. | Show the current target and draft state near the controls. Reject stale previews visibly; offer a clear way back after inspection. | A heuristic review identifies plausible problems. It is not a substitute for observing users. |
| Progressive disclosure · [R6] | Present common choices first and make additional choices discoverable. A forced sequence is a different technique. | Show the formula first and edit one selected part. Expose grouping/order/coverage when relevant; keep exact declarations and receipts available. | Never hide a choice that changes the mathematical claim. Avoid a wizard when users need to move repeatedly between related choices. |
| Animated transitions · [R7] | Controlled chart-transition experiments found perceptual benefits for some transitions. | Give motion a question: which occurrence went where, or what changed between exact cases? Compare replay against still endpoints. | This does not show that all animation helps, that an attractive motion proves a relation, or that it teaches a theorem. |
| Programmatic/direct manipulation correspondence · [R8] | Sketch-n-Sketch investigates GUI actions that transform an underlying program. | Let controls produce inspectable semantic edits. Preserve the possibility of readable notation beside a view. | Kaleion should not silently infer a general rule from a dragged example. Ambiguous correspondences need an explicit choice. |
| Accessible interaction · [R9] | Focus order, announced status, target size, cancellation, and alternatives to dragging have distinct requirements. | Make hold an optional shortcut; retain visible buttons and lists. Keep keyboard focus attached to the edited part. Report preview failure where editing occurs. | Emulated touches and DOM assertions do not establish screen-reader or physical-device usability. |

The strongest match to the artistic goal is an instrument that remains useful
when the subject changes. A grouping control should work on sum fibers, field
norms, and code syndromes because it declares a key—not because it recognizes a
lesson. Expressive power comes from compositions the author can inspect and alter.

## 2. Proposed interaction grammar

Use the same sequence of choices throughout the workspace, without forcing them
into a fixed wizard:

| Choice | Visible question | Mathematical responsibility |
| --- | --- | --- |
| Target | What am I touching: an object, occurrence, declared group, or the view? | Selection scope and captured identity; touching equal labels does not merge them |
| Instrument | Do I want to relate, measure, arrange, compare, inspect, or explore cases? | Availability follows capabilities and assumptions |
| Inputs | Which fields, groups, order, domain, or other arrangement does it use? | Explicit correspondence and arithmetic domain |
| Effect | What would this action create or change? | Draft versus evaluated preview versus applied construction |
| Evidence | Why is this value or membership here? | Contributors, declared reads, finite witnesses, and limits |

These are **shared interaction patterns**, not five new core classes. They may
appear together in a sheet, a context menu, or a future canvas instrument.

Hold should open contextual options after a visible indication that the hold was
recognized. It must not itself commit a construction. Moving away, cancellation,
or a second touch must end the pending hold. An Options button must expose the
same actions. Persistent selector modes need persistent labels; cursor shape or
color alone is insufficient on touch devices.

For future direct placement, first distinguish **move this view**, **change these
positions**, and **declare a rule that produces positions**. A two-finger camera
motion is not a new arrangement. A hand-positioned example is not automatically
a symbolic law. A group key is not an order, and a selected group is not a new
universe. Preserve these differences even when the visual controls resemble one
another.

## 3. A practical quality rubric

Use this as a review worksheet for a concrete task, with a screenshot or test
reference for each claim. Do not combine the rows into a numerical usability score.

| Review question | Acceptable evidence | Failure worth recording |
| --- | --- | --- |
| Can the author predict the target and effect before Apply? | Visible source, operation, and draft/preview state agree with the semantic command | Inspecting another object silently retargets a pending edit |
| Can the author try, inspect, and return cheaply? | Unfinished fields, exact numbers, grouping choices, and local undo survive a browsing detour | Rebuilding a formula after selecting another object |
| Is feedback current and near the action? | Editing invalidates the ready message; validation errors appear by Preview/Apply | A stale success message or an error above an off-screen canvas |
| Does the same instrument transfer? | One control completes tasks in two unrelated lesson families without a lesson ID | A new special-purpose menu for each demonstration |
| Can the author tell a zero from absent evidence? | Declared domain, zero membership, missing keys, and execution failure have distinguishable reports | Treating missing coverage as an empty successful result |
| Can the author inspect a dependency? | Follow a measured value to its contributors and a placement to its driver | An attractive picture whose inputs cannot be recovered |
| Can someone use keyboard or simple taps? | Sequential keyboard task, equivalent visible controls, focus recovery, target checks | A disappearing focused token, hold-only command, or drag-only control |
| Does motion answer a question? | Correct endpoint/correspondence prediction with replay and a static alternative | Frames mistaken for additional exact cases or universal evidence |
| Is mathematical meaning independent of presentation? | Pan/zoom, inspection, and draft edits leave committed workspace data unchanged | Pixel coordinates or display sampling become implicit mathematical inputs |
| Can someone explore beyond the example? | A new relation and follow-up question constructed without recipe-specific controls | Success only when repeating memorized lesson steps |

For touch controls, target at least 44 × 44 CSS pixels as a **project design goal**
where practical. WCAG 2.2 SC 2.5.8's AA minimum is 24 × 24 with specified
exceptions; these are not interchangeable standards. Dense plotted points need
an equivalent accessible list instead of distorting mathematical positions. A
keyboard equivalent does not by itself replace a single-pointer alternative to
dragging. [R9]

## 4. Initial audit and current disposition

Severity here is local prioritization: **high** risks lost work or misleading
state; **medium** adds substantial friction or an untested interpretation;
**open** requires capability development or human observation.

| ID | Finding (initial baseline unless noted) | Evidence | Current disposition |
| --- | --- | --- | --- |
| A1 | Clicking another object while composing removes the form, with no draft-return control | `studio.js` object handler clears the panel; fresh-browser probe reproduced it | Addressed · one recoverable draft; creating a dependency while drafting remains constrained |
| A2 | After a valid preview, changing its expression disables Apply but leaves the old ready message | Fresh-browser probe and `changed()` handler | Addressed · current local status and invalidation tests |
| A3 | Activating a formula token with Enter replaces the focused node; focus falls to the document body | Fresh-browser probe of `expressions.js` | Addressed · focus recovery on open/edit/close/undo |
| A4 | Key removal destroys a focused chip without assigning a successor | `groups.js` inspection | Addressed · successor chip or field-picker focus |
| A5 | Group selection separates candidates from incidence and retains declared zero groups | Group contracts and additive/modular browser investigations | Preserve; use the same distinction in coverage checks |
| A6 | Preview/apply and captured history are separate; driver inspection can use saved data | Adapter/core contracts and save/reopen browser checks | Preserve; no new numerical execution in the view layer |
| A7 | Formula, canvas, and actions can be far apart on a narrow screen | 320 px screenshots: the form is below the canvas | Partly addressed · local feedback and focus-moving Canvas / Construction and evidence links; simultaneous visibility and reach remain untested |
| A8 | Contextual actions have visible and keyboard alternatives; View pan/zoom still lack complete button alternatives | Context resolver and gesture handlers | Addressed for camera actions · shared Fit/zoom/directional-pan controls on main and linked views; physical input and accessibility audit remain open |
| A9 | A single object canvas obscures comparisons and immutable earlier inputs | Existing studio limit and lesson coverage matrix | Partly addressed · linked evidence plus PR #29's simultaneous named-root previews and definition paths; free pinning and direct shared geometry remain open |
| A10 | No novice task or physical tablet trial has been conducted | Available evidence consists of code, deterministic fixtures, and emulated Chromium | Open · run the formative protocol below |
| A11 | The first object-tab click after editing a number can disappear | Input blur triggers a render that replaces the tab before its click arrives; reproduced in the baseline probe | Addressed · unchanged controls survive render; one-click navigation regression |
| A12 | Value comparison requires manual inspection; missing-both keys have no comparison report | Still absent at the `bba8b19` reevaluation baseline | Addressed · exact selected fields, independent expected domain and inspectable residual/missing/outside witnesses |
| A13 | The starting point and replay control are hard to discover | Project owner's desktop feedback; the current studio hides replay until a recent movement | Open · four saved canvases and an existing-controls walkthrough provide material for feedback; no UI redesign in this increment |
| A14 | Selecting an object does not adequately reveal how it was constructed | Maintainer feedback after PR #29; now checked through all four saved canvases plus earlier/local/failed inputs | Implemented · selection reveals actual constructor, arguments, scoped inputs and result status; Back restores context and captured results lead to occurrence evidence. Human interpretation remains untested |
| A15 | Simultaneous preview panels still fall short of directly manipulating mathematical objects | PR #29 used independent XY previews; the shared-scene gate now exercises cells/points, direct mark inspection, 3D slices and saved views | Partly implemented · common scale/local frames, explicit charts, name-handle movement, Sequence creation and reviewed combination targets. Direct mathematical manipulators, reusable rules and human evaluation remain open |
| A16 | Reusable rules and live dependencies lack a complete visible authoring contract | Core Lens is reusable; current connections describe immutable definitions, while Icarus exposes movable relation tokens | Open · separate rule, application, and captured incidence; add explicit recipe ports before promising propagation through editable cables |

The baseline probe uses actual controls and records the browser version, focused
element, message, Apply availability, and presence of a draft-return control.
Reproduction sequence: create A and B; start a relation on A; activate a formula
number with Enter; preview; edit the number; select B. The first click can be
swallowed (A11); clicking again navigates and loses the draft (A1). The JSON trace
is a local build artifact, not a fabricated participant observation.

### Reevaluation: what the interface now supports

**September 23 follow-up from the project owner:** after trying the desktop
interaction study, the user could not readily find a starting point or a scrub
control, and asked for saved canvases before further UI options. This is direct
project feedback, not a formal novice study or evidence of which study page was
open. The response is four [ordinary saved canvases](../examples/canvases/README.md)
and a short exploration guide, using the existing Open and Undo/Redo controls.
No lesson picker, new menu, or playback redesign is included. The current studio
scrubber needs a recent action and is not restored directly on file open; the
guide explicitly uses Undo then Redo to expose it. Examples can help us observe
inspection and editing, but do not resolve blank-canvas discoverability by themselves.

The strongest progress is continuity across instruments: an idea survives an
inspection detour, a measured quantity leads to its captured inputs, and returning
restores selection and camera state. Cases extend the same loop to changed
assumptions. These are observed capabilities; easier discovery is still a
hypothesis. The growing object rail, multiple key declarations, and long phone
sheets may increase the effort of finding and interpreting controls.

| Design lens | Progress through the current increment | Remaining question / next observation |
| --- | --- | --- |
| Direct manipulation and recovery | Drafts, previews, exact undo/redo, and evidence return paths preserve context | Can a new user predict which actions change a construction and which only inspect it? |
| Instrument reuse | One group, coverage, evidence, case, and comparison grammar serves unrelated constructions | Can someone transfer without a recipe, and find the next instrument among the contextual choices? |
| Visible dependencies | Radon inspection separates occurrence value, contribution weight, driver read, and selected comparison field | Can users explain those differences without facilitator prompts? |
| Explicit assumptions | Named parameters reevaluate one graph; comparison declares fields, ordered keys, and an independent domain | Do users deliberately choose a domain, or accept a convenient operand that hides missing keys? |
| Progressive disclosure | Comparison starts with all claim-changing inputs visible, then collapses inputs after a check; its report repeats the declaration | Are three key lists manageable on a phone? Does collapsing inputs hinder revising the question? |
| Motion | Exact case evaluation is separate from request-free captured replay, including reduced-motion handling | Test endpoint/correspondence prediction against still views; smooth playback alone is insufficient evidence |
| Accessible alternatives and proximity | Shared camera buttons and narrow-screen jump links reduce required gestures and navigation | Real-device reach, screen-reader status/focus, occlusion, and simultaneous view/control access remain open |

Three concrete gaps determined this increment. Manual reconstruction checks lacked
a reusable residual/domain inspector (new A12, addressed by
[keyed comparison](KEYED_COMPARISON.md)); camera actions needed tap alternatives
(A8); phone navigation needed a bounded improvement before a larger layout trial
(A7). The comparison belongs in the selected object's menu, not a lesson-specific
workflow. It treats zero, absence, ambiguity, and unavailable input separately,
as required by the touch-workspace proposal. Totals, support, and structure
isomorphism remain different questions.

The next design work should test the present grammar with people. The maintainer's
subsequent desktop use of the saved canvases supplied specific feedback: the
constructions and Undo/Redo animations were useful, but getting started remained
unclear and the single-object canvas concealed the intended spatial building
experience. This is one person's formative feedback, not the proposed novice
study. It justifies the bounded [spatial workspace experiment](SPATIAL_WORKSPACE.md):
simultaneous object previews, selection/movement, visible definition inputs, and
drag-to-propose Product or keyed Arrange through the existing declaration editor.
It does not yet justify arbitrary graph rewrites or a larger permanent tool shelf.
A compact bottom sheet
or contextual palette is a candidate to compare with this layout, not an already
validated replacement. Persistent comparison recipes, named subexpressions, and
a saved-case browser are useful development candidates once their reuse and
visibility costs have concrete task evidence.

### Icarus comparison: construction must be visible before evidence

The maintainer's next report identifies a specific unresolved question: selecting
a workspace object still does not make its construction clear. The requested
reference is their older Icarus application, particularly its grid, directly
created vectors/products, reusable relation tokens, and spatial interactions.
This feedback supports A14–A16; it does not establish that all of Icarus's controls
are intuitive or should be adopted.

The [design brief](UNIFIED_CANVAS_DESIGN.md) records the exact source revisions
and the bounded browser exercise: vector drawing and inspection, a product from
two vectors, a four-member relation on a six-by-six domain, extraction, and
reattachment. Source inspection distinguishes working mechanisms from prospective
3D and general recurrence ideas. No private source or browser screenshots are
copied into Kaleion; the brief includes an independently drawn concept.

The revised priority is **readable construction on selection**, connected to
existing occurrence evidence. A measurement receipt answers why one result has
its value; an object's constructor explains its source, reducer, groups, weight,
order, and parameters. Neither substitutes for the other. Input navigation must
retain the earlier-definition and local-case boundaries already protected by
the spatial workspace.

Against this study's rubric, simultaneous objects alone did not resolve A14 or
the direct-manipulation goal. The construction inspector now addresses A14's
missing information; it does not establish comprehension. Grid cells and points should
share selection identity; choosing logical axes versus placement stays explicit.
Reusable rules should expose their arguments and bindings. A persistent transport
should label Cases, Generation, or Replay, with seeking captured samples separated
from acquiring new evaluations. These are design hypotheses with concrete
acceptance tasks, not completed fixes.

The next human observation should begin without an editing instruction: select
Moving pairs, explain how its y coordinate is obtained, follow the rank source,
and return. Then ask the person to create two short sources, propose a product,
reuse a relation, and explain what the chosen scrubber changes. Repeat in an
unrelated lesson. This tests discovery, interpretation, and transfer rather than
only whether the controls execute correctly.

### Construction inspection: implementation and tradeoffs

The selected object's constructor is now visible without opening Options or
choosing an occurrence. Coordinates, grouping, contribution weight, strict order,
item keys and parameter bindings use the same read-only inspector across saved
investigations. Input buttons lead through unnamed expansions and distinguish
earlier definitions from local parameter scopes; the actual captured result
connects to existing occurrence receipts. Back restores the selected occurrence,
main/workspace/linked cameras, previous controls and input-button focus. A draft
survives the detour on its original target.

This improves recognition and dependency visibility without treating an old
capture as a live wire. Product's lowered Grid/count/read definitions remain
visible rather than being guessed back into an editable recipe. That fidelity
also has a cost: intermediate definitions can require several steps to interpret.
The exact-operation view supports unfamiliar constructors but is not a substitute
for readable authored recipes in later work.

The sidebar preserves the construction header while evidence or editing occupies
the activity area; opening those tasks collapses the declaration. Screenshots
show no horizontal overflow at 320 pixels, but phone sheets remain long and the
picture may be off-screen. A7, A10, A13, A15 and A16 remain open or partial. The
common-scene increment below extends direct object interaction while human
observation still needs to test whether this declaration/evidence split is understandable.

### Shared scene: closer to direct manipulation

The workspace now draws cells or points using one coordinate scale, with local
axes and explicit view offsets. Selection leads from a mark to its captured
receipt; a list retains depth-overlapping and sliced-out occurrences. Changing
marks preserves the selected reference and camera. Changing Logical axes versus
Placement is a separate, labeled chart decision. Name-handle movement, camera
orbit and view slices leave mathematical export unchanged.

This closes part of A15's gap: objects can be touched directly, constructed as
finite sequences, and retained alongside a reviewed product. It also exposes
tradeoffs. Shared scale makes relative extents honest but long sources compress
the fitted overview. Three-dimensional glyphs can occlude each other; plane
buttons, Selected, slices and an occurrence list help, but do not establish
comfortable picking. Representation controls are compact and expandable above
the canvas; expanding both chart and occurrence details still pushes the picture
down on a phone. Physical-device density and reach trials remain necessary.

Canvas and view saves now retain the scene camera, chart choices and offsets.
Mathematics-only export preserves the ordinary workspace for other clients.
This gives provisional spatial organization a useful lifetime without putting
camera movement into mathematical undo. Focus, linked evidence and replay still
use their labeled XY views; the UI must not imply that a 3D scene means every
instrument has already gained 3D rendering.

## 5. First design experiment: an idea survives a detour

**Hypothesis:** retaining an unfinished construction while someone inspects a
source reduces the rebuilding needed to explore. Keeping feedback and focus near
the edited part should make its state easier to interpret. Behavioral tests can
verify retention and state consistency; only human trials can assess the effect
on thinking, comfort, or discoverability.

The first increment implemented one recoverable draft in the current browser tab:

- The target, selector context, form controls, and local expression undo belong to
  the draft. Selecting a different object parks it rather than retargeting it.
- A visible draft tray offers Resume and Discard. Inspecting occurrences or groups
  is read-only. Resume restores the draft on its original target.
- A parked preview is invalidated; resuming requires Preview again. This deliberate
  first implementation avoids presenting an old scene as current feedback.
- A short message by Preview/Apply distinguishes editing, evaluating, ready, and
  failed. Changing any input removes the ready claim immediately.
- One active draft temporarily reserves construction/history/open actions. The
  tray explains how to finish or discard it. Save exports applied work only;
  drafts are not persisted through reload. This is a bounded experiment, with a
  visible cost: creating a new dependency mid-draft still requires another design.
- Formula editing and key removal have explicit keyboard focus destinations.
  Touch users keep native inputs; keyboard support is an additional path.
- Escape closes a formula-part inspector first. Outside that inspector it parks
  the construction; Cancel or Discard is the explicit destructive choice.

This took precedence over adding coverage controls because A1–A3 obstructed the
basic edit–inspect–return loop every future instrument uses. The subsequent
[coverage experiment](COVERAGE_INSTRUMENT.md) now reuses that loop.

### Information hiding

Keep [Parnas's project guidepost](../DESIGN.md#decompose-by-decisions-that-may-change):
a module owns a decision that can change, rather than a stage of a lesson.

| Changeable decision | Owner | Boundary |
| --- | --- | --- |
| How long an unfinished idea survives navigation | [`drafts.js`](../examples/studio/web/drafts.js) | Park/resume/discard and revision validation; no mathematical evaluation |
| What a formula looks like and where editing focus goes | `expressions.js` | Structured expression and field contexts |
| How ordered fields are chosen | `groups.js` | Field names and their declared order |
| Which actions fit a target | `context.js` | Selection capabilities; no lesson identifiers |
| How a preview becomes a recorded construction | Existing adapter/history | Revisioned token and exact captured state |
| How an applied change moves | Existing motion/view code | Captured endpoints and paths |
| What finite keyed equality means | `kaleion.comparison` | Exact selected fields and independent domain; no evaluation or UI |
| How to inspect a comparison | `comparison.py`, `comparison.js`, existing linked views | Bounded scoped witnesses, input choices, and return navigation |
| Which inputs move a camera | `camera.js` and existing view callbacks | Shared buttons; no mathematical extent or placement changes |
| What a selected definition declares | `construction.py`, `construction.js` | Actual IR and captured scopes; read-only browsing and return context, no recipe inference or evaluation |
| How captured objects share a scene | `scene.js`, `workspace.js` | One projection and explicit local offsets; picking follows captured identity, slices are view filters |
| How scene choices survive Open | `document.js` | Versioned view envelope; original mathematical JSON text remains exact and independently exportable |
| How earlier weights become a measurement | `Grouping`, shared order plan, exact scan and existing contributor ranges | Explicit groups/order/keys; the Measure client edits declarations, not numerical state |

Do not create a new core operation for draft retention, visual focus, or error
placement. No saved-schema or public Python migration is needed. A future native,
notebook, or touch client can share semantic edit contracts without adopting the
same layout or DOM controller.

## 6. Cross-lesson acceptance tasks

Each new instrument should pass two unrelated constructions and one broken
assumption. These are acceptance tasks, not buttons or lesson-specific code paths.

| Pattern | Transfer pair | Counterexample / semantic checkpoint |
| --- | --- | --- |
| Build a source and declare extent | Spiral prefix (01); dilated lattice region (08) | A viewport boundary is not a finite mathematical boundary |
| Apply a relation | Floor-sum region (02–03); modular line (05) | Change a modulus or coefficient; explain precisely which memberships change |
| Group and measure | Sum fiber (07); Hermitian ownership (10) | A group with zero hits remains distinguishable from an absent key |
| Order and reuse a measurement | Young packing (06); norm fibers (09) | Ties require an explicit decision; storage order must not silently decide |
| Drive placement from another object | Quotient profile (04); ownership/rank placement (10) | Reorder a driver and preserve keyed correspondence |
| Explore cases and motion | Spiral unrolling (01); field/code cycles (09–11) | Replay time does not create new parameter cases |
| Compare and explain | Reconstruction (05); code/field incidence (11) | Equality of values differs from an incidence-preserving correspondence |

For the first experiment, the executable tasks are deliberately smaller: start a
modular relation, inspect an unrelated additive object, then return and apply to
the original target; repeat with a grouped measurement draft and an occurrence
receipt. Include a failed preview and an edit after a successful preview.

## 7. Testing method and reporting

**Deterministic gate:** offline core tests and discovery example remain required.
The browser gate exercises actual authoring controls, exact preview/apply,
unchanged workspace data during browsing, draft recovery, keyboard focus,
status transitions, cancellation, and narrow-screen layout. A passing gate means
those behaviors work under that browser; it is not a measured usability score.

### Results of the first authoring-loop increment

The [browser gate](studies/check-construction-studio.cjs) passes against Chromium
153.0.8010.0 using a fresh studio host. It reproduces the interruption with both
a modular-relation draft and a grouped-measurement draft. The original target,
formula, retained keys, name, and local expression undo survive. Browsing and
editing leave exported workspace JSON byte-for-byte unchanged. An invalid
preview produces local failure feedback; an edit or parked draft invalidates a
ready preview. Keyboard checks verify token/inspector and removed-key focus.
One object-tab click after an input blur reaches its intended target.

The existing exact results, zero groups, strict-order rejection, contributor
inspection, save/open, recorded undo/redo, and hold/cancellation checks still
pass. Layouts at 1250, 736, 360, and 320 CSS pixels have no horizontal overflow.
Desktop and phone screenshots were inspected; the phone form still requires
vertical scrolling, so these results do not resolve A7. Reports and screenshots
are generated in ignored `build/studio-check/`.

The required Python suite passes **144 tests**; the discovery example reproduces
its expected counts, drivers, sieve, and saved history. No notebook or video
export changed. Physical touch, Safari, screen-reader behavior, novice learning,
and free exploration remain untested. A1–A4 and A11 have deterministic regression
coverage; A8–A10 remain open. A successful browser gate is not a claim that the
whole interface is accessible or intuitive.

### Progress since that baseline

These are historical gate totals, not participant counts or usability scores.

| Increment | Behavioral evidence added | Required Python suite |
| --- | --- | --- |
| [Coverage](COVERAGE_INSTRUMENT.md) | Zero/absent/multiple/outside witnesses; guarded owner adoption; modular/additive controls and bounded Hermitian adapter | 151 |
| [Linked views](LINKED_EVIDENCE_VIEWS.md) | Expected/matched items, earlier drivers, quotient contributors, independent cameras | 156 |
| [Weighted evidence](WEIGHTED_EVIDENCE.md) | Radon contribution → weight read → source field, signed sums, restored selection/camera | 160 |
| [Parameter cases](PARAMETER_CASES.md), merged `bba8b19` | Prime/composite Radon, lattice growth, isolated failures, case undo, request-free replay | 166 |
| [Keyed comparison](KEYED_COMPARISON.md), merged `91a6e33` | Exact selected fields and independent domain; residual receipts, lattice transfer, missing-both keys; shared camera buttons and phone navigation | 173 |
| [Ordered accumulation](ORDERED_PREFIX.md), merged PR #27 | Young layers and quotient columns use the same prefix/placement controls; nested measured contributors, tied-order recovery, zero/signed weights | 184 |
| [Saved canvases](../examples/canvases/README.md), merged PR #28 | Four editable investigations open with captured evidence and reversible movement | 190 |
| [Spatial workspace](SPATIAL_WORKSPACE.md), merged PR #29 | Named objects visible together; definition paths distinguish earlier and local inputs; reviewed drag/tap composition preserves declaration and history boundaries | 195 |
| [Construction inspection](CONSTRUCTION_INSPECTION.md), after merged design PR #30 | Readable constructors and exact expressions; scoped input navigation, failed/unfamiliar declarations, captured-result evidence and restored context | 203 |
| [Shared scene](SHARED_SCENE.md), after merged PR #31 | Common-scale cells/points, 3D orbit/slices, source creation, exact saved view documents and direct occurrence inspection | 206 |

PR #29 reported the required suite and discovery example passing; the subsequent
Icarus/design review does not rerun or change those executable gates. The expanded Chromium 153
gate uses actual controls for prime/composite reconstruction and lattice equality,
returns through nested evidence to the same comparison and camera, distinguishes
missing zero-valued items from equality, and rejects duplicate keys. Camera taps,
keyboard pan, and phone jump links leave exported workspace JSON unchanged. New
navigation/camera controls meet the 44-pixel target goal in the tested phone
layout. Desktop and 320-pixel screenshots were inspected; absence of overflow
does not establish comfortable reach or low scrolling cost. No physical touch,
Safari, screen-reader, or novice trial has been completed.

The accumulation control adds a substantive shared operation while reusing the
existing fields, weight editor, order chips and receipts. The result's cardinality
matters: Count/Sum return group measurements, while Rank/Prefix sum return one
measurement per selected item. The form now explains those differences beside the
choices. Browser tasks derive a first zero with no contributors, then a later zero
with a real zero-weight contributor, and inspect a transformed weight read.
They recover a parked prefix draft and return through an offset's layer/cell
evidence with its selected contributor and camera preserved. This supports the
instrument-reuse and continuity criteria; whether users understand the distinction
between Rank and Prefix sum remains a formative-study question.

The spatial browser gate additionally opens all four saved canvases in the
shared view, creates a product with a real pointer drag, checks keyed placement
and a missing-key rejection, and retains a parked proposal's operands. View
movement, camera changes, cancellation and option opening leave exported work
unchanged. Emulated touch exposed and now guards a release-after-hold bug that
could choose a newly opened menu item under the finger. Desktop and narrow-screen
images were inspected. The saved-canvas and full construction browser gates also
pass, preserving replay, comparison and nested evidence; this does not establish
physical-device ergonomics or whether users understand the new overview.

The construction-inspector gate passes in Chromium 153. It selects objects in
all four saved canvases, follows their actual inputs, opens captured evidence,
and returns to the same selected occurrence, cameras and focus. Further fixtures
exercise earlier drivers, local cases (including bindings equal to global ones),
failed/empty captures, an unknown constructor, an integer above 64 bits, a parked
draft and a delayed reply after a new selection. Exported JSON is unchanged and
no evaluation/history request is issued. Eight new Python tests also disable the
evaluator while inspecting saved definitions. The full **203-test** suite,
discovery example, and inspector/studio/spatial/saved-canvas browser gates pass.
Light, dark and narrow-screen images were inspected. A phone group-tap regression
now uses the visible Canvas jump and asserts an unobscured target instead of
scrolling a point underneath the sticky navigation. These checks do not add
human, physical-touch, Safari or screen-reader evidence.

The shared-scene increment adds a fifth saved example: lesson 03's 240-cell box.
Its finite partition and captured contributors are independently checked.
The offline geometry/document gate verifies projection, chart/slice identity,
empty declared bounds, large exact integers and invalid documents. The Chromium
scene gate checks direct mark picking, Sequence creation, mark/chart changes,
view-only slice/orbit cancellation, exact camera/offset/selection restoration,
failed/empty captures and phone widths. The existing inspector, spatial,
saved-canvas and full-studio gates pass as regressions. Required tests total
**206**, and discovery outputs are unchanged. These are automated and visual
inspection results; no participant or physical-device evidence has been added.

### Proposed human observation

Add three tasks motivated by the maintainer's feedback: construct every pair by
bringing two objects together; use a count as another object's height; explain
why an earlier consumer does not retarget when a named source is rearranged.
Record whether people identify the active source/destination, review the keys,
and predict what Apply changes. Ask them to distinguish moving a view offset,
changing its chart, changing mathematical x/y/z, selecting an exact parameter
case, and scrubbing recorded motion. The scene now shares a coordinate scale;
test whether users understand its local frames and avoid treating visual overlap
as mathematical equality. Dense scenes, crossing/occluded paths and the Focus
detour are explicit unresolved design costs.

**Formative human study, proposed:** start with 6–8 consenting adult volunteers,
including people comfortable with school algebra but unfamiliar with the API and
some experienced mathematical/programmatic users. Report each group's experience;
do not treat this convenience sample as representative. No recruitment or
recording occurs automatically.

Give a brief orientation to Objects/Occurrences/Groups/View and one construction.
Counterbalance additive-first and modular-first task order. Ask participants to
think aloud, but separate spontaneous remarks from answers prompted by the
facilitator. Use the same task wording and time budget across rounds.

1. Construct a relation from a blank canvas and predict what Preview will show.
2. Begin another construction, inspect a different object, and recover the idea.
3. Find a zero group and explain its difference from a missing group.
4. Use a measurement as a placement driver and explain the chosen keys.
5. Recover from an invalid rule and distinguish local expression undo from
   workspace undo.
6. Transfer a learned instrument to a different mathematical setting with no
   step-by-step recipe. Finish with time for a self-chosen question.

For the case/comparison round, ask participants to predict what changing `p` does,
then explain why a zero division remainder need not mean reconstruction succeeds.
Remove an expected zero-valued item from both operands and ask whether agreement
on the remaining keys settles the original question. Have them follow a mismatch
to its source and return. On a real phone/tablet, compare jump navigation with a
prototype bottom sheet: record lost context, occlusion, repeated scrolling, reach,
and whether camera motion is mistaken for changing mathematical extent.

Record unassisted completion, facilitator interventions, wrong-target actions,
lost edits, recovery actions, and whether the predicted effect matches the
committed one. Record time to the first usable result and time spent finding an
action, but do not optimize away deliberate mathematical thinking. Ask what felt
controllable, surprising, or difficult; record new questions the person chose to
pursue. A positive satisfaction comment does not establish conceptual transfer.

Before the next iteration, prioritize any lost work, incorrect target/effect, or
inability to operate essential controls. Then address recurring hesitation. The
release criteria for draft retention are zero lost input and zero accidental
commits in the specified deterministic cases. Human success-rate targets should
be set after observing a baseline, not invented as a validated threshold.

Use this record for each review:

| Field | Record |
| --- | --- |
| Build and environment | Commit, browser/device, viewport, input method, reduced-motion setting |
| Task and background | Goal, relevant experience, orientation given |
| Observation | Concrete action and outcome; quote only with permission |
| Interpretation | Hypothesis, alternative explanation, severity |
| Evidence | Test name or local recording/screenshot reference |
| Next change | Owner, bounded change, test that would disconfirm the hypothesis |

## 8. Development sequence

The list below records the original sequence and delivered increments. Following
the Icarus review, the [next PR sequence](UNIFIED_CANVAS_DESIGN.md#a-sequence-of-small-reviewable-pull-requests)
started with construction inspection and shared representations, now implemented.
Visible captured tracks follow. Reusable rules and editable recipes retain
explicit scope and compatibility contracts; those later steps remain planned.

1. **Stable authoring loop:** draft retention, accurate local feedback, and focus
   recovery. Delivered and tested against additive/modular controls;
   evaluate its one-draft constraint during human observation.
2. **Coverage as an explicit claim:** retain an independent expected domain; show
   zero/one/multiple witnesses; guard unique-owner adoption. Delivered as the
   [coverage instrument](COVERAGE_INSTRUMENT.md), with outside-key witnesses and
   assigned fields. Simple/additive browser tasks and a bounded Hermitian adapter
   case share the contract; complete Hermitian UI authoring remains open.
3. **Comparison and dependency views:** keep two results visible and follow a
   measurement to its input. [Delivered for coverage and quotient-driven motion](LINKED_EVIDENCE_VIEWS.md),
   including empty evidence and earlier drivers. [Radon weight-read navigation](WEIGHTED_EVIDENCE.md)
   now adds ordered tuples, explicit weight/source roles, and return views, tested
   against signed sums too. [Keyed comparison](KEYED_COMPARISON.md) now reuses these
   views for exact residuals and missing/outside keys over an independent domain.
   The [spatial workspace](SPATIAL_WORKSPACE.md) now shows all named roots and
   bounded definition paths. Local scopes and earlier unnamed reads stay explicit
   boundaries; they are not relabeled as current roots. Arbitrary captured-view
   pinning, editable live wiring and human layout trials remain open.
4. **Case versus replay controls:** [delivered explicit integer cases](PARAMETER_CASES.md)
   use named parameters in expressions and extents, with evaluate/apply and exact
   restored endpoints. Separate scrubbable replay has a static/reduced-motion path.
   Radon prime/composite and lattice growth transfer tasks exercise the controls. Evaluate whether
   motion helps identify a correspondence, not merely whether it is smooth.
   Ordered parameter tracks and recurrence steps are specified in the spatial
   brief as separate meanings of time; no new slider is delivered in this increment.
5. **Reusable instruments and notation:** composite read keys are now editable; named expressions,
   source constructors, and reusable lens/placement recipes. Measure the effort
   to transfer them across lessons before proposing a generic graph editor.
6. **Touch layout trials:** compare the current side/below sheet with a bottom
   sheet and a compact contextual palette on real devices. Check occlusion,
   reach, scrolling, alternative input, and ability to see the effect while editing.
   Shared camera buttons and focus-moving phone links are now the baseline, not
   evidence that the larger proximity problem is solved.

## Sources

Accessed September 22, 2026. These are research or original author/standards
sources. Their age does not establish applicability; each application above has
an explicit Kaleion test. The Parnas principle is retained from the repository's
existing design contract; ACM/CMU retrieval was unavailable in this run, so this
study does not claim a new full-text reading of that paper.

[R1]: https://www.cs.umd.edu/~ben/papers/Shneiderman1983Direct.pdf
[R2]: https://iihm.imag.fr/blanch/ens/2024-2025/INFO4/IHM/readings/2004-BeaudouinLafon-InteractionNotInterfaces.pdf
[R3]: https://www.cl.cam.ac.uk/~afb21/publications/CT2001.pdf
[R4]: https://onlinelibrary.wiley.com/doi/10.1207/s15516709cog1804_1
[R5]: https://www.nngroup.com/articles/ten-usability-heuristics/
[R6]: https://www.nngroup.com/articles/progressive-disclosure/
[R7]: https://www.microsoft.com/en-us/research/publication/animated-transitions-in-statistical-data-graphics/
[R8]: https://arxiv.org/abs/1608.02829
[R9]: https://www.w3.org/WAI/WCAG22/Understanding/

- **R1:** Ben Shneiderman (1983), *Direct Manipulation: A Step Beyond Programming
  Languages*, IEEE Computer 16(8), 57–69. See the synthesis on pp. 64–65.
- **R2:** Michel Beaudouin-Lafon (2004), *Designing Interaction, not Interfaces*,
  AVI '04, 15–22. Sections 3–4 develop instruments, reification/polymorphism/reuse,
  and situated interaction; this is the author's account building on his 2000 work.
- **R3:** Alan F. Blackwell et al. (2001), *Cognitive Dimensions of Notations:
  Design Tools for Cognitive Technology*. The review of dimensions and discussion
  of activity profiles are used here, rather than treating dimensions as laws.
- **R4:** David Kirsh and Paul Maglio (1994), *On Distinguishing Epistemic from
  Pragmatic Action*, Cognitive Science 18(4), 513–549. Publisher abstract inspected.
- **R5:** Jakob Nielsen, *10 Usability Heuristics for User Interface Design*,
  originally 1994; article last reviewed January 30, 2024.
- **R6:** Jakob Nielsen (2006), *Progressive Disclosure*, including its distinction
  from staged disclosure and its navigation costs.
- **R7:** Jeffrey Heer and George Robertson (2007), *Animated Transitions in
  Statistical Data Graphics*. Publisher abstract inspected; no effect-size or
  classroom-learning claim is inferred from it.
- **R8:** Brian Hempel and Ravi Chugh (2016), *Semi-Automated SVG Programming via
  Direct Manipulation*. Author abstract inspected; used as a design precedent,
  not evidence that arbitrary graphical edits have a unique symbolic meaning.
- **R9:** W3C, WCAG 2.2 Understanding documents:
  [Focus Order](https://www.w3.org/WAI/WCAG22/Understanding/focus-order.html),
  [Status Messages](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html),
  [Target Size (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html),
  [Dragging Movements](https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html),
  and [Pointer Cancellation](https://www.w3.org/WAI/WCAG22/Understanding/pointer-cancellation.html).
  These explanatory documents distinguish requirements, exceptions, and advice.
