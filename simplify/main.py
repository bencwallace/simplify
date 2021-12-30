import ast
from typing import List, Optional

from simplify.simplifier import Simplifier
from simplify.utils import parse_bindings


# TODO: Use Typer
def main(source: str, bind_exprs: Optional[List[str]] = None) -> str:
    if not bind_exprs:
        bind_exprs = []
    tree = ast.parse(source)
    bindings = parse_bindings(bind_exprs)
    result = Simplifier(bindings).visit(tree)
    text = ast.unparse(result)
    return text
