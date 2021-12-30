#!/usr/bin/env python3
import ast
import sys

from simplify.simplifier import Simplifier
from simplify.utils import load_obj_from_path, obj_to_tree, parse_bindings


def main():
    # Usage: python simplify.py [--path path.to.python[:obj]] [--source source] [bindings...]
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} [path.to.python[:obj]|source] [bindings...]")
        sys.exit(1)

    if sys.argv[1] == "--source":
        tree = ast.parse(sys.argv[2])
    elif sys.argv[1] == "--module":
        python_path = sys.argv[2]
        obj = load_obj_from_path(python_path)
        tree = obj_to_tree(obj)
    elif sys.argv[1] == "--path":
        with open(sys.argv[2]) as f:
            tree = ast.parse(f.read())
    else:
        raise ValueError("Expected either --module, --source, or --path.")

    binding_exprs = sys.argv[3:]
    bindings = parse_bindings(binding_exprs)
    result = Simplifier(bindings).visit(tree)
    text = ast.unparse(result)
    print(text)


if __name__ == "__main__":
    main()
