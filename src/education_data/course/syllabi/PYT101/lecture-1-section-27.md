We can visit each element in a list and process it with some statements using a `for`-loop, for example:


```python
degrees = [0, 10, 20, 40, 100]
for C in degrees:
    print("list element:", C)
print(f"The list has {len(degrees)} elements.")
```

Notice again how the statements to be executed within the loop must be indented! Let us now revisit the conversion table example using the `for` loop:


```python
Cdegrees = [-20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40]
for C in Cdegrees:
    F = (9 / 5) * C + 32
    print(C, F)
```

We can easily beautify the table using the *printf syntax* we encountered previously:


```python
for C in Cdegrees:
    F = (9.0 / 5) * C + 32
    print(f"{C:5d} {F:5.1f}")
```

It is also possible to rewrite the `for` loop as a `while` loop, i.e.

```python
for element in somelist:
    # process element
```

can always be transformed to a `while` loop
```python
index = 0
while index < len(somelist):
    element = somelist[index]
    # process element
    index += 1
```

Let us see how a previous example would look like if we used `while` instead of `for` loop:


```python
Cdegrees = [-20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40]
index = 0
while index < len(Cdegrees):
    C = Cdegrees[index]
    F = (9.0 / 5) * C + 32
    print(f"{C:5d} {F:5.1f}")
    index += 1
```

Rather than just printing out the Fahrenheit values, let us also store these computed values in a list of their own:


```python
Cdegrees = [-20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40]
Fdegrees = []  # start with empty list
for C in Cdegrees:
    F = (9 / 5) * C + 32
    Fdegrees.append(F)  # add new element to Fdegrees
print(Fdegrees)
```

In Python, `for` loops usually loop over list values (elements), i.e.

```python
for element in somelist:
    # process variable element
```

However, we can also loop over list indices:

```python
for i in range(0, len(somelist), 1):
    element = somelist[i]
    # process element or somelist[i] directly
```

The statement `range(start, stop, increment)` generates a list of integers *start*, *start+increment*, *start+2\*increment*, and so on up to, but not including, *stop*. We can also write `range(stop)` as an abbreviation for `range(0, stop, 1)`:


```python
for i in range(3):  # same as range(0, 3, 1)
    print(i)
```


```python
for i in range(2, 8, 3):
    print(i)
```