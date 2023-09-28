import ast
from textwrap import dedent

import pytest

from simplify.bindings import get_bindings
from simplify.utils import eq_nodes


# @pytest.mark.parametrize(
#     "call_source, is_reducible",
#     [
#         ("f(1, 2, z=3)", True),
#         ("f(1, y=2, z=3)", True),
#         ("f(x=1, y=2, z=3)", False),
#         ("f(1, 2, 3)", False),
#         ("f(1, 2)", False),
#         ("f(1, z=3)", False),
#     ],
# )
# def test_call_is_reducible(call_source, is_reducible):
#     # TODO
#     def_source = dedent(
#         """
#         def f(x, /, y, *, z):
#             pass
#         """
#     )
#     def_node = ast.parse(def_source).body[0]
#     call_node = ast.parse(call_source).body[0].value
#     assert is_valid_call(def_node, call_node) == is_reducible


@pytest.mark.parametrize(
    "call_source, bindings",
    [
        (
            "f(1, 2)",
            {"x": ast.Constant(1), "y": ast.Constant(2), "z": ast.Tuple([], ast.Load())},
        ),
        (
            "f(1, 2, 3, 4)",
            {
                "x": ast.Constant(1),
                "y": ast.Constant(2),
                "z": ast.Tuple([ast.Constant(3), ast.Constant(4)], ast.Load()),
            },
        ),
        (
            "f(1, y=2)",
            {"x": ast.Constant(1), "y": ast.Constant(2), "z": ast.Tuple([], ast.Load())},
        ),
        ("f(x=1, y=2)", {}),
        ("f(1)", {}),
    ],
)
def test_call_get_bindings(call_source, bindings):
    # TODO
    def_source = dedent(
        """
        def f(x, /, y, *z):
            pass
        """
    )
    def_node = ast.parse(def_source).body[0].args
    call_node = ast.parse(call_source).body[0].value
    result = get_bindings(def_node, call_node)
    assert len(result) == len(bindings)
    for k, v in result.items():
        assert eq_nodes(bindings[k], v)
