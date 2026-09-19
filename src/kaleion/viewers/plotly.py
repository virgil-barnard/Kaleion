"""Small Plotly adapters. No construction evaluation or workspace mutation here."""

from html import escape

import numpy as np
import plotly.graph_objects as go

from ._display import BACKGROUND, FOREGROUND, GRID, bounds, prepare, rgba, series


def _trace(data, *, connect=False, show_values=True):
    dimension = data.positions.shape[1]
    colors = [rgba(c, a) for c, a in zip(data.colors, data.opacity)]
    text = [label if len(label) <= 15 else "" for label in data.labels]
    common = dict(
        mode="markers" + ("+lines" if connect else "") + ("+text" if show_values else ""),
        x=data.positions[:, 0].tolist(), y=data.positions[:, 1].tolist(),
        text=text, hovertext=list(data.hover), hovertemplate="%{hovertext}<extra></extra>",
        marker=dict(color=colors, size=7 if dimension == 3 else 25),
        textfont=dict(size=11, color=[rgba(FOREGROUND if dimension == 3 else BACKGROUND, a)
                                     for a in data.opacity]),
        textposition="top center" if dimension == 3 else "middle center",
        line=dict(color=GRID, width=2), showlegend=False,
    )
    if dimension == 3:
        return go.Scatter3d(z=data.positions[:, 2].tolist(), **common)
    return go.Scatter(**common)


def _layout(data, title):
    ranges = bounds(data)
    layout = dict(
        template="plotly_dark", title=dict(text=title, x=0.04),
        paper_bgcolor=BACKGROUND, plot_bgcolor=BACKGROUND,
        font=dict(color=FOREGROUND, family="Arial, sans-serif"),
        height=540, margin=dict(l=50, r=35, t=80, b=55),
        uirevision="kaleion-camera", hovermode="closest",
    )
    axes = {c: dict(title=c, range=r, autorange=False, gridcolor=GRID, zeroline=False)
            for c, r in zip("xyz", ranges)}
    if len(ranges) == 3:
        layout["scene"] = dict(
            **{f"{c}axis": {**a, "backgroundcolor": BACKGROUND} for c, a in axes.items()},
            aspectmode="data",
            bgcolor=BACKGROUND, uirevision="kaleion-camera",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.1)),
        )
    else:
        layout.update(xaxis=axes["x"], yaxis={**axes["y"], "scaleanchor": "x", "scaleratio": 1})
    return layout


def snapshot_figure(snapshot, *, title="Kaleion · exact state", connect=False, show_values=True):
    """Show a placed Snapshot or IncidenceSnapshot (or one presentation Frame).

    Amber points satisfy an incidence; grey points do not. ``connect=True``
    draws storage order, which is meaningful only when explicitly chosen.
    Integer labels stay strings in JavaScript, including values above 2**53.
    """
    data = prepare(snapshot)
    if data.status != "ready":
        title += f"<br><sup>{escape(data.status)}</sup>"
    return go.Figure(data=[_trace(data, connect=connect, show_values=show_values)],
                     layout=_layout([data], title))


def animation_figure(samples, *, labels=None, title="Kaleion · playback", duration=60,
                     connect=False, show_values=True):
    """Play already evaluated samples with fixed bounds and a scrubber.

    Exact sweep cases are discrete. For smooth motion supply densely sampled
    Kaleion Frames: Plotly does not interpolate the mathematical construction.
    Camera state is retained during 3D playback. Purple means changing incidence.
    """
    if not np.isfinite(duration) or duration <= 0:
        raise ValueError("Frame duration must be positive milliseconds")
    data, labels = series(samples, labels)
    layout = _layout(data, title)
    layout.update(height=610, margin=dict(l=50, r=35, t=90, b=145))

    def frame_title(index):
        status = "" if data[index].status == "ready" else f" · {data[index].status}"
        return f"{title}<br><sup>{escape(labels[index] + status)}</sup>"

    frames = [go.Frame(
        name=str(i), data=[_trace(d, connect=connect, show_values=show_values)],
        traces=[0], layout=dict(title=dict(text=frame_title(i))),
    ) for i, d in enumerate(data)]
    options = dict(frame=dict(duration=duration, redraw=True), transition=dict(duration=0),
                   mode="immediate", fromcurrent=True)
    instant = dict(frame=dict(duration=0, redraw=True), transition=dict(duration=0), mode="immediate")
    layout["title"]["text"] = frame_title(0)
    layout["updatemenus"] = [dict(
        type="buttons", direction="right", x=0, y=-0.12, xanchor="left", yanchor="top",
        bgcolor=GRID, bordercolor=GRID, showactive=False,
        buttons=[dict(label="Play", method="animate", args=[None, options]),
                 dict(label="Pause", method="animate", args=[[None], instant]),
                 dict(label="Restart", method="animate", args=[["0"], instant])],
    )]
    layout["sliders"] = [dict(
        x=0, y=-0.28, len=1, currentvalue=dict(visible=False),
        steps=[dict(label=label if len(data) <= 20 and len(label) <= 12 else str(i), method="animate",
                    args=[[str(i)], instant]) for i, label in enumerate(labels)],
    )]
    return go.Figure(data=frames[0].data, layout=layout, frames=frames)


def transition_figure(transition, name, *, steps=41, title="Kaleion · motion", **kwargs):
    """Sample a captured forward or reversed Transition, including both ends."""
    if isinstance(steps, bool) or not isinstance(steps, int) or steps < 2:
        raise ValueError("Use an integer number of steps, at least two")
    times = np.linspace(0, 1, steps)
    samples = [transition.frame(name, float(t)) for t in times]
    if any(frame is None for frame in samples):
        raise ValueError(f"No placed motion track for {name!r}")
    direction = "Undo" if transition.backwards else "Forward"
    return animation_figure(samples, labels=[f"{direction} · {t:.0%}" for t in times],
                            title=title, **kwargs)
