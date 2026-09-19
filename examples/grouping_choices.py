"""Explicit discovery choices: python3 examples/grouping_choices.py.

The same definitions can feed Plotly or a future visual authoring interface.
This example needs only Kaleion's core dependencies.
"""

from kaleion import Collection, F, Motion, Workspace


def main():
    points = (Collection.grid(3, 4, values=F.i + F.j)
              .annotate(point=F.key).arrange(x=F.j, y=F.i))

    # Choose groups, then choose the order of their members.
    groups = points.group_by(F.value)
    counts = groups.count()
    ranks = groups.order_by(F.point).ranks(key=F.point)

    # Name the measured quantity and the target key it reads.
    slot = ranks.bind(on=F.point, key=F.key)
    stacks = points.arrange(x=F.value, y=slot)
    probes = Collection.sequence(6, start=0).arrange(x=F.value, y=0, z=0)
    height = counts.bind(on=F.value, key=F.key)
    lifted = probes.place(x=F.x, y=F.y, z=height)

    # Choose one representative per sum, then require one actual contributor.
    first = points.where(slot == 0)
    coverage = first.group_by(F.value).coverage()
    representatives = coverage.unique(value=F.point)

    workspace = Workspace({"counts": counts, "ranks": ranks, "stacks": stacks,
                           "coverage": coverage.counts, "representatives": representatives,
                           "probes": probes})
    assert not workspace.state.errors
    result = workspace.state.results
    assert result["counts"].values.tolist() == [1, 2, 3, 3, 2, 1]
    assert result["representatives"].values.tolist() == [0, 1, 2, 3, 7, 11]
    motion = workspace.set("probes", lifted, motion=Motion.arc(height=1, dimension=3))
    undo = workspace.undo()
    assert (motion.frame("probes", .25).positions == undo.frame("probes", .75).positions).all()

    # The total remains six, but one sum is uncovered and another is covered twice.
    bad = points.where(((slot == 0) & (F.value != 0)) | ((F.value == 2) & (slot == 1)))
    bad_coverage = bad.group_by(F.value).coverage()
    failure = Workspace({"counts": bad_coverage.counts,
                         "missing": bad_coverage.missing, "overlaps": bad_coverage.overlaps,
                         "representatives": bad_coverage.unique(value=F.point)}).state
    assert failure.results["counts"].values.tolist() == [0, 1, 2, 1, 1, 1]
    assert "representatives" in failure.errors
    print("Group sizes:", result["counts"].values.tolist())
    print("Checked representatives:", result["representatives"].values.tolist())
    print("Predecessors of point 6:", len(result["ranks"].contributor_ids(6)))
    print("The same total with bad coverage:", failure.results["counts"].values.tolist())
    print("Unique assignment rejected; measurements and witnesses remain available.")
    print("Independent probes use measured heights; their recorded motion reverses exactly.")


if __name__ == "__main__":
    main()
