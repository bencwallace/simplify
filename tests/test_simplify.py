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
    ],
)
def test_assign(source, result):
    assert result == transform_source(source)
