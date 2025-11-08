Write a function `distance` that returns a `list` of $y$ values calculated using the formula:

$$y(t) = v_0t − {1\over2} gt^2,$$

for `n` number of values $t$ ranging from `t_start` to `t_end`. Specify the keyword arguments `v0=6.0` and `g=9.81`.


```python
# Uncomment and complete this code - keep the names the same for testing purposes.

# def distance(t_start, t_end, n, v0=6.0, g=9.81):
#     ...
```


```python
with pybryt.check(pybryt_reference(1, 16)):
    distance(0, 10, 5)
```


```python
import numbers
import numpy as np

res = distance(0, 10, 10)
assert isinstance(res, list)
assert all([isinstance(i, numbers.Real) for i in res])
assert np.isclose(res[0], 0)

### BEGIN HIDDEN TESTS
assert callable(distance)
assert np.allclose(distance(0, 10, 5), [0.0, -15.65625, -92.625, -230.90625, -430.5])
### END HIDDEN TESTS
```