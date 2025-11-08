Often we want to print out results using a combination of text and numbers, e.g. `"At t=0.6 s, y is 1.23 m"`. In Python, we can do this using f-strings:


```python
print(f"At t={t} s, y is {y} m.")  # f-string method - string literal begins with an f
```

We enclose our sentence in (single or double) quotes to denote a string literal and add `f` in front of it to tell Python to replace `{t}` and `{y}` with the values of `t` and `y`, respectively.

When printing out floating-point numbers, we should **never** quote numbers to a higher accuracy than they were measured. Python provides a *printf formatting* syntax exactly for this purpose. We can see in the following example where the *format* `g` expresses the floating-point number with the minimum number of significant figures, and the *format* `.2f` specifies that only two digits are printed out after the decimal point. We specify the format inside `{}` and separate it from the variable name with `:`.


```python
print(f"At t={t:g} s, y is {y:.2f} m.")  # f-string with specified formatting
```

Sometimes we want a multi-line output. This is achieved using a triple quotation, i.e. `"""`:


```python
print(f"""At t={t:f} s, a ball with
initial velocity v0={v0:.3E} m/s
is located at the height y={y:.2f} m.
""")
```

Notice in this example we used `f`, `.3E`, and `.2f` to define formats, into which we inserted the values of `t`, `v0`, and `y` respectively. You can find more details about the format specification mini-language in the Python [documentation](https://docs.python.org/3/library/string.html#format-specification-mini-language).

Instead of using the f-string formatted printing, Python offers another two syntax alternatives: string's `format` method and the `%` operator. Let us have a look at how we can print `"At t=0.6 s, y is 1.23 m"` using these two alternative solutions.


```python
print("At t={:g} s, y is {:.2f} m.".format(t, y))  # string's format method
print("At t=%g s, y is %.2f m." % (t, y))  # % operator
```

Notice that we defined slots in a string using curly braces `{}` where we also specified the formatting style in the same way we did before. We inserted the values into the slots by passing them to the `format()` method or by writing them in curly braces.

The `%` operator expands out the input tuple place by place (so the first *slot* gets the first element, the second the second, and so on). If there is only one *slot* then using a tuple is optional.