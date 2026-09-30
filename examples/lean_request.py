"""Export exact Kaleion theorem requests as unproved Lean proposition definitions.

The generated ``.lean`` files contain no proof, axiom, ``sorry``, or ``admit``.
They are inputs for a future independent Lean/mathlib checker, not certificates.
"""

import argparse
import json
from pathlib import Path

from examples.proof_assistance import SPEC
from examples.quotient_equality import quotient_equality
from examples.statements import (coprime_interior_goal, goals_from_statement,
                                 indicator_order_goal, lean_request)
from examples.studio.statements import comparison_statement


def requests():
    workspace = quotient_equality()
    statement = comparison_statement(
        workspace.state.roots,
        workspace.state.parameters,
        SPEC,
        {"vary": ["a", "b"], "assumptions": "a > 1 and b > 1",
         "coprime": [["a", "b"]]},
    )
    comparison = next(
        goal for goal in goals_from_statement(statement)
        if goal.source == "comparison"
    )
    return tuple(map(lean_request, (
        indicator_order_goal(), coprime_interior_goal(), comparison,
    )))


def export(directory):
    directory.mkdir(parents=True, exist_ok=True)
    emitted = requests()
    manifest = {"requests": []}
    for request in emitted:
        filename = f"{request.definition.rsplit('.', 1)[-1]}.lean"
        (directory / filename).write_text(request.source, encoding="utf-8")
        manifest["requests"].append({**request.data(), "filename": filename})
    (directory / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("build/lean-requests"))
    args = parser.parse_args()
    manifest = export(args.out)
    summary = {
        "directory": str(args.out),
        "requests": [
            {key: value for key, value in request.items()
             if key in ("filename", "statement_fingerprint", "goal_fingerprint",
                        "source_sha256")}
            for request in manifest["requests"]
        ],
        "checked_proofs": 0,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
