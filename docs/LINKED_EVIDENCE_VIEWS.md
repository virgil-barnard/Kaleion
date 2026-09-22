# Keep a result beside the evidence for it

September 22, 2026 · A shared, read-only studio instrument

A missing match is hard to see on a canvas containing only matches. A measured
height is hard to explain when following its driver makes the height disappear.
The studio now keeps two captured views together and highlights the explicit
connection between them. The same renderer serves coverage, keyed reads, and
measurement contributors; it has no lesson names or mathematical predicates.

Run `python3 -m examples.studio` in the existing virtual environment. See the
[studio guide](CONSTRUCTION_STUDIO.md) for blank-canvas constructions.

## One interaction, three sources of correspondence

| Starting point | Control | Left view | Right view | Source of the link |
| --- | --- | --- | --- | --- |
| A coverage report | **View expected and matches** | Expected domain | Candidate domain with incidence | Declared key alignment in the captured coverage report |
| An occurrence receipt | **Follow keyed read** | Inspected output | Its actual driver version | Scoped references in the binding receipt |
| A measurement receipt | **View measurement and contributors** | Retained measurement | Original source universe | Measurement origin and captured contributor references |

**Evidence link** selects a correspondence. In coverage, this also updates the
report's key selection; tapping an expected point follows that key to its
candidates. Each card has an occurrence list for exact selection when points
coincide. **Inspect selected occurrence** opens its ordinary receipt while both
views remain visible. From coverage, **Back to coverage** restores the report.
From a keyed driver, the contributor control follows the next evidence step.

Each view has independent Fit, zoom buttons, and drag-to-pan. Changing the link
preserves both cameras. Faint points give context; their presence is not evidence
of membership. Candidate entries explicitly say **Match** or **outside relation**,
and contributor entries show their exact weights separately from source values.
A green outline selects one occurrence; repeated values remain distinct.

Closing the pair returns to the working canvas. Choosing another object, resuming
a draft, starting a construction, importing, or applying/undoing/redoing closes
it. A pair is temporary view state, not part of saved mathematical history. The
construction modes are hidden while inspecting the pair so a captured dependency
cannot be mistaken for the current editable root. Main workspace navigation
remains available; an unfinished draft can remain parked.

## Try the distinction that breaks the picture

Use the [coverage investigation](COVERAGE_INSTRUMENT.md): expected labels
`[2,0,1]`, candidates on a `3 × 3` grid, and relation `j < i`.

1. Check by source key `i` and expected key `value`, then open the paired views.
2. Select expected zero. It has three candidates and **zero matches**. The right
   list identifies all three as outside the relation.
3. Keep only matching occurrences, and check against the same expected domain.
   Expected zero is still visible on the left. There is now **no candidate group**
   on the right. Its empty list is disabled; no phantom point is drawn.
4. Try the additive example's outside key. The right has matches while the left
   explicitly has **no expected item**. Neither side is silently reconstructed
   from the other.

The renderer receives occurrence references from the report. It never matches
labels or positions, and does not infer equality or isomorphism from two views.

## Transfer to quotient-driven motion

Construct a `7 × 11` grid with value `11*i + 7*j`. Apply the relation
`value ≥ 77`, then count by `i`. The result is `[0,1,3,4,6,7,9]`.

For retained key three, the four contributors have `(i,j)` equal to
`(3,7), (3,8), (3,9), (3,10)`. Their labels are `82,89,96,103`, each with count
weight one. **View measurement and contributors** shows the count four beside
these four highlighted cells. Other source cells remain faint context. For key
zero, the measurement remains visible and the full source stays present, with
no highlighted contributors. This differs from one contribution of weight zero
or signed contributions that cancel.

Next add probe values `[6,0,3]`, and arrange them with `x=value` and `y` read from
the counts, target key `value`, source key `i`, read `value`. Their positions are
`[(6,9),(0,0),(3,4)]`. Rearrange the named counts to height `99`, then inspect the
probe at three. Its binding still reads the earlier captured count four. The
right card says **Captured dependency** and shows that version, rather than
substituting the current object with the same name. Following its contributors
still finds the four original cells. Existing immutable-definition semantics
are unchanged; this does not implement reactive source editing.

These are finite, independently checked constructions. Displaying the evidence
is not a proof of a universal quotient identity.

## Module boundaries and migration

| Decision that can change | Owner | Boundary |
| --- | --- | --- |
| How captured data becomes a bounded display record | `examples/studio/views.py` | Capture ID, exact field strings, floating placement, scoped row references, incidence mask |
| Which source produced a zero measurement | `measurement_evidence` in that module | Existing `Inspection` receipt plus the captured reduction origin's source universe |
| Which evidence is selected | Coverage/receipt controllers | Explicit lists of scoped references and explanatory notes; no camera coordinates |
| How two views look, select, and move | `web/evidence.js` | Two capture descriptions, declared links, semantic inspection callbacks; independent cameras |
| How a snapshot projects before placement | `web/views.js` | Shared display projection for the working canvas and evidence cards |
| What changes mathematical state | Existing adapter/history | Preview, Apply, undo/redo; none of the view queries enter this path |

This applies Parnas's criterion to changeable decisions. It introduces no core
operation, Python API, graph schema, history schema, dependency, or notebook
migration. The display serializer is shared with the existing object descriptions;
`exact_wire` remains importable from the experimental adapter. Two new read-only
host queries accept the current revision: `/api/capture` selects an evaluated
version and `/api/contributors` describes its measurement evidence. They only
read results retained in the current state, including dependencies. They cannot
request arbitrary historical states, evaluate unavailable data, or consume frames.

A contributor query expands at most 2000 items and rejects an incomplete result;
the ordinary compact receipt still defaults to 32. The source view independently
checks the same 2000-item limit. Unavailable captures and stale revisions are
errors, not empty views. Empty sources and zero fibers are valid. Captures that
already exist need no conversion.

## Validation and remaining questions

Five new offline tests cover coverage with an absent group; quotient contributors
and zero groups; zero, signed, and very large exact weights/labels; complete
40-item evidence beyond the compact receipt limit; earlier drivers; saved
history; empty sources; unavailable/stale captures; and pending-preview isolation.
Read-only cases run with graph execution disabled and check unchanged workspace
JSON. The required full suite passes **156 tests**, and `examples/discovery.py`
retains its expected counts, transforms, sieve, and history exports.

The expanded browser gate authors coverage and quotient constructions through
real controls. It checks linked key selection and report return, coincident-point
lists, a missing candidate group, independent cameras, pan cancellation, zero
contributors, earlier drivers, keyboard inspection, and unchanged saved data.
Chromium 153.0.8010.0 passes; desktop and 320-pixel screenshots were inspected.
Existing checks still cover draft recovery, exact previews, reversible placement,
save/open, and four viewport widths. Run:

```sh
python3 -m unittest discover -s tests -p test_studio_views.py -v
python3 -m unittest discover -s tests -v
python3 examples/discovery.py --out build/example-output
node docs/studies/check-construction-studio.cjs
```

The browser command requires a separate Playwright/Chromium installation; see the
[host options](CONSTRUCTION_STUDIO.md#validation-and-reproduction). Generated
reports/screenshots remain in ignored `build/studio-check/`. No notebook source
or animation/video export changes in this increment.

These are behavioral checks, not a novice usability study. Touch is emulated;
physical tablets, Safari, and screen readers remain untested. Cards stack on a
phone and still require substantial vertical scrolling. 3D captures show an
explicit XY projection; there is no 3D camera here. There are two temporary views,
not arbitrary pinned canvases or synchronized multi-root replay. Contributor
selection currently explains one measurement at a time; it does not create a
new lens. Unlinked context points never invent a correspondence.

The [weighted-evidence follow-up](WEIGHTED_EVIDENCE.md) now implements the Radon
transfer: ordered key tuples, contribution-specific weight reads, source-field
reads, and return navigation preserving selections and cameras. One shared
receipt module replaces the previous inline controller. The compact/complete
receipt distinction and read-only capture contract above remain unchanged.

**Next experiment:** exact parameter-case controls, kept distinct from motion
replay. Continue comparing stacked cards with a compact sheet using the design
study's human tasks; phone navigation remains an open usability question.
