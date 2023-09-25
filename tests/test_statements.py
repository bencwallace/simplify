import ast

import pytest

from simplify.main import transform_source
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
    source = "x = 42; x *= (1 + 1); x"
    result = "84"
    assert transform_source(source) == result


def test_aug_assign_hard():
    source = "x = 42; x *= y; x"
    result = "42 * y"
    assert transform_source(source) == result


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
