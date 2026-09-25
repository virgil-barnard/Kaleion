# 12 · Remainder fibers and hidden carries

[Notebook](../../notebooks/12_residue_fibers.ipynb) ·
[Worked canvas](../../examples/canvases/12_residue_fibers.json) ·
[Canvas recipes](../../examples/residue_fibers.py)

**Question:** Can a measured fiber determine a motion, and what algebra does that
motion reveal? This continues the [division investigation](../DIVISION_MOTION.md)
into kernels, quotient groups, the generalized Chinese remainder theorem (CRT),
and the carry in a group extension. These are established mathematical concepts;
the experiment is how little special-purpose authoring machinery they require.

## Observe before naming

For positive integers `a,b`, start with `0 <= n < a*b`. Fold the line onto
`(n % a, n % b)`. Keep every occurrence, even when two share a position. Count
each fiber over an independently declared `a` by `b` pair domain. Count the fiber
at `(0,0)` separately; call that measurement `d`. Derive `L = a*b // d`.

| Case | Measured d | Derived L | Fibers over the entire pair domain | Shift by L |
| --- | --- | --- | --- | --- |
| `(7,5)` | 1 | 35 | 35 ones | Every occurrence stays in its slot |
| `(6,4)` | 2 | 12 | 12 zeros and 12 twos | Exchange the two members of each occupied fiber |
| `(6,6)` | 6 | 6 | 30 zeros and 6 sixes | Cycle six members of each diagonal fiber |
| `(1,1)` | 1 | 1 | One one | Stationary |

Group by the two residues, explicitly order by the original integer, then count
strict predecessors. A keyed rank read gives each occurrence a height. Roll the
original integer axis by the measured `L`. The group action preserves both
residues and cycles the heights. Undo samples the captured reverse path.

Finally select the first `L` integers, order them, and repeat that period `d`
times. Copies retain their original representative and gain distinct identities.
Give copy number `h` the label `t + L*h`. This recovers every integer as a set.
It does **not** make addition componentwise: `11 + 1` at `(6,4)` moves from sheet
zero to sheet one. Ignoring the carry incorrectly predicts zero instead of 12.

## Exact explanation

Let `g = gcd(a,b)`, `a=g*A`, `b=g*B`, with `gcd(A,B)=1`. A simultaneous multiple
of `a,b` is a multiple of `g*A*B = lcm(a,b)`. Exactly `g` such multiples lie in
`[0,ab)`. Thus our measurement `d=g` and derived period `L=lcm(a,b)`.

Two integers have the same remainders precisely when their difference is a
multiple of `L`. Every occupied fiber therefore consists of
`t, t+L, ..., t+(d-1)*L`, for a unique `0 <= t < L`. This proves its uniform size,
its strict ranks, and the effect of the measured shift.

A pair `(r,s)` occurs exactly when `(r-s) % d = 0`. Necessity follows by
subtracting the two congruences. For sufficiency choose `q` solving
`A*q = (s-r)/d (mod B)`; `A` is invertible modulo `B`. Then `r+a*q` is a solution.
If `B=1`, no restriction on `q` is needed. Consequently

$$\#\{n:0\le n<ab,\ n\equiv r\pmod a,\ n\equiv s\pmod b\}
=\begin{cases}d&r\equiv s\pmod d,\\0&\text{otherwise}.\end{cases}$$

The compatible pairs form the fiber product
`Z/a ×_(Z/d) Z/b`: their coordinates agree after reduction modulo `d`.
The image of `n -> (n mod a,n mod b)` is isomorphic to `Z/L`, the quotient by its
kernel. For `d=1`, every pair occurs once: the ordinary CRT.

The layer construction expresses the additive exact sequence

$$0\longrightarrow\mathbb Z/d\xrightarrow{h\mapsto Lh}\mathbb Z/(ab)
\xrightarrow{n\mapsto n\bmod L}\mathbb Z/L\longrightarrow0.$$

Writing `n=t+L*h` introduces the carry

$$ (t,h)+(u,k)=((t+u)\bmod L,\ (h+k+\lfloor(t+u)/L\rfloor)\bmod d). $$

When `d>1`, this extension does not split: `d` divides `L`, so multiplication by
`L` annihilates every element of `Z/L × Z/d`, but not `1` in `Z/(Ld)`.
This is a concrete way to encounter a nontrivial group extension without asking
the renderer to decide what an isomorphism means. The elementary arguments here
are separate from finite validation and from presentation frames.

Background: [J. S. Milne, *Algebraic Number Theory*, §1, Chinese remainder theorem](https://www.jmilne.org/math/CourseNotes/ANTc.pdf).
The fiber and carry derivations above specialize the integer setting. No proof
assistant or automatic generalization is implemented.

## Explore the saved canvas

Run `python3 -m examples.studio`, then **Open → Remainder fibers and hidden carries**.
The default is `(6,4)`. Choose **View → 3D** to see the heights. With **Moving residues** selected, Undo three times and
Redo each step: fold, separate by measured ranks, cycle by measured period.

- **Fiber sizes** against **Pair domain**, keyed by `(r,s)` over **Pair domain**:
  zero equal values and 24 differences. Both domains are complete; none is a
  missing-data discrepancy.
- **Fiber sizes** against **Predicted sizes**, using the same keys/domain:
  24 equal values. A zero-pair measurement has two contributors, integers 0 and 12;
  `(0,1)` has a genuine zero with no contributors.
- Before the final Roll, inspect a raised occurrence. Follow its rank read to
  the earlier integer in the same fiber. Roll's motion keeps occurrence identity,
  while its `n` field becomes the destination slot and its value keeps the
  original integer. Do not read `n` as the original integer after Roll.
- **Copied sheets** is a separate construction with new identities. Follow its
  source occurrence chain to see which representative was copied. Its repeat
  count depends on **Kernel size**, rather than a frozen literal 2.
- Change parameters to `(7,5)`. Both kernel and copy count become 1, the period
  becomes 35, and the all-ones comparison passes. Comparisons are reports over
  their captured case; run them again after changing parameters.

The saved canvas includes all twelve construction/measurement roots and three
motion steps. The addition table and failed inverse investigation are in the
notebook; they are not extra saved canvas roots.

## Recreate the motion from blank

Use Parameters to declare `a=6`, `b=4`. The following uses the Vector's default
index `i`; the saved recipe calls the same index `n`. All tools are shared with
other lessons. Apply after each preview. A new result name retains its input.

| Step | Shared controls and declaration |
| --- | --- |
| Integer domain | Create **Vector**, size `a*b`, formula contents `i`; name **Integers**. |
| Kernel | Relation on Integers: `(value % a = 0) and (value % b = 0)`; name **Kernel**. |
| Measured size | **More tools → Sum / count** on Kernel; Count with no group keys, name **Kernel size**. It contains one value, 2. |
| Derived period | Assign values on Kernel size: `a*b // value`; new name **Period**. It contains 12 and retains its derivation. |
| Residue fields | Add field `r = value % a` to Integers, then `s = value % b` to that result; call the final object **Points**. |
| Strict ranks | Measure Points; Rank, group keys `r,s`, member order `i`, unique item key `i`; name **Ranks**. |
| Fold | Arrange Points with three coordinates `(r,s,0)`. Keep the name Points to record later movement on it. |
| Separate | Arrange Points again. Keep `x=r,y=s`; set `z` to a keyed read from Ranks: target `i`, source `key`, read `value`. |
| Cycle | Arrange / move → Cyclic shift, axis `i`; shift from Period using a keyed read with target **number 0**, source `key`, read `value`. |

The browser acceptance check declares these relations, counts, ranks, placements
and shifts from blank, then verifies identities, endpoints, and undo. Its member
order uses the explicit `index` field, equivalent to `i` in this unreordered source.
Close the Details panel and use **View → 3D** after assigning the three coordinates; a top-down XY view hides
the separation along z. Orbit changes only the viewpoint.

To build all fiber counts, create a **Cube** with sizes `a,b,a*b` and contents
`k`. Its relation is `(k % a = i) and (k % b = j)`. Count by `i,j`. Create a separate
Grid of sizes `a,b` filled with ones as the comparison domain. The cube explicitly
includes every candidate, which is why empty fibers survive the reduction.
To construct the prediction too, put the relation `(i-j) % d = 0` on the pair
Grid, using a keyed read from Kernel size for `d`. Count by both `i,j` to obtain
singleton membership zeros/ones, then assign values `value * d`. This uses the
same lens → count → value assignment controls as the division examples.

### Make a measurement control a constructor

On any source choose **More tools → Reindex / extend → Repeat**. Set **Repeat
count from → A single value from an object**, then choose **Kernel size**.
The source is copied twice, or once after the coprime parameter change. A scalar
with value zero creates an empty result; zero occurrences in the driver is an
error. A multi-value object is also an error, even when its values agree.

For the actual period recipe, select from Points using
`i < read Period(value; source key ↔ target 0)`. Use the expression controls to
build the keyed right operand. Order by `i` before repetition. The current **Take an address list** operation
can make that ordering explicit: supply a Vector of addresses `0,...,L-1` and
order its rows by `i`. For this unmodified Vector, selected items are already in
increasing `i` order; the saved Python recipe still declares `.order_by(F.n)`.
Repeat the flattened sequence by Kernel size. Add field
`sheet = index // read Period(...)`, then set values to
`i + read Period(...)*sheet`. Place at `(r,s,sheet)` if the residue fields were
carried on the selected source. Formula controls allow these keyed subexpressions;
plain formula text does not name objects.

The UI still lacks a standalone general **Order by** action and a measured
constructor size for creating the address Vector. The saved period is not
evidence those controls exist. From a newly created, unreordered Vector, selection
already preserves the required order; after arbitrary reordering, supply explicit
addresses or use Python's `order_by`. Repetition itself can now be fully driven
by a measurement. These are specific remaining authoring gaps, not reasons for a
CRT-specific control.

## Module decisions and migration

The investigation uses Grid, Annotate, incidence, Count, Rank, Bind, Select,
Order, Tile, Values, Place and Roll. No installed-core operation, dependency,
arithmetic domain, or saved schema changes.

- `examples/residue_fibers.py` owns the mathematical recipes and chosen cases.
- `reindexing.py` distinguishes a single constructor input from a per-item read.
  The optional `times: {"object": "Kernel size"}` declaration lowers to the
  existing `.scalar()`. Existing `times: {"formula": "2"}` commands still work.
  The graph keeps that dependency and checks cardinality again on every case.
- `web/reindexing.js` owns disclosure of the two repeat-count choices. It contains
  no residue, gcd, or lesson logic. Copies/lineage remain the core's responsibility.
- Notebook/Plotly code owns charts, colors, playback captions and video export.
  Pointwise `Inspection.bindings` does not yet provide a scalar-constructor read
  receipt; use How this is made and inspect Kernel size directly.

This follows Parnas's criterion: hide arity checking, mathematical construction,
and presentation choices behind their respective boundaries. A `QuotientGroup`
subclass would not simplify these independent decisions.

## Functions and authoring scaffolding

The notebook defines **zero functions**. Its inline work declares domains and
predicates, records placements and Roll, formats count/carry heatmaps, inspects
receipts, checks an inverse claim, samples reverse motion, and exports captures,
five HTML figures and a 100-frame 2D MP4. Zero helper definitions does not mean
the investigation needs no authoring decisions.

| Function/helper | Responsibility |
| --- | --- |
| `residue_definitions()` | Three declared domains, incidence, counts, predicted counts, and ranks; returns named generic definitions. |
| `copied_period(integers,size,period)` | Explicit representative selection and ordering; measured repetition; copy ordinal and reconstructed label. |
| `residue_fibers(a,b)` | Registers twelve roots and records three motions, with a 2,000-item budget. |
| `studio.coverage.unique_assignment` | Existing guarded inverse recipe, used directly in the notebook counterexample. |
| `snapshot_views.rectangular_values` | Reads exact count keys for a rectangular view; the notebook independently declares the comparison domain. |
| `lesson_views.style`, `save_figures` | Shared figure styling and HTML writing. |
| Public `Inspection`, `compare_keyed_values`, Plotly/video viewers | Captured receipts, finite evidence, and presentation; none chooses the mathematics. |

The notebook keeps the short mathematical construction visible; the three canvas
functions package the same definitions for a saved example. Count/Rank/Bind
repeats lesson 07; kernel/coverage repeats lessons 09–11; copied periods reuse the
division investigation. The new scalar input choice also works on unrelated
repeated motifs. A general case-family or group-action class is not required.

## Validation and next experiment

See [notebook validation](../../notebooks/VALIDATION.md) for actual execution and
rendering evidence. The witness product has `(a*b)**2` occurrences; the studio's
2,000-item budget permits `a*b <= 44`. Small positive examples are intended.
Counts and algebra are exact; geometry is floating presentation. Physical tablet
usability, novice discovery, and a general proof-assistant workflow remain untested.

Next, use two commuting residue shifts to observe an orbit lattice, then transform
its integer generators with explicit unimodular shears toward Smith normal form.
Before adding an algebraic type, test whether one can keep a changing generator
basis, quotient classes, and occurrence identity visibly distinct using the same
instruments. A missing point in the original domain should break uniform fibers
and supply the next counterexample.
