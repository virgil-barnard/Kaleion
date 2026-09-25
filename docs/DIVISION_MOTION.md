# Division as a construction, a measurement, and a movement

The two source presentations are Virgil Barnard's
[Isomorphism with the Division Alogrithm](https://github.com/virgil-barnard/Icarus/blob/main/docs/Isomorphism%20with%20the%20Division%20Alogrithm.pdf)
(especially pages 6–18 and 19–24) and
[Modular Relation Matrix Presentation](https://github.com/virgil-barnard/Icarus/blob/main/docs/Modular%20Relation%20Matrix%20Presentation.pdf)
(pages 1–3 and 5–12). Their diagrams connect incidence, counting, cyclic shifts,
remainder order, and changes of generators. This investigation reconstructs those
connections with explicit formulas; it does not transcribe overlapping slide text.

Run `python3 -m examples.studio`, then **Open**:

| Worked canvas | Movement to replay | Mathematical question |
| --- | --- | --- |
| Division in motion | Select Moving table; Undo three times, then Redo | Can carry counts move a table into remainder order? |
| Quotient and remainder relations | Select Cycled table; Undo/Redo | Can a relation supply a transformation, and can two relations compose into a quotient? |
| Euclidean step · 3 and 4 become 7 and 4 | Select Moving extension; Undo twice, then Redo | What remains invariant under a shear on an explicitly extended domain? |
| Euclidean step · 4 and 7 become 11 and 7 | The same two stages | Does the same construction survive exchanging roles and repeating the step? |

**View → Selected** centers a particular object. **View → XY** gives a flat view
when the composition's three-index witness domain initially opens in 3D.
The supplied objects are editable ordinary captures. Opening one does not run
lesson-specific viewer code. The [recipes](../examples/division_relations.py)
are short symbolic Python and the instructions below recreate them with controls.

## The shared instrument

**Arrange / move → Change** now asks which quantity changes:

| Choice | Keeps | Changes | Existing builder |
| --- | --- | --- | --- |
| Coordinates | Occurrences, values, integer keys | Position of each occurrence | `arrange(...)` |
| Displacement | Occurrences, values, integer keys | Adds a vector to each current position | `move(vector(...))` |
| Cyclic shift | Domain, slot positions, set of occurrences | Which occurrence and its carried fields occupy each logical slot | `roll(axis=..., shift=...)` |

A displacement may depend on individual fields, group keys, or keyed reads from
another object. It works on scattered 1D–3D placements. A cyclic shift has a
narrower contract: a placed rectangular domain, a declared logical axis, and one
exact integer shift per fiber along that axis. Positive shifts move an item from
slot `j` to `(j + shift) % length`. Varying the shift along that same fiber fails.
The period comes from the domain, and large signed shifts reduce exactly.

Connecting two objects or choosing **Combine → Drive a transformation** opens
this same editor. Its initial keyed read supplies y for Coordinates, x for
Displacement, or the Shift for Cyclic shift. These are editable starting choices;
review the target/source keys before Preview. The connection does not infer a
correspondence from labels or proximity.

Coordinates, displacements, named fields, and measurement weights now share
**Write a formula / Use controls**. Short arithmetic uses the existing bounded
parser. Controls retain explicit driver, target key, source key and read-field
choices for a **Keyed read**. Switching syntax views never evaluates or commits.
The coordinate default on an already placed object is its current placement.

Set coordinates before displacing or cycling an unplaced collection. Each Apply
records one exact step. Preview and Cancel retain their existing meanings. Undo
restores the capture and reverses its recorded path, including after Save/Open.
Changing a named root does not rewrite the immutable inputs of older derived
objects. Inspect **How this is made** to see which version a relation uses.

## Counts reveal the division algorithm

Take positive integers `a,b`, with `0 ≤ i < b` and `0 ≤ j < a`. Define

\[
S(i,j)=ai+bj,\qquad M(i,j)=S(i,j)\bmod ab,
\qquad C(i,j)=[S(i,j)\ge ab].
\]

Write `ai = bqᵢ + rᵢ`, with `0 ≤ rᵢ < b`. Since `0 ≤ qᵢ < a`,
`S(i,j) ≥ ab` exactly when `j ≥ a − qᵢ`. Thus

\[
q_i=\sum_{j=0}^{a-1}C(i,j)=\lfloor ai/b\rfloor,
\qquad r_i=ai-bq_i.
\]

This argument needs no coprimality. At `(11,7)` the counts are
`[0,1,3,4,6,7,9]`; remainders are `[0,4,1,5,2,6,3]`.
The zero count has zero contributors. In contrast, a one-hot relation extracting
quotient zero has one contributor of weight zero. Both evidence meanings survive.

Let `k = (j + qᵢ) % a`. Then

\[
M(i,j)=r_i+bk.
\]

First displace each fiber by `(qᵢ,0)`. Then wrap it into columns `k`. Its first
column now contains the remainders. Finally place each fiber at height `rᵢ`.
When `gcd(a,b)=1`, multiplication by `a` permutes the residues modulo `b`, so
the result has one occurrence at each cell and contains every value `0,...,ab−1`.
For `d=gcd(a,b)>1`, there are only `b/d` distinct remainder heights: coincident
occurrences remain distinct. Correct quotient counts do not imply a permutation.

### Build it from blank

Use constants `11,7` initially, or declare parameters `a=11,b=7` and substitute
their names in the formulas and sizes. For each declaration, Preview then Apply.

1. **Grid**: sizes `i=7,j=11`, contents `11*i + 7*j`, name **Raw**.
2. Raw → **Relation → Customize the formula → Write a rule**:
   `value >= 77`, name **Carries**.
3. Carries → **Sum / count**, Count, along `j` only: name **Quotients**.
   The retained key is `i`, including its zero group.
4. Quotients → **More tools → Set values from a formula**:
   `11*i - 7*value`, name **Remainders**. This remains derived from the counts.
5. Make another Grid with sizes `7,11`, contents `(11*i + 7*j) % 77`, name
   **Moving table**. Arrange / move → Coordinates: `x=j`, `y=i`.
6. Arrange / move → Displacement: x is a **Keyed read** from Quotients,
   target `i`, source `i`, read `value`; y is `0`. Apply. This is the shear.
7. Coordinates: x is `(j + read Quotients) % 11`, y is `i`. Build the read in
   controls with the same keys. This returns the cells to a rectangular chart
   while retaining their original `i,j` fields.
8. Coordinates: retain that x expression and make y a Keyed read from Remainders,
   matching `i` to `i`. Apply, inspect, Undo/Redo each stage.

For a direct cyclic reindexing instead of the two geometric stages, start from
the placed rectangle and choose **Cyclic shift**, axis `j`, shift supplied by
the same Quotients read. This has the same visible wrapped endpoint but different
logical addressing: the output's `j` names the destination slot. The geometric
construction retains its original logical `j`. Do not interchange these meanings
in a comparison. Carried fields and occurrence identities follow the values.

To check the division statement, construct `7*value + read Remainders` on
Quotients, and compare it by `i` with an independent vector `11*i` on seven keys.
The saved canvas calls these **Reconstructed multiples** and **Multiples**.
Inspect a translated item to follow its actual quotient read and contributors.

## Quotient and remainder relations are reusable data

Make two grids with contents `j`, then create relations:

\[
Q(i,j)=[j=q_i]\quad(b\times a),\qquad
R(i,j)=[j=r_i]\quad(b\times b).
\]

Their weighted sums along `j`, weight `j`, recover the quotient and remainder
arrangements. Declare these through **Relation** with keyed reads, then **Sum /
count → Sum weights → Weight formula**. The same extracted quotient supplies the
cyclic-shift instrument. No matrix multiplication class or quotient-only action
is necessary. Counting R along `i` tests whether every remainder column has one
owner. At `(12,8)` that coverage is `[4,0,0,0,4,0,0,0]`.

The second paper also suggests a useful factorization. On the reciprocal domain
`0 ≤ n < a, 0 ≤ q < b`, define

\[
A(n,r)=[r=bn\bmod a],\quad
B(r,q)=[aq+r\equiv0\pmod b],\quad 0\le r<a,
\]
\[
D(n,q)=\sum_{r=0}^{a-1}A(n,r)B(r,q).
\]

The canvas constructs A and B as incidences, counts each singleton to obtain
explicit 0/1 fields (including zeros), and **reads those measured fields** on a
three-index candidate domain. Counting matching triples along `r` constructs D.
Its graph therefore retains the actual two factor definitions and their evidence.

From `bn=aq+r` follows `aq+r=0 mod b`. If `gcd(a,b)=1`, there is exactly one
`q` in `0,...,b−1` satisfying that congruence; it is `floor(bn/a)`. Thus D equals
the independently constructed quotient incidence. B is the paper's truncated
periodic remainder matrix, expressible without a hardcoded modular inverse.

To recreate the composition, make A on axes `n,r` of sizes `a,a` and B on `r,q`
of sizes `a,b`, using the predicates above. **Measure → Count**, retaining *both*
keys, produces **First factor cells** and **Periodic factor cells**. On a Cube
with axes `n,r,q` and sizes `a,a,b`, form a relation whose two keyed reads equal
one, joined with **and**. Use **Key tuple** in controls for `(n,r)` and `(r,q)`
on both sides of each read. Sum/count along `r`, leaving `n,q`. This is the same
product–relation–measurement pattern as the Radon and additive lessons.

Compare **Composed Q.value** with **Direct Q.value**, both keyed by `(n,q)`, over
**Comparison domain**. At `(11,7)`, all 77 values agree. Change parameters to
`a=12,b=8`: there are 36 extra matches, no missing keys, and no numerical roundoff.
The second factor has four possible quotients for a reached remainder, so the
composed incidence has 48 hits versus 12 in the direct quotient relation.
The failing finite comparison points to the lost uniqueness assumption.

## The Euclidean step includes a domain extension

Pages 19–24 of the first paper move from `(3,4)` through `(7,4)` to `(11,7)`.
The finite tables have 12, 28 and 77 cells. Groups of different cardinalities
are not isomorphic; extending the table and changing the modulus must be visible
construction choices. The implementation makes no group-isomorphism claim
between those finite tables.

Let `A = r + q*b`, with `b>0`, `0<r<b`, `q≥0`. Construct the extended domain
`0 ≤ i < b`, `0 ≤ j < A` with values

\[
V(i,j)=(ri+bj)\bmod Ab,
\qquad k=(j-qi)\bmod A.
\]

Displace by `(-q*i,0)` and place at `(k,i)`. The same occurrences and values
now form the larger matrix, because

\[
Ai+bk\equiv(r+qb)i+b(j-qi)\equiv ri+bj\pmod{Ab}.
\]

Each row's `j → k` is a permutation, for any such q. This identity does not
require coprimality either. The *labels* cover all residues only when the two
generators are coprime. The canonical division interpretation additionally asks
`r<b`; the geometric equality can be investigated beyond that assumption.

From blank for the first step:

1. Grid `4 × 7`, contents `(3*i + 4*j) % 28`, name **Extended seed**.
2. More tools → Add a named field: `destination = (j - i) % 7`.
   Name the result **Moving extension**; arrange at `x=j,y=i`.
3. Displacement: `x=0-i,y=0`. Apply and inspect the staggered rows.
4. Coordinates: `x=destination,y=i`. Apply to reassemble.
5. Independently create Grid `4 × 7`, contents `(7*i + 4*j) % 28`.
   Compare left keys `(i,destination)` against right keys `(i,j)`, using the
   independent grid's `(i,j)` as expected domain: 28 equal values.

The saved example additionally shows the original `4 × 3` table and the relation
`j ≥ 3` selecting the 16 new cells. The extended seed uses modulus 28 from its
creation; old prefix labels need not agree with the earlier modulus-12 table.
These are new declared occurrences, not inferred copies of coincident values.

For the next step exchange generator roles: `r=4,b=7,q=1`, so `A=11`. Use the
same formulas on `7 × 11`; comparison gives 77 equal values. Increasing q to 2
tests a larger shear and extension. The two saved cases expose each extension
separately, rather than inventing an implicit correspondence across domain growth.

## Information hiding, compatibility, and limits

Following Parnas's criterion, the mathematical meaning and the gesture are not
one module. `transforms.js` owns the explicit edit choices and eligibility;
`notation.js` owns syntax views; the adapter lowers declarations to existing
builders. The core still owns exact arithmetic, cyclic addressing, item identity,
captured evidence and reverse paths. The four recipes own the mathematics of
the papers. The catalog and renderer do not dispatch on a lesson's formulas.

No new core operation, dependency, or saved format is introduced. Existing
`place` commands remain accepted; `move` and `roll` expose existing core builders
through the studio command protocol. Saved examples remain schema 1. The parser
endpoint is read-only. New editor modes retain Preview/Apply revision checks.

These are finite comparisons with the mathematical arguments written above,
not automatically checked universal proofs. Exact comparisons use integer fields;
floating coordinates and animation frames never become evidence. Playback uses
the existing captured linear paths, so cyclic crossings may overlap in transit.
Synchronized multi-object replay, a separated return lane for wrapping cells,
and a general periodic-extension/gather editor remain useful follow-ups.

Next experiment: derive a guarded address map from R's unique matches, then
apply it to an unrelated scattered arrangement. A failed nonunit case should
remain an inspectable relation rather than quietly becoming a permutation.
Before abstracting periodic extension, compare the Euclidean enlargement with
the second paper's truncation/zero-padding construction: which new occurrences
are copies, which are new values, and which keys must remain attached?

## Functions and authoring scaffolding

| Function or module | Responsibility |
| --- | --- |
| `division_parts()` | Common modular table, carry incidence, counted quotient and derived remainder |
| `division_motion()` | Three separately recorded transformations and exact reconstruction inputs |
| `relation_matrices()` | Q/R incidences, weighted extraction, measured factor composition, direct comparison domain, one recorded roll |
| `euclidean_step(r,b,q)` | Explicit enlarged domain and destination keys; shear, reassembly, independent direct formula |
| `euclidean_next()` | The next parameter choice; no new operation |
| `save_canvases.main()` | Ordinary capture export, with deliberate `--only` regeneration |
| `transformControls()` | Shared choice of coordinates/displacement/cycle and scalar declarations |
| `scalarNotation()` / shared `formulaNotation()` | Reuse the relation editor's syntax-switching machinery for arithmetic |
| Existing `Inspection`, comparison and history | Contributor/driver receipts, finite keyed equality, capture and reverse sampling |

The construction functions assemble definitions and workspace edits. There is no
local renderer, matrix multiplication kernel, quotient backend or proof engine.
The composition has `a*a*b` candidate triples and is bounded by the studio's
2,000-item operation limit. A future sparse join would need its own tested domain
and evidence contract. Current arithmetic and geometry retain their documented
integer-budget and float64 limits.

## Validation

See [VALIDATION.md](../VALIDATION.md) for the recorded checks and host limits.
Reproduce targeted checks using the existing virtual environment:

```sh
python3 -m unittest discover -s tests -p test_division_relations.py -v
python3 examples/save_canvases.py --out build/division-canvases --only 12_division_motion 12_relation_matrices 12_euclidean_step 12_euclidean_next
node docs/studies/check-division-motion.cjs
```

The browser check needs an existing Playwright/Chromium installation, as described
in the [studio validation guide](CONSTRUCTION_STUDIO.md#validation-and-reproduction).
It uses public authoring controls from blank; read-only API calls check outcomes.
Physical-touch and unprompted novice comprehension still require human testing.

The README preview is `build/division-check/measured-shear.png` from that browser
gate, copied to `docs/images/division-motion.png`. It shows an applied exact
endpoint, constructed with constants 11 and 7 through the public controls.
