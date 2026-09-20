"""Presentation of captured lesson 11 data; no construction or evaluation here."""

from itertools import combinations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from kaleion.viewers.plotly import animation_figure
from lesson_views import BACKGROUND, COLORS, INK, style, xy_cells


def binary_panels(snapshots, titles, *, title, height=470):
    figure = make_subplots(rows=1, cols=len(snapshots), subplot_titles=titles,
                           horizontal_spacing=.10)
    for column, snapshot in enumerate(snapshots, 1):
        trace = xy_cells(snapshot)
        trace.mode = "markers+text"
        trace.text = list(map(str, snapshot.values))
        trace.textfont = dict(size=11, color=INK)
        trace.marker.color = [COLORS[(column-1) % len(COLORS)] if v else "#27384c"
                              for v in snapshot.values]
        figure.add_trace(trace, row=1, col=column)
        figure.update_xaxes(title_text="Coefficient degree j", dtick=1, row=1, col=column)
        figure.update_yaxes(title_text="Row", dtick=1, row=1, col=column)
    return style(figure, title, height=height)


def _line_path(vectors, positions):
    """Route a captured triple in the lesson's fixed triangle-and-circle chart."""
    if set(vectors) == {3, 5, 6}:
        angle = np.linspace(0, 2*np.pi, 90)
        return np.cos(angle), np.sin(angle)
    a, b = max(combinations(vectors, 2),
               key=lambda pair: np.sum((positions[pair[0]]-positions[pair[1]])**2))
    return np.array([positions[a][0], positions[b][0]]), np.array([positions[a][1], positions[b][1]])


def _captured_lines(supports):
    return [tuple(int(v) for v, r, hit in zip(supports.fields["vector"],
                                             supports.fields["line_rank"], supports.values)
                  if r == rank and hit)
            for rank in sorted(set(supports.fields["line_rank"]))]


def fano_gallery(panels, chart):
    """Seven captured support masks. Amber selects C; violet its paired dual word."""
    positions = dict(zip(map(int, chart.values), chart.positions))
    lines = _captured_lines(panels)
    figure = go.Figure()
    for rank, selected in enumerate(lines):
        cx, cy = 6*(rank % 4), -5*(rank // 4)
        for line in lines:
            x, y = _line_path(line, positions)
            figure.add_trace(go.Scatter(
                x=(x+cx).tolist(), y=(y+cy).tolist(), mode="lines", hoverinfo="skip",
                line=dict(color=COLORS[1] if line == selected else "#35465e",
                          width=3 if line == selected else 1), showlegend=False))
        mask = panels.fields["line_rank"] == rank
        word = int(panels.fields["word"][mask][0])
        figure.add_annotation(x=cx, y=cy+2.6, text=f"c = {word} · d = {127-word}",
                              showarrow=False, font=dict(size=14))
    figure.add_trace(go.Scatter(
        x=panels.positions[:, 0].tolist(), y=panels.positions[:, 1].tolist(),
        mode="markers+text", text=list(map(str, panels.fields["vector"])),
        textposition="middle center", textfont=dict(color=BACKGROUND, size=11),
        marker=dict(size=24, color=[COLORS[1] if v else COLORS[2] for v in panels.values]),
        hovertext=[f"Codeword {word}: bit {degree} = {value}<br>H column label: {vector}"
                   f"<br>Dual complement: {127-int(word)}<br>Occurrence: {oid}"
                   for word, degree, value, vector, oid in zip(
                       panels.fields["word"], panels.fields["degree"], panels.values,
                       panels.fields["vector"], panels.ids)],
        hovertemplate="%{hovertext}<extra></extra>"))
    figure.add_annotation(x=18, y=-4.6, showarrow=False, align="left",
                          text="Amber: C · 3 points<br>Violet: C⊥ · 4 points"
                               "<br><br>Points label H columns."
                               "<br>A circle is also a line.",
                          font=dict(size=12))
    style(figure, "Seven lines · seven dual complements", height=630)
    figure.update_xaxes(visible=False, range=[-2.7, 21])
    figure.update_yaxes(visible=False, range=[-7.2, 3.2], scaleanchor="x")
    return figure


def linked_field_motion(ring_frames, plane_frames, labels, *, supports, chart, seed):
    """Show the same captured action in two charts, with one shared scrubber."""
    if len(ring_frames) != len(plane_frames) or len(labels) != len(ring_frames):
        raise ValueError("Both charts need the same sampled times")
    figure = animation_figure(ring_frames, labels=labels,
                              title="One action · cyclic shift and projective motion", duration=65)
    plane = animation_figure(plane_frames, labels=labels, duration=65)
    colors = {oid: COLORS[1] if hit == 0 else COLORS[2]
              for oid, hit in zip(seed.ids, seed.fields["seed_trace"])}
    for frame, other, sample in zip(figure.frames, plane.frames, ring_frames):
        second = go.Scatter(other.data[0])
        second.x = [x+8 for x in second.x]
        color = [colors[a if a is not None else b]
                 for a, b in zip(sample.before_ids, sample.after_ids)]
        frame.data[0].marker.color = color
        second.marker.color = color
        for trace in (frame.data[0], second):
            trace.marker.size = 30
            trace.textfont = dict(size=11, color=BACKGROUND)
            trace.zorder = 2
        frame.data = [frame.data[0], second]
        frame.traces = [0, 1]
    figure.data[0].update(figure.frames[0].data[0])
    figure.add_trace(figure.frames[0].data[1])
    positions = dict(zip(map(int, chart.values), chart.positions))
    for line in _captured_lines(supports):
        x, y = _line_path(line, positions)
        figure.add_trace(go.Scatter(x=(x+8).tolist(), y=y.tolist(), mode="lines",
                                    line=dict(color="#35465e", width=1), hoverinfo="skip"))
    angle = np.linspace(0, 2*np.pi, 90)
    figure.add_trace(go.Scatter(x=(2*np.cos(angle)).tolist(), y=(2*np.sin(angle)).tolist(),
                                mode="lines", line=dict(color="#35465e", width=1), hoverinfo="skip"))
    figure.update_layout(showlegend=False, height=650)
    for x, text in ((0, "Cyclic shift · j ↦ j + 1"),
                    (8, "Projective action · z ↦ α z")):
        figure.add_annotation(x=x, y=2.7, text=text, showarrow=False, font=dict(size=15))
    figure.add_annotation(x=4, y=-2.8, showarrow=False, font=dict(size=13),
                          text="The same seven occurrences appear in both charts."
                               "<br>Amber follows a line; labels pack field coefficients.")
    figure.update_xaxes(visible=False, range=[-3.3, 11.3])
    figure.update_yaxes(visible=False, range=[-3.3, 3.3], scaleanchor="x")
    return figure
