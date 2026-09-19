"""Compare the former dense rank recipe with compact ordered ranks on one host.

python3 examples/grouping_probe.py --out build/grouping-probe.json
This is a diagnostic, not a timing threshold or proof of general performance.
"""

import argparse
import hashlib
import json
from pathlib import Path
from statistics import median
import subprocess
from time import perf_counter
import tracemalloc

from kaleion import Collection, F, Workspace


def measure(construction):
    times = []
    for _ in range(3):
        start = perf_counter()
        workspace = Workspace({"ranks": construction})
        times.append(perf_counter() - start)
        assert not workspace.state.errors
    tracemalloc.start()
    workspace = Workspace({"ranks": construction})
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    state = workspace.state
    result = state.results["ranks"]
    payload = json.dumps(json.loads(workspace.to_json()), separators=(",", ":"))
    reopened = Workspace.from_json(payload)
    assert reopened.state.results["ranks"].values.tolist() == result.values.tolist()
    return result, {
        "median_evaluation_ms": round(median(times) * 1000, 3),
        "peak_traced_bytes": peak,
        "compact_workspace_bytes": len(payload.encode()),
        "largest_evaluated_extent": max(r["extent"] for r in state.provenance["trace"].values()),
        "evaluated_nodes": len(state.evaluated),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("build/grouping-probe.json"))
    args = parser.parse_args()
    n, groups = 96, 6
    source = Collection.sequence(n, start=0).annotate(group=F.value % groups)
    pairs = Collection.grid(n, n).annotate(
        left_group=source.bind(on=F.i, key=F.key, read=F.group),
        right_group=source.bind(on=F.j, key=F.key, read=F.group))
    dense = pairs.where((F.left_group == F.right_group) & (F.j < F.i)).count(by=F.i)
    compact = source.group_by(F.group).order_by(F.key).ranks()
    before, a = measure(dense)
    after, b = measure(compact)
    expected = [sum(j % groups == i % groups for j in range(i)) for i in range(n)]
    assert before.values.tolist() == after.values.tolist() == expected
    for i, count in enumerate(expected):
        assert len(before.contributor_ids(i)) == len(after.contributor_ids(i)) == count
    prefix = after.metadata["contributor_prefixes"]
    root = Path(__file__).resolve().parents[1]
    digest = hashlib.sha256()
    for path in sorted((root / "src/kaleion").glob("*.py")):
        digest.update(path.name.encode() + b"\0" + path.read_bytes())
    document = {
        "schema": 1, "base_revision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
        "core_source_sha256": digest.hexdigest(), "items": n, "groups": groups,
        "dense_recipe": a, "ordered_rank": b,
        "enumerated_predecessors": sum(expected),
        "stored_ordered_occurrences": sum(map(len, prefix["groups"])),
        "stored_prefix_ranges": len(prefix["ranges"]),
        "limitations": "One finite fixture on one host; inputs prebuilt; three timing runs. "
                       "Both recipes run in the same current evaluator. No timing gate.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(document, indent=2) + "\n")
    print(json.dumps(document, indent=2))


if __name__ == "__main__":
    main()
