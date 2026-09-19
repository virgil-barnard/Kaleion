# Contributing to Kaleion

Kaleion develops through small, reviewable pull requests. Use a feature branch, describe the mathematical or interaction problem it addresses, and leave merging to the repository maintainer.

Coding agents should also follow [AGENTS.md](AGENTS.md), which states the project's testing and implementation conventions.

## Run the reference checks

Use Python 3.11 or newer. From the repository root, set up a virtual environment (WSL, Linux, or macOS):

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
```

With the environment activated:

```sh
python3 -m unittest discover -s tests -v
python3 examples/discovery.py --out build/example-output
python3 -m pip wheel --no-deps . --wheel-dir dist
```

Activate the environment again with `source .venv/bin/activate` in each new terminal. Run `deactivate` when finished. See [README.md](README.md#run-it) for Ubuntu/WSL setup troubleshooting.

The example output directory above is ignored by Git. The committed files in `examples/output/` are reference exports; regenerate those intentionally when a change requires new fixtures. Their source identities and capture timestamps vary between runs.

For a change, run the checks that exercise its behavior and report the results. The baseline suite includes the quotient/remainder examples, structural spiral discovery, general drivers, provenance, and reversible history. Add a regression test when a new behavior or a concrete failure needs coverage.

## Preserve the design boundaries

- Keep construction definitions, numerical evaluation, snapshots, motion, and history separately usable.
- Declare keys, domains, address conventions, and correspondence explicitly. Equal labels or overlapping coordinates do not imply equal identities.
- Keep mathematical evaluation tied to exact snapshots. Presentation frames are not input arrangements.
- Treat finite examples as evidence for those cases; avoid turning a successful visualization into an implicit universal claim.
- Introduce a new primitive when an actual construction exposes a missing capability. Discuss changes to saved formats and numerical conventions in the pull request.

The module contracts are in [DESIGN.md](DESIGN.md); the longer-term scope is in [KALEION_DISCOVERY_ARCHITECTURE.md](KALEION_DISCOVERY_ARCHITECTURE.md).

## Pull requests and attribution

Explain the problem, the resulting behavior, the checks run, and any remaining limitation relevant to review. Preserve the existing commit history and use accurate author information. Identify AI assistance in the pull request so its contribution is traceable alongside the implementation and test evidence.

The initial workflows and design direction come from Virgil Barnard's mathematical investigations. The v0.1 Python core was developed collaboratively with OpenAI Codex. Future contributions are recorded in commits and pull requests.

The next planned feature is a small visual replay viewer for captured snapshots and motion. It should exercise these contracts before expanding the authoring interface.
