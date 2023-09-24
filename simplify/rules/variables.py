import ast
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simplify.simplifier import Simplifier
else:
    Simplifier = "Simplifier"


def visit_name(node: ast.Name, simplifier: Simplifier):
    match node:
        case ast.Name(id, ast.Load()) if id in simplifier.env:
            # TODO: Inline non-constant names
            return simplifier.env[id]
        case ast.Name(_):
            return node
