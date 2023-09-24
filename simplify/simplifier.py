import ast
from contextlib import contextmanager
from typing import Any, Iterable, Optional, Union

from simplify.environment import Environment
from simplify.rules import control_flow, expressions, function_and_class_defs, statements, variables


class Simplifier(ast.NodeTransformer):
    def __init__(self, bindings: Optional[dict] = None):
        self.global_env = Environment()
        self.env = self.global_env
        if bindings is None:
            bindings = {}
        for name, val in bindings.items():
            self.env[name] = val

    def visit(self, node: Union[ast.AST, Iterable]) -> Any:
        if isinstance(node, Iterable):
            return list(map(self.visit, node))
        if node is None:
            return None
        return super().visit(node)

    @contextmanager
    def new_environment(self, name):
        self.env = self.env.add_env(name)
        yield
        self.env = self.env.enclosing
        self.env.del_env(name)

    # CONTROL FLOW #

    def visit_If(self, node: ast.If) -> Union[ast.If, Iterable]:
        return control_flow.visit_if(node, self)

    def visit_For(self, node: ast.For) -> Union[ast.For, list]:
        return control_flow.visit_for(node, self)

    # EXPRESSIONS #

    def visit_BoolOp(self, node: ast.BoolOp) -> Union[ast.BoolOp, ast.Constant]:
        return expressions.visit_bool_op(node, self)

    def visit_BinOp(self, node: ast.BinOp) -> Union[ast.BinOp, ast.Constant]:
        return expressions.visit_bin_op(node, self)

    def visit_IfExp(self, node: ast.IfExp) -> Union[ast.IfExp, Iterable]:
        return expressions.visit_if_exp(node, self)

    def visit_Compare(self, node: ast.Compare) -> Union[ast.Compare, ast.Constant]:
        return expressions.visit_compare(node, self)

    def visit_Call(self, node: ast.Call) -> ast.Call:
        return expressions.visit_call(node, self)

    # FUNCTION AND CLASS DEFINITIONS"

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        return function_and_class_defs.visit_function_def(node, self)

    def visit_Global(self, node: ast.Global) -> None:
        return function_and_class_defs.visit_global(node, self)

    def visit_Return(self, node: ast.Return) -> ast.Return:
        return function_and_class_defs.visit_return(node, self)

    # STATEMENTS #

    def visit_Delete(self, node: ast.Delete) -> Optional[ast.Delete]:
        return statements.visit_delete(node, self)

    def visit_Assign(self, node: ast.Assign) -> Optional[ast.Assign]:
        return statements.visit_assign(node, self)

    def visit_AugAssign(self, node: ast.AugAssign):
        return statements.visit_aug_assign(node, self)

    # VARIABLES #

    def visit_Name(self, node: ast.Name) -> Union[ast.Name, ast.Constant]:
        return variables.visit_name(node, self)
