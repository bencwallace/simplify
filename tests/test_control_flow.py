import ast
from textwrap import dedent

import pytest

from simplify.scope import Scope
from simplify.main import transform_source
from simplify.simplifier import Simplifier


def test_if():
    source = dedent(
        """
    if 1 + 1 == 2:
        yes
    if False:
        no
    """
    )
    result = "yes"
    assert result == transform_source(source)


@pytest.mark.parametrize("template", ["return x", "print(x)"])
def test_for(template):
    source = dedent(
        f"""
        for x in [1, 2, 3]:
            {template}
        """
    )
    result = dedent(
        f"""
        {template.replace("x", "1")}
        {template.replace("x", "2")}
        {template.replace("x", "3")}
        """
    ).strip("\n")
    source_tree = ast.parse(source)
    simplifier = Simplifier()
    result_tree = simplifier.visit(source_tree)
    assert result == ast.unparse(result_tree)
    result_scope = Scope()
    result_scope["x"] = ast.Constant(3)
    assert simplifier.scope == result_scope
