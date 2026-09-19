"""Bounded diagnostics for the September core design review.

Run from the repository root after installation:
    python3 examples/core_design_probe.py > build/core-design-probes.json

This reports observed behavior, including known baseline defects. It is not a CI
acceptance test or a stable public-API example; internal probes should be updated
with the proposed refactor. Timings describe one host, not promised performance.
"""
from dataclasses import replace
import json
import platform
from statistics import median
import subprocess
from time import perf_counter
from unittest.mock import patch

import numpy as np

from kaleion import Collection, F, Motion, Transition, Workspace, param, vector
from kaleion import model


def collect():
    report = {"revision": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
              "python": platform.python_version(), "numpy": np.__version__}
    source = Collection.sequence(4).arrange(F.value, 0)
    incidence = source.where(F.value > param("n")).with_params(n=2)
    report["case_composition"] = {}
    for name, operation in (("evaluate", lambda: incidence.evaluate()),
                            ("complement", lambda: (~incidence).evaluate()),
                            ("intersection", lambda: (incidence & incidence).evaluate()),
                            ("select_then_arrange", lambda: incidence.select().arrange(F.value, 0).evaluate())):
        try:
            result = operation()
            report["case_composition"][name] = {"type": type(result).__name__,
                "cardinality": getattr(result, "cardinality", None)}
        except Exception as error:
            report["case_composition"][name] = {"error": type(error).__name__, "message": str(error)}

    snap = Collection.grid(20, 10, values=1).arrange(F.i, F.j).evaluate()
    with patch("kaleion.model.exact", wraps=model.exact) as exact, patch("kaleion.model.readonly", wraps=model.readonly) as readonly:
        renamed = replace(snap, node=snap.node + ":review")
        report["snapshot_node_only_replace"] = {
            "occurrences": len(snap), "exact_calls": exact.call_count, "readonly_calls": readonly.call_count,
            "shares_values": bool(np.shares_memory(snap.values, renamed.values)),
            "shares_positions": bool(np.shares_memory(snap.positions, renamed.positions)),
            "shared_fields": sum(np.shares_memory(snap.fields[k], renamed.fields[k]) for k in snap.fields),
            "fields": len(snap.fields)}

    driver = Collection.literal([10, 20], keys=[1, 0])
    target = Collection.sequence(2, start=0).arrange(F.value, 0)
    driven = target.move(vector(driver.bind(on=F.key), 0))
    state = Workspace({"driver": driver, "target": target, "driven": driven}).state
    assert not state.errors
    r = state.results
    report["binding_evidence"] = {
        "driver_is_definition_dependency": driver.node.id in {node.id for node in driven.node.parents()},
        "direct_driver_parent_refs": sum(ref.node == r["driver"].node for row in r["driven"].parents for ref in row),
        "direct_target_parent_refs": sum(ref.node == r["target"].node for row in r["driven"].parents for ref in row),
        "positions": r["driven"].positions.tolist()}

    report["reduction_seconds"] = []
    for length in (250, 500, 1000, 2000):
        data = Collection.sequence(length, start=0)
        for per_item in (False, True):
            count = data.count(by=F.s if per_item else None)
            elapsed = []
            for _ in range(3):
                start = perf_counter()
                result = count.evaluate()
                elapsed.append(perf_counter() - start)
            assert result.values.tolist() == ([1] * length if per_item else [length])
            report["reduction_seconds"].append({"items": length, "groups": length if per_item else 1,
                "selected": length, "median_of_3": median(elapsed)})

    data = Collection.sequence(200, start=0).arrange(F.value, 0)
    workspace = Workspace({"points": data})
    outward = workspace.set("points", data.gather(list(range(200))).with_values(F.value).arrange(F.s, 1), motion=Motion())
    calls = []
    original = Transition._tracks
    def tracked(self, name):
        calls.append(name)
        return original(self, name)
    with patch.object(Transition, "_tracks", tracked):
        frames = [outward.frame("points", t / 20) for t in range(21)]
    report["motion_preparation"] = {"occurrences": 200, "frames": len(frames), "track_constructions": len(calls)}

    return report


if __name__ == "__main__":
    print(json.dumps(collect(), indent=2))
