# UI design for mathematical discovery

September 22, 2026 · Research, studio audit, and a testable design direction

**Recommendation:** build a workspace of reusable mathematical instruments, with
low-cost experimentation and visible consequences. Judge it by whether someone
can transfer an interaction to an unfamiliar construction, explain what changed,
and pursue their own question. Completing a scripted lesson is necessary evidence
of expressiveness, but insufficient evidence of discovery or novice usability.

This study reviews primary HCI research, authors' design guidance, and W3C
accessibility guidance. It audits the studio at merged commit `1c35d358`, after
shared group selection and compact formula editing. Findings about the code and
browser are observations; proposed effects on learners are hypotheses. No human
participants were recruited and no accessibility conformance audit was performed.
The existing [all-lesson coverage matrix](CONSTRUCTION_STUDIO.md#all-lessons-are-the-target-remaining-composition-coverage)
remains the capability inventory. This document supplies the evaluation criteria.

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

## 4. Audit of the current studio

Severity here is local prioritization: **high** risks lost work or misleading
state; **medium** adds substantial friction or an untested interpretation;
**open** requires capability development or human observation.

| ID | Baseline finding at `1c35d358` | Evidence | Priority / disposition |
| --- | --- | --- | --- |
| A1 | Clicking another object while composing removes the form, with no draft-return control | `studio.js` object handler clears the panel; fresh-browser probe reproduced it | High · preserve a draft through inspection in this increment |
| A2 | After a valid preview, changing its expression disables Apply but leaves the old ready message | Fresh-browser probe and `changed()` handler | High · report current draft phase beside its controls |
| A3 | Activating a formula token with Enter replaces the focused node; focus falls to the document body | Fresh-browser probe of `expressions.js` | High · preserve a useful focus destination on open/edit/close/undo |
| A4 | Key removal destroys a focused chip without assigning a successor | `groups.js` inspection | Medium · return focus to the next chip or field picker |
| A5 | Group selection separates candidates from incidence and retains declared zero groups | Group contracts and additive/modular browser investigations | Preserve; use the same distinction in coverage checks |
| A6 | Preview/apply and captured history are separate; driver inspection can use saved data | Adapter/core contracts and save/reopen browser checks | Preserve; no new numerical execution in the view layer |
| A7 | Formula, canvas, and actions can be far apart on a narrow screen | 320 px screenshots: the form is below the canvas | Medium · local feedback now; compare a mobile bottom sheet/sticky preview later |
| A8 | Contextual actions have visible and keyboard alternatives; View pan/zoom still lack complete button alternatives | Context resolver and gesture handlers | Open · add equivalent camera controls; no WCAG conformance claim |
| A9 | A single object canvas obscures comparisons and immutable earlier inputs | Existing studio limit and lesson coverage matrix | Open · paired views and dependency selection need a concrete cross-lesson trial |
| A10 | No novice task or physical tablet trial has been conducted | Available evidence consists of code, deterministic fixtures, and emulated Chromium | Open · run the formative protocol below |
| A11 | The first object-tab click after editing a number can disappear | Input blur triggers a render that replaces the tab before its click arrives; reproduced in the baseline probe | High · preserve unchanged controls and test one-click navigation |

The baseline probe uses actual controls and records the browser version, focused
element, message, Apply availability, and presence of a draft-return control.
Reproduction sequence: create A and B; start a relation on A; activate a formula
number with Enter; preview; edit the number; select B. The first click can be
swallowed (A11); clicking again navigates and loses the draft (A1). The JSON trace
is a local build artifact, not a fabricated participant observation.

## 5. First design experiment: an idea survives a detour

**Hypothesis:** retaining an unfinished construction while someone inspects a
source reduces the rebuilding needed to explore. Keeping feedback and focus near
the edited part should make its state easier to interpret. Behavioral tests can
verify retention and state consistency; only human trials can assess the effect
on thinking, comfort, or discoverability.

This increment implements one recoverable draft in the current browser tab:

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

### Results of this increment

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

### Proposed human observation

The subsequent [coverage instrument](COVERAGE_INSTRUMENT.md) provides another
executable task for this protocol: distinguish a zero group from a wholly absent
candidate key, inspect witnesses, then adopt a sole value as a new field. It is
tested through modular and additive browser constructions and a restricted
Hermitian adapter case. The suite now has 151 passing tests; this extends the
behavioral evidence without adding human-study results. Paired views remain the
next experiment for audit item A9.

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

1. **Stable authoring loop:** draft retention, accurate local feedback, and focus
   recovery. Delivered and tested against additive/modular controls in this increment;
   evaluate its one-draft constraint during human observation.
2. **Coverage as an explicit claim:** retain an independent expected domain; show
   zero/one/multiple witnesses; guard unique-owner adoption. Delivered as the
   [coverage instrument](COVERAGE_INSTRUMENT.md), with outside-key witnesses and
   assigned fields. Simple/additive browser tasks and a bounded Hermitian adapter
   case share the contract; complete Hermitian UI authoring remains open.
3. **Comparison and dependency views:** keep two results visible and follow a
   measurement to its input. Use Radon reconstruction and quotient-driven motion.
4. **Case versus replay controls:** exact parameter stepping beside scrubbable
   recorded motion, with a static and reduced-motion path. Evaluate whether
   motion helps identify a correspondence, not merely whether it is smooth.
5. **Reusable instruments and notation:** named expressions, composite read keys,
   source constructors, and reusable lens/placement recipes. Measure the effort
   to transfer them across lessons before proposing a generic graph editor.
6. **Touch layout trials:** compare the current side/below sheet with a bottom
   sheet and a compact contextual palette on real devices. Check occlusion,
   reach, scrolling, alternative input, and ability to see the effect while editing.

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
