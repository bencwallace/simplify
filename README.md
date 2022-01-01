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
>>> simplify --source "(True or x) and y"  # short-circuit evaluation in boolean expressions
y
>>> simplify --source "x = 42; x * y" --bind y=2  # inject variable bindings into code
84
>>> cat << EOF | simplify --stdin  # simplify statements involving local scope
> x = 1
> def f():
>     x = 2
>     x
> EOF
def f():
    2
```

## Types of simplifications

* Partial evaluation of expressions
* Inlining
  * Variables
  * Function calls
* Unrolling loops
