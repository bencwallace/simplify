import ast
from textwrap import dedent


from simplify.simplifier import Simplifier
from simplify.scope import Scope


def test_scope():
    source = dedent(
        """
        x = 13
        def f(z):
            y = 2
            return
        """
    )
    source_tree = ast.parse(source)
    simplifier = Simplifier()
    simplifier.visit(source_tree)

    result_scope = Scope()
    result_scope["x"] = ast.Constant(13)
    result_scope["f"] = ast.FunctionDef(
        name="f",
        args=ast.arguments([], [ast.arg("z")], None, [], [], None, []),
        body=[
            ast.Return(),
        ],
        decorator_list=[],
    )
    assert result_scope == simplifier.scope
