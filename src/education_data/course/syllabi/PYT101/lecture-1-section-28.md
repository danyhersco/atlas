Consider this example where we compute two lists in a `for` loop:


```python
n = 16

# empty lists
Cdegrees = []
Fdegrees = []

for i in range(n):
    Cdegrees.append(-5 + i * 0.5)
    Fdegrees.append((9 / 5) * Cdegrees[i] + 32)

print("Cdegrees = ", Cdegrees)
print("Fdegrees = ", Fdegrees)
```

As constructing lists is a very common task, the above way of doing it can become very tedious both to write and read. Therefore, Python has a compact construct, called *list comprehension* for generating lists from a `for` loop:


```python
n = 16
Cdegrees = [-5 + i * 0.5 for i in range(n)]
Fdegrees = [(9 / 5) * C + 32 for C in Cdegrees]
print("Cdegrees = ", Cdegrees)
print("Fdegrees = ", Fdegrees)
```

The most general form of a list comprehension is:
```python
somelist = [expression for element in somelist if condition]
```

Here the `condition` can be used to pick out elements which satisfy a specific property.