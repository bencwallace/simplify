import ast

import pytest

from simplify.scope import Scope
from simplify.simplifier import Simplifier


@pytest.mark.parametrize(
    "source, result, state, global_ids",
    [
        ("x = 1", "", {"x": ast.Constant(1)}, []),
        ("x = 1; x", "1", {"x": ast.Constant(1)}, []),
        ("x = y = 1; x + y", "2", {"x": ast.Constant(1), "y": ast.Constant(1)}, []),
        ("global x; x = 1; x", "1", {"x": ast.Constant(1)}, ["x"]),
    ],
)
def test_assign(source, result, state, global_ids):
    source_tree = ast.parse(source)
    simplifier = Simplifier()
    result_tree = simplifier.visit(source_tree)
    assert result == ast.unparse(result_tree)
    result_scope = Scope()
    for k, v in state.items():
        result_scope[k] = v
    for k in global_ids:
        result_scope.global_ids.append(k)
    assert simplifier.scope == result_scope
    assert simplifier.scope.global_ids == global_ids


def test_aug_assign():
    source = "x = 42; x *= (1 + 1)"
    result = ""
    source_tree = ast.parse(source)
    simplifier = Simplifier()
    result_tree = simplifier.visit(source_tree)
    assert result == ast.unparse(result_tree)
    result_scope = Scope()
    result_scope["x"] = ast.Constant(84)
    assert simplifier.scope == result_scope


def test_aug_assign_hard():
    source = "x = 42; x *= y"
    result = "x *= y"
    source_tree = ast.parse(source)
    simplifier = Simplifier()
    result_tree = simplifier.visit(source_tree)
    assert result == ast.unparse(result_tree)
    result_scope = Scope()
    result_scope["x"] = ast.AugAssign(ast.Name("x", ast.Store()), ast.Mult(), ast.Name("y", ast.Load()))
    assert simplifier.scope == result_scope


@pytest.mark.parametrize(
    "source, result, state",
    [
        ("del x", "del x", {}),
        ("x = 'a'; del x", "", {}),
    ],
)
def test_delete(source, result, state):
    source_tree = ast.parse(source)
    simplifier = Simplifier()
    result_tree = simplifier.visit(source_tree)
    assert result == ast.unparse(result_tree)
    assert simplifier.scope.flatten() == state
