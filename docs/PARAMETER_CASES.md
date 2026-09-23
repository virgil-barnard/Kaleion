# Change an assumption; inspect an exact case

The construction studio now declares named integer parameters, uses them in
expressions and grid extents, and explicitly evaluates a proposed case. The
same controls change a finite Radon modulus and grow a lattice triangle.
Definitions, evaluated cases, and presentation time retain separate meanings.

## Interaction contract

1. Open **Cases…**, choose **Declare parameter**, and enter a name and exact
   integer, such as `p = 3`. **Evaluate case** previews the binding;
   **Apply case** retains that evaluated state. Declaring before building is fine.
2. In a formula, replace a part with **Parameter** and choose `p`. Its token is
   `$p`, distinguishing it from a field or a numeric literal. In the compact
   axis-length input, `p, p` defines a parameterized square. **Edit axis formulas**
   opens the same structured editor for lengths such as `$p + 1`.
3. Construct relations, sums, reads, and placements as usual. Those definitions
   retain parameter references. Applying a new construction uses the current case.
4. Reopen **Cases…**, change the integer, and choose **Evaluate case**. The
   current parameter banner still identifies the applied case; the canvas and
   result report explicitly identify the proposed preview. No history changes yet.
5. **Apply case** keeps that precise capture without executing it again. Inspect
   its measurements and contributors through the existing controls. **Cancel**
   keeps the applied case. Editing a proposed value invalidates its preview.
6. **Undo** and **Redo** restore the earlier/later captures, including their
   parameters, exact results, errors, identities, and evidence. They do not rerun
   the graph. Saving and reopening retains those captures and pending redo.

A case draft can be parked while browsing an applied source, then resumed with
its proposed values intact. Other mutations wait until the draft is applied or
discarded. Preview receipts are not queried against applied data: apply the case
before using the evidence inspector.

Changing a parameter reevaluates the workspace's existing definitions, including
their captured definition dependencies. It does not rewrite the graph to use the
latest object of the same name. Explicit local `with_params(...)` bindings in an
imported definition still override the surrounding parameter. Declaring `p` does
not replace literal `3`s in an existing construction; use parameter expressions
when authoring the definition.

## A case is not a replay frame

| Control | Mathematical effect | Presentation |
| --- | --- | --- |
| Edit a parameter field | None | Proposed exact text |
| Evaluate case | Evaluate definitions with the proposed bindings, without committing | Labeled case preview and per-object ready/failed report |
| Apply case | Retain the evaluated capture as one history edit | Exact endpoint; no interpolated parameter cases |
| Undo/redo a case | Restore a retained state | Exact endpoint; no graph execution |
| Replay captured transformation | None | Scrub/play the latest available construction transition on its original object |
| Return to result | None | Show the exact applied endpoint |

The replay slider sends no requests and performs no mathematical calculation.
Labels belong to the applied result; moving marks are presentation coordinates.
Opening a construction tool returns to the exact result. Selecting another object,
opening Cases, or adopting a new state clears the previous replay. Reduced-motion
preference suppresses automatic playback; explicit replay and static endpoints
remain available. There is no automatic transition between parameter cases in
this increment: matching points across changed universes needs its own design.

## Radon: division can be exact while reconstruction fails

Start from the [weighted-evidence recipe](WEIGHTED_EVIDENCE.md). Replace only
the occurrences of its modulus by the declared parameter `$p`:

| Construction choice | Parameterized definition |
| --- | --- |
| Image extents | `$p, $p` on axes `u,v` |
| Image value | `u * (v + 1)` |
| Line extents | `$p + 1, $p` on axes `m,t` |
| Nonvertical incidence | `line_m < $p` and `(point_v - line_m*point_u - line_t) mod $p = 0` |
| Vertical incidence | `line_m = $p` and `point_u = line_t` |
| Recovered field | `(backprojection - read(total)) div $p` |
| Remainder field | `(backprojection - read(total)) mod $p` |

The two incidence clauses combine with **or**. Ordered point/line keys, weighted
sums, the one-family total, and the evidence chain are unchanged. At `p = 3`, all
nine values recover exactly. Change only the case to `p = 4` and inspect `(0,0)`:

| Quantity | `p = 3` | `p = 4` |
| --- | ---: | ---: |
| Original image value | 0 | 0 |
| Backprojection | 18 | 56 |
| One-family total | 18 | 60 |
| Floor quotient | 0 | −1 |
| Division remainder | 0 | 0 |
| Incident line measurements | 4 | 5 |

Modulo four, the nonzero coordinate differences need not be invertible. The
prime-modulus incidence argument no longer applies. Integer quotient/remainder
checks alone cannot establish reconstruction equality. This is a valid evaluated
case that disproves the attempted extension of the formula; it is not an
evaluation error. Arithmetic modulo four here is not the four-element field.

## Transfer: a triangle grows

Declare `n = 2`. Build a grid with extents `$n + 1, $n + 1`, axes `i,j`, and
value `1`. Relate `i + j < $n`, then Count retaining `i`.

| Case | Row counts | Total |
| --- | --- | ---: |
| `n = 2` | `[2,1,0]` | 3 |
| `n = 4` | `[4,3,2,1,0]` | 10 |
| `n = 0` | `[0]` | 0 |

The last row is retained because it belongs to the declared grid domain. The
zero case has one candidate point and zero incident points. This exercises the
case controller independently of Radon; it does not yet build lesson 08's
measured family, finite differences, or quasipolynomial investigation.

## Failure and compatibility

Malformed names/integers, unchanged bindings, and stale revisions reject a
proposal without changing applied work. Valid integer bindings can instead make
a definition fail: for example, `% p` with `p = 0`. The case preview explicitly
reports that object and its failed dependents; independent roots remain ready.
Applying retains those failures. No earlier geometry or measurements are relabeled
as current results, and no error is converted into a zero count.

The studio supports up to 16 integer parameters with 1–32 character ASCII names,
starting with a letter. Decimal strings preserve the existing 4096-bit exact
integer bound. There are no parameter deletion/rename controls, asynchronous
evaluation/cancellation, cross-case cache, or independent saved-case library.
Undo retention remains 40 history steps, shared with construction edits; older
cases can leave that bounded history. The 2000-item operation and 32 MiB import
budgets remain. A very large case/history can exceed the import budget.

The wire protocol adds `{"parameter":"p"}`, expression-valued grid lengths,
and a revisioned `preview-case` request. Existing string lengths remain accepted.
All lower to existing `param`, Grid, and `State.evaluate` behavior. Ordinary
schema-1 workspaces already store parameters per state; no schema migration,
core operation, dependency, or notebook change is required. The case editor is
limited to integer environments; floating-parameter captures are not editable
through it.

## Ownership and verification

| Decision | Owner |
| --- | --- |
| Named parameter syntax and formula context | `web/expressions.js` |
| Parameter rows and finite-case result report | `web/cases.js` |
| Exact input policy, revision/token validation, one-use capture commitment | `studio/adapter.py` |
| Arithmetic, local scopes, failure propagation, and captured history | Existing core modules |
| Replay sampling display, without requests or definitions | `web/replay.js` |
| Draft lifetime, canvas selection, and controller composition | Existing `drafts.js` and `studio.js` |

Run the [studio validation commands](CONSTRUCTION_STUDIO.md#validation-and-reproduction).
Six new offline tests exercise the shared Radon graph across cases, independent
lattice counts, local binding isolation, zero groups, exact large parameters,
failed dependents, stale/superseded previews, and saved undo/redo/evidence with
graph execution disabled. The browser gate constructs parameterized Radon and
triangle investigations through real controls, changes assumptions, inspects
captured evidence, parks/resumes a case draft, and checks replay makes no API
requests or saved-state changes. It also exercises keyboard, narrow-screen,
and reduced-motion paths alongside the earlier studio checks.

Physical touch, Safari, screen-reader, and novice usability testing remain open.
Next test a **finite comparison instrument**: align recovered and original values
over an independently declared key domain, expose missing keys and residuals,
then follow a discrepancy into these existing evidence views. That would let the
interface expose the full failed claim directly instead of requiring the author
to inspect two separately chosen values. Case families and multi-view history
comparison should remain separate from replay.
