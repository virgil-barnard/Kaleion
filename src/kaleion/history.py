"""Definitions, evaluation snapshots, observations, and undo/redo ownership."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from types import MappingProxyType

from .api import Object, wrap
from .ir import freeze, graph, load_graph, encode
from .evaluate import Evaluator
from .model import plain, snapshot_dict, snapshot_from_dict
from .motion import Motion, Transition


def _needs_tuple_schema(value):
    """Detect optional contents in every retained state, including redo/evidence."""
    if isinstance(value, dict):
        return (value.get("op") == "tuples"
                or ("ids" in value and "values" in value and value["values"] is None)
                or any(_needs_tuple_schema(v) for v in value.values()))
    return isinstance(value, list) and any(_needs_tuple_schema(v) for v in value)


@dataclass(frozen=True, eq=False)
class State:
    roots: object
    parameters: object
    results: object
    errors: object
    evaluated: object
    provenance: object

    def __post_init__(self):
        for key in ("roots", "parameters", "results", "errors", "evaluated"):
            object.__setattr__(self, key, MappingProxyType(dict(getattr(self, key))))
        object.__setattr__(self, "provenance", freeze(self.provenance))

    @classmethod
    def evaluate(cls, roots, parameters, max_items=10_000):
        engine = Evaluator(parameters, max_items=max_items)
        results, errors = engine.run(roots)
        provenance = {
            "graph": graph({k: v.node for k, v in roots.items()}),
            "parameters": dict(parameters),
            "trace": engine.records,
            "meaning": "Finite evaluated definitions and correspondence; no universal equality asserted",
        }
        return cls(roots, parameters, results, errors, engine.evaluated, provenance)

    def to_dict(self):
        return {
            "provenance": plain(self.provenance),
            "results": {k: snapshot_dict(v) for k, v in self.results.items()},
            "errors": dict(self.errors),
            "evaluated": {k: snapshot_dict(v) for k, v in self.evaluated.items()},
        }

    @classmethod
    def from_dict(cls, d):
        prov = d["provenance"]
        roots = {k: wrap(v) for k, v in load_graph(prov["graph"]).items()}
        return cls(
            roots,
            prov["parameters"],
            {k: snapshot_from_dict(v) for k, v in d["results"].items()},
            d["errors"],
            {k: snapshot_from_dict(v) for k, v in d["evaluated"].items()},
            prov,
        )


@dataclass(frozen=True)
class Observation:
    note: str
    time: str
    state: State


class Workspace:
    def __init__(
        self, roots=None, parameters=None, *, max_items=10_000, max_history=100
    ):
        if not isinstance(max_history, int) or not 1 <= max_history <= 1000:
            raise ValueError("History limit must lie in [1,1000]")
        self.max_items, self.max_history = max_items, max_history
        self.state = State.evaluate(roots or {}, parameters or {}, max_items)
        self._past, self._future, self.observations = [], [], []

    @property
    def can_undo(self):
        return bool(self._past)

    @property
    def can_redo(self):
        return bool(self._future)

    def _commit(self, roots, parameters, motions=None):
        next_state = State.evaluate(roots, parameters, self.max_items)
        transition = Transition(
            self.state, next_state, MappingProxyType(dict(motions or {}))
        )
        transition.validate()
        self._past.append(transition)
        if len(self._past) > self.max_history:
            self._past.pop(0)
        self._future.clear()
        self.state = next_state
        return transition

    def set(self, name, construction, *, motion=None):
        if not isinstance(construction, Object):
            raise TypeError("Set a symbolic construction")
        return self._commit(
            {**self.state.roots, name: construction},
            self.state.parameters,
            {name: motion} if motion is not None else None,
        )

    def remove(self, name):
        roots = dict(self.state.roots)
        if name not in roots:
            raise KeyError(name)
        del roots[name]
        return self._commit(roots, self.state.parameters)

    def set_parameters(self, *, motions=None, **parameters):
        return self._commit(
            self.state.roots, {**self.state.parameters, **parameters}, motions
        )

    def undo(self):
        if not self._past:
            raise IndexError("Nothing to undo")
        transition = self._past.pop()
        self._future.append(transition)
        self.state = transition.before
        return transition.reverse()

    def redo(self):
        if not self._future:
            raise IndexError("Nothing to redo")
        transition = self._future.pop()
        self._past.append(transition)
        self.state = transition.after
        return transition

    def capture(self, note=""):
        obs = Observation(note, datetime.now(timezone.utc).isoformat(), self.state)
        self.observations.append(obs)
        return obs

    def restore(self, observation):
        next_state = observation.state
        transition = Transition(self.state, next_state, {})
        transition.validate()
        self._past.append(transition)
        if len(self._past) > self.max_history:
            self._past.pop(0)
        self._future.clear()
        self.state = next_state
        return transition

    def to_json(self):
        # History stores exact evaluated states and the recorded path definition.
        states = []
        ids = {}

        def state_id(s):
            key = id(s)
            if key not in ids:
                ids[key] = len(states)
                states.append(s.to_dict())
            return ids[key]

        def step(t):
            return {
                "before": state_id(t.before),
                "after": state_id(t.after),
                "motions": {
                    k: None if m.path is None else [encode(e) for e in m.path]
                    for k, m in t.motions.items()
                },
            }

        current = state_id(self.state)
        past = [step(t) for t in self._past]
        future = [step(t) for t in self._future]
        observations = [
            {"note": o.note, "time": o.time, "state": state_id(o.state)}
            for o in self.observations
        ]
        return json.dumps(
            {
                "format": "kaleion-python",
                "schema": 2 if _needs_tuple_schema(states) else 1,
                "max_items": self.max_items,
                "max_history": self.max_history,
                "states": states,
                "current": current,
                "past": past,
                "future": future,
                "observations": observations,
            },
            indent=2,
            allow_nan=False,
        )

    @classmethod
    def from_json(cls, text):
        if len(text.encode()) > 32 * 1024 * 1024:
            raise ValueError("Workspace exceeds 32 MiB import budget")
        doc = json.loads(text)
        # The v0.1 rename changes the envelope name, not the stored schema.
        if (
            doc.get("format") not in ("kaleion-python", "icarus-python")
            or doc.get("schema") not in (1, 2)
        ):
            raise ValueError("Unsupported workspace")
        if len(doc["states"]) > 1000:
            raise ValueError("Too many saved states")
        if doc["schema"] == 1 and _needs_tuple_schema(doc["states"]):
            raise ValueError("Tuple-only domains require workspace schema 2")
        states = [State.from_dict(s) for s in doc["states"]]
        from .ir import Expr

        def expr(d, depth=0):
            if depth > 100:
                raise ValueError("Motion expression exceeds budget")
            if isinstance(d, dict) and "$expr" in d:
                return Expr(d["$expr"], tuple(expr(a, depth + 1) for a in d["args"]))
            if isinstance(d, list):
                return tuple(expr(a, depth + 1) for a in d)
            if isinstance(d, dict):
                raise ValueError("Motion cannot reference external nodes")
            return d

        def step(s):
            motions = {
                k: Motion(None if p is None else tuple(expr(e) for e in p))
                for k, p in s["motions"].items()
            }
            t = Transition(
                states[s["before"]], states[s["after"]], MappingProxyType(motions)
            )
            t.validate()
            return t

        obj = cls(max_items=doc["max_items"], max_history=doc["max_history"])
        obj.state = states[doc["current"]]
        obj._past = [step(s) for s in doc["past"]]
        obj._future = [step(s) for s in doc["future"]]
        obj.observations = [
            Observation(o["note"], o["time"], states[o["state"]])
            for o in doc["observations"]
        ]
        return obj
