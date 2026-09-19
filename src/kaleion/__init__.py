"""Kaleion discovery core: symbolic construction, exact contents, explicit motion."""

from .api import (
    Collection,
    Arrangement,
    Lens,
    Incidence,
    Transform,
    Move,
    Values,
    Place,
    wrap,
)
from .ir import (
    Expr,
    F,
    param,
    vector,
    choose,
    sin,
    cos,
    sqrt,
    floor,
    ceil,
    graph,
    load_graph,
)
from .evaluate import Evaluator, EvaluationError
from .model import Snapshot, IncidenceSnapshot, Ref
from .motion import Motion, Transition, Frame
from .history import Workspace, State, Observation
from .sweep import Construction, Sweep
from .grouping import Grouping, Coverage

__version__ = "0.1.0"
__all__ = [
    "Collection",
    "Arrangement",
    "Lens",
    "Incidence",
    "Transform",
    "Move",
    "Values",
    "Place",
    "Expr",
    "F",
    "param",
    "vector",
    "choose",
    "sin",
    "cos",
    "sqrt",
    "floor",
    "ceil",
    "Evaluator",
    "EvaluationError",
    "Snapshot",
    "IncidenceSnapshot",
    "Ref",
    "Motion",
    "Transition",
    "Frame",
    "Workspace",
    "State",
    "Observation",
    "Construction",
    "Sweep",
    "graph",
    "load_graph",
    "wrap",
    "Grouping",
    "Coverage",
]
