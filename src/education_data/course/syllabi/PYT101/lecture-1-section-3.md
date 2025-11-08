From mathematics, you are already familiar with *variables* (e.g. $v_0 = 5$, $g = 9.81$, $t = 0.6$, $y = v_0t - \frac{1}{2}gt^2$), and know how important they are for working out complicated problems. Similarly, you can use variables in a program to make it easier to read and understand.


```python
v0 = 5
g = 9.81
t = 0.6
y = v0 * t - 0.5 * g * t**2
print(y)
```

This program performs the same calculations as the previous one and gives the same output. However, this program spans several lines and uses variables. 

We usually use one letter for a variable in mathematics, resorting to using the Greek alphabet and other characters for more clarity. The main reason for this is to avoid becoming exhausted from writing when working out long expressions or derivations. However, when programming, you should use more descriptive names for variables. This might not seem like an important consideration for the trivial example here. Still, it becomes increasingly important as the program gets more complicated and if someone else has to read your code.

### Good variable names make a program easier to understand!

Python *allows* variable names to include:
* lowercase `a-z`, uppercase `A-Z`, underscore (`_`), and digits `0-9`, **but** the name cannot start with a digit or contain a whitespace.
* "textlike" [Unicode](http://www.unicode.org/) characters from other languages are also allowed.

Variable names are case-sensitive (strictly, character sensitive, i.e. `a` is different from `A`).

**Good** variable names are often:
* standard one-letter symbols,
* words or abbreviations of words,
* phrases joined together in [snake_case](https://en.wikipedia.org/wiki/Snake_case) or [camelCase](https://en.wikipedia.org/wiki/Camel_case).

Let us rewrite the previous example using more descriptive variable names:


```python
initial_velocity = 5
acceleration_of_gravity = 9.81
TIME = 0.6
VerticalPositionOfBall = (
    initial_velocity * TIME - 0.5 * acceleration_of_gravity * TIME**2
)
print(VerticalPositionOfBall)
```

In Python, you can check if the name you would like to give to your variable is valid or not, i.e. check if it is a valid identifier. To do that, you can enclose the variable name in quotes (to form a string literal) and call its `isidentifier()` method:


```python
print("initial_velocity".isidentifier())  # snake_case-style variable name
print("InitialVelocity".isidentifier())  # CamelCase-style variable name
print("initial velocity".isidentifier())  # variable name contains space
```

Certain words have a **special meaning** in Python and **cannot be used as variable names**. We refer to them as **keywords**, and in Python 3.9 they are:

`and`, `as`, `assert`, `async`, `await`, `break`, `class`, `continue`, `def`, `del`, `elif`, `else`, `except`, `finally`, `for`, `from`, `global`, `if`, `import`, `in`, `is`, `lambda`, `nonlocal`, `not`, `or`, `pass`, `raise`, `return`, `try`, `while`, `with`, and `yield`. 

Similarly, `True`, `False`, and `None` are keywords we use for the values of variables, and we cannot use them for variable names. Keywords are very important in programming and, in these lectures, we will learn how to use some of them.

Finally, Python has some "builtin" functions which are always available. While Python will let you do it, it is usually a bad idea to use these names, since this would *overshadow* the builtin function and prevent us from calling it. The full list of builtin functions in Python 3.9 is `abs()`, `aiter()`, `all()`, `any()`, `anext()`, `ascii()`, `bin()`, `bool()`, `breakpoint()`, `bytearray()`, `bytes()`, `callable()`, `chr()`, `classmethod()`, `compile()`, `complex()`, `delattr()`, `dict()`, `dir()`, `divmod()`, `enumerate()`, `eval()`, `exec()`, `filter()`, `float()`, `format()`, `frozenset()`, `getattr()`, `globals()`, `hasattr()`, `hash()`, `help()`, `hex()`, `id()`, `input()`, `int()`, `isinstance()`, `issubclass()`, `iter()`, `len()`, `list()`, `locals()`, `map()`, `max()`, `memoryview()`, `min()`, `next()`, `object()`, `oct()`, `open()`, `ord()`, `pow()`, `print()`, `property()`, `range()`, `repr()`, `reversed()`, `round()`, `set()`, `setattr()`, `slice()`, `sorted()`, `staticmethod()`, `str()`, `sum()`, `super()`, `tuple()`, `type()`, `vars()`, and  `zip()`.

Please note that the list of keywords and builtins may differ between different Python versions.