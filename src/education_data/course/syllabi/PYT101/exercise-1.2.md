Here in the UK, we are famous for our love of performing mental arithmetic. That is why we still use both imperial and metric measurement systems - hours of fun entertainment for the family switching back and forth between the two.

Make a program where you set a length given in metres and then compute and write out the corresponding length measured in:
* inches (one inch is 2.54 cm)
* feet (one foot is 12 inches)
* yards (one yard is 3 feet)
* miles (one British mile is 1760 yards)

**Note**: In this course, we are using [pybryt](https://microsoft.github.io/pybryt/html/index.html) for automated assessment scoring. Therefore, while it is generally important to always carefully follow the instructions of a question, it is particularly important here so that *pybryt* can recognise the validity of your answer. In addition to PyBryt, after each exercise, there is a cell with `assert` statements for additional testing in case your solution is not covered with PyBryt references.

*Uncomment* and modify the relevant lines in the following code cell. The conversion to inches is done for you to illustrate what is required.


```python
metres = 640

# 1 inch = 2.54 cm. Remember to convert 2.54 cm to 0.0254 m here.
inches = metres / 0.0254

# Uncomment and complete the following code. Do not change variable names for testing.
# feet =

# yards =

# miles =
```


```python
with pybryt.check(pybryt_reference(1, 2)):
    feet, yards, miles
```


```python
import numbers
import numpy as np

assert all([isinstance(i, numbers.Real) for i in [feet, yards, miles]])

### BEGIN HIDDEN TESTS
assert np.isclose(feet, 2099.737532808399)
assert np.isclose(yards, 699.912510936133)
assert np.isclose(miles, 0.3976775630318938)
### END HIDDEN TESTS
```