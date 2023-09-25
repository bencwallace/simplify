import ast
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simplify.simplifier import Simplifier
else:
    Simplifier = "Simplifier"


def visit_name(node: ast.Name, simp: Simplifier):
    match node:
        case ast.Name(id, ast.Load()) if id in simp.scope:
            return simp.scope[id]
        case ast.Name(_):
            return node
