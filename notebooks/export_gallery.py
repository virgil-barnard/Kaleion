"""Prepare README previews from executed lessons, without rerunning their code.

By default, write HTML figures whose camera button downloads a named PNG.
Optional --png-dir uses Plotly's Kaleido/Chrome exporter for batch generation.
Neither exporter is part of Kaleion's mathematical core.
"""

import argparse
import json
from pathlib import Path

import plotly.graph_objects as go


# Notebook, figure title prefix, recorded frame name, filename, short caption.
# A frame selects already captured presentation data; no values are interpolated.
PREVIEWS = (
    ("01_discovery_workbench", "Rectangular spiral · exact cases", "3",
     "01-spiral", "A rectangular spiral · structural cycle ends"),
    ("02_floor_sum_proof", "Two incidences · one declared universe", None,
     "02-floor-sums", "Two incidences fill a rectangle"),
    ("03_three_incidence_box", "11 · 7 · 5 — three incidences", None,
     "03-three-incidences", "Three incidences fill a box · 86 + 80 + 74 = 240"),
    ("04_measured_motion", "Three counts lift an independent plane", "25",
     "04-measured-motion", "Measurements become motion · after two lifts"),
    ("05_finite_radon", "y − 0x ≡ 0 (mod 5)", "2:1",
     "05-finite-radon", "Recover an image from modular line counts"),
    ("06_young_layers", "Count the layers · turn the cells", "10",
     "06-young-layers", "Turn a Young diagram · halfway through the motion"),
    ("07_additive_structure", "Coincidence does not erase occurrences", "41",
     "07-additive-structure", "Equal sums form stacks · measured ranks set the heights"),
    ("08_ehrhart_counts", "Integer dilations · count", "6",
     "08-ehrhart-counts", "Count lattice points as a triangle grows · n = 6"),
    ("09_norm_fibers", "One measured fiber per level", None,
     "09-norm-fibers", "Norm fibers · multiplication becomes a cyclic turn"),
    ("10_hermitian_partitions", "28 points · two measured partitions", "49",
     "10-hermitian-partitions", "The same 28 points · seven measured groups of four"),
    ("11_cyclic_code_plane", "Seven lines · seven dual complements", None,
     "11-code-and-dual", "A code and its dual · seven projective lines and their complements"),
    ("11_cyclic_code_plane", "One action · cyclic shift and projective motion", "16",
     "11-field-and-plane", "Field multiplication · one cyclic turn moves a projective line"),
    ("12_residue_fibers", "A new copy for each representative and sheet", None,
     "12-residue-fibers", "Remainder fibers · one period, two copies"),
)


def preview(notebook, title_prefix, frame_name, caption):
    document = json.loads(notebook.read_text())
    figures = []
    for cell in document["cells"]:
        for output in cell.get("outputs", []):
            if output.get("output_type") == "error":
                raise ValueError(f"{notebook}: execute the lesson without errors first")
            data = output.get("data", {}).get("application/vnd.plotly.v1+json")
            if data and data.get("layout", {}).get("title", {}).get("text", "").startswith(title_prefix):
                figures.append(data)
    if not figures:
        raise ValueError(f"{notebook}: no saved Plotly figure beginning {title_prefix!r}")
    # Lesson 02 repeats its title for a counterexample; the first is the main case.
    figure = go.Figure(figures[0])
    if frame_name is not None:
        frame = next((f for f in figure.frames if f.name == frame_name), None)
        if frame is None:
            raise ValueError(f"{notebook}: missing recorded frame {frame_name!r}")
        indices = frame.traces if frame.traces is not None else range(len(frame.data))
        for index, update in zip(indices, frame.data):
            figure.data[index].update(update)
        figure.update_layout(frame.layout)
    figure.frames = ()
    figure.layout.updatemenus = ()
    figure.layout.sliders = ()
    figure.update_layout(
        width=960, height=600,
        title=dict(text=caption, x=0.04, y=0.96, font=dict(size=21 if notebook.name.startswith("11_") else 23)),
        font=dict(size=16),
        margin=dict(l=65, r=45, t=95, b=70),
    )
    if notebook.name.startswith("02_"):
        # Keep the colored partition at thumbnail scale; the notebook retains
        # its full notation panel and proof beside this same incidence data.
        figure.layout.annotations = ()
        figure.layout.xaxis.domain = (0, 1)
    if notebook.name.startswith("01_"):
        figure.update_xaxes(range=(-3, 6), dtick=1)
        figure.update_yaxes(range=(-3, 3), dtick=1)
    if notebook.name.startswith("03_"):
        figure.update_layout(scene_camera_eye=dict(x=1.3, y=1.3, z=1.1))
    if notebook.name.startswith("04_"):
        figure.update_layout(scene_camera_eye=dict(x=1.3, y=1.3, z=1.0))
    if notebook.name.startswith("06_"):
        # The recorded halfway plane is x = y. View it from the side rather
        # than edge-on, and fit this frame instead of the entire packing path.
        figure.update_layout(
            scene_camera_eye=dict(x=1.6, y=-1.9, z=1.25),
            scene_xaxis_range=(0.5, 3.5), scene_yaxis_range=(0.5, 3.5),
            scene_xaxis_dtick=1, scene_yaxis_dtick=1,
        )
    if notebook.name.startswith("09_"):
        figure.update_layout(scene_zaxis_title="Norm")
    if notebook.name.startswith("12_"):
        # Independent display scales separate the two exact integer sheets.
        figure.update_layout(scene_aspectmode="manual",
                             scene_aspectratio=dict(x=1.5, y=1.1, z=1),
                             scene_camera_eye=dict(x=1.4, y=-1.9, z=1.3),
                             scene_xaxis_dtick=1, scene_yaxis_dtick=1, scene_zaxis_dtick=1)
    if notebook.name.startswith("10_"):
        # Fit the selected partition, rather than the bounds of the whole path.
        figure.update_xaxes(
            range=(-1.6, 19.6), tickvals=list(range(0, 19, 3)),
            ticktext=list(map(str, range(1, 8))),
            title="Secant group (ordered by pole key)",
        )
        figure.update_yaxes(
            range=(-0.7, 3.7), dtick=1, title="Rank within group", scaleanchor=None,
        )
    return figure


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executed-dir", type=Path, default=Path("build/notebooks"))
    parser.add_argument("--output-dir", type=Path, default=Path("build/readme-gallery"))
    parser.add_argument("--png-dir", type=Path, help="Also export PNGs; requires Kaleido and Chrome")
    parser.add_argument("--only", nargs="+", choices=[p[3] for p in PREVIEWS],
                        help="Export only these preview filenames")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if args.png_dir:
        args.png_dir.mkdir(parents=True, exist_ok=True)
    for name, prefix, frame, filename, caption in PREVIEWS:
        if args.only and filename not in args.only:
            continue
        notebook = args.executed_dir / f"{name}.executed.ipynb"
        figure = preview(notebook, prefix, frame, caption)
        destination = args.output_dir / f"{filename}.html"
        figure.write_html(
            destination, include_plotlyjs="directory", auto_play=False,
            config=dict(displaylogo=False, displayModeBar=True,
                        toImageButtonOptions=dict(format="png", filename=filename,
                                                  width=960, height=600, scale=1)),
        )
        if args.png_dir:
            figure.write_image(args.png_dir / f"{filename}.png", width=960, height=600)
        print(destination)


if __name__ == "__main__":
    main()
