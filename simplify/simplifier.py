import ast
import functools
from contextlib import contextmanager
from typing import Any, Iterable, Optional, Union

from simplify.data import BIN_OPS, CMP_OPS
from simplify.environment import Environment


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
        return super().visit(node)

    @contextmanager
    def new_environment(self, name):
        old_env = self.env
        new_env = Environment(old_env)
        old_env[name] = new_env
        self.env = new_env
        yield
        self.env = old_env

    # STATEMENTS #

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        # TODO: Add decorators, etc.
        # TODO: Check if return value can be extracted
        with self.new_environment(node.name):
            result = super().generic_visit(node)
        self.env[node.name] = result
        return result

    def visit_Return(self, node: ast.Return) -> ast.Return:
        if node.value:
            return ast.Return(self.visit(node.value))
        return ast.Return()

    def visit_Delete(self, node: ast.Delete) -> Optional[ast.Delete]:
        targets = []
        for t in self.visit(node.targets):
            # TODO: Case t not a Name
            if t.id in self.env:
                del self.env[t.id]
            else:
                targets.append(t)
        if targets:
            return ast.Delete(targets)
        return None

    # TODO: Handle type comment
    def visit_Assign(self, node: ast.Assign) -> Optional[ast.Assign]:
        targets = self.visit(node.targets)
        val = self.visit(node.value)
        if isinstance(val, ast.Constant):
            for t in targets:
                # TODO: Check if possible for t not to be a Name
                if t.id in self.env.globals:
                    self.global_env[t.id] = val.value
                else:
                    self.env[t.id] = val.value
            return None
        return ast.Assign(targets, val)

    def visit_If(self, node: ast.If) -> Union[ast.If, Iterable]:
        test = self.visit(node.test)
        if not isinstance(test, ast.Constant):
            return ast.If(test, self.visit(node.body), self.visit(node.orelse))
        if test.value:
            return self.visit(node.body)
        return self.visit(node.orelse)

    def visit_Global(self, node: ast.Global) -> None:
        self.env.add_globals(*node.names)

    def visit_AugAssign(self, node: ast.AugAssign):
        # TODO
        return super().visit_AugAssign(node)

    # EXPRESSIONS #

    def visit_BoolOp(self, node: ast.BoolOp) -> Union[ast.BoolOp, ast.Constant]:
        values = self.visit(node.values)
        if not values:
            return ast.BoolOp(node.op, values)

        const_values = [v for v in values if isinstance(v, ast.Constant)]
        non_const_values = [v for v in values if not isinstance(v, ast.Constant)]

        if isinstance(node.op, ast.And):
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
        elif isinstance(node.op, ast.Or):
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
        else:
            raise RuntimeError(f"Unrecognized boolean operator: {type(node.op).__name__}")

    def visit_BinOp(self, node: ast.BinOp) -> Union[ast.BinOp, ast.Constant]:
        left = self.visit(node.left)
        right = self.visit(node.right)

        if not isinstance(left, ast.Constant) or not isinstance(right, ast.Constant):
            return ast.BinOp(left, node.op, right)
        return ast.Constant(BIN_OPS[type(node.op)](left.value, right.value))

    def visit_IfExp(self, node: ast.IfExp) -> Union[ast.IfExp, Iterable]:
        test = self.visit(node.test)
        if not isinstance(test, ast.Constant):
            return ast.IfExp(test, self.visit(node.body), self.visit(node.orelse))
        if test.value:
            return self.visit(node.body)
        return self.visit(node.orelse)

    def visit_Compare(self, node: ast.Compare) -> Union[ast.Compare, ast.Constant]:
        left = self.visit(node.left)
        comparators = [self.visit(c) for c in node.comparators]

        if not isinstance(left, ast.Constant) or not all(isinstance(c, ast.Constant) for c in comparators):
            return ast.Compare(left, node.ops, comparators)
        result = True
        for l, op, r in zip([left] + comparators, node.ops, comparators):
            result = result and CMP_OPS[type(op)](l.value, r.value)
        return ast.Constant(result)

    def visit_Call(self, node: ast.Call) -> ast.Call:
        # TODO: Add kwargs
        # TODO: "Fuse" calls
        # TODO: Replace call by resulting partial value
        func = self.visit(node.func)
        # if isinstance(func, ast.Name) and func.id in self.env:
        #     f = self.env[func.id]
        #     # TODO: Remove relevant args, kwargs from signature and insert corresponding definitions at beginning of body
        return ast.Call(func, self.visit(node.args), self.visit(node.keywords))

    def visit_Name(self, node: ast.Name) -> Union[ast.Name, ast.Constant]:
        if isinstance(node.ctx, ast.Load) and node.id in self.env:
            return ast.Constant(self.env[node.id])
        return super().generic_visit(node)
