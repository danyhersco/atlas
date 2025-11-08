The drag force, due to air resistance, on an object can be expressed as
$$F_d = \frac{1}{2}C_D\rho Av^2$$
where:
* $\rho$ is the density of the air,
* $v$ is the velocity of the object,
* $A$ is the cross-sectional area (perpendicular to the velocity direction),
* and $C_D$ is the drag coefficient, which depends on the shape of the object and the roughness of the surface.

**Complete and fix** the following code that computes the drag force.


```python
density = 1.2  # units of kg/m^3
ball_radius = 0.11  # units of m
C_D = 0.2  # drag coefficient

v = 50.8  # m/s (fastest recorded speed of football)

# Uncomment, fix, and complete the following lines.
# A = pi*ball_radius  # cross sectional area of a sphere
# F_d =

# Challenge yourself to use the formatted print statement
# shown above to write out the force with one decimal in
# units of Newton (1 N = 1 kgm/s^2).
```


```python
with pybryt.check(pybryt_reference(1, 3)):
    A, F_d
```


```python
import numbers
import numpy as np

assert isinstance(F_d, numbers.Real)

### BEGIN HIDDEN TESTS
assert isinstance(A, numbers.Real)
assert np.isclose(F_d, 11.771828154393067)
assert np.isclose(A, 0.0380132711084365)
### END HIDDEN TESTS
```