"""Explicit parameter cases, separate from presentation time."""

from dataclasses import dataclass
from types import MappingProxyType

from .api import Object, Incidence
from .history import State
from .model import IncidenceSnapshot
from .motion import Motion, Transition


@dataclass(frozen=True)
class Construction:
    output: Object
    parameters: tuple[str, ...]

    def __call__(self, **bindings):
        if set(bindings) - set(self.parameters):
            raise ValueError("Unknown constructor parameter")
        return self.output.with_params(**bindings)


@dataclass(frozen=True)
class Sweep:
    output: Object
    parameter: str
    cases: tuple
    parameters: object = None

    def __post_init__(self):
        object.__setattr__(self, "cases", tuple(self.cases))
        if len(self.cases) > 1000:
            raise ValueError("Sweep exceeds 1000-case budget")
        object.__setattr__(
            self, "parameters", MappingProxyType(dict(self.parameters or {}))
        )

    def at(self, index):
        if not 0 <= index < len(self.cases):
            raise IndexError("Case outside sweep")
        return self.output.evaluate(
            **{**self.parameters, self.parameter: self.cases[index]}
        )

    def retain(self, through, *, identity="source"):
        if identity not in ("source", "occurrence"):
            raise ValueError("Choose source or occurrence identity")
        if not isinstance(self.output, Incidence):
            raise TypeError("Retain an incidence")
        if not 0 <= through < len(self.cases):
            raise IndexError("Case outside sweep")
        seen = {}
        for index in range(through + 1):
            result = self.at(index)
            ids = result.source.sources if identity == "source" else result.source.ids
            for i, matched in enumerate(result.mask):
                if matched and ids[i] not in seen:
                    seen[ids[i]] = {
                        "identity": ids[i],
                        "value": int(result.source.values[i]),
                        "case": self.cases[index],
                        "case_index": index,
                    }
        return tuple(seen.values())

    def transition(self, start, end, *, motion=None):
        if not 0 <= start < len(self.cases) or not 0 <= end < len(self.cases):
            raise IndexError("Case outside sweep")
        before = State.evaluate(
            {"result": self.output},
            {**self.parameters, self.parameter: self.cases[start]},
        )
        after = State.evaluate(
            {"result": self.output},
            {**self.parameters, self.parameter: self.cases[end]},
        )
        t = Transition(before, after, {"result": motion or Motion()})
        t.validate()
        return t
