import ast

import pytest

from simplify.main import transform_source
from simplify.simplifier import Simplifier


@pytest.mark.parametrize(
    "source, result",
    [
        ("x = 1; x", "1"),
        ("x = y = 1; x + y", "2"),
        ("global x; x = 1; x", "1"),  # TODO: better test
    ],
)
def test_assign(source, result):
    assert transform_source(source) == result


def test_assign_attr():
    source = "x.y = 3.14; x.y"
    result = "3.14"
    assert transform_source(source) == result


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
