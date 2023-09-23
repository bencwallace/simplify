import ast

import pytest

from simplify.simplifier import Simplifier


@pytest.mark.parametrize(
    "source, result, state, global_ids",
    [
        ("x = 1", "", {"x": 1}, []),
        ("x = 1; x", "1", {"x": 1}, []),
        ("x = y = 1; x + y", "2", {"x": 1, "y": 1}, []),
        ("global x; x = 1; x", "1", {"x": 1}, ["x"]),
    ],
)
def test_assign(source, result, state, global_ids):
    source_tree = ast.parse(source)
    simplifier = Simplifier()
    result_tree = simplifier.visit(source_tree)
    assert result == ast.unparse(result_tree)
    assert simplifier.env.flatten() == state
    assert simplifier.env.global_ids == global_ids


def test_aug_assign():
    source = "x = 42; x *= (1 + 1)"
    result = ""
    source_tree = ast.parse(source)
    simplifier = Simplifier()
    result_tree = simplifier.visit(source_tree)
    assert result == ast.unparse(result_tree)
    assert simplifier.env.flatten() == {"x": 84}


def test_aug_assign_hard():
    source = "x = 42; x *= y"
    result = "x *= y"
    source_tree = ast.parse(source)
    simplifier = Simplifier()
    result_tree = simplifier.visit(source_tree)
    assert result == ast.unparse(result_tree)
    assert simplifier.env.flatten() == {}


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
