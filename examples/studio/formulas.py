"""Small arithmetic notation, lowered to the same bounded expression protocol.

No Python evaluation, calls, attributes or subscripts. Parsing does not resolve
fields, parameters or values; those remain explicit in the captured definition.
"""
import ast


def formula(text, parameters=(), fields=()):
    if not isinstance(text, str) or not text.strip() or len(text) > 256:
        raise ValueError("Write a formula of 1–256 characters, such as i + 2*j")
    try:
        root = ast.parse(text.strip(), mode="eval")
    except (SyntaxError, ValueError) as error:
        raise ValueError("Use indices, integer constants, + − * // %, and parentheses") from error
    if sum(1 for _ in ast.walk(root)) > 80:
        raise ValueError("Formula is too large")
    signs = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.FloorDiv: "//", ast.Mod: "%"}

    def lower(node, depth=0):
        if depth > 16:
            raise ValueError("Formula is nested too deeply")
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return {"integer": str(node.value)}
        if isinstance(node, ast.Name):
            if node.id in parameters and node.id in fields:
                raise ValueError(f"{node.id} names both an index/field and a parameter; use distinct names or the detailed formula editor")
            return {"parameter" if node.id in parameters else "field": node.id}
        if isinstance(node, ast.BinOp) and type(node.op) in signs:
            return {"op": signs[type(node.op)], "args": [lower(node.left, depth+1), lower(node.right, depth+1)]}
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = lower(node.operand, depth+1)
            return value if isinstance(node.op, ast.UAdd) else {"op": "-", "args": [{"integer": "0"}, value]}
        raise ValueError("Use indices, integer constants, + − * // %, and parentheses; no calls or Python code")

    return lower(root.body)
