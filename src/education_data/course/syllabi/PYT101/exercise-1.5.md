The bell-shaped Gaussian function,

$$f(x)=\frac{1}{s\sqrt{2\pi}}\exp\left(-\frac{1}{2} \left(\frac{x-m}{s}\right)^2\right)$$

is one of the most widely used functions in science and engineering. The mean $m$ and standard deviation $s$ are real numbers, and $s$ must be greater than zero. Write a program for evaluating the Gaussian function when $m = 0$, $s = 2$, and $x = 1$.


```python
# Uncomment and complete the code below (don't change variable names)

# from math import pi, ...

# f_x =
```


```python
with pybryt.check(pybryt_reference(1, 5)):
    f_x
```


```python
import numbers
import numpy as np

assert isinstance(f_x, numbers.Real)

### BEGIN HIDDEN TESTS
assert np.isclose(f_x, 0.17603266338214976)
### END HIDDEN TESTS
```