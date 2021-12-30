# Simplify

Simplify Python code the way you would mathematical expressions.

## Examples

```bash
>>> alias simplify="python -m simplify"
>>> simplify --source "2 + 2"  # evaluate arithmetic
4
>>> simplify --source "13 if 42 + 24 == 66 else 31"  # evaluate conditional expressions
13
>>> simplify --source "x = 42; 2 * x"  # evaluate expressions depending on global state
84
>>> simplify --source "x = 42; x * y"  # partially evaluate expressions
42 * y
>>> simplify --source "x = 42; x * y" --bind y=2  # inject variable bindings into code
84
```

## Other possibilities

* Unrolling loops
* Flattening composed functions
