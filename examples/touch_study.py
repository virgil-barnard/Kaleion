"""Export a bounded touch interaction study from actual Kaleion captures.

python3 examples/touch_study.py --out build/touch-study.html
Use --fragment for the in-conversation preview. The browser chooses among these
captured cases and paths; it is not a second evaluator or a general GUI adapter.
"""

import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path

import numpy as np

from kaleion import Collection, F, Inspection, Motion, Product, Workspace, param


def investigation(values):
    left, right = Collection.literal(values), Collection.literal(values)
    product = Product(left=left, right=right)
    pairs = (product.domain.annotate(a=product.read("left"), b=product.read("right"))
             .annotate(total=F.a + F.b, pair_key=F.key)
             .with_values(F.total).arrange(F.a, F.b))
    bins = Collection.sequence(2 * max(values) + 3, start=0)
    measurement = Product(pair=pairs, bin=bins)
    domain = measurement.domain.annotate(pair_key=measurement.read("pair", F.pair_key),
                                        total=measurement.read("pair", F.total),
                                        s=measurement.read("bin"))
    counts = domain.where(F.total == F.s).count(by=F.bin).arrange(F.bin, F.value)
    ranks = pairs.group_by(F.total).order_by(F.pair_key).ranks(key=F.pair_key)
    layouts = {"grid": pairs, "gather": pairs.arrange(F.total, 0),
               "stack": pairs.arrange(F.total, ranks.bind(on=F.pair_key))}
    state = Workspace({**layouts, "counts": counts, "ranks": ranks}).state
    assert not state.errors, dict(state.errors)
    inspect = Inspection(state)
    point_data = []
    for i in range(len(values) ** 2):
        ref = inspect.find("grid", i)
        item = inspect.item(ref)
        rank = inspect.measurement(inspect.find("ranks", i), limit=len(values) ** 2)
        read, = inspect.bindings(inspect.find("stack", i))
        assert read.value == rank.item.value and not rank.truncated
        point_data.append({"key": i, "a": item.fields["a"], "b": item.fields["b"],
                           "sum": item.value, "rank": rank.item.value,
                           "ref": [ref.node, ref.occurrence],
                           "rank_ref": [read.driver.node, read.driver.occurrence],
                           "predecessors": [c.item.fields["pair_key"] for c in rank.contributors]})
    measurements = []
    for k in range(2 * max(values) + 3):
        receipt = inspect.measurement(inspect.find("counts", k), limit=len(values) ** 2)
        assert not receipt.truncated
        measurements.append({"key": k, "value": receipt.item.value, "population": receipt.population,
                             "contributors": [c.item.fields["pair_key"] for c in receipt.contributors],
                             "ref": [receipt.item.ref.node, receipt.item.ref.occurrence]})
    oracle = Counter(a + b for a in values for b in values)
    assert [m["value"] for m in measurements] == [oracle[k] for k in range(len(measurements))]
    lens = pairs.where(F.total == param("s"))
    masks = [lens.evaluate(s=k).mask.tolist() for k in range(len(measurements))]
    paths = {}
    for start, stop in combinations(layouts, 2):
        workspace = Workspace({"pairs": layouts[start]})
        forward = workspace.set("pairs", layouts[stop], motion=Motion.arc(height=.5))
        reverse = workspace.undo()
        frames = [forward.frame("pairs", float(t)).positions.round(8).tolist()
                  for t in np.linspace(0, 1, 41)]
        backwards = [reverse.frame("pairs", float(t)).positions.round(8).tolist()
                     for t in np.linspace(0, 1, 41)]
        np.testing.assert_allclose(backwards, frames[::-1], atol=1e-8)
        paths[start + ":" + stop] = frames
        paths[stop + ":" + start] = backwards
    return {"values": values, "points": point_data, "counts": measurements, "masks": masks,
            "layouts": {name: state.results[name].positions.tolist() for name in layouts},
            "paths": paths, "energy": sum(v * v for v in oracle.values())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("build/touch-study.html"))
    parser.add_argument("--fragment", action="store_true")
    args = parser.parse_args()
    data = [investigation([0, 1, 2, 3]), investigation([0, 1, 3, 7])]
    assert [d["energy"] for d in data] == [44, 28]
    template = Path(__file__).resolve().parents[1] / "docs" / "studies" / "touch-pairs.template.html"
    html = template.read_text().replace("__KALEION_STUDY_DATA__", json.dumps(data, separators=(",", ":")))
    if not args.fragment:
        html = ('<!doctype html><html lang="en"><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                '<title>Kaleion · Touch interaction study</title>'
                '<style>body{margin:0;padding:16px;background:light-dark(#edece8,#171918);color-scheme:light dark}</style>'
                '<body>' + html + '</body></html>')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html)
    print(f"Wrote {args.out} ({len(html.encode()):,} bytes): two captures, exact counts, six reversible paths per capture")


if __name__ == "__main__":
    main()
