A `while`-loop executes repeatedly a set of statements as long as a boolean `condition` is `True`

```python
while condition:
    <statement 1>
    <statement 2>
    ...

<first statement after the loop>
```

Note that all statements to be executed within the loop must be indented by the same amount! The loop ends when an unindented statement is encountered.

In Python, indentations are very important. For instance, when writing a `while` loop:


```python
counter = 0
while counter <= 10:
    counter = counter + 1

print(counter)
```

Let us take a look at what happens when we forget to indent correctly:

```python
counter = 0
while counter <= 10:
counter = counter + 1
print(counter)


  File "<ipython-input-86-d8461f52562c>", line 3
    counter = counter + 1
    ^
IndentationError: expected an indented block
```

Let us now use the `while`-loop to create the table above:


```python
C = -20  # Initialise C
dC = 5  # Increment for C within the loop
while C <= 40:  # Loop heading with condition (C <= 40)
    F = (9 / 5) * C + 32  # 1st statement inside loop
    print(C, F)  # 2nd statement inside loop
    C = C + dC  # Increment C for the next iteration of the loop.
```