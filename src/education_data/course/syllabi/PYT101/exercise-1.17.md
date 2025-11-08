Write a function that returns the cumulative sum of the numbers in a list. The function should return a list, whose `i`-th element is the sum of the input list up to and including the `i`-th element.

For example, for the list `[1, 4, 2, 5, 3]` should return `[1, 5, 7, 12, 15]`.


```python
# Uncomment and complete this code - keep the names the same for testing purposes.

# def my_cumsum(x):
#     ...
```


```python
with pybryt.check(pybryt_reference(1, 17)):
    my_cumsum([55, 111, -33, 65])
```


```python
import numbers
import numpy as np

res = my_cumsum(range(10))
assert isinstance(res, list)
assert all([isinstance(i, numbers.Real) for i in res])
assert np.isclose(res[0], 0)
assert np.isclose(res[-1], 45)

### BEGIN HIDDEN TESTS
assert callable(my_cumsum)
assert np.allclose(my_cumsum(range(100)), np.cumsum(range(100)))
### END HIDDEN TESTS
```