Let $p$ be a bank's annual interest rate in per cent. After $n$ years, an initial amount $A_0$ has then grown to

$$A_n = A_0\left(1+\frac{p}{100}\right)^n.$$

Write a program for computing how much money 1000 euros have grown to after three years with a 5% annual interest rate.


```python
# Uncomment and complete the code below (and, as always, don't change variable names)

# p = ...
# A_0 = ...

# A_n = ...

# print(f"The amount of money in the account after {n:d} years is {A_n:.2f} euros")
```


```python
with pybryt.check(pybryt_reference(1, 4)):
    p, A_0, n, A_n
```


```python
import numbers
import numpy as np

assert isinstance(A_n, numbers.Real)

### BEGIN HIDDEN TESTS
assert np.isclose(A_n, 1157.6250000000002)
### END HIDDEN TESTS
```