"""Exercise the first optional proof-assistance boundary on real constructions.

This is counterexample search and solver validation, not a kernel-checked proof.
Install it separately with ``python3 -m pip install -e '.[proof]'``.
"""

import argparse
import json
from pathlib import Path

from examples.quotient_equality import quotient_equality
from examples.statements import Z3Assistant, goals_from_statement, indicator_order_goal
from examples.studio.statements import comparison_statement


SPEC = {
    "name": "Moving cover", "left_by": ["i", "j"], "left_value": "value",
    "right": "Independent ones", "right_by": ["i", "j"], "right_value": "value",
    "expected": "Independent ones", "expected_by": ["i", "j"],
}


def run():
    workspace = quotient_equality()
    # Deliberately omit coprimality. This lets the solver find the overlap that
    # the finite 6,4 canvas also reveals; adding gcd is currently unsupported.
    statement = comparison_statement(
        workspace.state.roots, workspace.state.parameters, SPEC,
        {"vary": ["a", "b"], "assumptions": "a > 1 and b > 1", "coprime": []},
    )
    assistant = Z3Assistant()
    goals = goals_from_statement(statement)
    attempts = [assistant.check(indicator_order_goal()).data()]
    attempts.extend(assistant.check(goal).data() for goal in goals)
    return {"statement_fingerprint": statement["fingerprint"],
            "backend": assistant.backend, "attempts": attempts}


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
