You were selected to be the next astronaut to go to Mars. Congratulations! 

Kepler's third law expresses the relationship between the distance of planets from the Sun, $a$, and their orbital periods, $P$:

$$ P^2 = \frac{4\pi^2}{G(M + m)}a^3  $$

where
* $P$ is the period (in seconds);
* $G$ is the gravitational constant ($G = 6.67 \cdot 10^{-11} \,\text{m}^3\text{kg}^{-1}\text{s}^{-2}$);
* $M$ is the mass of the Sun ($M = 2 \cdot 10^{30} \text{kg}$);
* $m$ is the mass of the planet (in kg);
* $a$ is the distance between the planet and the Sun (in m).

How many Earth birthdays will you celebrate during your 10-years Mars mission? Write a Python function `period` that calculates the period of a planet. Using `period` function, calculate the period of the Earth, `P_earth`, and the period of Mars, `P_mars`. Finally, calculate `birthdays` which is how many Earth years are equivalent to 10 years on Mars.

We know that:
* The average distance between the Earth and the Sun is $a = 1.5 \cdot 10^{11} \,\text{m}$;
* The average distance between Mars and the Sun is 0.5 larger than the Earth-Sun distance;
* The mass of the Earth is $m_1 = 6 \cdot 10^{24} \,\text{kg}$;
* Mars's mass is about 10% of the Earth's mass.

**Hint**: You do not need to do any unit conversion. 


```python
# Uncomment and complete this code - keep the names the same for testing purposes.

# from math import pi, sqrt

# def period(a, m_planet, m_sun=2e30, G=6.67e-11):
#    ...

# P_mars = ...

# P_earth = ...

# birthdays = ...
```


```python
with pybryt.check(pybryt_reference(1, 9)):
    period(a=1e11, m_planet=1e24), P_mars, P_earth, birthdays
```


```python
import numbers
import numpy as np

res = period(a=1, m_planet=1, m_sun=1, G=0.5)
assert isinstance(res, numbers.Real)
assert np.isclose(res, 2 * np.pi)

### BEGIN HIDDEN TESTS
assert callable(period)
assert np.isclose(P_earth, 31603718.929927427)
assert np.isclose(P_mars, 58059817.3950661)
assert np.isclose(birthdays, 18.3711978719333)
### END HIDDEN TESTS
```