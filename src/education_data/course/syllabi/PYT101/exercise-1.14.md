Write a function `even_numbers(n)` using a `for` loop, which generates and returns a list of all even numbers from 0 to $n$. For instance, `even_numbers(10)` should return list `[0, 2, 4, 6, 8]`. In this exercise, do not use list comprehensions.


```python
# Uncomment and complete code. Do not change the variable names.

# def even_numbers(n):
#     ...
```


```python
with pybryt.check(pybryt_reference(1, 14)):
    even_numbers(11)
```


```python
import numbers
import numpy as np

res = even_numbers(10)
assert isinstance(res, list)
assert len(res) == 5
assert np.allclose(res, [0, 2, 4, 6, 8])

### BEGIN HIDDEN TESTS
assert callable(even_numbers)
assert all(i % 2 == 0 for i in even_numbers(200))
### END HIDDEN TESTS
```