A rubber ball is dropped from a height `h_0`. After each bounce, the height it rebounds to decreases by 10%, i.e. after one bounce, it reaches `0.9*h_0`, after two bounces it reaches `0.9*0.9*h_0`, etc. Write a Python function `compute_heights` that returns a list of the maximum heights of the ball after each bounce (including after 0 bounces, i.e. its initial height), until either the ball has bounced `n` times *or* its maximum height falls below `h1`. The function should take `h_0`, `h_1` and `n` as keyword arguments, with default values of `1.0`, `0.3` and `10`, respectively.

**HINT:** If `n` bounces of the ball are not reached, the last value of height in the list should be the first height at which the ball fell below `h1`. More precisely, the last value is less than `h1`.


```python
# Uncomment and complete this code - keep the names the same for testing purposes.

# def compute_heights(h_0=1.0, h_1=0.3, n=10):
#     ...
```


```python
with pybryt.check(pybryt_reference(1, 18)):
    compute_heights(h_0=1.0, h_1=0.3, n=10)
```


```python
import numbers
import numpy as np

res = compute_heights(h_0=1.0, h_1=0, n=10)
assert isinstance(res, list)
assert all([isinstance(i, numbers.Real) for i in res])
assert np.isclose(res[0], 1)
assert np.isclose(res[-1], 0.9**10)

### BEGIN HIDDEN TESTS
assert callable(compute_heights)
assert np.allclose(
    compute_heights(h_0=1.0, h_1=0.5, n=10),
    [
        1.0,
        0.9,
        0.81,
        0.7290000000000001,
        0.6561000000000001,
        0.5904900000000002,
        0.5314410000000002,
        0.47829690000000014,
    ],
)
### END HIDDEN TESTS
```