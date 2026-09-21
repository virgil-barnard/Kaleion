"""A small exploration loop with no plotting dependency.

Run with python3 examples/inspection_choices.py. Lessons 04 and 05 apply the same
inspection queries to a lifted plane and a finite Radon reconstruction.
"""

from kaleion import Collection, F, Inspection, Motion, Workspace, vector


def main():
    # Declare the universe, relation, and retained measurement keys independently.
    cells = Collection.grid(4, 5, values=10 * F.i + F.j)
    selected = cells.where(F.j < F.i)
    counts = selected.group_by(F.i).count()

    # Storage order differs. Keys, not ordinal positions, align the two sources.
    probes = Collection.literal([103, 101, 100, 102], keys=[3, 1, 0, 2]).arrange(F.key, 0)
    height = counts.bind(on=F.key, key=F.i)
    lifted = probes.move(vector(0, height))
    workspace = Workspace({"counts": counts, "probes": probes})
    forward = workspace.set("probes", lifted, motion=Motion.arc(height=1))
    inspect = Inspection(workspace.state)

    point = inspect.find("probes", 3)
    read, = inspect.bindings(point)
    receipt = inspect.measurement(read.driver)
    assert receipt.item.value == 3
    assert [c.item.value for c in receipt.contributors] == [30, 31, 32]
    assert all(c.weight == 1 for c in receipt.contributors)
    print("Point 3:", inspect.item(point).position)
    print("Matched key:", read.key, "count:", receipt.item.value)
    print("Counted source values:", [c.item.value for c in receipt.contributors])

    # Zero is a measured result. It is not a missing or failed binding.
    zero_read, = inspect.bindings(inspect.find("probes", 0))
    zero = inspect.measurement(zero_read.driver)
    assert (zero.item.value, zero.population, zero.contributor_count) == (0, 5, 0)
    print("Zero group: population", zero.population, "selected", zero.contributor_count)

    # Breaking the driver domain must fail, leaving the independent count usable.
    incomplete = counts.where(F.i != 0).select()
    failed = Workspace({"counts": counts, "probes": probes.move(
        vector(0, incomplete.bind(on=F.key, key=F.i)))})
    assert "probes" in failed.state.errors and "counts" in failed.state.results
    print("Missing driver key: dependent placement failed; counts remain available")

    # A zero weighted sum can have contributors: keep weights distinct from labels.
    weighted = Collection.literal([90, 80, 70], fields={"weight": [7, -7, 0]})
    measured = Workspace({"sum": weighted.sum(value=F.weight)})
    weights = Inspection(measured.state)
    cancellation = weights.measurement(weights.find("sum", 0))
    assert cancellation.item.value == 0 and cancellation.contributor_count == 3
    print("Zero sum: weights", [c.weight for c in cancellation.contributors])

    # Inspection and presentation do not commit an edit. Undo reuses its path.
    reverse = workspace.undo()
    assert reverse.frame("probes", .25).positions.tolist() == forward.frame("probes", .75).positions.tolist()
    reopened = Workspace.from_json(workspace.to_json())
    reopened.redo()
    saved = Inspection(reopened.state)
    saved_read, = saved.bindings(saved.find("probes", 3))
    assert saved.measurement(saved_read.driver).to_dict() == receipt.to_dict()
    print("Saved inspection and recorded reverse path agree")


if __name__ == "__main__":
    main()
