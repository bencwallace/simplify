#!/usr/bin/env python3
import inspect
import sys

from simplify.main import main
from simplify.utils import load_obj_from_path

if __name__ == "__main__":
    # Usage: python simplify.py [--path path.to.python[:obj]] [--source source] [bindings...]
    if len(sys.argv) < 2:
        print(
            f"Usage: {sys.argv[0]} "
            '[--source "<inline source>"] '
            "[--module path.to.python[:obj]] "
            "[--path path/to/python/file.py] "
            "[--bind bindings...]",
            file=sys.stderr,
        )
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
    elif sys.argv[1] == "--stdin":
        lines = []
        while True:
            try:
                lines.append(input())
            except EOFError:
                break
        source = "\n".join(lines)
    else:
        print("Expected either --module, --source, or --path.", file=sys.stderr)
        sys.exit(1)

    bind_exprs = None
    if len(sys.argv) >= 4:
        if not sys.argv[3] == "--bind":
            print(f"Invalid option: {sys.argv[3]}")
            sys.exit(1)
        bind_exprs = sys.argv[4:]
    print(main(source, bind_exprs))
