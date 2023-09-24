import ast

import pytest

from simplify.environment import Environment
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
    result_env = Environment()
    for k, v in state.items():
        result_env[k] = v
    for k in global_ids:
        result_env.global_ids.append(k)
    assert simplifier.env == result_env
    assert simplifier.env.global_ids == global_ids


def test_aug_assign():
    source = "x = 42; x *= (1 + 1)"
    result = ""
    source_tree = ast.parse(source)
    simplifier = Simplifier()
    result_tree = simplifier.visit(source_tree)
    assert result == ast.unparse(result_tree)
    result_env = Environment()
    result_env["x"] = ast.Constant(84)
    assert simplifier.env == result_env


def test_aug_assign_hard():
    source = "x = 42; x *= y"
    result = "x *= y"
    source_tree = ast.parse(source)
    simplifier = Simplifier()
    result_tree = simplifier.visit(source_tree)
    assert result == ast.unparse(result_tree)
    result_env = Environment()
    result_env["x"] = ast.AugAssign(ast.Name("x", ast.Store()), ast.Mult(), ast.Name("y", ast.Load()))
    assert simplifier.env == result_env


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
    assert simplifier.env.flatten() == state
