We have already used Python functions above, e.g. `sqrt` from the `math` module. In general, a function is a collection of statements we can execute wherever and whenever we want. For example, consider any of the formulae we implemented above. 

Functions can take any number of inputs (called *arguments* or *parameters*) to produce outputs. Functions help to organise programs, make them more understandable, shorter, and easier to extend. Wouldn't it be nice to implement it just once and then be able to use it again any time you need it, rather than having to write out the whole formula again?

For our first example, we will reuse the formula for the position of a ball in a vertical motion, which we have seen earlier.


```python
def ball_height(v0, t, g=9.81):
    """Function to calculate and return height of the ball in vertical motion.

    Parameters
    ----------
    v0 : float
        Initial velocity (units, m/s).
    t : float
        Time at which we want to know the height of the ball (units, seconds).
    g : float, optional
        Acceleration due to gravity (units, m/s^2). By default 9.81 m/s^2.

    Returns
    -------
    float
        Height of the ball in metres.

    """
    height = v0 * t - 0.5 * g * t**2

    return height
```

Let us break this example down:
* Function *signature* (header):
    * Functions start with `def` followed by the name we want to give the function (`ball_height` in this case). Just like with variables, function names must be valid identifiers.
    * Following the name, we have parentheses followed by a colon `(...):` containing zero or more function *arguments*.
    * In this case, `v0` and `t` are *positional arguments*, while `g` is known as a *keyword argument* (more about this later).
* Function *body*:
    * The first thing to notice is that the body of the function is indented one level. All code that is indented with respect to `def`-line belongs to a function.
    * Best practice is to include a [docstring](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_numpy.html) to explain to others (or remind our future self) how to use the function. Docstring is defined as a multi-line string literal (enclosed in triple quotes """).
    * The function output is passed back via the `return` statement.
 
Notice that this just defines the function. Nothing is executed until we actually *call* the function:


```python
# We pass 5 and 0.6 to v0 and t, respectively.
# Since we do not pass a value for g,
# a default value we defined in function's signature is used.
# The value function returns (height) is put in variable h.
h = ball_height(5, 0.6)

print(f"Ball height: {h:g} metres.")
```

No return value implies that `None` is returned. `None` is a special Python object (singleton) that semantically often represents an ”empty” or undefined value. It is surprisingly useful, and we will use it a lot later.

Functions can also return multiple values. Let us extend the previous example to calculate the ball's velocity as well as its height:


```python
def ball_height_velocity(v0, t, g=9.81):
    """Function to calculate ball's height and its velocity.

    Parameters
    ----------
    v0 : float
        Initial velocity (units, m/s).
    t : float
        Time at which we want to know the height of the ball (units, seconds).
    g : float, optional
        Acceleration due to gravity (units, m/s^2). By default 9.81 m/s^2.

    Returns
    -------
    float
        Height of ball in metres.
    float
        Velocity of ball in m/s.

    """
    height = v0 * t - 0.5 * g * t**2
    velocity = v0 - g * t

    return height, velocity


# We pass 5 and 0.6 to v0 and t, respectively.
# The first value function returns (height) is put into variable h,
# whereas the second one (velocity) is placed in v - iterable unpacking.
h, v = ball_height_velocity(5, 0.6)

print("Ball height: %g metres." % h)
print("Ball velocity: %g m/s." % v)
```