"""Bounded diagnostics for the September core design review.

Run from the repository root after installation:
    python3 examples/core_design_probe.py > build/core-design-probes.json

This reports observed behavior against the review's recorded baseline. It is not a
CI acceptance test or a stable public-API example. Internal probes track the current
implementation. Timings describe one host, not promised performance.
"""
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import platform
from statistics import median
import subprocess
from time import perf_counter
import tracemalloc
from unittest.mock import patch

import numpy as np

from kaleion import Collection, Evaluator, F, Motion, Transition, Workspace, param, vector
from kaleion import model


def collect():
    report = {"revision": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
              "python": platform.python_version(), "numpy": np.__version__}
    core_dir = Path(model.__file__).resolve().parent
    working_tree = core_dir == Path("src/kaleion").resolve()
    report["core_source"] = "working tree" if working_tree else "alternate import path"
    report["core_modified_from_revision"] = bool(subprocess.check_output(
        ["git", "status", "--porcelain", "--", "src/kaleion"], text=True)) if working_tree else None
    core = sha256()
    for path in sorted(core_dir.rglob("*.py")):
        name = Path("src/kaleion") / path.relative_to(core_dir)
        core.update(str(name).encode() + b"\0" + path.read_bytes() + b"\0")
    report["core_sha256"] = core.hexdigest()
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
    if hasattr(snap, "_with_changes"):
        with patch("kaleion.model.exact", wraps=model.exact) as exact, patch("kaleion.model.readonly", wraps=model.readonly) as readonly:
            renamed = snap._with_changes(node=snap.node + ":runtime")
            report["snapshot_internal_update"] = {
                "exact_calls": exact.call_count, "readonly_calls": readonly.call_count,
                "shares_values": bool(np.shares_memory(snap.values, renamed.values)),
                "shares_positions": bool(np.shares_memory(snap.positions, renamed.positions)),
                "shared_fields": sum(np.shares_memory(snap.fields[k], renamed.fields[k]) for k in snap.fields)}
    else:
        report["snapshot_internal_update"] = {"available": False}

    # One retained construction graph: these buffers can be shared within an
    # evaluation. This does not imply caching between workspace edits or cases.
    points = Collection.sequence(2000, start=0).arrange(F.value, 0)
    chain = points
    for _ in range(24):
        chain = chain.move(vector(1, 0))
    elapsed = []
    for _ in range(3):
        start = perf_counter()
        engine = Evaluator()
        result = engine.get(chain.node)
        elapsed.append(perf_counter() - start)
    np.testing.assert_array_equal(result.positions[:, 0], np.arange(2000) + 24)
    retained = list(engine.evaluated.values())
    values = {id(s.values): s.values for s in retained}
    attributes = {id(a): a for s in retained for a in s.fields.values()}
    positions = {id(s.positions): s.positions for s in retained if s.positions is not None}
    tracemalloc.start()
    measured = Evaluator()
    measured.get(chain.node)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    report["placement_chain"] = {
        "items": 2000, "moves": 24, "retained_snapshots": len(retained),
        "median_of_3_seconds": median(elapsed), "peak_traced_bytes": peak,
        "value_buffers": len(values), "attribute_buffers": len(attributes),
        "position_buffers": len(positions),
        "value_and_attribute_array_bytes": sum(a.nbytes for a in (*values.values(), *attributes.values())),
        "array_bytes_note": "Unique ndarray storage; excludes Python scalar objects, lineage, and metadata"}

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
    calls = []
    original = Transition._prepare_tracks
    def tracked(self, name):
        calls.append(name)
        return original(self, name)
    with patch.object(Transition, "_prepare_tracks", tracked):
        outward = workspace.set("points", data.gather(list(range(200))).with_values(F.value).arrange(F.s, 1), motion=Motion())
        during_capture = len(calls)
        frames = [outward.frame("points", t / 20) for t in range(21)]
        backward = workspace.undo()
        reverse_frames = [backward.frame("points", t / 20) for t in range(21)]
    report["motion_preparation"] = {
        "occurrences": 200, "frames": len(frames), "reverse_frames": len(reverse_frames),
        "track_constructions": len(calls), "during_capture": during_capture,
        "during_frames_and_reverse": len(calls) - during_capture}

    return report


if __name__ == "__main__":
    print(json.dumps(collect(), indent=2))
