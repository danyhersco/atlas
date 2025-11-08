You just started University and moved away from home. You're trying to impress your new flatmates by cooking brunch. Write a Python script to help you cook the perfect egg! 

You know from A-levels that, when the temperature exceeds a critical point, the proteins in the egg first denature and then coagulate. The process becomes faster as the temperature increases. In the egg white, the proteins start to coagulate for temperatures above 63$^\circ$C, while in the yolk the proteins start to coagulate for temperatures above 70$^\circ$C. 

The time $t$ (in seconds) it takes for the centre of the yolk to reach the temperature $T_y$ (in degrees Celsius) can be expressed as: 

$$t = \frac{M^{2/3}c \rho^{1/3}}{K \pi^2 (4 \pi /3)^{2/3} } ln \left[0.76 \frac{T_0-T_w}{T_y-T_w}\right]$$

where:
* $M$ is the mass of the egg;
* $\rho$ is the density;
* $c$ is the specific heat capacity;
* $K$ is thermal conductivity;
* $T_w$ temperature of the boiling water (in $^\circ$C);
* $T_0$ is the initial temeprature of the egg (in $^\circ$C), before being put in the water.

Write a function that returns the time $t$ needed for the egg to cook, knowing that $T_w = 100^\circ\text{C}$, $M = 50\,\text{g}$, $\rho = 1.038\,\text{gcm}^{−3}$, $c = 3.7\,\text{Jg}^{−1}\text{K}^{−1}$, and $K = 5.4 \cdot 10^{−3}\,\text{Wcm}^{−1}\text{K}^{−1}$. Find $t$ for an egg taken from the fridge ($T_0 = 4^\circ\text{C}$) and for one at room temperature ($T_0 = 20^\circ\text{C}$). $T_y = 70^\circ\text{C}$ for a perfect soft-boiled egg.

**Hint**: You do not need to do any unit conversion. 


```python
# Uncomment and complete this code - keep the names the same for testing purposes.

# from math import pi

# def perfect_egg(T0, M=50, rho=1.038, Tw=100, c=3.7, K=5.4e-3, Ty=70):
#    ...
#    return t
```


```python
with pybryt.check(pybryt_reference(1, 8)):
    perfect_egg(T0=4, M=50, rho=1.038, Tw=100, c=3.7, K=5.4e-3, Ty=70)
    perfect_egg(T0=20, M=50, rho=1.038, Tw=100, c=3.7, K=5.4e-3, Ty=70)
```


```python
import numbers
import numpy as np

res1 = perfect_egg(T0=4, M=50, rho=1.038, Tw=100, c=3.7, K=5.4e-3, Ty=70)
res2 = perfect_egg(T0=20, M=50, rho=1.038, Tw=100, c=3.7, K=5.4e-3, Ty=70)
assert isinstance(res1, numbers.Real)
assert isinstance(res2, numbers.Real)

### BEGIN HIDDEN TESTS
assert callable(perfect_egg)
assert np.isclose(res1, 326.2798626986453)
assert np.isclose(res2, 259.3428560570137)
### END HIDDEN TESTS
```