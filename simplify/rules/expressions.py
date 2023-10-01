import ast
import functools
from typing import TYPE_CHECKING

from simplify.bindings import get_bindings
from simplify.data import BIN_OPS, CMP_OPS, UNARY_OPS
from simplify.utils import split_list_on_predicate, unpack

if TYPE_CHECKING:
    from simplify.simplifier import Simplifier
else:
    Simplifier = "Simplifier"


def visit_bin_op(node: ast.BinOp, simp: Simplifier):
    node = super(type(simp), simp).generic_visit(node)
    match node:
        case ast.BinOp(ast.Constant(lval), op, ast.Constant(rval)):
            return ast.Constant(BIN_OPS[type(op)](lval, rval))
        case ast.BinOp(_):
            return node


def visit_bool_op(node: ast.BoolOp, simp: Simplifier):
    node = super(type(simp), simp).generic_visit(node)
    match node:
        case ast.BoolOp(_, []):
            return node
        case ast.BoolOp(ast.And(), values):
            const_values, non_const_values = split_list_on_predicate(values, lambda x: isinstance(x, ast.Constant))

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
            const_values, non_const_values = split_list_on_predicate(values, lambda x: isinstance(x, ast.Constant))

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


def visit_compare(node: ast.Compare, simp: Simplifier):
    # TODO: Further reduce constant comparisons to get composed ast.BoolOp
    # TODO: Plugins for further reduction (e.g. by term re-ordering)
    node = simp.generic_visit(node)
    match node:
        case ast.Compare(ast.Constant(value), ops, [*comps]) if all(isinstance(c, ast.Constant) for c in comps):
            result = True
            right_vals = [c.value for c in comps]
            for left, op, right in zip([value] + right_vals, ops, right_vals):
                result = result and CMP_OPS[type(op)](left, right)
            return ast.Constant(result)
        case ast.Compare(_):
            return node


def visit_call(node: ast.Call, simp: Simplifier):
    # TODO: Inline calls (look up node.func.id in self.scope)
    # TODO: Partial evaluation of calls
    func, call_args, _ = unpack(node)
    call_args = simp.visit(call_args)
    match func:
        # simplest case
        case ast.Lambda(ast.arguments(args=lambda_args), body) if len(lambda_args) == len(call_args):
            with simp.new_scope({lbd_arg.arg: cl_arg for lbd_arg, cl_arg in zip(lambda_args, call_args)}):
                return simp.visit(body)
        case ast.Name(name, ast.Load()) if name in simp.scope:
            fn_def = simp.scope[name]
            match fn_def:
                case ast.FunctionDef(_, _, body):
                    bindings = get_bindings(fn_def.args, node)
                    with simp.new_scope(bindings):
                        body = simp.visit(fn_def.body)
                        match body:
                            case [ast.Return(value)]:
                                return value
    return super(type(simp), simp).generic_visit(node)


def visit_if_exp(node: ast.IfExp, simp: Simplifier):
    test, body, orelse = unpack(node)
    test = simp.visit(test)
    match test:
        case ast.Constant(value) if value:
            return simp.visit(body)
        case ast.Constant(value) if not value:
            return simp.visit(orelse)
        case _:
            return ast.IfExp(test, simp.visit(body), simp.visit(orelse))


def visit_unary_op(node: ast.UnaryOp, simp: Simplifier):
    op, operand = unpack(node)
    operand = simp.visit(operand)
    if isinstance(operand, ast.Constant):
        return ast.Constant(UNARY_OPS[type(op)](operand.value))
    return ast.UnaryOp(op, operand)
