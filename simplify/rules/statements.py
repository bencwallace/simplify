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
    match target:
        case ast.Name(id) if id in simplifier.scope:
            x = simplifier.scope[id]
            y = super(type(simplifier), simplifier).visit(value)
            x = ast.BinOp(x, op, y)
            x = super(type(simplifier), simplifier).visit(x)
            simplifier.scope[id] = x
            return None
        case _:
            # TODO
            return node


# TODO: Substitute RHS expressions (not just constants) into places where LHS appears
# TODO: handle unpacking expressions
def visit_assign(node: ast.Assign, simplifier: Simplifier):
    targets, value, _ = unpack(node)
    new_targets = []
    value = simplifier.visit(value)
    for t in targets:
        match t:
            case ast.Name(id):
                simplifier.scope[id] = value
            case _:
                new_targets.append(t)
    if new_targets:
        return ast.Assign(new_targets, value)
    return None


def visit_delete(node: ast.Delete, simplifier: Simplifier):
    new_targets = []
    (targets,) = unpack(node)
    for t in simplifier.visit(targets):
        # TODO: case t not a Name
        if t.id in simplifier.scope:
            del simplifier.scope[t.id]
        else:
            new_targets.append(t)
    if new_targets:
        return ast.Delete(new_targets)
    return None
