Besides *positional arguments*, functions can have arguments of the form `argument_name=value` and they are called *keyword arguments*:


```python
def somefunc(arg1, arg2, kwarg1=True, kwarg2=0):
    print(f"arg1: {arg1}, arg2: {arg2}, kwarg1: {kwarg1}, kwarg2: {kwarg2}")


# Note that we have not specified inputs for kwarg1 and kwarg2.
somefunc("Hello", [1, 2])
```


```python
# Note that we replace the default value for kwarg1.
somefunc("Hello", [1, 2], kwarg1="Hi")
```


```python
# Note that we replace the default value for kwarg2.
somefunc("Hello", [1, 2], kwarg2="Hi")
```


```python
# Here, we replace both default values for keyword arguments kwarg1 and kwarg2.
somefunc("Hello", [1, 2], kwarg2="Hi", kwarg1=6)
```

If we use `argument_name=value` for all arguments, their sequence in the function call can be in any order.


```python
somefunc(kwarg2="Hello", arg1="Hi", kwarg1=6, arg2=[2])
```