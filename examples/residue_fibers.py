"""Count remainder fibers, then use the measured period as a motion argument.

These are bounded authoring recipes, not a group or CRT implementation. Positive
integer parameters a,b are assumed. The all-pairs witness domain has (a*b)**2
items; the saved example uses 576. No gcd/lcm routine supplies the construction.
"""

from kaleion import Collection, F, Workspace, param


def residue_definitions():
    """Keep the integer domain, expected pairs, witnesses, and measures distinct."""
    a, b = param("a"), param("b")
    integers = (Collection.grid(a * b, axes=("n",), values=F.n)
                .annotate(r=F.n % a, s=F.n % b).arrange(F.n, 0, 0))
    kernel = integers.where((F.r == 0) & (F.s == 0))
    size = kernel.count()
    period = size.with_values(a * b // F.value)
    # Explicit expected axes retain every zero fiber, even a wholly empty row.
    triples = Collection.grid(a, b, a * b, axes=("r", "s", "n"), values=F.n)
    relation = triples.where((F.n % a == F.r) & (F.n % b == F.s))
    counts = relation.count(by=(F.r, F.s)).arrange(F.r, F.s, F.value)
    pairs = Collection.grid(a, b, axes=("r", "s"), values=1).arrange(F.r, F.s, 0)
    d = size.bind(on=0)
    compatible = pairs.where((F.r - F.s) % d == 0)
    membership = compatible.count(by=(F.r, F.s)).arrange(F.r, F.s, 0)
    predicted = membership.with_values(d * F.value)
    ranks = integers.group_by(F.r, F.s).order_by(F.n).ranks(key=F.n)
    return {
        "Integer line": integers, "Remainder relation": relation,
        "Fiber sizes": counts, "Kernel": kernel, "Kernel size": size,
        "Period": period, "Ranks": ranks, "Pair domain": pairs,
        "Predicted sizes": predicted,
    }


def copied_period(integers, size, period):
    """A set decomposition with explicit new copies and preserved representative n.

    Ordering before Tile makes the sheet ordinal a deliberate address convention.
    The reconstructed label is not a cardinality. This recipe does not claim that
    addition is componentwise in (representative, sheet); there is a carry.
    """
    length = period.bind(on=0)
    first = integers.where(F.n < length).select().order_by(F.n)
    copies = first.tile(size.scalar()).annotate(sheet=F.index // length)
    lifted = copies.with_values(F.n + length * F.sheet).arrange(F.r, F.s, F.sheet)
    return first, lifted


def residue_fibers(*, a=6, b=4):
    """Record folding, measured separation, and a fiber-preserving cyclic action."""
    roots = residue_definitions()
    integers, ranks = roots["Integer line"], roots["Ranks"]
    first, copies = copied_period(integers, roots["Kernel size"], roots["Period"])
    roots.update({"One period": first, "Copied sheets": copies, "Moving residues": integers})
    workspace = Workspace(roots, {"a": a, "b": b}, max_items=2000, max_history=40)
    folded = integers.arrange(F.r, F.s, 0)
    stacked = integers.arrange(F.r, F.s, ranks.bind(on=F.n))
    workspace.set("Moving residues", folded)
    workspace.set("Moving residues", stacked)
    # The slots belong to the original n-axis. Roll transports the same items
    # through those fixed positions; n becomes the destination slot, value stays
    # the original integer. Its residues stay fixed under this measured shift.
    workspace.set("Moving residues", stacked.roll(axis="n", shift=roots["Period"].bind(on=0)))
    return workspace
