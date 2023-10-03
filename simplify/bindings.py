import ast
from typing import Dict, Optional

from simplify.utils import unpack


class BindingError(Exception):
    pass


def _bind_pos_only(posonlyargs: list[ast.arg], call_args: list[ast.expr]):
    bindings = {}
    call_args_it = iter(call_args)
    for defn_arg in posonlyargs:
        try:
            call_arg = next(call_args_it)
        except StopIteration:
            raise BindingError()  # insufficient positional arguments
        bindings[defn_arg.arg] = call_arg
    return bindings


def _bind_pos(args: list[ast.arg], call_args: list[ast.expr], call_kwargs: list[ast.keyword]):
    bindings = {}
    call_args_it = iter(call_args)

    for defn_arg in args:
        try:
            call_arg = next(call_args_it)
            bindings[defn_arg.arg] = call_arg
        except StopIteration:
            # insufficient positional arguments -- fall back to keyword arguments
            for call_kwarg in call_kwargs:
                if call_kwarg.arg == defn_arg.arg:
                    bindings[defn_arg.arg] = call_kwarg.value
                    break  # important -- indicates result found
            else:
                raise BindingError()  # insufficient keyword arguments
    return bindings


def get_bindings(fn_args: ast.arguments, call: ast.Call):
    bindings: Dict[str, ast.expr] = {}

    call_args: list[ast.expr]
    call_kwargs: list[ast.keyword]
    _, call_args, call_kwargs = unpack(call)

    posonlyargs, args, vararg, kwonlyargs, kw_defaults, kwarg, defaults = unpack(fn_args)
    args: list[ast.arg]
    kwonlyargs: list[ast.arg]
    kwarg: Optional[ast.arg]

    # POSITIONAL ARGUMENTS #
    try:
        posonly_bindings = _bind_pos_only(posonlyargs, call_args)
    except BindingError:
        return {}
    bindings.update(posonly_bindings)

    try:
        pos_bindings = _bind_pos(args, call_args[len(bindings) :], call_kwargs)
    except BindingError:
        return {}
    bindings.update(pos_bindings)

    if vararg:
        bindings[vararg.arg] = ast.Tuple(list(call_args[len(bindings) :]), ast.Load())

    # TODO: KWARGS, defaults #

    return bindings
