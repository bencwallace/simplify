import ast
from contextlib import contextmanager
from typing import Optional

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

    def _visit_nodes(self, nodes: list):
        return [self.visit(n) for n in nodes]

    @contextmanager
    def new_environment(self, name):
        old_env = self.env
        new_env = Environment(old_env)
        old_env[name] = new_env
        self.env = new_env
        yield
        self.env = old_env

    # STATEMENTS #

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # TODO: Add decorators, etc.
        # TODO: Check if return value can be extracted
        with self.new_environment(node.name):
            result = super().generic_visit(node)
        self.env[node.name] = exec(result)
        return result

    # TODO: Similar for delete (and others?)
    def visit_Assign(self, node):
        val = self.visit(node.value)
        if isinstance(val, ast.Constant):
            for t in node.targets:
                if t.id in self.env.globals:
                    self.env.set(t.id, val.value, is_global=True)
                else:
                    self.env[t.id] = val.value
        return None

    def visit_If(self, node):
        test = self.visit(node.test)
        if not isinstance(test, ast.Constant):
            return ast.If(test, self._visit_nodes(node.body), self._visit_nodes(node.orelse))
        if test.value:
            return self._visit_nodes(node.body)
        return self._visit_nodes(node.orelse)

    def visit_Global(self, node: ast.Global):
        self.env.add_globals(*node.names)

    # EXPRESSIONS #

    # TODO: Similar for other statements/expressions
    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        if not isinstance(left, ast.Constant) or not isinstance(right, ast.Constant):
            return ast.BinOp(left, node.op, right)
        return ast.Constant(BIN_OPS[type(node.op)](left.value, right.value))

    def visit_IfExp(self, node):
        test = self.visit(node.test)
        if not isinstance(test, ast.Constant):
            return ast.IfExp(test, self.visit(node.body), self.visit(node.orelse))
        if test.value:
            return self.visit(node.body)
        return self.visit(node.orelse)

    def visit_Compare(self, node):
        left = self.visit(node.left)
        comparators = [self.visit(c) for c in node.comparators]

        if not isinstance(left, ast.Constant) or not all(isinstance(c, ast.Constant) for c in comparators):
            return ast.Compare(left, node.ops, comparators)
        result = True
        for l, op, r in zip([left] + comparators, node.ops, comparators):
            result = result and CMP_OPS[type(op)](l.value, r.value)
        return ast.Constant(result)

    def visit_Call(self, node):
        # TODO: Add kwargs
        # TODO: "Fuse" calls
        pass

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            if node.id in self.env:
                return ast.Constant(self.env[node.id])
            return node
        raise NotImplementedError(f"Name expression of type {type(node.ctx).__name__} not supported.")
