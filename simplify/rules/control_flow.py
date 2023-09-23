import ast
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from simplify.simplifier import Simplifier
else:
    Simplifier = "Simplifier"


def visit_if(node: ast.If, simplifier: Simplifier):
    match node:
        case ast.If(test, body, orelse):
            test = simplifier.visit(test)
            match test:
                case ast.Constant(value) if value:
                    return simplifier.visit(body)
                case ast.Constant(value) if not value:
                    return simplifier.visit(orelse)
                case _:
                    return ast.If(test, simplifier.visit(body), simplifier.visit(orelse))
