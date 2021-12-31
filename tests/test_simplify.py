import pytest

from simplify.main import transform_source


@pytest.mark.parametrize(
    "source",
    [
        "",
        "None",
        "1",
        "hello",
        "{}",
        "[]",
    ],
)
def test_literal(source):
    assert source == transform_source(source)


@pytest.mark.parametrize(
    "expr, answer",
    [
        ("1 + 1", "2"),
        ("2 * 2", "4"),
        ("8 % 4", "0"),
    ],
)
def test_arithmetic(expr, answer):
    assert answer == transform_source(expr)


@pytest.mark.parametrize(
    "source, result",
    [
        ("x = 1", ""),
        ("x = 1; x", "1"),
    ],
)
def test_assign(source, result):
    assert result == transform_source(source)


@pytest.mark.parametrize(
    "source, result",
    [
        ("del x", "del x"),
        ("x = 'a'; del x", ""),
    ],
)
def test_del(source, result):
    assert result == transform_source(source)


@pytest.mark.parametrize(
    "source, result",
    [
        ("False and True", "False"),
        ("False or True", "True"),
        ("False and x", "False"),
        ("True and x", "x"),
        ("False or x", "x"),
        ("x or True", "True"),
    ],
)
def test_bool(source, result):
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
    assert result == transform_source(source)
