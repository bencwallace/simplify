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
    x = super(type(simplifier), simplifier).visit(value)
    y = simplifier.env[id]
    if isinstance(x, ast.Constant) and isinstance(y, ast.Constant):
        simplifier.env[id] = ast.Constant(BIN_OPS[type(op)](x.value, y.value))
        return None
    simplifier.env[id] = node
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
                simplifier.env[id] = value
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
        if t.id in simplifier.env:
            del simplifier.env[t.id]
        else:
            new_targets.append(t)
    if new_targets:
        return ast.Delete(new_targets)
    return None
