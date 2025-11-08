The built-in Python function [sum](https://docs.python.org/3/library/functions.html#sum) takes a list as an argument and computes the sum of the elements in the list:
```python
>> sum([1, 3, 5, -5])
4
```
Implement your own version of the sum function and name it `my_sum`.


```python
# Uncomment and complete this code - keep the names the same for testing purposes.

# def my_sum(x):
#     ...
```


```python
with pybryt.check(pybryt_reference(1, 15)):
    my_sum([2.1, 98, -451, 273, 1111, 23.98])
```


```python
import numbers
import numpy as np

res = my_sum([-1, 1, 2, 3, 0.1])
assert isinstance(res, numbers.Real)
assert np.isclose(res, 5.1)

### BEGIN HIDDEN TESTS
assert callable(my_sum)
assert np.isclose(my_sum([]), 0)
assert np.isclose(my_sum(range(1, 101)), (100 * 101) / 2)
### END HIDDEN TESTS
```