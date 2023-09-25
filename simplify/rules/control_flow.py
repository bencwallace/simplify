import ast
from copy import deepcopy
from typing import TYPE_CHECKING

from simplify.utils import unpack


if TYPE_CHECKING:
    from simplify.simplifier import Simplifier
else:
    Simplifier = "Simplifier"


def visit_if(node: ast.If, simp: Simplifier):
    test, body, orelse = unpack(node)
    test = simp.visit(test)
    match test:
        case ast.Constant(value) if value:
            return simp.visit(body)
        case ast.Constant(value) if not value:
            return simp.visit(orelse)
        case _:
            return ast.If(test, simp.visit(body), simp.visit(orelse))


def visit_for(node: ast.For, simp: Simplifier):
    match node:
        case ast.For(ast.Name(id), ast.List(elts), body):
            result = []
            for e in elts:
                match e:
                    case ast.Constant(value):
                        simp.scope[id] = ast.Constant(value)
                        result.extend(simp.visit(deepcopy(body)))
                    case _:
                        if id in simp.scope:
                            del simp.scope[id]
                        return node  # TODO
            return result
        case _:
            # TODO
            return node
