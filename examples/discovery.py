"""Run the complete reference scenarios without a renderer or browser.

python3 examples/discovery.py --out examples/output
"""

import argparse
import json
from pathlib import Path

import numpy as np

from kaleion import (
    Arrangement,
    Collection,
    Construction,
    F,
    Motion,
    Move,
    Values,
    Sweep,
    Workspace,
    graph,
    param,
    vector,
)


def quotient():
    a, b = param("a"), param("b")
    region = Collection.grid(
        b, a, values=a * F.i + b * F.j, name="Quotient region"
    ).arrange(F.j, -F.i)
    incidence = region.where(F.value >= a * b)
    counts = incidence.count(by=F.i)
    count_arrangement = counts.arrange(F.key, F.value)

    remainder = Collection.grid(
        b, a, values=F.i + b * F.j, name="Remainder table"
    ).arrange(F.j, -F.i)
    rows = remainder.where(F.value % a == 0).select().order_by(F.value).with_values(F.i)
    ordered = remainder.items.gather(rows, axis="i").arrange(F.j, -F.i)
    rolled = ordered.roll(axis="j", shift=-count_arrangement.bind(on=F.i))
    return region, incidence, counts, count_arrangement, rolled


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("examples/output"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    parameters = {"a": 11, "b": 7}
    region, incidence, counts, driver, rolled = quotient()
    print("Row counts:", counts.evaluate(**parameters).values.tolist())
    matrix = rolled.evaluate(**parameters)
    print(
        "Gather + Roll first column:",
        matrix.values.reshape(matrix.shape)[:, 0].tolist(),
    )

    # No row structure: nine labelled points, placed independently in three dimensions.
    cloud = Arrangement.points(
        range(9),
        [(i % 3, (i * i) % 5, i % 2) for i in range(9)],
        name="Scattered integers",
    )
    displacement = driver.bind(on=F.value % 7)
    moved = cloud | Move(vector(displacement, 0, -displacement))
    changed = cloud | Values(F.value + displacement)
    print(
        "Same driver, changed values:", changed.evaluate(**parameters).values.tolist()
    )

    # One derived integer becomes a constructor argument.
    spiral_template = Construction(Arrangement.spiral(36, initial=param("n")), ("n",))
    seed = counts.where(F.key == 3).select().scalar()
    generated = spiral_template(n=seed)
    print(
        "Driven spiral cycle endpoints:",
        generated.where(F.cycle_end).select().evaluate(**parameters).values.tolist(),
    )

    # History records exact states and a path. Undo evaluates no inverse operation.
    workspace = Workspace(
        {"cloud": cloud, "counts": driver, "quotient": region}, parameters
    )
    workspace.capture("The count at key zero is zero; the group still exists.")
    forward = workspace.set(
        "cloud", moved, motion=Motion.arc(height=2, axis=1, dimension=3)
    )
    backward = workspace.undo()
    frames = []
    for direction, transition in (("forward", forward), ("undo", backward)):
        for t in np.linspace(0, 1, 21):
            frame = transition.frame("cloud", float(t))
            frames.append(
                {
                    "direction": direction,
                    "time": float(t),
                    "positions": frame.positions.tolist(),
                    "opacity": frame.opacity.tolist(),
                    "before_ids": frame.before_ids,
                    "after_ids": frame.after_ids,
                    "labels_before": [
                        None if v is None else int(v) for v in frame.values_before
                    ],
                    "labels_after": [
                        None if v is None else int(v) for v in frame.values_after
                    ],
                }
            )
    for t in (0, 0.1, 0.5, 0.9, 1):
        np.testing.assert_allclose(
            forward.frame("cloud", 1 - t).positions,
            backward.frame("cloud", t).positions,
        )
    workspace.redo()
    workspace.capture("Residue classes displaced by quotient-region cardinalities.")
    workspace.set_parameters(a=12)
    print("Updated counts:", workspace.state.results["counts"].values.tolist())
    workspace.undo()

    positive_spiral = Arrangement.spiral(36, initial=param("n"))
    sweep = Sweep(positive_spiral.where(F.cycle_end), "n", range(1, 18))
    print("Retained composite values:", sorted(r["value"] for r in sweep.retain(16)))

    # Other index primitives remain explicit and compose with any placement.
    seq = Collection.literal([1, 2, 3])
    print(
        "Tile then pad:",
        seq.tile(2).pad(1, 1, attribute_fill={"s": 0}).evaluate().values.tolist(),
    )
    young = Collection.young([4, 2, 1]).arrange(F.j, -F.i)
    print("Young diagram occurrences:", len(young.evaluate()))

    (args.out / "workspace.json").write_text(workspace.to_json())
    (args.out / "motion.json").write_text(json.dumps(frames, indent=2))
    definitions = graph(
        {
            "counts": counts.node,
            "driver": driver.node,
            "moved": moved.node,
            "values": changed.node,
            "constructor": generated.node,
            "gather_roll": rolled.node,
        }
    )
    (args.out / "construction-graph.json").write_text(json.dumps(definitions, indent=2))
    print("Wrote workspace.json, motion.json, and construction-graph.json to", args.out)


if __name__ == "__main__":
    main()
