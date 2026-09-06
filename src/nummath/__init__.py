import ast
import math
import operator
import sys


class SafeMathEvaluator:
    # Whitelist allowed mathematical operators
    _OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def __init__(self):
        # Safe math constants and functions (sin, cos, pi, e, sqrt, etc.)
        self._SAFE_ENV = {
            k: v for k, v in math.__dict__.items() if not k.startswith("__")
        }

    def _eval_node(self, node, local_vars):
        # Numbers / Floats
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Unsupported constant type: {type(node.value).__name__}")

        # Binary Ops: 1 + 2, 5 * 3, 10 / 2
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left, local_vars)
            right = self._eval_node(node.right, local_vars)
            op_type = type(node.op)
            if op_type in self._OPERATORS:
                return self._OPERATORS[op_type](left, right)
            raise ValueError(f"Unsupported operator: {type(node.op).__name__}")

        # Unary Ops: -5, +3
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand, local_vars)
            op_type = type(node.op)
            if op_type in self._OPERATORS:
                return self._OPERATORS[op_type](operand)
            raise ValueError(f"Unsupported operator: {type(node.op).__name__}")

        # Variables / Constants (x, pi, e, etc.)
        elif isinstance(node, ast.Name):
            if node.id in local_vars:
                return local_vars[node.id]
            elif node.id in self._SAFE_ENV:
                return self._SAFE_ENV[node.id]
            raise NameError(f"Undefined variable or constant: '{node.id}'")

        # Function Calls: sin(x), sqrt(16)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in self._SAFE_ENV:
                func = self._SAFE_ENV[node.func.id]
                if callable(func):
                    args = [self._eval_node(arg, local_vars) for arg in node.args]
                    return func(*args)
            raise NameError(f"Unsupported function: '{getattr(node.func, 'id', 'unknown')}'")

        raise SyntaxError("Invalid expression syntax")

    def equation(self, math_expr: str, **variables) -> float:
        """
        Evaluates a mathematical string expression safely.
        
        Pass variables as keyword arguments to use them inside the expression.
        """
        clean_expr = str(math_expr).replace('ร—', '*').replace('รท', '/')
        parsed = ast.parse(clean_expr, mode='eval')
        return self._eval_node(parsed.body, variables)


# Instance setup
_evaluator = SafeMathEvaluator()


# Standard wrapper function (allows setting attributes like .equation)
def equation(math_expr: str, **variables) -> float:
    """
    Evaluates a mathematical string expression safely.
    
    Pass variables as keyword arguments to use them inside the expression.
    """
    return _evaluator.equation(math_expr, **variables)


# Attach .equation attribute so both nummath(...) and nummath.equation(...) work
equation.equation = equation

# Overwrite module exports at the VERY BOTTOM
sys.modules[__name__] = equation
