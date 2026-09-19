"""Visible coordinate formulas for the finite-geometry lessons, not a value domain.

An integer code a + p*b represents a + b*i, with i*i = -1 and 0 <= a,b < p.
These functions accept Python integers or Kaleion expressions and only compose
ordinary arithmetic. The quotient is a field when p is prime and p % 4 == 3;
lesson 09 deliberately also uses p=5 to exhibit a reducible counterexample.
"""


def field_multiply(left, right, p):
    """Multiply coefficient codes in F_p[X]/(X² + 1)."""
    a, b = left % p, left // p
    c, d = right % p, right // p
    return (a*c - b*d) % p + p*((a*d + b*c) % p)


def field_sum(terms, p):
    """Add coefficient codes; integer addition of their codes is different."""
    terms = tuple(terms)
    return sum(z % p for z in terms) % p + p*(sum(z // p for z in terms) % p)


def field_conjugate(z, p):
    return z % p + p*((-(z // p)) % p)


def field_norm(z, p):
    """The scalar residue a²+b², represented in 0,...,p-1."""
    return ((z % p)**2 + (z // p)**2) % p


def hermitian_pair(left, right, p):
    """h(left,right) = sum left_j * conjugate(right_j), linear in left."""
    if len(left) != len(right):
        raise ValueError("Hermitian vectors need the same number of coordinates")
    return field_sum((field_multiply(x, field_conjugate(y, p), p)
                      for x, y in zip(left, right)), p)


def element_label(z, p):
    """Presentation label; codes remain the exact stored integer values."""
    a, b = int(z) % p, int(z) // p
    return str(a) if b == 0 else f"{a} + {b}i"
