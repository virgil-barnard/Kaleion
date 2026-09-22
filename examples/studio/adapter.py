"""A bounded semantic command boundary for a lesson-independent authoring study.

No screen coordinates, selector modes, Python source, or lesson names enter here.
Definitions, exact previews, captured history, and presentation remain separate.
"""

import operator
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from kaleion import Collection, F, Inspection, Product, Workspace
from kaleion.history import Observation, State
from kaleion.ir import expression as constant
from kaleion.model import IncidenceSnapshot, Ref
from .groups import captured_groups
from .coverage import captured_coverage, unique_assignment


OPERATORS = {
    "+": operator.add, "-": operator.sub, "*": operator.mul,
    "//": operator.floordiv, "%": operator.mod,
    "=": operator.eq, "≠": operator.ne, "<": operator.lt, "≤": operator.le,
    ">": operator.gt, "≥": operator.ge, "and": operator.and_, "or": operator.or_,
}

ARGUMENTS = {
    "integers": {"values"}, "grid": {"shape", "axes", "value"},
    "product": {"factors"}, "field": {"source", "field", "value"},
    "lens": {"source", "rule"}, "select": {"source"},
    "measure": {"source", "by", "reducer", "weight", "order", "key"},
    "place": {"source", "coordinates"},
    "group_lens": {"source", "capture", "by", "group"},
    "assignment": {"source", "by", "expected", "expected_by", "capture", "expected_capture", "value", "field"},
}


def integer(text):
    """Decimal strings cross the browser boundary without IEEE-754 rounding."""
    if not isinstance(text, str) or not re.fullmatch(r"-?(0|[1-9][0-9]*)", text):
        raise ValueError("Use an integer written as a decimal string")
    if len(text) > 1235 or int(text).bit_length() > 4096:
        raise ValueError("Integer exceeds the 4096-bit arithmetic budget")
    return int(text)


def exact_wire(value):
    """Receipt integers are strings; floating presentation coordinates stay floats."""
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


def expression(spec, roots, depth=0):
    if depth > 20 or not isinstance(spec, dict):
        raise ValueError("Expression needs a bounded structured formula")
    if set(spec) == {"integer"}:
        return constant(integer(spec["integer"]))
    if set(spec) == {"field"} and isinstance(spec["field"], str):
        return F[spec["field"]]
    if set(spec) == {"op", "args"} and spec["op"] in OPERATORS:
        if not isinstance(spec["args"], list) or len(spec["args"]) != 2:
            raise ValueError("Binary operations need two arguments")
        return OPERATORS[spec["op"]](
            *(expression(v, roots, depth + 1) for v in spec["args"]))
    if set(spec) == {"read"}:
        read = spec["read"]
        if not isinstance(read, dict) or set(read) != {"object", "on", "key", "value"}:
            raise ValueError("A keyed read needs a source, target key, source key, and value")
        return roots[read["object"]].bind(
            **{name: expression(read[source], roots, depth + 1)
               for name, source in (("on", "on"), ("key", "key"), ("read", "value"))})
    raise ValueError("Unsupported expression form; Python source is not accepted")


def build(command, roots, *, captured=None):
    """Lower explicit authoring choices into existing public builders only."""
    if not isinstance(command, dict) or set(command) != {"action", "name", "args"}:
        raise ValueError("A command needs action, name, and args")
    action, name, args = command["action"], command["name"], command["args"]
    if not isinstance(name, str) or not name.strip() or len(name) > 80:
        raise ValueError("Choose an object name of 1–80 characters")
    if not isinstance(args, dict):
        raise ValueError("Arguments must be a record")
    if action not in ARGUMENTS or set(args) - ARGUMENTS[action]:
        raise ValueError("Unsupported action or argument")
    required = ARGUMENTS[action] - ({"weight", "order", "key"} if action == "measure" else set())
    if required - set(args):
        raise ValueError("The declaration is missing required choices")
    if len(roots) >= 60 and name not in roots:
        raise ValueError("The study supports at most 60 objects in one workspace")
    if name in roots and (action != "place" or args.get("source") != name):
        raise ValueError("Choose a new name; existing constructions are retained")
    ex = lambda value: expression(value, roots)
    if action == "integers":
        if not isinstance(args["values"], list) or len(args["values"]) > 2000:
            raise ValueError("The study supports at most 2000 source occurrences")
        result = Collection.literal([integer(v) for v in args["values"]], name=name)
    elif action == "grid":
        axes = args["axes"]
        if (not isinstance(axes, list) or not isinstance(args["shape"], list)
                or not all(isinstance(a, str) and a.isidentifier() for a in axes)):
            raise ValueError("Give each axis a distinct field name")
        result = Collection.grid(*(integer(v) for v in args["shape"]), axes=axes,
                                 values=ex(args["value"]), name=name)
    elif action == "product":
        factors = args["factors"]
        product = Product(**{role: roots[entry["source"]] for role, entry in factors.items()})
        fields = {}
        for role, entry in factors.items():
            for field in entry["fields"]:
                alias = f"{role}_{field}"
                if alias in fields or alias in factors:
                    raise ValueError("Copied field names must not collide with roles or each other")
                fields[alias] = product.read(role, F[field])
        result = product.domain.annotate(**fields)
    else:
        source = roots[args["source"]]
        if action == "field":
            result = source.annotate(**{args["field"]: ex(args["value"])})
        elif action == "lens":
            result = source.where(ex(args["rule"]))
        elif action == "select":
            result = source.select()
        elif action == "measure":
            keys = args["by"]
            if not isinstance(keys, list) or not all(isinstance(k, str) for k in keys):
                raise ValueError("Retained keys must be an explicit list of fields")
            groups = source.group_by(*(F[k] for k in keys))
            reducer = args["reducer"]
            if reducer == "count":
                result = groups.count()
            elif reducer == "sum":
                result = groups.sum(value=ex(args["weight"]))
            elif reducer == "rank":
                result = groups.order_by(*(F[k] for k in args["order"])).ranks(key=F[args["key"]])
            else:
                raise ValueError("Choose Count, Sum, or Rank")
        elif action == "place":
            # Placement edits one view root. Existing derived roots keep their
            # immutable input definitions; this study does not rewrite a DAG.
            result = source.arrange(*(ex(c) for c in args["coordinates"]))
        elif action == "group_lens":
            if captured is None or args["source"] not in captured.results:
                raise ValueError("Choose a ready captured source for this group")
            groups = captured_groups(captured.results[args["source"]], args["by"])
            if args["capture"] != groups.capture:
                raise ValueError("The group selection belongs to an earlier capture")
            result = groups.lens(source, args["group"])
        elif action == "assignment":
            if captured is None:
                raise ValueError("Check coverage on captured inputs before assigning values")
            expected = roots[args["expected"]]
            report = captured_coverage(captured.results[args["source"]], args["by"],
                                       captured.results[args["expected"]], args["expected_by"])
            if (report.groups.capture != args["capture"]
                    or report.expected.node != args["expected_capture"]):
                raise ValueError("Coverage belongs to an earlier capture; check again")
            if not report.passed:
                raise ValueError("Assignment requires exactly one match per expected key and no outside matches")
            field = args["field"]
            if not isinstance(field, str) or not field.isidentifier() or field in report.expected.context():
                raise ValueError("Choose a new field name; expected labels and key fields are retained")
            result = unique_assignment(source, args["by"], expected, args["expected_by"], ex(args["value"]), field)
        else:
            raise ValueError(f"Unsupported authoring action: {action}")
    return name, result


def describe(state):
    """Read-only display data. Table projection is not a mathematical placement."""
    objects = []
    for name, definition in state.roots.items():
        obj = dict(name=name, kind=definition.node.kind, status="ready")
        if name in state.errors:
            objects.append({**obj, "status": "failed", "error": state.errors[name]})
            continue
        result = state.results[name]
        incidence = isinstance(result, IncidenceSnapshot)
        source = result.source if incidence else result
        context = source.context()
        fields = list(context)
        rows = []
        for i, oid in enumerate(source.ids):
            rows.append(dict(ref=[source.node, oid],
                             fields={k: exact_wire(v[i]) for k, v in context.items()},
                             position=None if source.positions is None else source.positions[i].tolist(),
                             match=True if not incidence else bool(result.mask[i])))
        objects.append({**obj, "fields": fields, "axes": list(source.axes), "rows": rows,
                        "placed": source.positions is not None,
                        "dimension": None if source.positions is None else source.positions.shape[1],
                        "declaration": str(definition.node.op) + " · " + name})
    return objects


@dataclass
class Preview:
    token: str
    revision: int
    name: str
    state: State


class Studio:
    """One local session; a preview is replaceable, a commit captures exactly it."""

    def __init__(self):
        self.workspace = Workspace(max_items=2000, max_history=40)
        self.revision = 0
        self.pending = None

    def check(self, revision):
        if type(revision) is not int or revision != self.revision:
            raise ValueError("This selection is out of date; refresh the workspace")

    def state(self):
        return dict(revision=self.revision, objects=describe(self.workspace.state),
                    undo=self.workspace.can_undo, redo=self.workspace.can_redo)

    def preview(self, command, revision):
        self.check(revision)
        self.pending = None
        name, definition = build(command, self.workspace.state.roots, captured=self.workspace.state)
        state = State.evaluate({**self.workspace.state.roots, name: definition}, {}, max_items=2000)
        if name in state.errors:
            raise ValueError(state.errors[name])
        # Validate correspondence/dimensionality before offering Apply.
        from kaleion.motion import Transition
        Transition(self.workspace.state, state, {}).validate()
        self.pending = Preview(uuid4().hex, revision, name, state)
        return dict(token=self.pending.token, revision=revision, name=name,
                    objects=describe(state))

    def commit(self, token, revision):
        self.check(revision)
        if self.pending is None or self.pending.token != token or self.pending.revision != revision:
            raise ValueError("Preview is no longer current; preview this declaration again")
        preview = self.pending
        transition = self.workspace.restore(Observation(
            "Studio declaration", datetime.now(timezone.utc).isoformat(), preview.state))
        self.pending = None
        self.revision += 1
        return {**self.state(), "active": preview.name,
                "motion": self.frames(transition, preview.name)}

    @staticmethod
    def frames(transition, name):
        frames = []
        for i in range(25):
            frame = transition.frame(name, i / 24)
            if frame is None:
                return []
            frames.append(dict(positions=frame.positions.tolist(), opacity=frame.opacity.tolist(),
                               before=list(frame.before_ids), after=list(frame.after_ids)))
        return frames

    def history(self, direction, revision, active):
        self.check(revision)
        if direction not in {"undo", "redo"}:
            raise ValueError("Unknown history action")
        transition = getattr(self.workspace, direction)()
        self.pending = None
        self.revision += 1
        return {**self.state(), "motion": self.frames(transition, active)}

    def inspect(self, name, ref, revision):
        self.check(revision)
        result = self.workspace.state.results[name]
        source = result.source if isinstance(result, IncidenceSnapshot) else result
        if len(ref) != 2 or ref[0] != source.node or ref[1] not in source.ids:
            raise ValueError("Select an occurrence in this captured object")
        return self.inspect_ref(ref, revision)

    def groups(self, name, by, revision):
        """Return a revision-scoped selection report, not a new measurement root."""
        self.check(revision)
        report = captured_groups(self.workspace.state.results[name], by)

        def refs(indices):
            return [[report.source.node, report.source.ids[i]] for i in indices]

        return dict(revision=revision, name=name, capture=report.capture, by=list(report.by),
                    domain=report.domain, groups=[
                        dict(key=exact_wire(key), key_types=["boolean" if isinstance(v, bool) else
                             "integer" if isinstance(v, int) else "number" if isinstance(v, float)
                             else "text" for v in key],
                             population=str(len(members)), count=str(len(matches)),
                             members=refs(members), matches=refs(matches))
                        for key, members, matches in zip(report.keys, report.members, report.matches)])

    def coverage(self, name, by, expected, expected_by, revision):
        """A captured coverage report over a separately chosen expected domain."""
        self.check(revision)
        report = captured_coverage(self.workspace.state.results[name], by,
                                   self.workspace.state.results[expected], expected_by)
        groups = report.groups

        def row(key, group, index=None):
            members = () if group is None else groups.members[group]
            matches = () if group is None else groups.matches[group]
            refs = lambda items: [[groups.source.node, groups.source.ids[i]] for i in items]
            return dict(key=exact_wire(key), key_types=["boolean" if isinstance(v, bool) else
                        "integer" if isinstance(v, int) else "number" if isinstance(v, float)
                        else "text" for v in key],
                        group=group, present=group is not None,
                        population=str(len(members)), count=str(len(matches)),
                        members=refs(members), matches=refs(matches),
                        expected_ref=None if index is None else [report.expected.node, report.expected.ids[index]],
                        status="missing" if not matches else "unique" if len(matches) == 1 else "multiple")

        return dict(revision=revision, name=name, by=list(by), expected=expected,
                    expected_by=list(expected_by), capture=groups.capture,
                    expected_capture=report.expected.node, passed=report.passed,
                    empty=not report.keys,
                    summary=dict(expected=str(len(report.keys)), unique=str(report.counts.count(1)),
                                 missing=str(report.counts.count(0)), multiple=str(sum(n > 1 for n in report.counts)),
                                 outside=str(len(report.unexpected))),
                    rows=[row(key, group, i) for i, (key, group) in enumerate(zip(report.keys, report.indices))],
                    unexpected=[row(groups.keys[i], i) for i in report.unexpected])

    def inspect_ref(self, ref, revision):
        """Follow a receipt to its captured driver, including an earlier version."""
        self.check(revision)
        if not isinstance(ref, list) or len(ref) != 2:
            raise ValueError("Use a scoped captured reference")
        inspector = Inspection(self.workspace.state)
        scoped = Ref(*ref)
        receipt = {"item": inspector.item(scoped).to_dict()}
        for query, fn in (("measurement", inspector.measurement), ("bindings", inspector.bindings)):
            try:
                value = fn(scoped)
                receipt[query] = [v.to_dict() for v in value] if isinstance(value, tuple) else value.to_dict()
            except (ValueError, KeyError, TypeError) as error:
                receipt[query] = {"unavailable": str(error)}
        return exact_wire(receipt)

    def reopen(self, text, revision):
        self.check(revision)
        restored = Workspace.from_json(text)
        if restored.max_items > 2000 or restored.max_history > 40:
            raise ValueError("Open a studio capture (2000 items, 40 history steps maximum)")
        self.workspace = restored
        self.pending = None
        self.revision += 1
        return self.state()
