import ast
import importlib
import inspect
from typing import List

from simplify.exceptions import InvalidBindingError, InvalidExpressionError, InvalidPythonPathError


class BindingsParser(ast.NodeTransformer):
    @staticmethod
    def eval_expr(node: ast.Expression):
        try:
            code = compile(node, "", mode="eval")
            return eval(code)
        except (SyntaxError, NameError) as e:
            raise InvalidExpressionError(node) from e

    def generic_visit(self, node):
        raise InvalidBindingError(node)

    def visit_Module(self, node):
        bindings = {}
        for stmt in node.body:
            bindings.update(self.visit(stmt))
        return bindings

    def visit_Assign(self, node):
        bindings = {}
        val = self.eval_expr(ast.Expression(node.value))
        for t in node.targets:
            bindings[t.id] = val
        return bindings


def load_obj_from_path(python_path: str) -> object:
    split_path = python_path.split(":")
    if not 1 <= len(split_path) <= 2:
        raise InvalidPythonPathError(python_path, "Path must have form module_path:callable_obj.")
    module_path = split_path[0]

    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError as e:
        raise InvalidPythonPathError(python_path, f"Module {module_path} not found.") from e

    if len(split_path) < 2:
        return module

    obj_name = split_path[1]
    try:
        obj = getattr(module, obj_name)
    except AttributeError as e:
        raise InvalidPythonPathError(python_path, f"Object {obj_name} not found in module {module_path}.") from e

    return obj


def get_arg_names(obj: object) -> List[str]:
    try:
        sig = inspect.signature(obj)
    except:
        raise ValueError(f"Object {obj.__name__} must be callable")
    return list(sig.parameters.keys())


def parse_bindings(binding_exprs: List[str]) -> dict:
    # TODO: scope bindings properly
    bindings = {}
    for b in binding_exprs:
        try:
            tree = ast.parse(b)
        except SyntaxError as e:
            raise InvalidBindingError(b) from e

        parser = BindingsParser()
        bindings.update(parser.visit(tree))
    return bindings
