"""Two independently indexed quotient incidences meet an independent unit field.

The reusable choices are singleton reduction, explicit key alignment, addition
of measured fields, and a finite comparison. No equality or color is inferred
from the picture. The non-coprime case exposes the exact overlap correction.
"""

from kaleion import Collection, F, Workspace, param


def quotient_equality(a=7, b=5):
    """Small canvas with two measured lifts and a separately constructed RHS."""
    a_, b_ = param("a"), param("b")
    lower_domain = Collection.grid(b_ - 1, a_ - 1, values=1).arrange(F.i + 1, F.j + 1)
    # Reverse axis/storage order deliberately: alignment must use keys, not zip.
    upper_domain = Collection.grid(a_ - 1, b_ - 1, axes=("j", "i"), values=1).arrange(F.i + 1, F.j + 1)
    lower = lower_domain.where(b_ * (F.j + 1) <= a_ * (F.i + 1))
    upper = upper_domain.where(a_ * (F.i + 1) <= b_ * (F.j + 1))
    keys = (F.i, F.j)
    lower_cells = lower.count(by=keys)
    upper_cells = upper.count(by=(F.j, F.i))
    ones = Collection.grid(b_ - 1, a_ - 1, values=1).arrange(F.i + 1, F.j + 1, 1)
    probes = Collection.grid(b_ - 1, a_ - 1, values=0).arrange(F.i + 1, F.j + 1, 0)
    first = probes.with_values(lower_cells.bind(on=keys, key=keys)).arrange(F.i + 1, F.j + 1, F.value)
    covered = first.with_values(F.value + upper_cells.bind(on=keys, key=keys)).arrange(F.i + 1, F.j + 1, F.value)
    residual = covered.with_values(F.value - ones.bind(on=keys, key=keys)).arrange(F.i + 1, F.j + 1, F.value)
    workspace = Workspace({
        "Lower domain": lower_domain, "Upper domain": upper_domain,
        "Lower incidence": lower, "Upper incidence": upper,
        "Lower cells": lower_cells, "Upper cells": upper_cells,
        "Column quotients": lower.count(by=F.i).arrange(F.i + 1, F.value),
        "Row quotients": upper.count(by=F.j).arrange(F.j + 1, F.value),
        "Independent ones": ones, "Counted area": covered.sum(),
        "Rectangle area": ones.sum(), "Equality residual": residual,
        "Moving cover": probes,
    }, {"a": a, "b": b}, max_items=2000, max_history=40)
    workspace.set("Moving cover", first)
    workspace.set("Moving cover", covered)
    return workspace
