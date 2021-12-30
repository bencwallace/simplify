#!/usr/bin/env python3
import ast
import inspect
import sys

from simplify.main import main
from simplify.utils import load_obj_from_path

if __name__ == "__main__":
    # Usage: python simplify.py [--path path.to.python[:obj]] [--source source] [bindings...]
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} [path.to.python[:obj]|source] [bindings...]")
        sys.exit(1)

    # TODO: Store source and use ast.get_source_segment to print better error messages
    if sys.argv[1] == "--source":
        source = sys.argv[2]
    elif sys.argv[1] == "--module":
        python_path = sys.argv[2]
        obj = load_obj_from_path(python_path)
        source = inspect.getsource(obj)
    elif sys.argv[1] == "--path":
        with open(sys.argv[2]) as f:
            source = f.read()
    else:
        raise ValueError("Expected either --module, --source, or --path.")

    print(main(source, sys.argv[3:]))
