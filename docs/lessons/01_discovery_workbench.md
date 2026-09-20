# 01 · Discovery workbench

**Status:** available. [Open the notebook](../../notebooks/01_discovery_workbench.ipynb).

**Question:** How can the same integers reveal different patterns through placement,
incidence, and motion?

**Background:** integer arithmetic, elementary coordinates, and readable Python.
This notebook is a capability tour rather than a single theorem.

## Narrative

1. Place one sequence on a line, a snake, and a 3D helix. Ask what has changed and
   what remains the same: occurrence, integer content, and placement are distinct.
2. Apply lenses to values, logical indices, and geometry. A relation and the
   arrangement on which it is evaluated are separate objects.
3. Count a quotient region by retained row key. The counts become a new arrangement
   with contributor IDs, including its zero group.
4. Use those values to drive gathered/cyclically shifted remainder tables. Then
   use a driver on a scattered 3D cloud to separate changes in placement from
   changes in integer contents.
5. Scrub rectangular spiral cases. The incidence reads structural cycle endpoints;
   it is not a primality test disguised as a visual rule.
6. Try gather, substitution, tile, padding, a Young diagram, and a 3D incidence.
7. Capture, edit, undo, and reopen the investigation. Compare a recorded path with
   its reversed samples.

## Key observation

For `a=11, b=7`, the quotient-region counts are `[0, 1, 3, 4, 6, 7, 9]`.
They are mathematical inputs, not a summary printed beside the image. The
[next lesson](02_floor_sum_proof.md) identifies their exact floor-quotient meaning.

## Experiments

- Change the placement while retaining the same values and occurrence identities.
- Reorder a driver while preserving unique keys; its keyed action should agree.
- Move a lens and observe which universe is being counted.
- Inspect a count of zero and compare it with a failed dependency.
- Scrub past several spiral cases, then backward, and examine the retained interval.

## What this establishes, and what it does not

Finite assertions exercise the API contracts. The spiral example checks the stated
finite range; this tour does not supply a universal sieve theorem or a proof assistant.
The general recursive arrangement language, a GPU backend, and the touch UI remain
future work. Video export is an explicit 1D/2D raster adapter; 3D stays interactive.

The UI lesson is the repeated separation between **construct**, **place**, **inspect**,
**measure**, and **transform**. A single visual item can participate in several of
these roles without merging their responsibilities.

## Functions and authoring scaffolding

This notebook defines **no local functions**. Its scaffolding is inline; that
still represents authoring work. The [cross-lesson inventory](HELPER_INVENTORY.md)
compares these responsibilities with the later lessons.

| Inline responsibility | Primitives and choices required |
| --- | --- |
| Give one sequence several shapes | `Collection`, `arrange`, expressions, and trigonometry define the line, snake, and helix; identity checks distinguish placement from replacement. |
| Sweep a lens and measure a region | `Lens.window`, `where`, `Sweep`, and `count(by=...)` declare the domain, relation, cases, and retained keys. Counts become a separately placed profile. |
| Reuse a measurement as an argument | Explicit `bind` keys connect counts to a roll, displacement, or value change; a scalar count supplies a `Construction` parameter. `Move` and `Values` demonstrate distinct effects. |
| Recognize a structural spiral pattern | A rectangular-spiral sweep uses the `cycle_end` role, retains observations across specified cases, and checks the resulting values against an independent composite-number enumeration. A Plotly chart presents the retained mask. |
| Exercise other constructions | Lookup, gather, tile, pad, a Young diagram, and a three-dimensional incidence have their own small declarations and checks. |
| Present and preserve changes | Workspace edits, captures, undo, frame sampling, captions, graph/workspace JSON, and HTML/MP4 exports are assembled explicitly. Discrete sweep cases and smooth transition frames have different sampling rules. |

**Shared functions used.** There are no imports from the lesson helper modules.
The public viewers `snapshot_figure`, `animation_figure`, `transition_figure`, and
`write_mp4` consume snapshots or frames; they do not define the constructions.

**Abstraction evidence.** Transition sampling, captions, and export bookkeeping
recur throughout the series. Those are candidates for small authoring helpers.
The variety of domains here is also a useful check on any proposed abstraction:
it must not assume that an arrangement has rows or that screen position is a key.
