import ast
import inspect
from typing import List, Optional

import typer

from simplify.simplifier import Simplifier
from simplify.utils import load_obj_from_path, parse_bindings


def transform_source(source: str, bind_list: Optional[List[str]] = None) -> str:
    if bind_list is None:
        bind_list = []
    tree = ast.parse(source)
    bindings = parse_bindings(bind_list)
    result = Simplifier(bindings).visit(tree)
    text = ast.unparse(result)
    return text


def main(
    stdin: bool = typer.Option(False, help="Read multi-line source from standard input."),
    source: str = typer.Option("", help="Inline source text."),
    file: typer.FileText = typer.Option(None, help="Path to source file."),
    module: str = typer.Option("", help="Python path to module or object therein of the form `module_path:obj_name`."),
    bind: Optional[List[str]] = typer.Option(
        None, help="Statement of the form `name=val` binding value of constant expression to variable."
    ),
):
    one_of = {"--stdin": stdin, "--source": source, "--file": file, "--module": module}
    if not sum(map(bool, one_of.values())) == 1:
        typer.echo(f"Exactly one of the following must be provided: {', '.join(str(x) for x in one_of)}.", err=True)
        typer.Exit(code=1)

    # get source if needed
    if module:
        obj = load_obj_from_path(module)
        source = inspect.getsource(obj)
    elif file:
        source = "".join(file)
    elif stdin:
        lines = []
        while True:
            try:
                lines.append(input())
            except EOFError:
                break
        source = "\n".join(lines)

    print(transform_source(source, bind))
