"""Generate small, ordinary saved workspaces for the existing studio's Open button.

Run from the repository root: python3 examples/save_canvases.py
These are small tutorial constructions and lesson adaptations, not notebook exports.
There is no viewer code, new saved format, or lesson dispatch in the studio.
"""

import argparse
import json
from pathlib import Path

from kaleion import Collection, F, Motion, Product, Workspace, choose, param
if __package__:
    from .division_relations import division_motion, relation_matrices, euclidean_step, euclidean_next, periodic_extension, guarded_remainder_addresses
else:
    from division_relations import division_motion, relation_matrices, euclidean_step, euclidean_next, periodic_extension, guarded_remainder_addresses


def floor_sums():
    """Lesson 02: two incidences, their counts, and a recorded reassembly."""
    a, b = param("a"), param("b")
    rectangle = (Collection.grid(b - 1, a - 1, values=1)
                 .annotate(u=F.i + 1, v=F.j + 1).arrange(F.u, F.v))
    lower_rule, upper_rule = b * F.v <= a * F.u, a * F.u <= b * F.v
    lower, upper = rectangle.where(lower_rule), rectangle.where(upper_rule)
    separated = rectangle.arrange(F.u + choose(lower_rule, -4, 4), F.v)
    workspace = Workspace({
        "Rectangle": rectangle, "Lower region": lower, "Upper region": upper,
        "Overlap": rectangle.where(lower_rule & upper_rule),
        "Column counts": lower.count(by=F.u).arrange(F.u, F.value),
        "Row counts": upper.count(by=F.v).arrange(F.v, F.value),
        "Lower total": lower.count(), "Upper total": upper.count(),
        "Overlap total": rectangle.where(lower_rule & upper_rule).count(),
        "Pieces": separated,
    }, {"a": 11, "b": 7}, max_items=2000, max_history=40)
    workspace.set("Pieces", rectangle, motion=Motion.arc(height=1))
    return workspace


def ownership_regions():
    """The lesson's three weak largest-normalized-coordinate predicates."""
    a, b, c = param("a"), param("b"), param("c")
    box = (Collection.grid(a - 1, b - 1, c - 1, values=1)
           .annotate(u=F.i + 1, v=F.j + 1, w=F.k + 1)
           .arrange(F.u, F.v, F.w))
    x = box.where((a * F.v <= b * F.u) & (a * F.w <= c * F.u))
    y = box.where((b * F.u <= a * F.v) & (b * F.w <= c * F.v))
    z = box.where((c * F.u <= a * F.w) & (c * F.v <= b * F.w))
    return box, x, y, z


def incidence_box():
    """Lesson 03: a three-dimensional domain and three inspectable incidences."""
    box, x, y, z = ownership_regions()
    return Workspace({"Box": box, "X region": x, "Y region": y,
                      "Z region": z, "X sections": x.count(by=F.u),
                      "X volume": x.count(), "Y volume": y.count(),
                      "Z volume": z.count(), "Shared cells": (x & y) | (x & z) | (y & z)},
                     {"a": 11, "b": 7, "c": 5}, max_items=2000, max_history=40)


def blank_canvas():
    return Workspace({}, max_items=2000, max_history=40)


def triangle_parts():
    """A common recipe for the introductory motion and packing investigations."""
    n = param("n")
    grid = Collection.grid(n + 1, n + 1, values=F.i + F.j)
    triangle = grid.where(F.value < n)
    counts = triangle.count(by=F.i)
    formula = Collection.grid(n + 1, values=n - F.i)
    return grid, triangle, counts, formula


def first_motion():
    """A complete blank-canvas tutorial: a count supplies a marker's height."""
    grid, triangle, counts, formula = triangle_parts()
    markers = Collection.grid(param("n") + 1, values=0)
    workspace = Workspace({"Numbers": grid, "Triangle": triangle,
                           "Counts": counts, "Formula": formula, "Markers": markers},
                          {"n": 4}, max_items=2000, max_history=40)
    workspace.set("Markers", markers.arrange(F.i, counts.bind(on=F.key)))
    return workspace


def triangle_packing():
    """Ordered measurements turn a triangular region into a ten-cell strip."""
    grid, triangle, counts, formula = triangle_parts()
    cells = triangle.select()
    ranks = cells.group_by(F.i).order_by(F.j).ranks(key=F.key)
    offsets = counts.group_by().order_by(F.i).prefix_sums(key=F.i)
    workspace = Workspace({
        "Numbers": grid, "Triangle": triangle, "Counts": counts, "Formula": formula,
        "Row weights": triangle.sum(by=F.i, value=F.value),
        "Ranks": ranks, "Offsets": offsets, "Area": triangle.count(), "Moving cells": cells,
    }, {"n": 4}, max_items=2000, max_history=40)
    packed = cells.arrange(offsets.bind(on=F.i, key=F.i) + ranks.bind(on=F.key), 0)
    workspace.set("Moving cells", packed, motion=Motion.arc(height=.6))
    return workspace


def measured_plane():
    """Lesson 04: three captured measurements lift a separate plane in stages."""
    box, x, y, z = ownership_regions()
    heights = [region.count(by=(F.i, F.j)) for region in (x, y, z)]
    plane = Collection.grid(param("a") - 1, param("b") - 1, values=0).arrange(F.i + 1, F.j + 1, 0)
    reference = plane.with_values(param("c") - 1).arrange(F.i + 1, F.j + 1, F.value)
    workspace = Workspace({
        "Box": box, "X region": x, "Y region": y, "Z region": z,
        "X heights": heights[0], "Y heights": heights[1], "Z heights": heights[2],
        "Footprint": plane, "Expected height": reference, "Lifted plane": plane,
    }, {"a": 5, "b": 4, "c": 3}, max_items=2000, max_history=40)
    lifted = plane
    for height in heights:
        lifted = lifted.with_values(F.value + height.bind(on=(F.i, F.j), key=(F.i, F.j)))
        lifted = lifted.arrange(F.i + 1, F.j + 1, F.value)
        workspace.set("Lifted plane", lifted)
    return workspace


def cell_coverage(*, tied=False):
    """Compare derived singleton counts, with pairwise coprimality explicit."""
    box, x, y, z = ownership_regions()
    keys = (F.i, F.j, F.k)
    counts = [region.count(by=keys) for region in (x, y, z)]
    owners = box.with_values(sum(count.bind(on=keys, key=keys) for count in counts))
    one_per_cell = box.count(by=keys).arrange(F.i + 1, F.j + 1, F.k + 1)
    return Workspace({
        "Box": box, "X region": x, "Y region": y, "Z region": z,
        "X membership": counts[0], "Y membership": counts[1], "Z membership": counts[2],
        "One per cell": one_per_cell, "Counted volume": owners.sum(),
        "Box volume": box.count(), "Cell owners": owners,
    }, {"a": 6, "b": 4, "c": 5} if tied else {"a": 5, "b": 4, "c": 3},
       max_items=2000, max_history=40)


def tied_coverage():
    return cell_coverage(tied=True)


def radon():
    """Lesson 05: weighted line sums, reconstruction, and a 2D height profile."""
    p = param("p")
    image = Collection.grid(p, p, axes=("u", "v"), values=F.u * (F.v + 1)).arrange(F.u, F.v)
    lines = Collection.grid(p + 1, p, axes=("m", "t"), values=0).arrange(F.m, F.t)
    product = Product(point=image, line=lines)
    pairs = product.domain.annotate(
        u=product.read("point", F.u), v=product.read("point", F.v),
        m=product.read("line", F.m), t=product.read("line", F.t),
        weight=product.read("point"))
    on_line = (((F.m < p) & ((F.v - F.m * F.u - F.t) % p == 0))
               | ((F.m == p) & (F.u == F.t)))
    incidence = pairs.where(on_line)
    counts = incidence.sum(by=(F.m, F.t), value=F.weight).arrange(F.m, F.t)
    back = incidence.sum(by=(F.u, F.v), value=counts.bind(on=(F.m, F.t), key=(F.m, F.t)))
    total = counts.where(F.m == 0).sum()
    numerator = F.value - total.bind(on=0)
    recovered = back.annotate(recovered=numerator // p, remainder=numerator % p)
    probes = Collection.grid(p, p, axes=("u", "v"), values=0).arrange(p * F.u + F.v, 0)
    heights = probes.with_values(recovered.bind(on=(F.u, F.v), key=(F.u, F.v), read=F.recovered))
    workspace = Workspace({
        "Image": image, "Lines": lines, "Point-line relation": incidence,
        "Line sums": counts, "Backprojection": back, "Image total": total,
        "Recovered fields": recovered, "Pixel domain": probes, "Image heights": probes,
    }, {"p": 3}, max_items=2000, max_history=40)
    workspace.set("Image heights", heights.arrange(p * F.u + F.v, F.value))
    return workspace


def young_layers():
    """Lesson 06: layer measurements turn and pack the original ten cells."""
    heights = Collection.literal([5, 3, 2, 0])
    grid = Collection.grid(4, 5, values=1).arrange(F.i, F.j)
    diagram = grid.where(F.j < heights.bind(on=F.i))
    layers = diagram.count(by=F.j)
    offsets = layers.group_by().order_by(F.j).prefix_sums(key=F.j)
    cells = diagram.select().with_values(F.j + 1)
    turned = cells.arrange(F.j, F.i)
    strip = cells.arrange(F.i + offsets.bind(on=F.j, key=F.j), 0)
    workspace = Workspace({
        "Heights": heights, "Diagram": diagram,
        "Columns": diagram.count(by=F.i), "Layers": layers,
        "Offsets": offsets, "Cells": cells,
    }, max_items=2000, max_history=40)
    workspace.set("Cells", turned, motion=Motion.arc(height=.6))
    workspace.set("Cells", strip, motion=Motion.arc(height=.6))
    return workspace


def equal_sums():
    """Lesson 07: gather equal sums, then separate them with measured ranks."""
    left, right = Collection.literal([0, 1, 2, 3]), Collection.literal([0, 1, 2, 3])
    product = Product(left=left, right=right)
    pairs = (product.domain.annotate(a=product.read("left"), b=product.read("right"))
             .annotate(total=F.a + F.b, pair_key=F.key)
             .with_values(F.total).arrange(F.a, F.b))
    bins = Collection.sequence(9, start=0)
    measured = Product(pair=pairs, bin=bins)
    matching = measured.domain.annotate(
        total=measured.read("pair", F.total), pair_key=measured.read("pair", F.pair_key),
        s=measured.read("bin")).where(F.total == F.s)
    counts = matching.count(by=F.bin).arrange(F.bin, F.value)
    ranks = pairs.group_by(F.total).order_by(F.pair_key).ranks(key=F.pair_key)
    workspace = Workspace({
        "Left": left, "Right": right, "Pairs": pairs,
        "Sum lens": pairs.where(F.total == param("s")),
        "Counts": counts, "Ranks": ranks, "Energy": counts.sum(value=F.value ** 2),
        "Moving pairs": pairs,
    }, {"s": 3}, max_items=2000, max_history=40)
    workspace.set("Moving pairs", pairs.arrange(F.total, 0), motion=Motion.arc(height=.5))
    workspace.set("Moving pairs", pairs.arrange(F.total, ranks.bind(on=F.pair_key)),
                  motion=Motion.arc(height=.5))
    return workspace


BUILDERS = {"00_blank": blank_canvas, "00_first_motion": first_motion,
            "01_triangle_packing": triangle_packing,
            "02_floor_sums": floor_sums, "03_incidence_box": incidence_box,
            "03_cell_coverage": cell_coverage, "03_tied_coverage": tied_coverage,
            "04_measured_plane": measured_plane, "05_radon_reconstruction": radon,
            "06_young_layers": young_layers, "07_equal_sums": equal_sums,
            "12_division_motion": division_motion, "12_relation_matrices": relation_matrices,
            "12_euclidean_step": euclidean_step, "12_euclidean_next": euclidean_next,
            "12_periodic_extension": periodic_extension,
            "12_guarded_addresses": guarded_remainder_addresses}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("examples/canvases"))
    parser.add_argument("--only", nargs="+", choices=BUILDERS, help="Generate only the named canvases")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    for name in args.only or BUILDERS:
        workspace = BUILDERS[name]()
        if workspace.state.errors:
            raise ValueError(dict(workspace.state.errors))
        # Ordinary captured workspace, losslessly compacted. No viewer envelope.
        text = json.dumps(json.loads(workspace.to_json()), separators=(",", ":"), allow_nan=False) + "\n"
        path = args.out / (name + ".json")
        path.write_text(text)
        print(f"{path}: {len(text.encode()):,} bytes, {len(workspace.state.roots)} objects")


if __name__ == "__main__":
    main()
