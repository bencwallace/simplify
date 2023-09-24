import ast
import importlib
import inspect
from typing import Callable, List, Tuple, TypeVar

from simplify.exceptions import InvalidBindingError, InvalidExpressionError, InvalidPythonPathError


T = TypeVar("T")


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
    sig = inspect.signature(obj)
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


def split_list_on_predicate(x: List[T], p: Callable[[T], bool]) -> Tuple[List[T], List[T]]:
    p_true_in_x = []
    p_false_in_x = []
    for v in x:
        if p(v):
            p_true_in_x.append(v)
        else:
            p_false_in_x.append(v)
    return p_true_in_x, p_false_in_x


def unpack(node: ast.AST) -> Tuple[ast.AST, ...]:
    return tuple(getattr(node, attr) for attr in node.__match_args__)


def eq_nodes(x, y) -> bool:
    if type(x) is not type(y):
        return False
    if isinstance(x, list):
        if not len(x) == len(y):
            return False
        return all(eq_nodes(a, b) for a, b in zip(x, y))
    if isinstance(x, ast.AST):
        for attr in x.__match_args__:
            if not eq_nodes(getattr(x, attr), getattr(y, attr)):
                return False
        return True
    return x == y
