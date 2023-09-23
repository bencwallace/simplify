import ast
from copy import deepcopy
from typing import TYPE_CHECKING

from simplify.utils import unpack


if TYPE_CHECKING:
    from simplify.simplifier import Simplifier
else:
    Simplifier = "Simplifier"


def visit_if(node: ast.If, simplifier: Simplifier):
    test, body, orelse = unpack(node)
    test = simplifier.visit(test)
    match test:
        case ast.Constant(value) if value:
            return simplifier.visit(body)
        case ast.Constant(value) if not value:
            return simplifier.visit(orelse)
        case _:
            return ast.If(test, simplifier.visit(body), simplifier.visit(orelse))


def visit_for(node: ast.For, simplifier: Simplifier):
    match node:
        case ast.For(ast.Name(id), ast.List(elts), body):
            result = []
            for e in elts:
                match e:
                    case ast.Constant(value):
                        simplifier.env[id] = value
                        result.extend(simplifier.visit(deepcopy(body)))
                    case _:
                        if id in simplifier.env:
                            del simplifier.env[id]
                        return node  # TODO
            return result
        case _:
            # TODO
            return node
