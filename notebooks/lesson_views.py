"""Shared presentation helpers for lessons 06–08.

Inputs are captured snapshots or motion frames. Mathematical definitions and
evaluation stay in the notebooks. These helpers are not part of the core API.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from kaleion import IncidenceSnapshot
from kaleion.viewers.plotly import animation_figure

BACKGROUND = "#101b2b"
INK = "#e8eef7"
COLORS = ("#49c5b6", "#f0bc63", "#a5a0ff", "#ef86a8", "#73bcef", "#bacb77")


def style(figure, title, *, height=460):
    figure.update_layout(
        template="plotly_dark", paper_bgcolor=BACKGROUND, plot_bgcolor=BACKGROUND,
        font=dict(color=INK, family="Arial, sans-serif"), title=dict(text=title, x=.04),
        height=height, margin=dict(l=55, r=30, t=95, b=65), showlegend=False,
    )
    return figure


def xy_cells(snapshot, *, color=COLORS[0]):
    """Display the explicit xy projection of a placed finite snapshot."""
    incidence = isinstance(snapshot, IncidenceSnapshot)
    source = snapshot.source if incidence else snapshot
    if source.positions is None or source.positions.shape[1] < 2:
        raise ValueError("Place this construction in at least two dimensions first")
    selected = list(map(bool, snapshot.mask)) if incidence else [True] * len(source)
    hover = [f"Value: {value}<br>Selected: {hit}<br>Occurrence: {oid}"
             for value, hit, oid in zip(source.values, selected, source.ids)]
    return go.Scatter(
        x=source.positions[:, 0].tolist(), y=source.positions[:, 1].tolist(),
        mode="markers", marker=dict(symbol="square", size=23,
                                    color=[color if hit else "#27384c" for hit in selected],
                                    line=dict(color=BACKGROUND, width=1)),
        hovertext=hover, hovertemplate="(%{x},%{y})<br>%{hovertext}<extra></extra>",
    )


def cell_panels(snapshots, titles, *, title, height=460):
    if len(snapshots) != len(titles) or not snapshots:
        raise ValueError("Supply a title for each captured panel")
    fig = make_subplots(rows=1, cols=len(snapshots), subplot_titles=titles,
                        horizontal_spacing=.09)
    for col, snapshot in enumerate(snapshots, 1):
        fig.add_trace(xy_cells(snapshot, color=COLORS[(col - 1) % len(COLORS)]), row=1, col=col)
        fig.update_xaxes(title_text="x", dtick=1, row=1, col=col)
        fig.update_yaxes(title_text="y", dtick=1,
                         scaleanchor="x" + (str(col) if col > 1 else ""), row=1, col=col)
    return style(fig, title, height=height)


def profiles(snapshots, titles, *, keys, title, height=440):
    if len(snapshots) != len(titles) or len(keys) != len(titles) or not snapshots:
        raise ValueError("Supply matching snapshots, titles, and key-field names")
    fig = make_subplots(rows=1, cols=len(snapshots), subplot_titles=titles,
                        horizontal_spacing=.09)
    for col, (snapshot, key) in enumerate(zip(snapshots, keys), 1):
        fig.add_trace(go.Bar(
            x=list(map(int, snapshot.fields[key])), y=list(map(int, snapshot.values)),
            marker_color=COLORS[(col - 1) % len(COLORS)], text=list(map(str, snapshot.values)),
            textposition="outside", cliponaxis=False,
            hovertemplate=key + "=%{x}<br>value=%{text}<extra></extra>"), row=1, col=col)
        fig.update_xaxes(title_text=key, dtick=1, row=1, col=col)
        fig.update_yaxes(title_text="value", rangemode="tozero", row=1, col=col)
    return style(fig, title, height=height)


def replay(samples, labels, *, title, colors_by_id=None, duration=70):
    fig = animation_figure(samples, labels=labels, title=title,
                           duration=duration, show_values=False)
    if colors_by_id is not None:
        for frame, sample in zip(fig.frames, samples):
            ids = [before if before is not None else after
                   for before, after in zip(sample.before_ids, sample.after_ids)]
            frame.data[0].marker.color = [colors_by_id[oid] for oid in ids]
        fig.data[0].marker.color = fig.frames[0].data[0].marker.color
    return fig


def save_figures(directory, figures):
    for name, figure in figures.items():
        figure.write_html(directory / f"{name}.html", include_plotlyjs=True,
                          full_html=True, auto_play=False)
