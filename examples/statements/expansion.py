"""Lower a supported integer field projection of Kaleion definitions.

This module owns translation rules, not numerical evaluation, presentation, or
proof search. Unsupported operations stop expansion. In particular an observed
group domain is never replaced by the groups present in one captured case.
"""

from dataclasses import dataclass, replace

from kaleion.ir import Expr

from .terms import (Term, ZERO, ONE, TRUE, literal, term, bounded_sum,
                    render, domain_text)


class Unsupported(ValueError):
    def __init__(self, node, reason):
        self.node, self.operation, self.reason = node.id, node.op, reason
        super().__init__(f"{node.op}: {reason}")

    def data(self):
        return {"node": self.node, "operation": self.operation, "reason": self.reason}


@dataclass
class Table:
    dimensions: tuple
    fields: dict
    native: dict
    predicate: Term | None = None


@dataclass(frozen=True)
class Condition:
    dimensions: tuple
    predicate: Term
    reason: str
    node: str

    def data(self):
        return {"domain": [[v.data(), n.data()] for v, n in self.dimensions],
                "predicate": self.predicate.data(), "reason": self.reason, "node": self.node,
                "text": ((f"∀ {domain_text(self.dimensions)}, " if self.dimensions else "")
                         + render(self.predicate))}


def ordinal(dimensions):
    value = ZERO
    for variable, extent in dimensions:
        value = term("add", term("mul", value, extent), variable)
    return value


def is_column(expression):
    """Shape of the supported expression fragment, before algebraic folding.

    The runtime validates a scalar divisor even over an empty source, whereas
    an empty divisor column has no entries to validate.
    """
    if expression.op in ("field", "aligned"):
        return True
    if expression.op in ("literal", "param", "scalar"):
        return False
    return any(is_column(a) for a in expression.args if isinstance(a, Expr))


class Expansion:
    """One translation session with explicit fixed bindings and varied integers.

    Node identity AND lexical bindings form the cache key. Conditions quantify
    over the domain where the original expression is evaluated, including
    unselected entries of a reduction's eagerly evaluated weight.
    """

    def __init__(self, parameters, vary=()):
        if any(type(v) is not int for v in parameters.values()):
            raise ValueError("Expansion currently supports integer parameters only")
        if len(set(vary)) != len(vary) or not set(vary) <= parameters.keys():
            raise ValueError("Choose distinct declared integer parameters to vary")
        self.environment = {k: Term("parameter", (k,)) if k in vary else literal(v)
                            for k, v in parameters.items()}
        self.conditions = []
        self.projections = []
        self.nodes = {}
        self.cache = {}
        self.counter = 0
        self.steps = 0
        self.depth = 0

    def fresh(self):
        variable = Term("bound", (f"t[{self.counter}]",))
        self.counter += 1
        return variable

    def require(self, predicate, dimensions, reason, node):
        if predicate.sort != "boolean":
            raise ValueError("A well-definedness condition must be a predicate")
        condition = Condition(tuple(dimensions), predicate, reason, node.id)
        if predicate != TRUE and condition not in self.conditions:
            self.conditions.append(condition)

    def expression(self, expression, table, environment, node):
        self.steps += 1
        if self.steps > 20_000:
            raise ValueError("Construction expansion exceeds its expression budget")
        if not isinstance(expression, Expr):
            raise ValueError("Expected a recorded expression")
        op, a = expression.op, expression.args
        dimensions = () if table is None else table.dimensions
        if op == "literal":
            return literal(a[0])
        if op == "param":
            return environment[a[0]]
        if op == "field":
            if table is None or a[0] not in table.fields:
                raise ValueError(f"Field {a[0]!r} has no supported integer expansion (geometry is separate)")
            return table.fields[a[0]]
        if op == "scalar":
            source = self.compile(a[0], environment)
            if source.predicate is not None:
                raise ValueError("A scalar read needs a collection")
            size = ONE
            bindings = {}
            for variable, extent in source.dimensions:
                size = term("mul", size, extent)
                bindings[variable] = ZERO
            self.require(term("eq", size, ONE), (), "Scalar source has exactly one occurrence", node)
            return source.fields["value"].replace(bindings)
        if op == "aligned":
            if table is None:
                raise ValueError("A keyed read yields a column, not a scalar constructor argument")
            source = self.compile(a[0], environment)
            if source.predicate is not None:
                raise ValueError("A keyed read needs a collection")
            def parts(expr, context):
                expressions = expr.args if expr.op == "vector" else (expr,)
                return tuple(self.expression(e, context, environment, node) for e in expressions)
            requested, keys = parts(a[1], table), parts(a[2], source)
            source_vars = tuple(v for v, _ in source.dimensions)
            if (len(keys) != len(requested) or len(keys) != len(source_vars)
                    or len(set(keys)) != len(keys) or set(keys) != set(source_vars)):
                raise ValueError("Keyed expansion needs every source coordinate once; arbitrary key inversion is not supported")
            bindings = dict(zip(keys, requested))
            for variable, extent in source.dimensions:
                value = bindings[variable]
                self.require(term("and", term("le", ZERO, value), term("lt", value, extent)),
                             dimensions, "Keyed read covers every requested key; source keys are unique coordinates", node)
            read = self.expression(a[3], source, environment, node)
            return read.replace(bindings)
        if op not in {"add", "sub", "mul", "floordiv", "mod", "neg", "abs",
                      "eq", "ne", "lt", "le", "gt", "ge", "and", "or", "not"}:
            raise ValueError(f"Expression {op!r} is outside the supported integer projection")
        args = tuple(self.expression(e, table, environment, node) for e in a)
        if op in ("floordiv", "mod"):
            self.require(term("gt" if op == "mod" else "ne", args[1], ZERO),
                         dimensions if is_column(a[1]) else (),
                         "Modulus is a positive integer" if op == "mod" else "Integer divisor is nonzero", node)
        return term(op, *args)

    def compile(self, definition, environment=None):
        node = getattr(definition, "node", definition)
        environment = self.environment if environment is None else environment
        key = (node.id, tuple(sorted(environment.items())))
        if key in self.cache:
            return self.cache[key]
        if self.depth >= 100:
            raise Unsupported(node, "Construction expansion exceeds its nesting budget")
        if len(self.nodes) > 1000:
            raise Unsupported(node, "Construction expansion exceeds its node budget")
        self.nodes[node.id] = node.definition()
        self.depth += 1
        try:
            table = self._compile(node, environment)
        except Unsupported:
            raise
        except (ValueError, KeyError, TypeError) as error:
            raise Unsupported(node, str(error)) from error
        finally:
            self.depth -= 1
        self.cache[key] = table
        return table

    def _compile(self, node, environment):
        op, a = node.op, node.attributes
        expr = lambda rule, table=None: self.expression(rule, table, environment, node)
        if op == "case":
            # Bindings are simultaneous and evaluated in the outer scope.
            bindings = {k: expr(v) for k, v in a["bindings"].items()}
            return self.compile(node.inputs[0], {**environment, **bindings})
        if op == "require":
            checks = self.compile(node.inputs[1], environment)
            if checks.predicate is None:
                raise ValueError("A construction requirement needs an incidence of checks")
            self.require(checks.predicate, checks.dimensions, f"Recorded requirement: {a['message']}", node)
            return self.compile(node.inputs[0], environment)
        if op in ("grid", "tuples", "sequence"):
            shape = (a["length"],) if op == "sequence" else a["shape"]
            axes = ("s",) if op == "sequence" else a["axes"]
            dimensions = tuple((self.fresh(), expr(n)) for n in shape)
            for _, extent in dimensions:
                self.require(term("ge", extent, ZERO), (), "Constructor extent is a nonnegative integer", node)
            fields = {name: v for name, (v, _) in zip(axes, dimensions)}
            fields["index"] = ordinal(dimensions)
            table = Table(dimensions, fields, dict(zip(axes, (v for v, _ in dimensions))))
            if op == "sequence":
                fields["value"] = term("add", expr(a["start"]), term("mul", fields["s"], expr(a["step"])))
            elif op == "grid":
                fields["value"] = expr(a["values"], table)
            fields["key"] = fields["index"]
            return table
        if op == "literal":
            values = a["values"]
            variable = self.fresh()
            def column(values):
                if any(type(v) is not int for v in values):
                    raise ValueError("Literal tables need integer fields")
                if tuple(values) == tuple(range(len(values))):
                    return variable
                return Term("table", (tuple(values), variable))
            fields = {"s": variable, "index": variable,
                      "key": variable if a["keys"] is None else column(a["keys"]),
                      "value": column(values)}
            fields.update({k: column(v) for k, v in a["fields"].items()})
            return Table(((variable, literal(len(values))),), fields, {"s": variable})
        if op not in ("place", "move", "positions", "values", "annotate", "incidence", "reduce"):
            raise ValueError("No sound expansion rule yet; the captured comparison remains available")
        source = self.compile(node.inputs[0], environment)
        if op in ("place", "move", "positions"):
            projection = {"node": node.id, "operation": op,
                          "meaning": "Only integer fields and occurrence domain are projected; geometry is not a claim"}
            if projection not in self.projections:
                self.projections.append(projection)
            return source
        if op == "values":
            return replace(source, fields={**source.fields, "value": expr(a["rule"], source)})
        if op == "annotate":
            # The evaluator reads the original source for every field.
            return replace(source, fields={**source.fields, **{k: expr(v, source) for k, v in a["fields"].items()}})
        if op == "incidence":
            predicate = expr(a["rule"], source)
            if predicate.sort != "boolean":
                raise ValueError("An incidence requires a predicate")
            return replace(source, predicate=predicate)
        if source.predicate is None:
            raise ValueError("A reduction requires an incidence")
        groups = a["groups"]
        retained = []
        for name, rule in groups:
            if (rule.op != "field" or rule.args[0] not in source.native
                    or expr(rule, source) != source.native[rule.args[0]]):
                raise ValueError("Observed grouping requires an explicit domain rule; only unchanged native axes expand yet")
            retained.append((name, expr(rule, source)))
        if len(set(v for _, v in retained)) != len(retained):
            raise ValueError("Repeated grouping coordinates are not a rectangular key domain")
        extents = dict(source.dimensions)
        dimensions = tuple((v, extents[v]) for _, v in retained)
        eliminated = tuple((v, n) for v, n in source.dimensions if v not in dict(dimensions))
        reducer = a["reducer"]
        weight = expr(a["value"], source) if reducer == "sum" else ONE
        value = bounded_sum(term("mul", term("indicator", source.predicate), weight), eliminated)
        if reducer == "any":
            value = term("indicator", term("ne", value, ZERO))
        elif reducer not in ("sum", "count"):
            raise ValueError(f"Unknown reduction {reducer}")
        if not groups:
            dimensions = ((self.fresh(), ONE),)  # A total retains a zero-valued singleton even when empty.
        index = ordinal(dimensions)
        fields = {name: v for name, v in retained}
        fields.update(value=value, index=index, key=retained[0][1] if len(retained) == 1 else index)
        # Core reductions retain key fields, but have no native shape/axes.
        return Table(dimensions, fields, {})

    def keyed(self, definition, keys, value=None):
        """Normalize a bijective coordinate key to a common comparison order."""
        node = getattr(definition, "node", definition)
        table = self.compile(node)
        if table.predicate is not None:
            raise Unsupported(node, "Compare integer collections, not incidence membership")
        try:
            terms = tuple(table.fields[k] for k in keys)
            variables = tuple(v for v, _ in table.dimensions)
            if len(terms) != len(variables) or len(set(terms)) != len(terms) or set(terms) != set(variables):
                raise ValueError("Comparison keys must name each rectangular coordinate once; flattened multidimensional keys need a separate rule")
            common = tuple(Term("bound", (f"k[{i}]",)) for i in range(len(keys)))
            bindings = dict(zip(terms, common))
            sizes = dict(table.dimensions)
            domain = tuple((k, sizes[v]) for v, k in zip(terms, common))
            result = None if value is None else table.fields[value].replace(bindings)
            if result is not None and result.sort != "integer":
                raise ValueError("The compared field must be integer-valued")
            return domain, result
        except (ValueError, KeyError) as error:
            raise Unsupported(node, str(error)) from error
