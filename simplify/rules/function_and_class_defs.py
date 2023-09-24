import ast
from typing import TYPE_CHECKING

from simplify.utils import unpack

if TYPE_CHECKING:
    from simplify.simplifier import Simplifier
else:
    Simplifier = "Simplifier"


def visit_function_def(node: ast.FunctionDef, simplifier: Simplifier):
    # TODO: Add decorators, etc.
    # TODO: Check if return value can be extracted
    name, *_ = unpack(node)
    with simplifier.new_scope(name):
        result = super(type(simplifier), simplifier).generic_visit(
            node
        )  # must be visited in the function's local scope
    simplifier.scope[name] = result  # must be assigned in the scope enclosing the function
    return result


def visit_global(node: ast.Global, simplifier: Simplifier):
    (names,) = unpack(node)
    simplifier.scope.add_global(*names)


def visit_return(node: ast.Return, simplifier: Simplifier):
    (value,) = unpack(node)
    return ast.Return(simplifier.visit(value))
