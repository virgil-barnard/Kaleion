# Agent instructions for Kaleion

Kaleion is an experimental mathematics workspace. Read `README.md` and the relevant module contracts in `DESIGN.md` before changing behavior. Consult the longer architecture document when a change affects those contracts.

## Working environment

- Use Python 3.11 or newer and `python3` in documented commands.
- Work in a virtual environment. From the repository root on WSL/Linux/macOS:

  ```sh
  python3 -m venv .venv
  source .venv/bin/activate
  python3 -m pip install -e .
  ```

- Reuse an existing working environment. Avoid adding dependencies or tooling unless the change requires them; the runtime currently needs NumPy and the tests use the standard library.

## Implementation conventions

- Keep expressions, numerical evaluation, snapshots, motion, and history separately usable. Public operations build definitions; evaluation is explicit. Views consume evaluated results.
- Preserve exact integer arithmetic before any fixed-width operation can overflow. Floating geometry does not imply exact geometric equality. Make domains, shape rules, and address bounds explicit.
- Keep source identity, occurrence identity, logical indices, values, and placement distinct. Duplicate labels or coincident points are not an implicit correspondence. Drivers align by declared keys.
- Preserve provenance and retained zero groups. A failed or unavailable input must not become a false predicate or zero count. Failures should follow dependencies and leave independent roots usable.
- Undo restores captured state; reverse animation samples the recorded path. Presentation frames are not mathematical input arrangements.
- Keep saved-format compatibility explicit. Update import/export tests and documentation when a schema or operation meaning changes.
- Extend the operation vocabulary only for a concrete construction that existing operations cannot express clearly. Keep changes focused and avoid unrelated refactors.

## Unit tests

- Use `unittest` in `tests/test_*.py`, with descriptive `test_*` names and small deterministic fixtures. Use `numpy.testing` for array comparisons; give floating tolerances a reason. If randomness is needed, use a local seeded generator.
- Test observable contracts through the public API. Prefer an independently calculated expected result or invariant over repeating the implementation inside the test.
- For a bug fix, add a regression that reproduces the failure. For a new behavior, cover its meaningful boundary or invalid-input case. Do not add tests solely to mirror accessors or cosmetic edits.
- When relevant, exercise empty domains and fibers, zero counts, repeated gathers, ambiguous/missing keys, integers beyond 64-bit range, parameter-case isolation, provenance, and undo/redo or JSON round trips. Choose cases affected by the change rather than duplicating the whole suite.
- Do not assert freshly generated UUIDs or capture timestamps as fixed constants. Test identity preservation within an investigation or across save/load instead.
- Unit tests must run offline without a browser, GPU, or external service. Keep future backend/browser checks separately identifiable.

## Verification and pull requests

Run targeted checks while implementing. Before a PR that changes executable behavior, run:

```sh
python3 -m unittest discover -s tests -v
python3 examples/discovery.py --out build/example-output
```

For packaging or dependency changes, also run:

```sh
python3 -m pip wheel --no-deps . --wheel-dir dist
```

For documentation-only changes, verify the affected commands, examples, and links. Reuse relevant completed checks; broaden testing only for a remaining risk. Report the commands, outcomes, and relevant limits without claiming that finite fixtures prove a general identity.

Use a feature branch and open a pull request; leave merging to the maintainer unless explicitly requested. Preserve user edits and accurate attribution, and describe AI assistance in the PR. Keep virtual environments, caches, build outputs, and credentials out of commits. Regenerate committed `examples/output/` fixtures only deliberately; use the ignored `build/` directory for ordinary runs.
