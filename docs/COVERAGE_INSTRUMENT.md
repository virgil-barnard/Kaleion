# Coverage: from a relation to an assignment

September 22, 2026 · A shared studio instrument

**Question:** does each expected item have exactly one matching occurrence, and
what could that match tell us about the item?

The [construction studio](CONSTRUCTION_STUDIO.md) now exposes **Check coverage**
for ready objects and declared groups. The same control checks a modular
correspondence, additive fibers, or ownership in a finite geometry. It accepts
chosen fields and captured objects; it has no lesson identifiers.

## The choices and their meaning

| Choice | Meaning |
| --- | --- |
| Source group keys | Fields that identify the receiving item in the candidate construction; a composite key follows the declared field order |
| Expected domain | A separately chosen collection or arrangement containing the items the claim is about |
| Expected key fields | One unique key per expected occurrence, aligned to source keys by value, never by display or storage order |
| Requirement | Exactly one matching occurrence for each expected key, with no incident occurrences outside the expected domain |
| Supplied value | An integer expression in the matching occurrence's context, chosen after a successful check |
| New field | A fresh attribute on a derived copy of the expected items; their labels, keys, identities, and placement are retained |

Keys use the existing binding equality. Choosing coordinates compares their
stored floating values, with no geometric tolerance or camera-based inference.

For the captured candidate set \(C\), incidence \(R\subseteq C\), source key map
\(k\), and expected occurrence \(e\) with key \(q(e)\), the check counts

\[
c(e)=\left|\{r\in R:k(r)=q(e)\}\right|.
\]

Adoption requires unique expected keys, \(c(e)=1\) for every expected occurrence,
and no incident source key outside the declared expected domain. Duplicate
matches count twice even if their labels or proposed assigned values agree.
Nonincident candidates outside the expected domain do not violate this claim.

The expected domain is an authoring decision. The tool never derives it from
surviving matches automatically. Choosing a source derived from those matches
can still weaken the claim; the software cannot infer which absent items its
author intended to include. An empty expected domain is explicitly labeled and
makes no claim about any item. A failed or unavailable input is an error, not
an empty domain.

## Read the witnesses before adopting a value

**Check coverage** reads captured memberships and changes no definitions, history,
or saved data. Filter the report to missing, multiple, outside, or exactly-one
keys. Expected occurrence order controls only the listing.

- **Missing, with candidates:** the candidate group exists but has no matches.
  **Show candidate group** uses the existing group selector and canvas highlight.
- **Missing, without candidates:** the expected key has no candidate group.
  Its match count is zero, and **Inspect expected occurrence** shows the item
  that declared the obligation. No phantom source occurrence is invented.
- **Multiple:** inspect each matching occurrence, even when their values coincide.
- **Outside:** inspect incident occurrences whose keys have no expected item.

**Back to coverage** returns from a receipt with the same choices and filter.
Coverage can be inspected while another construction draft is parked. That
draft must be resumed or discarded before creating an assignment.

When the check holds, **Use unique matches…** opens the ordinary draft editor.
Choose a new field name, the value expression, and the result name. **Preview**
checks again; **Apply** retains that exact capture as one undoable action.
Changing the coverage choices removes the previous report and adoption control.

For a matched value of zero, the result's binding receipt leads to a weighted
sum with **one contributor of weight zero**. That evidence distinguishes a real
zero-valued assignment from an uncovered item. The new field can immediately
supply another expression, relation, grouping, or keyed placement driver.

## Build the first investigation from a blank canvas

Start the studio with `python3 -m examples.studio` in the active virtual
environment. The controls and setup are described in the [studio guide](CONSTRUCTION_STUDIO.md).

| Step | Declaration or action | What to notice |
| --- | --- | --- |
| 1 | Add integers `Expected = [2,0,1]` | This independently declares three point labels, deliberately out of numerical order |
| 2 | Add a `3 × 3` grid, axes `i,j`, value `1`; name it Candidates | Grid slots are candidates; their repeated value `1` does not identify an owner |
| 3 | Create a relation `j < i` | Counts by `i` are `[0,1,2]`: the total is three, but coverage is not unique |
| 4 | Check coverage: source key `i`, expected domain Expected, expected key `value` | In expected order the counts are `[2,0,1]`; adoption is unavailable |
| 5 | Inspect missing and multiple keys; show the candidate group | Three candidates can have zero matches; equal labels remain separate occurrences |
| 6 | Keep matching occurrences as a new collection and repeat the check | Key zero now has no candidate group, yet the expected item still exposes the missing assignment |
| 7 | On Candidates, create a new relation `j = i`; check the same expected domain | Every expected key has one match |
| 8 | Use unique matches: new field `owner`, supplied value `j`; name the result Assigned | Both the original labels and owner field are `[2,0,1]`; owner zero has one contributor |
| 9 | Arrange Expected with `x=value`, `y=0`; then set `y` to a keyed read from Assigned, target key `value`, source key `value`, read `owner` | The new field drives motion by key; undo restores the recorded placement |

## Transfer the instrument to another question

The existing additive construction uses `A=[0,1,3]`, `B=[0,2]`, and their six
pairs with field `total=left_value+right_value`. Choose expected sum labels
`[5,0,2,1]`. Each has one match, but two pairs with total three are outside the
expected domain, so the stated requirement fails. Declare the relation
`total ≠ 3` and check again. Now attach `right_value` as field `partner`; the
result is `[2,0,2,0]` in expected order. The control and guard are unchanged.

The adapter tests also use [lesson 10's Hermitian construction](lessons/10_hermitian_partitions.md):
seven declared blocks, 28 independently declared curve points, and canonical
point keys with reversed storage order. They form the bounded `7 × 28` candidate
product and evaluate the existing exact Hermitian relation. All 28 keys have
one owner. Removing the polar leaves exactly its four points uncovered; selecting
the survivors does not erase those obligations. The full `91 × 28` lesson
exceeds the studio's 2000-item operation limit, and its complete source-constructor
UI remains future work. This is an adapter transfer test, not a claim that the
whole lesson is available through touch controls.

## Keep reporting, construction, and presentation separate

| Changeable decision | Owner | Contract |
| --- | --- | --- |
| Which fields specify candidate groups | Existing `groups.py` and core indexing policy | Captured groups retain their native types, membership, and declared zero fibers |
| How to align expected obligations with those groups | `coverage.py::captured_coverage` | Linear captured-data query; missing groups and outside matches have explicit witnesses |
| How to adopt a sole value | `coverage.py::unique_assignment` | Existing Count, Sum, Bind, Require, and Annotate definitions; no new core operation |
| How the choices and witnesses appear | `web/coverage.js` | Shared field-key selectors, filtered witnesses, and semantic callbacks; no mathematical evaluation |
| Which capture may commit | Existing adapter, drafts, and history | Revision/capture checks, exact preview/apply, saved undo/redo |

The assignment recipe groups and sums the supplied expression, checks multiplicity
on the expected domain, checks each incident source key against that domain, and
checks that expected keys are unique. Guards remain dependencies in the saved
operation graph. Changing parameters later can fail these guards; a successful
browser report is never substituted for them. A missing keyed read fails explicitly.

The outer annotation exposes its ordinary binding receipt. Following it reveals
the weighted reduction and original contributors through `Inspection`, including
after save/reopen with graph execution disabled. Fields are attached after the
guards so the ordinary inspector can describe the direct read without a new
recursive inspection API.

This recipe does not extend the public `Coverage` helper, whose domain still
comes from its source's pre-mask groups. It adds no core primitive, public Python
signature, dependency, or saved schema. Existing captures need no migration.
The experimental command adapter adds an `assignment` declaration and a read-only
coverage query. At-least/at-most requirements and assignments that intentionally
allow multiple owners remain future contracts.

## Evidence and next experiment

The seven tests in `tests/test_studio_coverage.py` cover independent keys,
balanced missing/multiple counts, vanished groups, outside matches, exact large
integers, composite keys, duplicate values, empty domains, failed/stale inputs,
live graph guards, contributor receipts, save/reopen, keyed reuse, and Hermitian
ownership. Expected results use direct enumeration or the independent finite-field
oracle already used by the geometry lesson tests.

The browser gate constructs the simple and additive investigations through real
controls, inspects witnesses and returns, parks an assignment draft during a
coverage check, and uses an adopted field for reversible placement. It also
checks phone layout and saved assignments. The [design study's rubric](UI_DESIGN_STUDY.md#3-a-practical-quality-rubric)
remains the standard for interpretation: these finite behavioral checks do not
establish novice usability or universal mathematical claims.

Validation for this increment: **151 unit tests pass**, the discovery example
retains its expected outputs, and the expanded gate passes in Chromium
153.0.8010.0. Desktop and 320-pixel coverage views were inspected; the existing
four-width layout checks also pass. Reports, screenshots, and saved examples
remain under ignored `build/`. No notebook source or video export changed.

**View expected and matches** now opens [two linked views](LINKED_EVIDENCE_VIEWS.md).
A missing expected key keeps its item visible with no candidate highlighted;
choosing a link updates the report. The same renderer serves captured keyed
reads and quotient contributors. Next test a Radon weight-read chain and the
phone layout with people. Physical-device and novice transfer trials remain
necessary before choosing the final layout.
