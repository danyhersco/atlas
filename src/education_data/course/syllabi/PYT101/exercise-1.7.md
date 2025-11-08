Write a Python function `gaussian` to compute the Gaussian function:

$$f(x)=\frac{1}{s\sqrt{2\pi}}\exp\left(-\frac{1}{2} \left(\frac{x-m}{s}\right)^2\right)$$


```python
# Uncomment and complete this code - keep the function name the same for testing purposes.

# def gaussian(x, m=0, s=1):
#     ...
```


```python
with pybryt.check(pybryt_reference(1, 7)):
    gaussian(0.5)
```


```python
import numbers
import numpy as np

res = gaussian(x=0, m=0, s=1)
assert isinstance(res, numbers.Real)
assert np.isclose(res, 1 / np.sqrt(2 * np.pi))

### BEGIN HIDDEN TESTS
assert callable(gaussian)
assert np.isclose(gaussian(x=2, m=0, s=1), 0.05399096651318806)
### END HIDDEN TESTS
```