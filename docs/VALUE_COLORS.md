# Color as a measuring aid

Select any object, then **Appearance → Color**. Choose a uniform object color or
an integer field, a palette and its direction. **Apply colors** changes only the
view. **View → Theme** selects System, Light or Dark for the canvas and controls.
There are no lesson-specific palette or rendering branches.

**Automatic min–max** uses the full captured domain, including nonmatches and
items outside the display slice. Orbit, selection, slices and drawing limits do
not rescale it. **Fixed min–max** uses exact integer limits; values below or above
those limits use the end colors. **Use current limits** copies the automatic
limits into a fixed range. Apply the same limits and palette to several objects
when their colors are meant to be comparable. Automatic ranges are local to each
object and change when its captured case changes.

The selected object's compact legend stays on the canvas. Appearance shows the
full exact limits, including integers too long for the compact legend. Hover or
inspect still gives the exact value. Colors are approximate display quantities,
never an equality test or a numerical input. A finite palette cannot distinguish
every value in a large range.

- Equal limits give the limit value the midpoint color. Under fixed limits,
  smaller/larger values still use the respective end colors.
- Negative values and zero participate normally. A diverging palette's midpoint
  is the midpoint of the chosen limits; choose symmetric limits to center it on zero.
- Missing or noninteger fields use neutral gray. A tuple-only object can color
  its indices; it does not secretly acquire numeric contents.
- Relation nonmatches keep their value color, with low opacity and dashed edges.
  Selection and field inspection have separate outlines. Membership is never
  deduced from color, and nonmembership does not replace a value by zero.
- Cells, points and 3D faces share the same field mapping. Cube side shading
  conveys orientation; it is not another value. Labels choose black or white
  against their cell color.

Replay uses captured endpoint labels: the before value at fraction zero and the
after value thereafter, following the existing discrete-label contract. An
automatic value range includes both label endpoints throughout that replay, so
it does not pulse as time is scrubbed. Other color fields refer to the current
captured occurrence; an unavailable field is gray. No interpolated value is
created or passed back into mathematics. **Show result** restores the current
capture's usual range.

## Ownership and compatibility

`colors.js` owns palette lookup, exact normalization and label contrast.
Normalization subtracts and divides `BigInt` integers before producing a bounded
color fraction; neighboring integers beyond floating-point precision can still
map to distinct colors. Fractions are rounded down to a millionth before palette
interpolation; source values and legend limits remain unchanged.
`color-controls.js` owns editing. `workspace.js` connects the scale to captured
rows and marks; `document.js` validates the persisted view. The evaluator,
snapshots, history and mathematical export remain independent of all four.

**Canvas and view** now writes envelope/view version **2**, carrying a theme and
optional color choices per object. Version-1 canvases still open with System
and the default uniform color. Older clients reject version 2 rather than
silently discarding its meaning. **Mathematics only** retains the unchanged core
workspace formats. A saved comparison also includes this view record.

Run the offline contracts and optional browser gate:

```sh
node docs/studies/check-color-model.mjs
node docs/studies/check-scene-model.mjs
node docs/studies/check-colors-equality.cjs
```

The [quotient equality investigation](QUOTIENT_EQUALITY.md) exercises the controls
on ones and a double-owned cell. Use the residue-fiber canvas as a transfer task:
fixed limits 0–2 distinguish unreachable pairs, singleton fibers and double
fibers without changing the palette between parameter cases. Physical devices,
color-vision accessibility and novice interpretation still need human testing.
