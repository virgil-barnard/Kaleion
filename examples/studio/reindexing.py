"""Authoring recipes for copied domains; the core owns addressing and lineage.

No view coordinates become source addresses. Ordering is a checked construction,
not the current order of marks in a rendered table.
"""

from kaleion import F
from kaleion.model import Snapshot


def reindex(args, roots, captured, parse):
    common = {"source", "kind", "axis", "placement"}
    choices = {"tile": {"times"}, "gather": {"addresses", "field", "order", "bijective"},
               "concat": {"other"}}
    kind = args.get("kind")
    if kind not in choices or set(args) != common | choices[kind]:
        raise ValueError("Choose Repeat, Address list or Join and supply its choices")
    source = roots[args["source"]]
    snapshot = captured.results.get(args["source"])
    if not isinstance(snapshot, Snapshot):
        raise ValueError("Choose a ready collection; measure or select an incidence first")
    axis = args["axis"]
    if axis is not None and (not isinstance(axis, str) or axis not in snapshot.axes):
        raise ValueError("Choose a declared logical axis or the flattened sequence")
    if args["placement"] not in ("unplaced", "indices"):
        raise ValueError("Choose Unplaced or Index chart for the result")
    if kind == "tile":
        times = args["times"]
        if isinstance(times, dict) and set(times) == {"object"}:
            # A constructor takes one value, not one keyed read per source item.
            # scalar() checks this again in every parameter case, including empty
            # or multiple measurements. Never freeze the current displayed total.
            driver = captured.results.get(times["object"])
            if not isinstance(driver, Snapshot):
                raise ValueError("Choose a ready object supplying one integer value")
            times = roots[times["object"]].scalar()
        else:
            times = parse(times)
        result = source.tile(times, axis=axis)
    elif kind == "concat":
        other = captured.results.get(args["other"])
        if not isinstance(other, Snapshot):
            raise ValueError("Join another ready collection")
        result = source.concat(roots[args["other"]], axis=axis)
    else:
        address_snapshot = captured.results.get(args["addresses"])
        if not isinstance(address_snapshot, Snapshot):
            raise ValueError("Choose a ready address collection")
        if any(not isinstance(args[k], str) or args[k] not in address_snapshot.context()
               for k in ("field", "order")):
            raise ValueError("Choose an address field and an ordering field from the address object")
        if type(args["bijective"]) is not bool:
            raise ValueError("Declare whether every source slot must occur exactly once")
        addresses = roots[args["addresses"]]
        # Checking a report once is insufficient: this guard survives new cases.
        unique_order = addresses.count(by=F[args["order"]]).where(F.value == 1)
        ordered = addresses.require(unique_order, message="Address order must be unique")
        ordered = ordered.order_by(F[args["order"]]).with_values(F[args["field"]])
        operation = source.permute if args["bijective"] else source.gather
        result = operation(ordered, axis=axis)
    if args["placement"] == "indices":
        # A declared display chart, separate from the source-address decision.
        axes = list(reversed(snapshot.axes)) if axis is not None else []
        coordinates = [F[a] for a in axes] or [F.index]
        dimension = snapshot.positions.shape[1] if snapshot.positions is not None else max(2, len(coordinates))
        if len(coordinates) > dimension:
            raise ValueError("Index chart needs all logical axes; choose Unplaced, then Arrange")
        result = result.arrange(*coordinates, *([0] * (dimension - len(coordinates))))
    return result
