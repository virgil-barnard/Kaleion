"""Bounded display records from captured data, independent of named roots.

Capture identifiers select evaluated versions. Display labels never select a
version, and these queries neither execute a graph nor sample motion frames.
"""

from kaleion import Inspection
from kaleion.model import IncidenceSnapshot, Ref, Snapshot


def exact_wire(value):
    """Mathematical integers travel as strings; geometry remains floating point."""
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, int):
        return str(value)
    if isinstance(value, dict):
        return {k: exact_wire(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [exact_wire(v) for v in value]
    if hasattr(value, "item"):
        return exact_wire(value.item())
    return value


def snapshot_view(result):
    incidence = isinstance(result, IncidenceSnapshot)
    source = result.source if incidence else result
    if not isinstance(source, Snapshot):
        raise TypeError("Display a captured collection, arrangement, or incidence")
    context = source.context()
    rows = [dict(ref=[source.node, oid],
                 fields={k: exact_wire(v[i]) for k, v in context.items()},
                 position=None if source.positions is None else source.positions[i].tolist(),
                 match=True if not incidence else bool(result.mask[i]))
            for i, oid in enumerate(source.ids)]
    return dict(capture=result.node, fields=list(context), axes=list(source.axes), rows=rows,
                placed=source.positions is not None,
                dimension=None if source.positions is None else source.positions.shape[1])


def captured_result(state, capture):
    if not isinstance(capture, str) or not capture:
        raise ValueError("Choose a captured evaluation identifier")
    result = state.evaluated.get(capture)
    if result is None:
        result = next((s for s in state.results.values() if s.node == capture), None)
    if result is None:
        raise ValueError("This capture is unavailable in the current state; it cannot be evaluated here")
    return result


def captured_view(state, capture):
    """Describe an exact version, including an unnamed or earlier dependency."""
    result = captured_result(state, capture)
    source = result.source if isinstance(result, IncidenceSnapshot) else result
    if len(source) > 2000:
        raise ValueError("A studio view supports at most 2000 captured occurrences")
    return {**snapshot_view(result),
            "roots": [name for name, s in state.results.items() if s.node == capture]}


def measurement_evidence(state, ref):
    """Include the source universe even for a measurement with no contributors."""
    if not isinstance(ref, list) or len(ref) != 2 or not all(isinstance(v, str) for v in ref):
        raise ValueError("Use a scoped captured reference")
    receipt = Inspection(state).measurement(Ref(*ref), limit=2000)
    if receipt.truncated:
        raise ValueError("Contributor evidence exceeds the studio's 2000-item view budget")
    origin = captured_result(state, receipt.origin.node)
    universe = origin.metadata["universe"]
    # Verify availability and bounds even when there are no contributing items.
    captured_view(state, universe)
    return dict(measurement=exact_wire(receipt.to_dict()), universe=universe)
