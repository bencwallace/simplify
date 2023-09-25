import ast
from typing import TYPE_CHECKING

from simplify.utils import unpack

if TYPE_CHECKING:
    from simplify.simplifier import Simplifier
else:
    Simplifier = "Simplifier"


def visit_function_def(node: ast.FunctionDef, simp: Simplifier):
    # TODO: Add decorators, etc.
    # TODO: Check if return value can be extracted
    with simp.new_scope():
        result = super(type(simp), simp).generic_visit(node)  # must be visited in the function's local scope
    simp.scope[node.name] = result  # must be assigned in the scope enclosing the function
    return result


def visit_global(node: ast.Global, simp: Simplifier):
    (names,) = unpack(node)
    simp.scope.add_global(*names)


def visit_return(node: ast.Return, simp: Simplifier):
    (value,) = unpack(node)
    return ast.Return(simp.visit(value))
