import ast
from textwrap import dedent

import pytest

from simplify.main import transform_source
from simplify.simplifier import Simplifier


def test_function_def():
    source = dedent(
        """
        def f():
            return 1 + 1
        """
    )
    result = dedent(
        """
        def f():
            return 2
        """
    ).strip("\n")
    names = ["f"]
    source_tree = ast.parse(source)
    simplifier = Simplifier()
    result_tree = simplifier.visit(source_tree)
    assert result == ast.unparse(result_tree)
    assert list(simplifier.scope.flatten().keys()) == names


def test_lambda():
    source = dedent(
        """
        f = lambda x: x ** 2
        y = f(z)
        print(y)
        """
    )
    result = dedent(
        """
        print((lambda x: x ** 2)(z))
        """
    ).strip("\n")
    assert result == transform_source(source)


@pytest.mark.parametrize(
    "source, result, names",
    [
        ("def f(): return 1", "def f():\n    return 1", ["f"]),
        ("def f(): return", "def f():\n    return", ["f"]),
        ("def f(): return 1 + 1", "def f():\n    return 2", ["f"]),
    ],
)
def test_return(source, result, names):
    source_tree = ast.parse(source)
    simplifier = Simplifier()
    result_tree = simplifier.visit(source_tree)
    assert result == ast.unparse(result_tree)
    assert list(simplifier.scope.flatten().keys()) == names
