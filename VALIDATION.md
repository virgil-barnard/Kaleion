# Validation · 0.1.0

Executed September 19, 2026 on Python 3.12.14 with NumPy 2.3.5. The tests exercise the Python implementation; prior browser-prototype checks are recorded separately in the architecture document.

## Explicit grouping, order, coverage, and placement

- **94 tests pass** with `python3 -m unittest discover -s tests -v`. Twelve new
  public-contract regressions cover strict order and ties, composite keys (including
  a field named `key`), exact integers beyond 64 bits, zero groups, reordered
  drivers, compact rank evidence, missing/duplicate coverage, failure isolation,
  named 3D placement, and captured undo/redo without reevaluation. The eight
  finite-geometry tests now exercise the refactored notebook definitions.
- `python3 examples/discovery.py --out build/example-output` retains its results.
  The committed baseline and fresh example captures reproduce every saved root
  exactly under reevaluation. Schema-1 and legacy compatibility tests still pass.
  New `rank` and `require` operations and contributor-prefix version 1 require
  the updated implementation; dependencies and the outer saved schema are unchanged.
- `python3 examples/grouping_choices.py` checks measured stacks, independent
  3D probe placement and reverse motion, unique representatives, and bad coverage
  `[0,1,2,1,1,1]` despite an unchanged total. All eight README Python blocks and
  all four authoring-guide Python blocks execute in sequence.
- Changed lessons 07 and 10 execute all 19 code cells in fresh in-process IPython
  sessions. Nine workspace files reopen; their compact rank evidence is queryable
  with evaluation disabled. Source notebooks validate and retain cleared outputs.
- Offline browser checks load their 12 standalone views and both converted
  notebooks, verify measured endpoints and exact reverse paths, and exercise
  playback controls. Both MP4s decode completely. See the
  [viewer record](notebooks/VALIDATION.md#explicit-choice-refinement).
- The [reproducible diagnostic](examples/grouping_probe.py) compares the old dense
  predecessor recipe and ordered ranks in the same current evaluator. For 96 items
  in six groups, both match an independent predecessor-count oracle:

  | Measure | Dense recipe | Ordered rank |
  | --- | ---: | ---: |
  | Largest intermediate extent | 9,216 | 96 |
  | Evaluated nodes | 6 | 3 |
  | Compact workspace bytes | 6,357,997 | 80,962 |
  | Peak traced allocations | 3,700,180 B | 77,227 B |
  | Median evaluation, three runs | 47.295 ms | 1.305 ms |

The [raw results](docs/reviews/2026-09-grouping-probes.json) record the base revision
and core-source digest. These are one host's finite fixture, with inputs prebuilt;
no timing threshold or general speedup is asserted. Rank evidence stores 96 ordered
occurrences and 96 prefix ranges; querying all prefixes can still emit quadratic
output. Coverage uses the existing pre-mask group domain and does not manufacture
absent expected keys. Arbitrary key-domain comparisons and general driver-read
explanations remain future work. Earlier validation sections below are historical;
the eight unchanged notebooks were not reexecuted for this pass.

## Finite-geometry discovery lessons

- **82 tests pass** with `python3 -m unittest discover -s tests -v`. Eight new
  independent-oracle tests exercise the actual norm-fiber and Hermitian notebook
  definitions, including exact field coordinates, quotient contributors, keyed
  coverage/ranks, invalid choices, and saved reverse motion.
- `python3 examples/discovery.py --out build/example-output` retains all reference
  results. No core implementation, dependency, operation version, or schema changes.
- Both new notebooks execute 23 code cells in fresh in-process IPython sessions;
  the norm lesson also runs fully at `P=11`. Their source outputs remain cleared.
  Offline browser checks cover 13 new views, both converted notebooks, every polar
  selection, animation endpoints, reversed paths, camera retention, and controls.
  Both 100-frame MP4s decode completely. Two new static previews extend the gallery.
- All new captures reopen with provenance and history. The full Hermitian motion
  capture is about 18.3 MiB in compact JSON, below the unchanged 32 MiB import budget.
  The notebook narrows explicit pair domains and removes JSON whitespace; it does
  not discard evaluated states or evidence.

The [notebook validation record](notebooks/VALIDATION.md#norm-fibers-and-hermitian-partitions)
details these finite fixtures, visual checks, the existing Plotly Pause cancellation
event, and the host's lack of live kernel sockets. Prior checks below remain
historical evidence; the existing eight notebooks were not rerun for this addition.

## Snapshot ownership and shared indexing

- **74 tests pass.** Nine new tests cover external array/container aliasing,
  immutable field elements and references, exact NumPy integer inputs, validated
  internal updates, unchanged-buffer sharing, captured history, and independent
  coordinate oracles for all three axes. Large positive and negative fiber shifts,
  repeated gathers, tiling, concatenation, occurrence policies, and budgets are checked.
- The reference example retains all results. Both the committed baseline workspace
  and freshly exported workspace reopen; every saved root reproduces its serialized
  result under reevaluation, and JSON round trips are exact.
- All eight notebooks rerun their 77 code cells in fresh in-process IPython
  sessions, including videos and captured-state assertions. Notebook sources remain
  cleared. Live kernel sockets are unavailable on this host, as documented below.
- The [recorded comparison](docs/reviews/2026-09-ownership-indexing-probes.json)
  uses the same diagnostic against merged core `0b7d61c` and the refactored working
  tree, with both source digests recorded. For 2,000 items and 24 moves:

  | Measure | Merged baseline | Refactored |
  | --- | ---: | ---: |
  | Retained snapshots | 26 | 26 |
  | Integer-value buffers | 26 | 1 |
  | Attribute buffers | 52 | 2 |
  | Position buffers | 25 | 25 |
  | Value/attribute array storage | 1,248,000 B | 48,000 B |
  | Peak traced allocations during evaluation | 8.2 MB | 6.9 MB |
  | Median evaluation time, three runs | 54 ms | 42 ms |

The array-storage count excludes Python scalar objects, references, and metadata;
the traced peak includes allocations during one evaluation, excluding the prebuilt
definition. Timing and peak memory describe this fixture on one host. Internal
node-only updates share contents, positions, and all fields; public replacement
still copies. Separate evaluators and saved files do not deduplicate buffers.
No operation version or saved schema changes in this pass.

## README lesson gallery

Eight 960 × 600 PNG previews were exported from the freshly executed lessons,
using Plotly.js in Chromium with HTTP(S) requests blocked. All eight loaded and
exported without page errors. Their figures, selected frames, camera framing,
and README links were checked; together the PNGs are about 0.5 MB. The
[export recipe](docs/images/lessons/README.md) preserves the source selections.
This is a static export check, not a repeat of the full playback regression.
The optional Kaleido batch route is documented but was not used on this host.

## First core refinement

- **65 tests pass**, including ten new regressions for scoped Boolean incidences,
  typed selection, nested/scalar bindings, empty domains, failure isolation, graph
  and captured-history round trips, ordered contributors with signed weights,
  prepared/reversed motion, and the independent field interpreter.
- `python3 examples/discovery.py --out build/example-output` retains all reference
  values. The committed baseline workspace reopens, and reevaluating its saved
  definitions reproduces every serialized result exactly. Legacy Icarus import and
  pending-redo tests remain in the suite.
- All seven README Python blocks run in sequence. All eight notebooks execute
  their 77 code cells in fresh IPython processes, including MP4 exports and saved
  investigations. Source notebooks retain cleared outputs. See the host limitation
  and playback results in [notebooks/VALIDATION.md](notebooks/VALIDATION.md).
- The [refactor diagnostic](docs/reviews/2026-09-core-refactor-probes.json) records
  the working tree's core-source digest and its base revision. At 2,000 one-item
  groups, median evaluation time is about 0.027 s, versus about 0.50 s in the
  [baseline](docs/reviews/2026-09-core-design-probes.json). Contributor assembly is
  now one pass, with exact contributor ordering and zero groups retained.
- The captured 200-item transition prepares correspondence once during validation;
  21 forward and 21 reverse samples perform no additional preparation. Motion
  regressions also check duplicate gathers through several ancestors, fades,
  incidence membership, frozen path inputs, and sampling without source execution.

The timing comparison describes this finite fixture on one host. At that stage,
snapshot sharing and per-target driver-alignment evidence remained separate work. Prepared
tracks add retained presentation data per transition; they are rebuilt from saved
snapshots on reopening. Schema-1 and legacy imports remain supported; executing
the new `incidence_boolean` operation requires the updated evaluator.

## Reproduce

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
python3 -m unittest discover -s tests -v
python3 examples/discovery.py --out build/example-output
```

Baseline observation: **30 tests passed**, with no test failures. Editable installation and a wheel build also succeeded. All six then-existing Python code blocks in README.md were executed in sequence successfully. Runtime needs NumPy; tests require no extra test framework. The current refactor results appear above.

The original v0.1 archive's exported workspace was also loaded directly: all JSON data except the renamed format identifier was preserved on re-export, and its pending redo executed successfully. At that original release, the numerical, expression, model, and motion modules matched the baseline source after accounting for the package docstring rename.

Packaging check:

```sh
python3 -m pip wheel --no-deps --no-build-isolation . --wheel-dir dist
```

This command assumes setuptools and wheel are available in the build environment. It produced `kaleion-0.1.0-py3-none-any.whl`. The source ZIP excludes temporary environments, caches, and build outputs.

## Mathematical and construction fixtures

| Fixture | Verified result |
| --- | --- |
| Quotient incidence and Gather/Roll | For all 144 pairs 2 ≤ a,b ≤ 13, row counts equal floor(ai/b) and transformed values equal (ai+bj) mod ab |
| Non-coprime row mapping | Repeated sources are allowed by Gather; occurrences remain distinct; invalid Permute fails |
| a=11, b=7 counts | `[0,1,3,4,6,7,9]`; zero group and 11-item population retained |
| a=11, b=7 gathered/rolled first column | `[0,11,22,33,44,55,66]` |
| Column counts | `[0,0,1,1,2,3,3,4,5,5,6]` |
| Empty fibers | A 3-by-0 declared matrix counted for each i gives `[0,0,0]` |
| Count reuse | Counts receive another lens/reduction; changed placement preserves contributors |
| Measurement interpretation | Changing a count's label preserves its graph derivation without claiming the changed label is the original cardinality |
| General bindings | Count values drive scattered 3D positions, labels, and a spiral constructor argument; driver ordering does not change keyed results |
| Missing/duplicate driver keys | Explicit dependent failure, with independent results retained |
| Spiral | Contiguous nonoverlapping walk, completed rectangular prefixes, structural roles independent of later movement |
| Composite sweep through 36 | n=1 through 17 retains exactly the 24 composites, without a primality predicate in the construction |
| Backward sweep | Smaller requested intervals discard later-case retained matches |
| Extension matrices | E[7→11], E[11→7], E[7→7] built from shared Grid, Concat, Tile, and Gather operations |
| Lookup and Gather | Pointwise lookup commutes with the same fixed gather in the supplied fixture |
| 3D incidence | x=0 selects 16 points from a 4-by-4-by-4 lattice |
| Young filling | Valid partition indices and filling; no automatic standard-tableau assertion |
| Integer arithmetic | Values around 2**80 are transformed, squared, and summed without int64 overflow; exact integer floor/ceil remain exact |
| Invalid numerical work | Non-Boolean predicates, noninteger labels, invalid addresses, nonpositive moduli, and excessive powers fail explicitly |

## State, history, and motion

| Fixture | Verified result |
| --- | --- |
| Symbolic definitions | Expression truth coercion and ambiguous construction equality fail; typed pipelines evaluate correctly |
| Source ownership | Mutating constructor input arrays does not mutate retained definitions/results |
| Operation graph | JSON round trip preserves definition identity and results; a dependency cycle is rejected |
| Local parameter cases | Shared definitions evaluated at different local n values do not contaminate sibling caches |
| Curved reverse motion | Undo samples equal forward samples at 1−t for both coordinates and opacity |
| Lens edit | Before/after membership pairs and reversed fraction preserve highlight-transition semantics |
| Lossy edits | Duplicate Gather, Reduce, and replacement with zeros restore exact prior snapshots |
| Document changes | Creation, removal, parameter edits, and restoration are undoable; a new edit clears redo |
| Captures | Earlier observations retain their original parameters, values, contributors, and provenance |
| Failure | Failed branches leave unrelated roots usable; undo restores the prior state |
| Invalid path | Endpoint-invalid motion is rejected without committing the workspace edit |
| Saved history | JSON preserves pending redo, custom curved paths, labels, and contributor provenance |
| Rename compatibility | Legacy `icarus-python` schema 1 workspaces preserve exact state/history and re-export as `kaleion-python`; unknown formats remain rejected |
| Empty geometry | An empty 3D arrangement retains its coordinate dimension through JSON |

The runnable example exports 21 forward and 21 reverse frames for an arc-driven 3D displacement. It also writes a complete portable workspace and a standalone operation graph.

## What this evidence does not establish

These are finite executable fixtures, not proofs for all possible parameters, expressions, or future observations. Browser and renderer checks are recorded separately above and in [notebooks/VALIDATION.md](notebooks/VALIDATION.md). No GPU/autodiff backend, external proof system, or existing repository migration was exercised. There is no performance or usability claim for arbitrary recursive programs; the general recursive authoring mechanism remains future work.

The reference evaluator uses exact integer contents and floating-point geometry. Reversal compares the same recorded path samples; it does not establish that floating-point geometry represents exact real arithmetic. Process isolation, asynchronous cancellation, streaming extents, and compressed persistent history are also outside this release.
