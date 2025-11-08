An expression with value `True` or `False` is called a boolean expression. Example expressions for what you would write mathematically as
$C = 40$, $C \ne 40$, $C \ge 40$, $C \gt 40$ and $C \lt 40$ are:

```python
C == 40  # Note: the double == checks for equality!
C != 40  # This could also be written as "not C == 4"
C >= 40
C > 40
C < 40
```

Let us now test some boolean expressions:


```python
C = 41

print("C != 40: ", C != 40)
print("C < 40: ", C < 40)
print("C == 41: ", C == 41)
```

Several conditions can be combined with keywords `and` and `or` into a single boolean expression:

* **Rule 1**: (`C1 and C2`) is `True` only if both `C1` and `C2` are `True`.
* **Rule 2**: (`C1 or C2`) is `True` if either `C1` or `C2` are `True`.

Examples:


```python
x = 0
y = 1.2

print("x >= 0 and y < 1:", x >= 0 and y < 1)
print("x >= 0 or y < 1:", x >= 0 or y < 1)
```