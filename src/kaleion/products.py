"""Named roles for finite Cartesian products, composed from existing operations.

Product owns the slot convention and source reads. It does not evaluate, choose a
relation, identify equal labels, or infer placement from the factors' geometry.
"""

from dataclasses import dataclass
import keyword
from types import MappingProxyType

from .api import Collection
from .ir import F


@dataclass(frozen=True, eq=False, init=False)
class Product:
    """Declare two or three named factors and read their fields in product context.

    ``Product(point=points, line=lines).domain`` has one new occurrence per tuple
    of current source slots, unit values, named logical axes, and no placement.
    ``read("point", F.u)`` reads the corresponding source field. Duplicate labels
    and duplicate retained keys remain separate occurrences: slot addresses, not
    labels, supply this product's correspondence.

    Factor order determines storage order (last role varies fastest). Reordering
    a factor changes slot contents; it does not promise persistent pair identity
    across that edit. Retain semantic source keys explicitly when they are needed.
    The wrapper builds ordinary Grid/Count/Bind definitions and is not serialized.
    """

    factors: object
    domain: Collection

    def __init__(self, **factors):
        if not 2 <= len(factors) <= 3:
            raise ValueError("Declare two or three named product factors")
        reserved = {"value", "index", "key", "x", "y", "z"}
        if any(not name.isidentifier() or keyword.iskeyword(name) or name in reserved
               for name in factors):
            raise ValueError("Product roles need distinct identifiers, excluding built-in fields")
        if any(not isinstance(source, Collection) for source in factors.values()):
            raise TypeError("Product factors must be collections or arrangements; select an incidence explicitly")
        object.__setattr__(self, "factors", MappingProxyType(dict(factors)))
        object.__setattr__(self, "domain", Collection.grid(
            *(source.count().scalar() for source in factors.values()),
            axes=tuple(factors), values=1, name="Product: " + " × ".join(factors)))

    def read(self, role, field=F.value):
        """Read an expression in the named factor's captured source context.

        The product axis names a source slot. Copy fields with ``annotate`` before
        selection or reindexing if a later operation must retain these role reads.
        Geometry may be read explicitly but is never adopted automatically.
        """
        if role not in self.factors:
            raise KeyError(f"Unknown product role {role!r}; choose from {tuple(self.factors)}")
        return self.factors[role].bind(on=F[role], key=F.index, read=field)
