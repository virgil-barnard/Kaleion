"""Exercise the first optional proof-assistance boundary on real constructions.

This is counterexample search and solver validation, not a kernel-checked proof.
Install it separately with ``python3 -m pip install -e '.[proof]'``.
"""

import argparse
import json
from pathlib import Path

from examples.quotient_equality import quotient_equality
from examples.statements import (Z3Assistant, coprime_interior_goal,
                                 goals_from_statement, indicator_order_goal)
from examples.studio.statements import comparison_statement


SPEC = {
    "name": "Moving cover", "left_by": ["i", "j"], "left_value": "value",
    "right": "Independent ones", "right_by": ["i", "j"], "right_value": "value",
    "expected": "Independent ones", "expected_by": ["i", "j"],
}


def run():
    workspace = quotient_equality()
    choices = {"vary": ["a", "b"], "assumptions": "a > 1 and b > 1"}
    coprime_statement = comparison_statement(
        workspace.state.roots, workspace.state.parameters, SPEC,
        {**choices, "coprime": [["a", "b"]]},
    )
    # The stronger statement deliberately omits coprimality so the same adapter
    # must return a replayable tied-cell witness rather than a proof-shaped result.
    stronger_statement = comparison_statement(
        workspace.state.roots, workspace.state.parameters, SPEC,
        {**choices, "coprime": []},
    )
    assistant = Z3Assistant()
    attempts = []

    def record(case, goal):
        attempts.append({"case": case, **assistant.check(goal).data()})

    record("shared lemma", indicator_order_goal())
    record("shared lemma", coprime_interior_goal())
    for goal in goals_from_statement(coprime_statement):
        record("coprime construction", goal)
    stronger_goal = next(goal for goal in goals_from_statement(stronger_statement)
                         if goal.source == "comparison")
    record("stronger claim without coprimality", stronger_goal)
    return {
        "statement_fingerprints": {
            "coprime": coprime_statement["fingerprint"],
            "without_coprimality": stronger_statement["fingerprint"],
        },
        "backend": assistant.backend,
        "attempts": attempts,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="Optional JSON report path")
    args = parser.parse_args()
    report = run()
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
