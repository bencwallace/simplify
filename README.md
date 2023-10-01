# Simplify

Simplify Python code the way you would mathematical expressions.

## Examples

```bash
>>> alias simplify="python -m simplify"
>>> simplify --source "2 + 2"  # perform arithmetic
4
>>> simplify --source "13 if 42 + 24 == 66 else 31"  # short-circuit conditionals
13
>>> simplify --source "x = 42; 2 * x"  # resolve stateful expressions
84
>>> simplify --source "x = 42; x * y"  # perform partial evaluation
42 * y
>>> simplify --source "(True or x) and y"  # short-circuit boolean expressions
y
>>> simplify --source "x = 42; x * y" --bind y=2  # inject variable bindings into code
84
>>> simplify --source "(lambda x: x ** 2)(y + 3)"  # inline lambdas
(y + 3) ** 2
>>> cat << EOF | simplify --stdin  # inline simple function calls
> def f():
>     return 13
> print(f())
> EOF
def f():
    return 13
print(13)
>>> cat << EOF | simplify --stdin  # track local scope
> x = 1
> def f():
>     x = 2
>     x
> EOF
def f():
    2
>>> cat << EOF | simplify --stdin  # unfold loops
> for x in [1, 2, 3]:
>     print(x)
> EOF
print(1)
print(2)
print(3)
```
