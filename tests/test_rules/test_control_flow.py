from textwrap import dedent

import pytest

from simplify.main import transform_source


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
        xs = [1, 2, 3]
        for x in xs:
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
    assert transform_source(source) == result
