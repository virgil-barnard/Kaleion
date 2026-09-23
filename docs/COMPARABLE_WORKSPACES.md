# Learning from comparable mathematical workspaces

September 23, 2026 · Documentation survey and Kaleion design decisions

**Recommendation:** make the distinctive experience the passage from a visible
pattern to a reusable, explainable measurement. An author should be able to turn
that measurement into a new arrangement or movement, follow its contributors,
and change their mind without losing the construction. Beautiful animation and
short notation support this experience; neither is a novelty claim by itself.

This is a primary-source desk survey, not a hands-on comparative usability study,
an exhaustive prior-art search, or proof that another system cannot express our
examples. The sources below establish documented capabilities. The borrowing
decisions and proposed advantages are our inferences. Programmable systems can
implement workflows beyond their standard interfaces; an undocumented feature
must not be scored as absent. Sources were checked on the date above; no pricing
or market-share comparison is attempted.

Kaleion's baseline is merged main `73774cf` (PR #33), read alongside the
[UI study](UI_DESIGN_STUDY.md), [continuous canvas](CONTINUOUS_CANVAS.md),
[lesson coverage matrix](CONSTRUCTION_STUDIO.md#all-lessons-are-the-target-remaining-composition-coverage),
and [core refinement plan](CORE_REFINEMENT_PLAN.md). The companion increment adds
[compact relation notation](RELATION_NOTATION.md); other proposals here remain
future work.

## What is already well established

| Workspace and emphasis | Documented capability | Useful concept for Kaleion; constraint on borrowing |
| --- | --- | --- |
| **GeoGebra** · dynamic mathematics and reasoning | The construction protocol exposes dependencies through replayable steps; ProveDetails distinguishes symbolic conclusions, conditions, and undecided results. [G1][G1] [G2][G2] | Keep construction and assumptions visible. A replayable history or a geometry proof command is established prior art. Our finite comparison must never impersonate a general proof. |
| **Desmos** · concise expressions and interactive graphs | Actions change variables through clickable objects or a ticker. Keyboard operation, mathematical speech, audio trace, and Braille support have explicit documentation, with differences across calculators. [D1][D1] [D2][D2] | Connect a readable expression to a visible effect; treat non-pointer access as part of the instrument. Separate changing an exact case from replaying a saved path. |
| **Polypad** · mathematical play and manipulatives | Its catalog includes fraction bars, polyhedra, function machines, logic gates, and sound/music activities in a browser workspace. [P1][P1] | Make the first useful gesture produce something tangible. Avoid turning Kaleion into an ever-growing shelf of lesson-specific objects. Mathematical art and sonification are already explored here. |
| **Graspable Math** · symbolic manipulation by gesture | The official learning material covers touch/mouse algebra, term tracing, scrubbing, derivations, substitution, and undo. [M1][M1] | A term can be something to act upon. Highlight a term's meaning before offering its operations. Gestural algebra and derivation tracing are not new inventions of Kaleion. |
| **CODAP** · exploration through linked data representations | Selecting cases highlights related data; dragging an attribute creates a hierarchical collection, with group-level summaries. [C1][C1] [C2][C2] | A declared group should be easy to pick, inspect, and measure. Preserve our distinction between no observed member and a declared zero fiber when adopting such direct grouping. |
| **Wolfram notebooks** · computational exploration | Manipulate derives controls from specifications, supports discrete values and locators, saves local state, and offers explicit update and undo options. [W1][W1] | Borrow coherent parameter controls and scoped state. Automatic evaluation must respect Kaleion's exact budget, failures, and capture boundary. Controls generated from mathematical definitions are established. |
| **SageMath + Jupyter** · programmable mathematical research | Sage documents finite prime/extension fields and notebook interaction widgets. [S1][S1] [S2][S2] | Reuse specialist arithmetic through a future explicit adapter instead of recreating a CAS. Import a declared domain and representation, not just an untyped array of numbers. |
| **CindyJS / CindyGL** · interactive geometry and GPU visuals | Geometric operations and CindyScript support interactive constructions; CindyGL exposes GPU rendering to mathematically oriented authors. [Y1][Y1] | Learn from responsive visual experimentation. A renderer can change independently of the exact evaluator; GPU floating coordinates cannot decide incidence or equality. |
| **Manim** · authored mathematical animation | Transform exposes target objects, custom paths, and arc controls. [A1][A1] | Use timing, staging, and paths to make correspondence legible. Keep the mathematical correspondence separate from the path artistically chosen to display it. |
| **Observable** · reactive computational documents | Its runtime represents variables through named dependencies, scoped modules, and observers reporting pending, fulfilled, or rejected results. [O1][O1] | Show what depends on a choice and keep failures local. Reactivity is useful infrastructure, not evidence or a reason to silently mutate retained captures. |
| **Penrose** · diagrams from mathematical descriptions | Domain, Substance, and Style separate object vocabulary, mathematical relationships, and visual interpretation; layout is solved as an optimization problem. [N1][N1] | This is especially relevant prior art for our separation of meaning and placement. Borrow interchangeable visual interpretations; an attractive layout is not verification of the assertions it illustrates. |
| **Snap!** · composable visual programming | Custom blocks, first-class lists and procedures support user-created abstractions in a browser-based drag-and-drop language. [B1][B1] | Eventually let an author package a successful construction with explicit inputs. Blocks can communicate kinds of inputs, but a full programming palette would recreate the complexity we are trying to remove. |

These systems supply strong counterexamples to a claim that interactive
mathematics, animated construction, visual programming, reusable computations,
linked views, or a separation of mathematics and appearance is unique to Kaleion.
We should borrow their useful interaction ideas and compare actual tasks before
claiming a lower entry barrier.

## Where Kaleion could be distinctive

The promising combination is **arrange → relate → measure → reuse → explain**.
The result of measuring is another ordinary mathematical object, not a terminal
chart annotation. For example, a lens on integer pairs yields counts keyed by a
sum; those counts or ordered partial sums can supply the coordinates of another
arrangement. Inspecting a coordinate should lead back to the counted/weighted
occurrences, even after a different case has been explored.

This is a design position to test, not a claim of world-first functionality:

| Candidate distinction | Existing Kaleion evidence | What remains unestablished |
| --- | --- | --- |
| **Measurements become material for further construction** | Lessons 04–07, named keyed reads, weighted prefixes, contributor receipts | That a new author recognizes and uses this loop without a recipe |
| **Multiplicity and placement stay independent** | Equal values, repeated gathers, coincident positions, explicit keys and occurrence identity have distinct contracts | That authors can see the distinction without learning internal terminology |
| **Motion exposes a correspondence that can be inspected** | Captured history, reverse path sampling, separate case evaluation, earlier-source inspection | A general, approachable motion authoring instrument covering every lesson |
| **Failures and missing information remain visible** | Zero groups, declared coverage, missing keys, exact residuals, isolated failed roots | That the explanation is concise enough to invite further exploration |
| **One compositional vocabulary spans unrelated discrete mathematics** | Quotients, finite Radon transforms, partitions, codes, and finite geometry share core operations | Complete creation of all eleven lessons from a blank canvas; the current coverage matrix explicitly records gaps |

An appropriate public description today is: *an experimental canvas for composing
discrete mathematical constructions, reusing exact measurements, and following
the evidence behind motion*. Calling it easier, more powerful, or more original
than all alternatives would outrun our evidence.

## Gaps that matter more than additional features

The current browser studio deliberately limits a workspace to 60 roots and 2,000
source occurrences. It needs a local Python environment. Its controls expose a
useful subset of the core; polished notebooks still contain lesson scaffolding.
The following priorities concern these actual limits, not missing checkboxes in
a competitor matrix.

| Priority and gap | Small next experiment | Owner and gate |
| --- | --- | --- |
| **Now: notation costs too many edits** | Keep pattern starters; offer short rules and return to term controls. Try a modular line, lattice window, and binary projective incidence. | Delivered in this increment by the studio syntax adapter. Same exact predicate and saved format; no core primitive. |
| **Next: syntax is still detached from its meaning** | Select `i`, `j`, a condition, or a group key; highlight its scope on the existing canvas, with a text description. Offer tap-to-insert field/operator choices if typing is the bottleneck. | Presentation and expression editors. No evaluation merely to focus a name. A condition preview must be explicit and labeled. Test whether an author can explain a zero. |
| **Next: reuse still feels like completing a form** | Drag a measured result toward an arrangement; propose a coordinate/read binding with visible key matching. Keep the selector/button route. | Existing command adapter owns binding; gestures only propose. Reordered driver storage must produce the same placement; an ambiguous key must stop the proposal. |
| **Then: motion is easier to watch than to compose** | Compare two exact endpoints with persistent identity marks; let the author choose straight/arc presentation and scrub the saved path. Try stacking and a finite permutation with the same tool. | Correspondence remains in the core; timing/path/camera remain in presentation. Labels, births/deaths and reduced-motion endpoints must be inspectable. Do not infer a bijection from proximity. |
| **Then: discoveries are hard to preserve as questions** | Pin two captured cases, a sentence, a finite check, and a counterexample as an observation card. | Build on captured observations and comparison, adding presentation state only where sufficient. A family of computed cases needs its own evidence contract before becoming a mathematical input. |
| **Later: authors cannot make their own reusable instruments** | Extract an equal-sum/count/place recipe, expose its domain, keys and parameters, then apply it to line incidence. | Start with an authoring recipe over existing definitions. Define explicit bindings before proposing a general macro or new graph node. |
| **Ongoing: access and rendering limits** | Test keyboard and physical touch from a blank canvas; include a nonvisual explanation of group/count/correspondence. Benchmark larger scenes before replacing SVG or introducing level of detail. | Accessibility and rendering consume captures. Any sampling must be labeled as a view, never as mathematical coverage. More frames are not automatically more understandable. |
| **Later: setup and interchange cost** | Share a self-contained captured investigation that can be opened and inspected without Python; distinguish inspection from supported new evaluation. Investigate finite-field/CAS adapters separately. | Persistence and execution are different modules. Preserve exact domains, versioned definitions, labels and provenance. Do not promise a serverless evaluator in an exported picture. |

The [UI study's uncoached task](UI_DESIGN_STUDY.md#interaction-reset-after-maintainer-feedback)
remains the immediate human validation priority. The survey does not justify
resuming a large feature queue before learning from that task.

## An interface that feels like making something

The proposed artistic quality comes from continuous agency: make material,
touch what interests you, try an operation, see its consequence, and reuse it.
It does not require erasing mathematical distinctions.

- **A visible object is the starting point.** Tap selects it; hold or Details
  opens the same nearby choices. Hold is a shortcut, not the only way to discover
  an action. Background creates material; it does not inherit a hidden target.
- **A tool has a stable meaning.** Relation chooses matches; Sum / count produces
  a measurement; Arrange chooses coordinates. Their inputs can vary across
  lessons while their promises remain stable.
- **Notation is a view of the same construction.** Starters, term controls, and
  short text must agree. No separate text-only engine and no automatic guess
  that a handwritten sketch establishes a universal rule.
- **Movement should reveal an invariant or a break.** Highlight one item and its
  destination, let all related items follow, and keep endpoints available.
  Trails and ghosts are presentation choices. A counterexample should be as easy
  to inspect as the beautiful case.
- **Depth appears when needed.** A first count can be playful; tapping the result
  reveals its keys, zero groups, and contributors. A small interface cannot mean
  concealed assumptions.

These are hypotheses. Our current mobile screenshot still shows crowded object
labels after several constructions, and text entry still requires scrolling in
the bottom sheet. Automated layout checks only establish that controls fit and
remain usable by the script; they do not establish comfort with a phone keyboard.

## Keep the decisions separate: applying Parnas

The [project's information-hiding rule](../DESIGN.md#decompose-by-decisions-that-may-change)
gives a useful filter for every borrowed concept:

| Changeable decision | Owner | Must not decide |
| --- | --- | --- |
| How an author states a predicate | Starter/term/text editors and bounded syntax adapter | Numeric truth, contributor membership, or correspondence |
| Which operation a gesture proposes | Contextual command routing | Meaning based on a notebook name or current camera |
| What a count, read, reindex or domain means | Exact core definitions and evaluator | Widget layout, animation timing, or color |
| Which exact case and history step was retained | Capture/history | Re-running a later graph to reconstruct old evidence |
| How objects are laid out, emphasized and animated | Scene, evidence views and motion presentation | A proof, an inferred key match, or a sampled replacement for a finite domain |
| How a mathematical assertion is justified | Explicit finite reports; future proof adapter | A conclusion inferred from a convincing animation |

Do not introduce a universal “interactive mathematical object” superclass that
owns all six decisions. Shared controls should compose existing contracts. If a
new domain operation is necessary, first document a construction that cannot be
expressed and the independent test its contract requires.

## A comparison we should actually perform next

Use the same tasks in Kaleion and appropriate comparison tools, allowing an
experienced author to prepare reusable material where that is part of the tool's
normal workflow. Record setup separately from the learner's work. Do not grade
an animation library as a failed novice editor or assume a prepared applet equals
creation from scratch.

1. **Modular fibers:** create `j = (2*i+1) mod 5`, count by `i`, reuse the counts
   as heights, and inspect one contributor. Change to modulus 6 and try solving
   in the reverse direction; repeated/missing fibers challenge the assumption
   that every slope is invertible.
2. **Lattice window:** bound an incidence with two inequalities, predict a zero
   group, move a bound, then distinguish a new calculation from replay.
3. **Projective incidence:** construct the nonzero binary-vector dot-product
   relation, see three points per line, and omit one vector. Equal row counts
   alone must not certify a projective plane or an isomorphism.

For each task record time to first meaningful result, help requests, wrong
targets, lost work, recovery, and the author's explanation of domain and result.
Ask for a self-chosen variation and an unsupported conjecture. Compare completion
with understanding; quick clicking alone is not the success criterion. Repeat
the transferred task without teaching its route. Include physical touch and
keyboard users, and obtain permission before any recording.

If novices cannot construct a variation, simplify the same instrument before
adding another. If they can construct it but cannot explain a zero or a changed
case, improve the evidence presentation. The useful novelty would be demonstrated
by what people can discover and transfer, not by how many controls we invent.

## Primary sources

[G1]: https://geogebra.github.io/docs/manual/en/Construction_Protocol/
[G2]: https://geogebra.github.io/docs/manual/en/commands/ProveDetails/
[D1]: https://help.desmos.com/hc/en-us/articles/4407725009165-Actions
[D2]: https://help.desmos.com/hc/en-us/articles/4404860698253-Introduction-to-Accessibility-Features
[P1]: https://polypad.amplify.com/
[M1]: https://graspablemath.com/learn
[C1]: https://codap.concord.org/how-to/getting-started-with-tables/
[C2]: https://codap.concord.org/how-to/how-to-create-and-use-a-nested-or-hierarchically-structured-table/
[W1]: https://reference.wolfram.com/language/ref/Manipulate.html
[S1]: https://doc.sagemath.org/html/en/reference/finite_rings/sage/rings/finite_rings/finite_field_constructor.html
[S2]: https://doc.sagemath.org/html/en/reference/repl/sage/repl/ipython_kernel/interact.html
[Y1]: https://cindyjs.org/
[A1]: https://docs.manim.community/en/stable/reference/manim.animation.transform.Transform.html
[O1]: https://github.com/observablehq/runtime
[N1]: https://penrose.cs.cmu.edu/docs/ref
[B1]: https://snap.berkeley.edu/about

Links in the comparison table identify the official manuals, project documents,
and author-maintained sources used. Marketing claims of universal ease, device
coverage, or superiority were not adopted as measured facts.
