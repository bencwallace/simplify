import ast
import importlib
import inspect
from typing import List

from simplify.exceptions import InvalidBindingError, InvalidPythonPathError


class BindingsParser(ast.NodeTransformer):
    def visit_Assign(self, node):
        bindings = {}
        if isinstance(node.value, ast.Constant):
            val = self.visit(node.value)
        else:
            raise NotImplementedError("Only binding of constants to identifiers is supported.")
        for t in node.targets:
            bindings[t.id] = val
        return bindings

    def visit_Constant(self, node):
        return node.value

    def visit_Module(self, node):
        bindings = {}
        for n in node.body:
            bindings.update(self.visit(n))
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


def obj_to_tree(obj: object) -> ast.Module:
    source = inspect.getsource(obj)
    return ast.parse(source)


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


