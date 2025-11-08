Write a Python function `odd_numbers(n)` that uses a `while`-loop, and generates and returns a list of all odd numbers from $1$ to $n$. (Make sure that if $n$ is an even number, the largest generated odd number is $n-1$.)


```python
# Uncomment and complete code. Do not change the variable names.

# def odd_numbers(n):
#     ...
```


```python
with pybryt.check(pybryt_reference(1, 13)):
    odd_numbers(50)
```


```python
import numbers
import numpy as np

res = odd_numbers(10)
assert isinstance(res, list)
assert len(res) == 5
assert np.allclose(res, [1, 3, 5, 7, 9])

### BEGIN HIDDEN TESTS
assert callable(odd_numbers)
assert all(i % 2 for i in odd_numbers(200))
### END HIDDEN TESTS
```