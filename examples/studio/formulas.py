"""Small arithmetic/relation notation lowered to the existing expression protocol.

No Python evaluation, calls, attributes or subscripts. Names become explicit
field/parameter references; only Preview evaluates their values.
"""
import ast
import re


def formula(text, parameters=(), fields=(), *, relation=False):
    if not isinstance(text, str) or not text.strip() or len(text) > 256:
        raise ValueError("Write a formula of 1–256 characters, such as i + 2*j")
    # Normalize displayed mathematical symbols, never execute the submitted text.
    text = text.translate(str.maketrans({"−": "-", "×": "*", "≤": "<=", "≥": ">=", "≠": "!="}))
    if relation:
        text = re.sub(r"(?<![<>=!])=(?!=)", "==", text)
    help_text = ("Use integer arithmetic, = != < <= > >=, and/or, and parentheses"
                 if relation else "Use indices, integer constants, + - * // %, and parentheses")
    try:
        root = ast.parse(text.strip(), mode="eval")
    except (SyntaxError, ValueError) as error:
        raise ValueError(help_text) from error
    if sum(1 for _ in ast.walk(root)) > 80:
        raise ValueError("Formula is too large")
    def condition(node):
        if isinstance(node, ast.Compare):
            return
        if isinstance(node, ast.BoolOp):
            for part in node.values:
                condition(part)
            return
        raise ValueError("A rule needs a comparison, such as i = j, joined with and/or")

    if relation:
        condition(root.body)  # An empty source must not make a numeric rule valid.
    signs = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.FloorDiv: "//", ast.Mod: "%"}
    comparisons = {ast.Eq: "=", ast.NotEq: "≠", ast.Lt: "<", ast.LtE: "≤", ast.Gt: ">", ast.GtE: "≥"}

    def conjunction(parts, op="and"):
        result = parts[0]
        for part in parts[1:]:
            result = {"op": op, "args": [result, part]}
        return result

    def lower(node, depth=0):
        if depth > 16:
            raise ValueError("Formula is nested too deeply")
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return {"integer": str(node.value)}
        if isinstance(node, ast.Name):
            if node.id in parameters and node.id in fields:
                raise ValueError(f"{node.id} names both an index/field and a parameter; use distinct names or the detailed formula editor")
            if relation and node.id not in fields and node.id not in parameters:
                raise ValueError(f"Unknown name {node.id}; choose a field or declare a parameter")
            return {"parameter" if node.id in parameters else "field": node.id}
        if isinstance(node, ast.BinOp) and type(node.op) in signs:
            return {"op": signs[type(node.op)], "args": [lower(node.left, depth+1), lower(node.right, depth+1)]}
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = lower(node.operand, depth+1)
            return value if isinstance(node.op, ast.UAdd) else {"op": "-", "args": [{"integer": "0"}, value]}
        if relation and isinstance(node, ast.Compare) and all(type(op) in comparisons for op in node.ops):
            parts = [lower(v, depth+1) for v in [node.left, *node.comparators]]
            return conjunction([{"op": comparisons[type(op)], "args": [a, b]}
                                for a, op, b in zip(parts, node.ops, parts[1:])])
        if relation and isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
            return conjunction([lower(v, depth+1) for v in node.values],
                               "and" if isinstance(node.op, ast.And) else "or")
        raise ValueError(help_text + "; no calls or Python code")

    return lower(root.body)
