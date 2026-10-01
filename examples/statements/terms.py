"""Small typed statement language. No Kaleion execution or proof claims here.

Integer literals cross JSON as strings. Parameters and bound coordinates are
different symbols; substitution is structural and never reparses printed text.
The bounded interpreter is for checking a translation at a finite case only.
"""

from dataclasses import dataclass, field
import math
import operator


@dataclass(frozen=True)
class Term:
    op: str
    args: tuple
    sort: str = "integer"
    _cost: int = field(init=False, repr=False, compare=False)
    _depth: int = field(init=False, repr=False, compare=False)

    def __post_init__(self):
        def measure(value):
            if isinstance(value, Term):
                return value._cost, value._depth
            if isinstance(value, tuple):
                children = [measure(v) for v in value]
                return 1 + sum(c for c, _ in children), max((d for _, d in children), default=0)
            return 1, 0
        cost, depth = measure(self.args)
        if cost > 20_000 or depth >= 128:
            raise ValueError("Expanded statement exceeds its term budget; preserve shared subexpressions before expanding further")
        object.__setattr__(self, "_cost", cost + 1)
        object.__setattr__(self, "_depth", depth + 1)

    def data(self):
        def encode(v):
            if isinstance(v, Term):
                return v.data()
            if isinstance(v, tuple):
                return [encode(x) for x in v]
            return str(v) if type(v) is int else v
        return {"op": self.op, "sort": self.sort, "args": [encode(v) for v in self.args]}

    def replace(self, bindings):
        if self in bindings:
            return bindings[self]
        def replace(v):
            if isinstance(v, Term):
                return v.replace(bindings)
            if isinstance(v, tuple):
                return tuple(replace(x) for x in v)
            return v
        return Term(self.op, tuple(replace(a) for a in self.args), self.sort)


def literal(value):
    if type(value) not in (int, bool):
        raise ValueError("Statement literals must be exact integers or booleans")
    return Term("literal", (value,), "boolean" if type(value) is bool else "integer")


ZERO, ONE, TRUE = literal(0), literal(1), literal(True)
ARITHMETIC = {"add": operator.add, "sub": operator.sub, "mul": operator.mul,
              "floordiv": operator.floordiv, "mod": operator.mod, "gcd": math.gcd}
COMPARISONS = {"eq": operator.eq, "ne": operator.ne, "lt": operator.lt,
               "le": operator.le, "gt": operator.gt, "ge": operator.ge}


def term(op, *args):
    """Only unconditional, typed identities are folded; no theorem simplifier."""
    sorts = tuple(a.sort for a in args)
    if op in ARITHMETIC or op in COMPARISONS:
        if sorts != ("integer", "integer"):
            raise ValueError(f"{op} requires two integers")
        sort = "boolean" if op in COMPARISONS else "integer"
    elif op in ("and", "or"):
        if sorts != ("boolean", "boolean"):
            raise ValueError(f"{op} requires two predicates")
        sort = "boolean"
    elif op in ("neg", "abs", "indicator", "not"):
        required = "boolean" if op in ("indicator", "not") else "integer"
        if sorts != (required,):
            raise ValueError(f"{op} requires {required}")
        sort = "boolean" if op == "not" else "integer"
    else:
        raise ValueError(f"Unsupported statement operation {op}")
    if all(a.op == "literal" for a in args):
        values = [a.args[0] for a in args]
        functions = {**ARITHMETIC, **COMPARISONS, "and": operator.and_, "or": operator.or_,
                     "neg": operator.neg, "abs": abs, "indicator": int, "not": operator.not_}
        if op != "mod" or values[1] > 0:
            try:
                return literal(functions[op](*values))
            except ZeroDivisionError:
                pass  # The separate well-definedness obligation must stay visible.
    if op in ("add", "sub") and args[1] == ZERO:
        return args[0]
    if op == "add" and args[0] == ZERO:
        return args[1]
    if op == "mul" and ONE in args:
        return args[1] if args[0] == ONE else args[0]
    if op == "mul" and ZERO in args:
        return ZERO
    if op == "and" and TRUE in args:
        return args[1] if args[0] == TRUE else args[0]
    if op in ("eq", "le", "ge") and args[0] == args[1]:
        return TRUE
    return Term(op, tuple(args), sort)


def bounded_sum(body, dimensions):
    if body.sort != "integer":
        raise ValueError("A sum needs an integer summand")
    result = body
    for variable, extent in reversed(dimensions):
        result = Term("sum", (variable, extent, result))
    return result


SIGNS = {"add": "+", "sub": "−", "mul": "·", "eq": "=", "ne": "≠", "lt": "<",
         "le": "≤", "gt": ">", "ge": "≥", "and": "∧", "or": "∨", "mod": "mod"}


def render(t, parent_precedence=0):
    a = t.args
    if t.op == "literal":
        return str(a[0]).lower() if t.sort == "boolean" else str(a[0])
    if t.op == "parameter":
        return a[0]
    if t.op == "bound":
        return a[0]
    if t.op in SIGNS:
        precedence = {"or": 10, "and": 15, "add": 30, "sub": 30, "mul": 40, "mod": 40}.get(t.op, 20)
        text = f"{render(a[0], precedence)} {SIGNS[t.op]} {render(a[1], precedence+1)}"
        return f"({text})" if precedence < parent_precedence else text
    if t.op == "floordiv":
        return f"floor(({render(a[0])}) / ({render(a[1])}))"
    if t.op == "indicator":
        return f"[{render(a[0])}]"
    if t.op == "sum":
        text = f"Σ_{{0 ≤ {render(a[0])} < {render(a[1])}}} ({render(a[2])})"
        return f"({text})" if parent_precedence else text
    if t.op == "table":
        return f"({', '.join(map(str, a[0]))})[{render(a[1])}]"
    if t.op in ("neg", "not"):
        return f"{'−' if t.op == 'neg' else '¬'}({render(a[0])})"
    return f"{t.op}({', '.join(render(x) for x in a)})"


def domain_text(dimensions):
    return " × ".join(f"{{{render(v)} ∈ ℤ : 0 ≤ {render(v)} < {render(n)}}}" for v, n in dimensions) or "{()}"


def evaluate(t, parameters, coordinates=None, *, budget=None):
    """Finite interpretation; exhaustion/undefinedness is an error, never false."""
    budget = [100_000] if budget is None else budget
    coordinates = {} if coordinates is None else coordinates
    budget[0] -= 1
    if budget[0] < 0:
        raise ValueError("Finite statement inspection exceeds its budget")
    op, a = t.op, t.args
    if op == "literal":
        return a[0]
    if op == "parameter":
        value = parameters[a[0]]
        if type(value) is not int:
            raise ValueError("An integer parameter is required")
        return value
    if op == "bound":
        return coordinates[a[0]]
    if op == "sum":
        n = evaluate(a[1], parameters, coordinates, budget=budget)
        if n < 0 or n > budget[0]:
            raise ValueError("Invalid or over-budget summation domain")
        return sum(evaluate(a[2], parameters, {**coordinates, a[0].args[0]: i}, budget=budget)
                   for i in range(n))
    if op == "table":
        index = evaluate(a[1], parameters, coordinates, budget=budget)
        if not 0 <= index < len(a[0]):
            raise ValueError("Table address outside its domain")
        return a[0][index]
    values = [evaluate(v, parameters, coordinates, budget=budget) for v in a]
    if op == "mod" and values[1] <= 0:
        raise ValueError("Modulo uses a positive integer modulus")
    functions = {**ARITHMETIC, **COMPARISONS, "and": operator.and_, "or": operator.or_,
                 "neg": operator.neg, "abs": abs, "indicator": int, "not": operator.not_}
    return functions[op](*values)
