What if we need to compute $\sin x$, $\cos x$, $\ln x$, $e^x$ etc., in a program? Such functions are available in Python's `math` module. In fact, there is a vast universe of functionality for Python available in modules. We just `import` in whatever we need for the task at hand.

In this example, we compute $\sqrt{2}$ using the `sqrt` function from the `math` module:


```python
import math

# Since we imported library (import math),
# we access the sqrt function using math.sqrt.
r = math.sqrt(2)
print(r)
```

or:


```python
from math import sqrt

# This time, we did not import the entire library -
# we imported only sqrt function.
# Therefore, we can use it directly.
r = sqrt(2)
print(r)
```

Let us now have a look at a more complicated expression, such as

$$\sin x \cos x + 4\ln x$$


```python
from math import sin, cos, log

x = 1.2
print(sin(x) * cos(x) + 4 * log(x))  # log is ln (base e)
```