Instead of using an exact formula for converting Fahrenheit ($F$) to Celsius ($C$) degrees:

$$C = \frac{5}{9}(F - 32),$$

many people use an approximate formula for quicker conversion:

$$C \approx \hat{C} = \frac{F − 30}{2}.$$

Write a Python function `conversion_table` using a `while` loop that prints the conversion table consisting of three columns: $F$, $C$, and the approximate value $\hat{C}$, for $F = 0, 10, 20, \ldots, 100$. Besides, using the same while loop, count the number of rows printed and return the count. Ensure that all numbers in the conversion table are printed with two decimal places.


```python
# Uncomment and complete the code below. Do not change the names of variables.

# def conversion_table():
#     ...
```


```python
with pybryt.check(pybryt_reference(1, 12)):
    conversion_table()
```


```python
import numbers
import numpy as np

res = conversion_table()
assert isinstance(res, numbers.Real)
assert np.isclose(res, 11)

### BEGIN HIDDEN TESTS
assert callable(conversion_table)
### END HIDDEN TESTS
```