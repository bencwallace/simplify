import ast
import functools
import inspect
from contextlib import contextmanager
from typing import Any, Iterable, Optional, Union

from simplify.data import BIN_OPS, CMP_OPS
from simplify.environment import Environment
from simplify.utils import split_list_on_predicate


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
        old_env = self.env
        new_env = Environment(old_env.global_env, old_env)
        old_env[name] = new_env
        self.env = new_env
        yield
        self.env = old_env

    # STATEMENT VISITORS #

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        # TODO: Add decorators, etc.
        # TODO: Check if return value can be extracted
        match node:
            case ast.FunctionDef(name):
                with self.new_environment(name):
                    result = super().generic_visit(node)  # must be visited in the function's local scope
                self.env[name] = result  # must be assigned in the scope enclosing the function
                return result
            case _:
                raise self._visit_wrong_type_error(node)

    def visit_Return(self, node: ast.Return) -> ast.Return:
        match node:
            case ast.Return(value):
                return ast.Return(self.visit(value))
            case _:
                raise self._visit_wrong_type_error(node)

    def visit_Delete(self, node: ast.Delete) -> Optional[ast.Delete]:
        new_targets = []
        match node:
            case ast.Delete(targets):
                for t in self.visit(targets):
                    # TODO: case t not a Name
                    if t.id in self.env:
                        del self.env[t.id]
                    else:
                        new_targets.append(t)
            case _:
                raise self._visit_wrong_type_error(node)
        if new_targets:
            return ast.Delete(new_targets)
        return None

    # TODO: Handle type comment
    # TODO: Substitute RHS expressions (not just constants) into places where LHS appears
    def visit_Assign(self, node: ast.Assign) -> Optional[ast.Assign]:
        match node:
            case ast.Assign(targets, ast.Constant(value)):
                for t in self.visit(targets):
                    # TODO: Case t not a name
                    self.env[t.id] = value
                return None
            case ast.Assign(targets, value):
                return ast.Assign(self.visit(targets), self.visit(value))
            case _:
                raise self._visit_wrong_type_error(node)

    def visit_If(self, node: ast.If) -> Union[ast.If, Iterable]:
        # node = super().generic_visit(node)
        match node:
            case ast.If(test, body, orelse):
                test = self.visit(test)
                match test:
                    case ast.Constant(value) if value:
                        return self.visit(body)
                    case ast.Constant(value) if not value:
                        return self.visit(orelse)
                    case _:
                        return ast.If(test, self.visit(body), self.visit(orelse))
            case _:
                raise self._visit_wrong_type_error(node)

    def visit_Global(self, node: ast.Global) -> None:
        match node:
            case ast.Global(names):
                self.env.add_global(*names)
            case _:
                raise self._visit_wrong_type_error(node)

    def visit_AugAssign(self, node: ast.AugAssign):
        # TODO
        return super().visit_AugAssign(node)

    # EXPRESSION VISITORS #

    def visit_BoolOp(self, node: ast.BoolOp) -> Union[ast.BoolOp, ast.Constant]:
        node = super().generic_visit(node)
        match node:
            case ast.BoolOp(_, []):
                return node
            case ast.BoolOp(ast.And(), values):
                const_values, non_const_values = split_list_on_predicate(values, self._is_const_node)

                reduced_const_value = functools.reduce(lambda x, y: x and y, map(lambda v: v.value, const_values), True)
                if not non_const_values:
                    # Expression has been fully evaluated
                    return ast.Constant(reduced_const_value)
                elif reduced_const_value:
                    # Remove redundant `True` from `and`
                    return ast.BoolOp(node.op, non_const_values)
                else:
                    # Short-circuit evaluation
                    return ast.Constant(False)
            case ast.BoolOp(ast.Or(), values):
                const_values, non_const_values = split_list_on_predicate(values, self._is_const_node)

                reduced_const_value = functools.reduce(lambda x, y: x or y, map(lambda v: v.value, const_values), False)
                if not non_const_values:
                    # Expression has been fully evaluated
                    return ast.Constant(reduced_const_value)
                elif reduced_const_value:
                    # Short-circuit evaluation
                    return ast.Constant(True)
                else:
                    # Remove redundant `False` from `or`
                    return ast.BoolOp(node.op, non_const_values)
            case _:
                raise self._visit_wrong_type_error(node)

    def visit_BinOp(self, node: ast.BinOp) -> Union[ast.BinOp, ast.Constant]:
        node = super().generic_visit(node)
        match node:
            case ast.BinOp(ast.Constant(lval), op, ast.Constant(rval)):
                return ast.Constant(BIN_OPS[type(op)](lval, rval))
            case ast.BinOp(_):
                return node
            case _:
                raise self._visit_wrong_type_error(node)

    def visit_IfExp(self, node: ast.IfExp) -> Union[ast.IfExp, Iterable]:
        match node:
            case ast.IfExp(test, body, orelse):
                test = self.visit(test)
                match test:
                    case ast.Constant(value) if value:
                        return self.visit(body)
                    case ast.Constant(value) if not value:
                        return self.visit(orelse)
                    case _:
                        return ast.IfExp(test, self.visit(body), self.visit(orelse))
            case _:
                raise self._visit_wrong_type_error(node)

    def visit_Compare(self, node: ast.Compare) -> Union[ast.Compare, ast.Constant]:
        # TODO: Further reduce constant comparisons to get composed ast.BoolOp
        # TODO: Plugins for further reduction (e.g. by term re-ordering)
        node = self.generic_visit(node)
        match node:
            case ast.Compare(ast.Constant(value), ops, [*comps]) if all(self._is_const_node(c) for c in comps):
                result = True
                right_vals = [c.value for c in comps]
                for left, op, right in zip([value] + right_vals, ops, right_vals):
                    result = result and CMP_OPS[type(op)](left, right)
                return ast.Constant(result)
            case ast.Compare(_):
                return node
            case _:
                raise self._visit_wrong_type_error(node)

    def visit_Call(self, node: ast.Call) -> ast.Call:
        # TODO: Inline calls (look up node.func.id in self.env)
        # TODO: Partial evaluation of calls
        return super().generic_visit(node)

    def visit_Name(self, node: ast.Name) -> Union[ast.Name, ast.Constant]:
        match node:
            case ast.Name(id, ast.Load()) if id in self.env:
                # TODO: Inline non-constant names
                return ast.Constant(self.env[id])
            case ast.Name(_):
                return node
            case _:
                raise self._visit_wrong_type_error(node)

    # PRIVATE #

    @staticmethod
    def _is_const_node(x: ast.AST):
        return isinstance(x, ast.Constant)

    @staticmethod
    def _visit_wrong_type_error(wrong_arg) -> Exception:
        caller = inspect.stack()[1].function
        return RuntimeError(f"{caller} called on object of type {type(wrong_arg).__name__}")
