"""The two Icarus papers, expressed with ordinary Kaleion constructions.

These authoring recipes have no viewer or gesture policy. Each map, relation,
measurement and exact comparison input remains a separate inspectable object.
"""

from kaleion import Collection, F, Workspace, param, vector
if __package__:
    from .studio.coverage import unique_assignment
else:
    from studio.coverage import unique_assignment


def division_parts():
    a, b = param("a"), param("b")
    table = (Collection.grid(b, a, values=(a * F.i + b * F.j) % (a * b))
             .annotate(raw=a * F.i + b * F.j).arrange(F.j, F.i))
    carry = table.where(F.raw >= a * b)
    quotient = carry.count(by=F.i)
    remainder = quotient.with_values(a * F.i - b * F.value)
    return table, carry, quotient, remainder


def periodic_factor(a, b):
    """One measured b-by-b period, repeated and truncated to a rows."""
    domain = Collection.grid(b, b, axes=("r", "q"), values=0)
    relation = domain.where((a * F.q + F.r) % b == 0)
    cells = relation.count(by=(F.r, F.q))
    seed = domain.with_values(cells.bind(on=(F.r, F.q), key=(F.r, F.q))).arrange(F.q, F.r)
    addresses = Collection.grid(a, values=F.i)
    repeated = seed.tile((a + b - 1) // b, axis="r").arrange(F.q, F.r)
    prefix = repeated.gather(addresses, axis="r").arrange(F.q, F.r)
    return relation, seed, addresses, repeated, prefix


def division_motion():
    """Count → displace → wrap → order by remainders, retaining every item."""
    a, b = param("a"), param("b")
    table, carry, quotient, remainder = division_parts()
    q = quotient.bind(on=F.i, key=F.i)
    r = remainder.bind(on=F.i, key=F.i)
    # Integer fields, not interpolated coordinates, define the wrapped address.
    column = (F.j + q) % a
    reconstruction = quotient.with_values(b * F.value + r)
    expected = Collection.grid(b, values=a * F.i)
    workspace = Workspace({
        "Residue table": table, "Carry relation": carry,
        "Quotients": quotient, "Remainders": remainder,
        "Reconstructed multiples": reconstruction, "Multiples": expected,
        "Moving table": table,
    }, {"a": 11, "b": 7}, max_items=2000, max_history=40)
    shifted = table.move(vector(q, 0))
    workspace.set("Moving table", shifted)
    wrapped = shifted.arrange(column, F.i)
    workspace.set("Moving table", wrapped)
    workspace.set("Moving table", wrapped.arrange(column, r))
    return workspace


def relation_matrices():
    """Q and R as incidences; weighted extraction, roll, and factor composition."""
    a, b = param("a"), param("b")
    table, carry, quotient, remainder = division_parts()
    q, r = quotient.bind(on=F.i, key=F.i), remainder.bind(on=F.i, key=F.i)
    q_domain = Collection.grid(b, a, values=F.j).arrange(F.j, F.i)
    r_domain = Collection.grid(b, b, values=F.j).arrange(F.j, F.i)
    q_relation = q_domain.where(F.j == q)
    r_relation = r_domain.where(F.j == r)
    q_read = q_relation.sum(by=F.i, value=F.j)
    r_read = r_relation.sum(by=F.i, value=F.j)
    # The reciprocal Q_{b/a} factors through r = b*n mod a. The second
    # factor is a truncated periodic relation: a*q + r = 0 mod b.
    # It becomes single-valued when gcd(a,b)=1; we never assume an inverse.
    first = Collection.grid(a, a, axes=("n", "r"), values=1)
    second = Collection.grid(a, b, axes=("r", "q"), values=1)
    first_relation = first.where(F.r == (b * F.n) % a)
    second_relation = second.where((a * F.q + F.r) % b == 0)
    first_cells = first_relation.count(by=(F.n, F.r))
    _, period, addresses, _, second_cells = periodic_factor(a, b)
    triples = Collection.grid(a, a, b, axes=("n", "r", "q"), values=1)
    witnesses = triples.where(
        (first_cells.bind(on=(F.n, F.r), key=(F.n, F.r)) == 1)
        & (second_cells.bind(on=(F.r, F.q), key=(F.r, F.q)) == 1))
    composed = witnesses.count(by=(F.n, F.q)).arrange(F.q, F.n)
    expected_domain = Collection.grid(a, b, axes=("n", "q"), values=1)
    direct = expected_domain.where(F.q == (b * F.n) // a).count(by=(F.n, F.q)).arrange(F.q, F.n)
    workspace = Workspace({
        "Carry relation": carry, "Quotients": quotient, "Remainders": remainder,
        "Q relation": q_relation, "R relation": r_relation,
        "Q extraction": q_read, "R extraction": r_read,
        "R column coverage": r_relation.count(by=F.j),
        "First factor": first_relation, "Periodic factor": second_relation,
        "Factor period": period, "Factor row addresses": addresses,
        "First factor cells": first_cells, "Periodic factor cells": second_cells,
        "Composition witnesses": witnesses, "Composed Q": composed,
        "Direct Q": direct, "Comparison domain": expected_domain,
        "Cycled table": table,
    }, {"a": 11, "b": 7}, max_items=2000, max_history=40)
    # A positive shift sends an original slot j to j+q modulo a. The
    # output's j is the new slot; identities and carried raw fields travel.
    workspace.set("Cycled table", table.roll(axis="j", shift=q_read.bind(on=F.i, key=F.i)))
    return workspace


def euclidean_step(*, r=3, b=4, q=1):
    """An explicit extended domain, then a shear and cyclic reassembly.

    A = r + q*b. The old r-by-b table has fewer occurrences than the extended
    A-by-b table. No permutation or group isomorphism between those is claimed.
    """
    rem, divisor, multiple = param("r"), param("b"), param("q")
    width = rem + multiple * divisor
    seed = (Collection.grid(divisor, width, values=(rem * F.i + divisor * F.j) % (width * divisor))
            .annotate(destination=(F.j - multiple * F.i) % width).arrange(F.j, F.i))
    old = Collection.grid(divisor, rem, values=(rem * F.i + divisor * F.j) % (rem * divisor))
    expected = Collection.grid(divisor, width, values=(width * F.i + divisor * F.j) % (width * divisor))
    workspace = Workspace({
        "Previous table": old, "Extended seed": seed,
        "New cells": seed.where(F.j >= rem),
        "Direct larger table": expected.arrange(F.j, F.i),
        "Moving extension": seed,
    }, {"r": r, "b": b, "q": q}, max_items=2000, max_history=40)
    shifted = seed.move(vector(-multiple * F.i, 0))
    workspace.set("Moving extension", shifted)
    workspace.set("Moving extension", shifted.arrange(F.destination, F.i))
    return workspace


def euclidean_next():
    """The paper's next step, after exchanging the generator roles."""
    return euclidean_step(r=4, b=7)


def periodic_extension():
    """The paper's finite periodic factor and an explicit zero-column join."""
    a, b = param("a"), param("b")
    relation, seed, addresses, repeated, prefix = periodic_factor(a, b)
    direct_domain = Collection.grid(a, b, axes=("r", "q"), values=0)
    counts = direct_domain.where((a * F.q + F.r) % b == 0).count(by=(F.r, F.q))
    direct = direct_domain.with_values(counts.bind(on=(F.r, F.q), key=(F.r, F.q)))
    square = Collection.grid(b, b, axes=("r", "q"), values=0)
    remainder_counts = square.where(F.q == (a * F.r) % b).count(by=(F.r, F.q))
    remainder = square.with_values(remainder_counts.bind(on=(F.r, F.q), key=(F.r, F.q)))
    zeros = Collection.grid(b, a - b, axes=("r", "q"), values=0)
    workspace = Workspace({
        "Period relation": relation, "One period": seed, "Row addresses": addresses,
        "Moving factor": seed, "Direct factor": direct.arrange(F.q, F.r),
        "R square": remainder.arrange(F.q, F.r), "Zero columns": zeros,
        "Padded R": remainder.concat(zeros, axis="q").arrange(F.q, F.r),
    }, {"a": 11, "b": 7}, max_items=2000, max_history=40)
    workspace.set("Moving factor", repeated)
    workspace.set("Moving factor", prefix)
    return workspace


def guarded_remainder_addresses():
    """A relation becomes addresses only under a retained uniqueness guard."""
    a, b = param("a"), param("b")
    domain = Collection.grid(b, b, values=0)
    relation = domain.where(F.j == (a * F.i) % b)
    slots = Collection.grid(b, axes=("j",), values=0)
    addresses = unique_assignment(relation, ["j"], slots, ["j"], F.i, "address")
    # All labels agree. Only the explicit addresses identify the source items.
    points = Collection.grid(b, values=9).annotate(original=F.i).arrange(F.i, (F.i * F.i) % b, (2 * F.i) % b)
    ordered = addresses.order_by(F.j).with_values(F.address)
    target = points.permute(ordered).arrange(F.index, 0, 0)
    workspace = Workspace({
        "R relation": relation, "Expected slots": slots, "Guarded addresses": addresses,
        "Scattered source": points, "Moving copies": points,
    }, {"a": 11, "b": 7}, max_items=2000, max_history=40)
    workspace.set("Moving copies", target)
    return workspace
