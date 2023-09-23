import ast
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simplify.simplifier import Simplifier
else:
    Simplifier = "Simplifier"


def visit_function_def(node: ast.FunctionDef, simplifier: Simplifier):
    # TODO: Add decorators, etc.
    # TODO: Check if return value can be extracted
    match node:
        case ast.FunctionDef(name):
            with simplifier.new_environment(name):
                result = super(type(simplifier), simplifier).generic_visit(
                    node
                )  # must be visited in the function's local scope
            simplifier.env[name] = result  # must be assigned in the scope enclosing the function
            return result


def visit_global(node: ast.Global, simplifier: Simplifier):
    match node:
        case ast.Global(names):
            simplifier.env.add_global(*names)


def visit_return(node: ast.Return, simplifier: Simplifier):
    match node:
        case ast.Return(value):
            return ast.Return(simplifier.visit(value))
