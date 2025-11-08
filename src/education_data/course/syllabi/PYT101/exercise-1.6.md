Roots of a quadratic equation $ax^2 + bx + c = 0$ are:

$$x_1 = \frac{−b + \sqrt{b^2 −4ac}}{2a},$$
and
$$x_2 = \frac{−b − \sqrt{b^2 −4ac}}{2a}.$$

Uncomment and fix the errors in the following code.


```python
# from math import sqrt
#
# a = 2
# b = 1
# c = -2
#
# q = sqrt(b*b + 4*a*c)
# x1 = (-b + q)/2*a
# x2 = (-b - q)/2*a
```


```python
with pybryt.check(pybryt_reference(1, 6)):
    q, x1, x2
```


```python
import numbers
import numpy as np

assert isinstance(q, numbers.Real)
assert isinstance(x1, numbers.Real)
assert isinstance(x2, numbers.Real)

### BEGIN HIDDEN TESTS
assert np.isclose(q, 4.123105625617661)
assert np.isclose(x1, 0.7807764064044151)
assert np.isclose(x2, -1.2807764064044151)
### END HIDDEN TESTS
```