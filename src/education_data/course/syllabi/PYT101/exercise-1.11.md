Write a Python function `num_digits(a)` that uses a `while` loop to compute how many decimal digits we need to write a positive integer $a$. For instance, we need 2 digits to write 73, whereas we need 5 digits to write 12345.


```python
# Uncomment and complete the code below. Do not change the names of variables!

# def num_digits(a):
#     ...
```


```python
with pybryt.check(pybryt_reference(1, 11)):
    num_digits(999_999_999)
```


```python
import numbers
import numpy as np

res = num_digits(123_456_789)
assert isinstance(res, numbers.Real)
assert np.isclose(res, 9)

### BEGIN HIDDEN TESTS
assert callable(num_digits)

assert np.isclose(num_digits(0), 1)
assert np.isclose(num_digits(5), 1)
assert np.isclose(num_digits(10), 2)
assert np.isclose(num_digits(99), 2)
assert np.isclose(num_digits(100), 3)
### END HIDDEN TESTS
```