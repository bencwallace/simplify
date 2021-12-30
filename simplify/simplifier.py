import ast
import operator as op
from typing import Optional

from simplify.environment import Environment


BIN_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.MatMult: op.matmul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.LShift: op.lshift,
    ast.RShift: op.rshift,
    ast.BitOr: op.or_,
    ast.BitXor: op.xor,
    ast.BitAnd: op.and_,
    ast.FloorDiv: op.floordiv,
}

CMP_OPS = {
    ast.Eq: op.eq,
    ast.NotEq: op.ne,
    ast.Lt: op.lt,
    ast.LtE: lambda x, y: x < y or x == y,
    ast.Gt: op.gt,
    ast.GtE: lambda x, y: x > y or x == y,
    ast.Is: op.is_,
    ast.IsNot: op.is_not,
    ast.In: lambda x, y: x in y,
    ast.NotIn: lambda x, y: x not in y,
}


class EnvHandler:
    def __init__(self, simplifier, env_name):
        self._simplifier = simplifier
        self._env_name = env_name

    def __enter__(self):
        old_env = self._simplifier._environment
        new_env = Environment(old_env)
        old_env[self._env_name] = new_env
        self._simplifier._environment = new_env
        return new_env

    def __exit__(self, _, __, ___):
        self._simplifier._environment = self._simplifier._environment.enclosing


class Simplifier(ast.NodeTransformer):
    def __init__(self, bindings: Optional[dict] = None):
        self._environment = Environment()
        if bindings is None:
            bindings = {}
        for name, val in bindings.items():
            self._environment[name] = val

    def _visit_nodes(self, nodes: list):
        return [self.visit(n) for n in nodes]

    def new_environment(self, name):
        return EnvHandler(self, name)

    def visit_FunctionDef(self, node):
        # TODO: Add decorators, etc.
        # TODO: Check if return value can be extracted
        with self.new_environment(node.name):
            return super().generic_visit(node)

    def visit_Call(self, node):
        # TODO: Add kwargs
        pass

    # TODO: Similar for delete (and others?)
    def visit_Assign(self, node):
        val = self.visit(node.value)
        if isinstance(val, ast.Constant):
            for t in node.targets:
                self._environment[t.id] = val.value
        return None

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            if node.id in self._environment:
                return ast.Constant(self._environment[node.id])
            return node
        raise NotImplementedError(f"Name expression of type {type(node.ctx).__name__} not supported.")

    # TODO: Similar for other statements/expressions
    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        if not isinstance(left, ast.Constant) or not isinstance(right, ast.Constant):
            return ast.BinOp(left, node.op, right)
        return ast.Constant(BIN_OPS[type(node.op)](left.value, right.value))

    def visit_Compare(self, node):
        left = self.visit(node.left)
        comparators = [self.visit(c) for c in node.comparators]
        
        if not isinstance(left, ast.Constant) or not all(isinstance(c, ast.Constant) for c in comparators):
            return ast.Compare(left, node.ops, comparators)
        result = True
        for l, op, r in zip([left] + comparators, node.ops, comparators):
            result = result and CMP_OPS[type(op)](l.value, r.value)
        return ast.Constant(result)

    def visit_IfExp(self, node):
        test = self.visit(node.test)
        if not isinstance(test, ast.Constant):
            return ast.IfExp(test, self.visit(node.body), self.visit(node.orelse))
        if test.value:
            return self.visit(node.body)
        return self.visit(node.orelse)

    def visit_If(self, node):
        test = self.visit(node.test)
        if not isinstance(test, ast.Constant):
            return ast.If(test, self._visit_nodes(node.body), self._visit_nodes(node.orelse))
        if test.value:
            return self._visit_nodes(node.body)
        return self._visit_nodes(node.orelse)
