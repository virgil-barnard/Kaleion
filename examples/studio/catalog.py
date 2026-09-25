"""Read-only example discovery. Loading still uses the ordinary capture importer.

Only these committed files are exposed; no path supplied by the browser is opened.
This module does not construct or evaluate mathematics.
"""
from pathlib import Path

CANVASES = Path(__file__).resolve().parents[1] / "canvases"
EXAMPLES = [
    dict(id="00_blank", title="Blank canvas", focus=None,
         description="Start your own construction. Save anything you want to keep before loading.",
         next="Choose Create, or Open → Start walkthrough."),
    dict(id="12_division_motion", title="Division in motion", focus="Moving table",
         description="Count carry cells, shift each fiber, wrap it, then arrange by its derived remainder.",
         next="Undo three times on Moving table, then Redo each step. Quotients come from incidence counts; inspect their contributors."),
    dict(id="12_relation_matrices", title="Quotient and remainder relations", focus="Cycled table",
         description="Q and R extract their values by weighted sums. A modular relation composition reconstructs a quotient incidence.",
         next="Undo/Redo the cyclic shift. Compare Composed Q with Direct Q by n,q over Comparison domain. Try a=12,b=8."),
    dict(id="12_euclidean_step", title="Euclidean step · 3 and 4 become 7 and 4", focus="Moving extension",
         description="An explicitly extended domain is sheared and wrapped. New cells are visible as a separate relation.",
         next="Undo twice, then Redo. Compare Moving extension by i,destination with Direct larger table by i,j, over Direct larger table."),
    dict(id="12_euclidean_next", title="Euclidean step · 4 and 7 become 11 and 7", focus="Moving extension",
         description="Exchange the generator roles and repeat the same construction to reach the paper's 77 cells.",
         next="Undo twice, then Redo. Parameters q=2 gives the next repeated shear with the same formulas."),
    dict(id="00_first_motion", title="First motion · counts become heights", focus="Markers",
         description="Five markers use the triangle's column counts as heights: 4, 3, 2, 1, 0.",
         next="Select Markers, then Undo and Redo to replay the lift. The walkthrough builds this from scratch."),
    dict(id="01_triangle_packing", title="Pack a triangle", focus="Moving cells",
         description="Ordered ranks and measured offsets pack ten cells into a strip.",
         next="Undo and Redo on Moving cells. Inspect Offsets to follow counts of earlier rows."),
    dict(id="04_measured_plane", title="Three measurements lift a plane", focus="Lifted plane",
         description="Three measured surfaces add to a flat plane of height 2. A small 24-cell box keeps exploration light.",
         next="On Lifted plane, Undo three times, then Redo each lift. Compare with Expected height by i, j."),
    dict(id="03_cell_coverage", title="A box of ones", focus="Cell owners",
         description="At (a,b,c) = (5,4,3), every cell has exactly one owner; the counted volume is 24.",
         next="Compare Cell owners with One per cell by i, j, k over Box. This is a static comparison canvas."),
    dict(id="03_tied_coverage", title="When two regions claim a cell", focus="Cell owners",
         description="At (6,4,5), joint gcd one does not prevent ties. Two cells have two owners: volume 62 versus 60.",
         next="Make the same comparison. Inspect the two residuals and their X/Y membership counts."),
    dict(id="02_floor_sums", title="Two regions fill a rectangle", focus="Pieces",
         description="Two quotient regions reassemble into a rectangle; a non-coprime case exposes overlap.",
         next="Undo and Redo on Pieces. Parameters a=12, b=8 create three overlapping cells."),
    dict(id="03_incidence_box", title="Explore the larger incidence box", focus="X region",
         description="The original 240-cell box and its three regions. Static 3D geometry, no recorded placement edits.",
         next="Use View → 3D. Appearance → Points or a slice reduces drawing work if orbit feels slow."),
    dict(id="05_radon_reconstruction", title="Recover an image from line sums", focus="Image heights",
         description="Weighted incidence measurements reconstruct nine pixels; composite modulus breaks the pattern.",
         next="Undo and Redo on Image heights, then inspect a Backprojection weight and its source line sum."),
    dict(id="06_young_layers", title="Turn and pack Young layers", focus="Cells",
         description="Layer counts become cumulative offsets that pack ten original cells.",
         next="Undo twice on Cells, then Redo each move. Follow an offset through its measured layers."),
    dict(id="07_equal_sums", title="Gather pairs by their sums", focus="Moving pairs",
         description="Sixteen pairs collect into seven stacks; ranks separate coincident pairs.",
         next="Undo twice on Moving pairs, then Redo. Counts also retain two zero bins."),
]


def example_text(identifier):
    """Return the exact capture text; never round-trip its integer JSON values."""
    entry = next((entry for entry in EXAMPLES if entry["id"] == identifier), None)
    if entry is None:
        raise KeyError("Unknown example")
    return (CANVASES / (entry["id"] + ".json")).read_bytes()
