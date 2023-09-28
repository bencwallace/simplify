from textwrap import dedent

import pytest

from simplify.main import transform_source


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
    assert transform_source(source) == result


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
        """  # TODO: simplify further
    ).strip("\n")
    assert result == transform_source(source)


@pytest.mark.parametrize(
    "source, result",
    [
        ("def f(): return 1", "def f():\n    return 1"),
        ("def f(): return", "def f():\n    return"),
        ("def f(): return 1 + 1", "def f():\n    return 2"),
    ],
)
def test_return(source, result):
    assert transform_source(source) == result
