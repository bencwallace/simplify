import ast
from typing import TYPE_CHECKING

from simplify.data import BIN_OPS
from simplify.utils import unpack


if TYPE_CHECKING:
    from simplify.simplifier import Simplifier
else:
    Simplifier = "Simplifier"


def visit_aug_assign(node: ast.AugAssign, simp: Simplifier):
    target, op, value = unpack(node)
    name = None
    match target:
        case ast.Name(id) if id in simp.scope:
            name = id
        case ast.Attribute(ast.Name(id), attr) if f"{id}.{attr}" in simp.scope:
            name = f"{id}.{attr}"
    if not name:
        return node  # TODO
    simp.scope[name] = simp.visit(ast.BinOp(simp.scope[name], op, simp.visit(value)))


# TODO: Substitute RHS expressions (not just constants) into places where LHS appears
# TODO: handle unpacking expressions
def visit_assign(node: ast.Assign, simp: Simplifier):
    targets, value, _ = unpack(node)
    new_targets = []
    value = simp.visit(value)
    for t in targets:
        match t:
            case ast.Name(id):
                simp.scope[id] = value
            case ast.Attribute(ast.Name(id), attr):
                simp.scope[f"{id}.{attr}"] = value
            case _:
                new_targets.append(t)
    if new_targets:
        return ast.Assign(new_targets, value)
    return None


def visit_delete(node: ast.Delete, simp: Simplifier):
    new_targets = []
    (targets,) = unpack(node)
    for t in simp.visit(targets):
        match t:
            case ast.Name(id) if id in simp.scope:
                del simp.scope[t.id]
            case ast.Attribute(ast.Name(id), attr) if (name := f"{id}.{attr}") in simp.scope:
                del simp.scope[name]
            case _:
                new_targets.append(t)
    if new_targets:
        return ast.Delete(new_targets)
    return None
