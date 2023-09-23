import ast
from typing import TYPE_CHECKING

from simplify.data import BIN_OPS
from simplify.utils import unpack


if TYPE_CHECKING:
    from simplify.simplifier import Simplifier
else:
    Simplifier = "Simplifier"


def visit_aug_assign(node: ast.AugAssign, simplifier: Simplifier):
    target, op, value = unpack(node)
    id, _ = unpack(target)
    value = super(type(simplifier), simplifier).visit(value)
    match value:
        case ast.Constant(value):
            simplifier.env[id] = BIN_OPS[type(op)](simplifier.env[id], value)
            return None
        case _:
            del simplifier.env[id]
            return ast.AugAssign(ast.Name(id), op, value)


# TODO: Substitute RHS expressions (not just constants) into places where LHS appears
# TODO: handle unpacking expressions
def visit_assign(node: ast.Assign, simplifier: Simplifier):
    match node:
        # TODO: visit value before checking if constant
        case ast.Assign(targets, ast.Constant(value)):
            for t in simplifier.visit(targets):
                match t:
                    # TODO: case t a tuple
                    case ast.Name(id, _):
                        simplifier.env[id] = value
            return None
        case ast.Assign(targets, value):
            # value non-constant so targets become unknown
            for t in targets:
                match t:
                    case ast.Name(id):
                        del simplifier.env[id]
                    # TODO: recursively handle tuples
            return ast.Assign(
                simplifier.visit(targets), simplifier.visit(value)
            )  # TODO: this is wrong -- targets is a list


def visit_delete(node: ast.Delete, simplifier: Simplifier):
    new_targets = []
    (targets,) = unpack(node)
    for t in simplifier.visit(targets):
        # TODO: case t not a Name
        if t.id in simplifier.env:
            del simplifier.env[t.id]
        else:
            new_targets.append(t)
    if new_targets:
        return ast.Delete(new_targets)
    return None
