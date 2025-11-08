A formula for $\pi$ is given by the *Gregory-Leibniz series*:

$$\pi = 4 \left(\frac{1}{1} - \frac{1}{3} + \frac{1}{5} - \frac{1}{7} + \frac{1}{9} + ...  \right)$$

Note that the denominators of the terms in this series are the positive odd numbers. Write a Python function `calculate_pi(n)` following the guidelines below; each of the first three steps can be completed using a single list comprehension.

**Step 1**:

Produce a list of the first `n` odd numbers, for `n=100`.

**Step 2**:

Make a list of the signs of each term, i.e. `[1, -1, 1, -1, ...]`. Hint: think about the value of $(-1)^i$ for integer $i$.

**Step 3**:

Using the results of steps 1 and 2, make a list of the first `n` terms in the above series.

**Step 4**:

Use your `my_sum` function to sum this series, multiply by 4, and return the result.


```python
# Uncomment and complete this code - keep the names the same for testing purposes.

# def calculate_pi(n):
#     ...
```


```python
with pybryt.check(pybryt_reference(1, 19)):
    calculate_pi(100)
```


```python
import numbers
import numpy as np

res = calculate_pi(1000)
assert isinstance(res, numbers.Real)
assert np.isclose(res, np.pi, rtol=1e-3)

### BEGIN HIDDEN TESTS
assert callable(calculate_pi)
assert np.isclose(calculate_pi(1), 4)
assert np.isclose(calculate_pi(0), 0)
### END HIDDEN TESTS
```