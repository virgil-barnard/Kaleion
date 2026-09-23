# A workspace for composing objects

**Current implementation:** the [shared scene](SHARED_SCENE.md) now replaces this
first preview-panel experiment with one coordinate scale, local frames, cell/point
marks, 3D orbit and view slices. Drag object names to move view offsets. The
construction/combination contracts below still apply; the historical independent
scales and unsaved-layout limits have been superseded by the versioned canvas
document. Focus and current replay retain their labeled XY views.

The original interaction experiment started with several mathematical objects visible
together. The maintainer's desktop feedback supplied the concrete need: saved
canvases made the mathematics and replay discoverable, but the single-object
editor still did not feel like a place to build. That increment added a spatial
overview and reviewed composition gestures while retaining the existing Focus
view for exact inspection and authoring.

**After PR #29:** the maintainer still found object construction unclear and
requested a closer review of Icarus's direct canvas interactions. The
[unified canvas proposal](UNIFIED_CANVAS_DESIGN.md) records that review and the
implementation sequence. [Construction inspection](CONSTRUCTION_INSPECTION.md)
now reveals the selected object's declaration and lets inputs be followed with
a return path. This page documents the preview-panel experiment; use the
[shared-scene guide](SHARED_SCENE.md) for its implemented successor.
The planned track contract distinguishes acquisition
from seeking: evaluating new samples is explicit, while scrubbing retained
samples is read-only.

## Try this increment

These composition steps remain useful. In the current scene, drag object names;
the [shared-scene guide](SHARED_SCENE.md#start-with-the-objects) explains marks,
charts, cameras and saving the view.

Run `python3 -m examples.studio` in the existing environment, then open
`examples/canvases/07_equal_sums.json`.

1. In **Workspace**, select **Moving pairs**. All eight named objects remain
   visible. **Move objects** drags their name handles; mathematical positions,
   values and history stay unchanged. **Fit** shows the whole workspace;
   **Selected** centers the chosen object at a more readable scale.
2. Switch to **Connections**. The selected object's paths stand out. Expand
   **Inputs of Moving pairs** to select an input by name. Pairs supplies its
   occurrences; Ranks supplies values through a read.
3. Drag **Left** toward **Right**. A destination outline appears; release opens
   a proposal. Choose **Make every pair**, review the two named roles, and
   Preview/Apply. The result has sixteen distinct occurrence tuples. Return to
   Workspace to see it alongside its inputs. **Combine…** supplies the same
   path with two selectors, without dragging.
4. Select **Counts**, choose **Combine…**, and choose **Left** as destination.
   **Use source values as destination height** opens Arrange with an editable
   keyed read. The default reads Counts' `value`, matching target `key` to
   driver `key`. Preview/Apply puts Left at heights 1, 2, 3, 4. Counts is now a
   visible input to Left; earlier Pairs still refers to the earlier Left.
5. Double-click an object or choose **Focus** for Occurrences, Groups, camera
   controls, exact labels, comparison and captured evidence. **Options**,
   right-click, touch hold and Shift+F10 open the same contextual tools.
   Undo/Redo of a movement opens Focus and its captured replay scrubber.

Neither a drop nor opening a proposal evaluates or commits work. Invalid keys
fail during Preview; the applied workspace survives. An unfinished declaration
can be parked while browsing the workspace and resumed with its original inputs.

**Historical rendering limits (PR #29):** previews used independent XY scales and
drew at most the first 180 captured occurrences. Layout and camera reset on Open;
Save exported only the ordinary schema-1 workspace. The shared scene supersedes
those limits with common units, a labeled 6000-mark budget and optional saved
view state. Empty and failed roots remain selectable. On narrow screens, use the
object buttons and Selected/zoom/pan controls; a fitted overview alone is too
small for precise selection.

## What a connection means

The first connection overlay is a **definition map**, not editable live wiring.
It does not infer a correspondence from lengths, labels, coordinates or proximity.

| Visible relationship | Contract |
| --- | --- |
| Solid input path | Walk through unnamed construction inputs to the nearest currently named definition. The path can contain several operations. |
| Dashed read path | A definition-valued expression input matches a currently named definition. This includes keyed reads, scalar reads and source-address reads; it is not a claim that all such reads use keys. |
| Unshown input boundary | An earlier/unnamed read, unnamed source, or local parameter case cannot safely be represented as a connection to a current named root. Report it in the selected object's input list. |
| Two names for one definition | Both aliases can be shown. Independently constructed equal values do not create an edge. |

Changing the placement of a named root creates a new immutable definition. Existing
consumers retain their earlier inputs. The overlay therefore removes a stale
name-to-consumer edge instead of quietly retargeting it. A local parameter case
is also a boundary: its unscoped internal definition must not connect to a current
root evaluated under another parameter environment. This deliberately incomplete
map stays honest about what is not shown. Focus's captured evidence remains the
route to the actual driver value, matching key, weight and source occurrence.

The adapter summarizes definitions without executing them. The browser owns
layout, selection, camera and provisional drag paths. A proposal seeds the same
Product or Arrange editor as the ordinary menu; Preview/Apply, budgets, history
and inspection continue through the existing semantic boundary. No core
operation, dependency, saved schema or lesson recipe changes.

## Keep three meanings of time explicit

A single unlabeled time slider would conceal different mathematical questions.
Use a common visual control only when its selected track and meaning are explicit.
The following track design is **planned**, not implemented by this increment.

| Track | Meaning of a sample | What advancing it may do | Proposed visible label |
| --- | --- | --- | --- |
| Generation | A bounded recurrence's discrete step, with seed/state/update rule | Evaluate the next mathematical state; retain its derivation | `Generation · step 12` |
| Cases | A selected entry in an explicitly ordered list of parameter bindings | Evaluate an exact case or select an already captured one | `Case · p = 4 · 2 of 5` |
| Replay | Progress along a previously captured construction transition | Sample presentation geometry; no evaluation | `Replay · 40%` |

For a case track, declare a parameter once, then choose either an exact integer
interval with step or an arrangement's value field and explicit member order.
Track position is an ordinal sample index; it is not the parameter value or
physical time. Repeated parameter values may remain distinct visits. A failed
case remains an inspectable failed sample, never a zero or a frame to skip silently.
Parameter `p = 3` and `p = 4` must not acquire an interpolated `p = 3.5` because the
thumb is between ticks. In the Radon canvas, the latter includes a point where
division remains exact while reconstruction is wrong; a successful division is
not a successful reconstruction check.

The proposed sequence is **declare track → evaluate bounded cases → inspect
captured samples → apply a chosen case**. Scrubbing retained samples should make
no evaluation requests and should not add one Undo step per pointer event. An
uncaptured sample must explicitly request evaluation. Choosing a case updates
all dependent views together; independent roots stay available. Memory limits,
cancellation, retention and saved-track compatibility need a contract before
this is implemented. Existing Cases and Replay remain separate and functional.

## Next development sequence

1. **Observe construction, not just playback.** Ask the maintainer to create a
   product, inspect a read connection, and use a measured height. Record where
   Focus or the proposal loses context. Compare desktop and physical phone
   interaction before increasing the permanent tool vocabulary.
2. **Spatial manipulation and quick generation.** Add a small x/y/z assignment
   control with a visible coordinate declaration. Distinguish camera rotation,
   swapping placement coordinates, and transposing a rectangular domain. A
   planar object can occupy XY/XZ/YZ without pretending every source has a
   three-dimensional logical shape. Start quick generators with existing
   sequence/grid builders. A general recurrence needs an explicit seed, state,
   update rule, order and finite bound; use a concrete lesson to decide whether
   an existing recipe suffices or a bounded evaluator operation is warranted.
3. **Ordered parameter tracks.** Implement the case-track contract above and
   validate prime/composite Radon plus a lattice-growth transfer task. Measure
   whether users can distinguish a new evaluation from recorded playback.
4. **Richer composition and editable dependencies.** Offer concatenation only
   with its axis/shape and occurrence semantics visible. Equal-shaped vector
   arithmetic also needs an explicit pairing rule and chosen fields. Editing
   an existing connection must preview the affected definitions and failures
   and adopt an explicit replacement; a root name is not currently a mutable
   variable socket. Retain old captures and avoid a history entry per drag.

The game-like quality sought here is direct action, legible constraints, quick
feedback, reversible experiments and visible consequences. Points, badges and
decorative rewards do not address the current authoring problem.

## Evaluation and design reference

The [UI study](UI_DESIGN_STUDY.md) and [touch proposal](TOUCH_WORKSPACE.md) remain
the review criteria: active subject, semantic operation, visible effect, and a
recoverable idea. This increment reduces the need to remember unseen objects;
the costs to evaluate are visual density, independent scales, cable occlusion,
and the switch between Workspace and Focus. Layout is still a prototype, not a
validated response to all eleven lessons.

The maintainer supplied GearBlocks as an interaction reference. Its
[official building-controls development note](https://www.gearblocksgame.com/2021/10/29/gearblocks-on-steam-10/)
(October 29, 2021) describes drag/drop selection, explicit manipulation tools and
highlighting possible attachments. The design inference for Kaleion is to show
possible destinations and expose the chosen action before committing it. This
is not a claim that a mechanical joint and a mathematical dependency share a
contract, or that this note describes every current GearBlocks control.

Validation records live in `docs/studies/check-spatial-workspace.cjs`,
`check-saved-canvases.cjs`, `check-construction-studio.cjs` and
`tests/test_studio_connections.py`. Browser emulation is not physical-device,
screen-reader or novice usability evidence.
