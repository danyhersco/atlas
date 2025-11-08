The **Normal distribution** (often called the "Gaussian" distribution) is by far the most important continuous probability distribution. It models numerous natural and social phenomena.

### Properties

- **Support**: $X \in (-\infty, \infty)$
- **Parameters**: $\mu$ = mean, $\sigma$ = standard deviation ($\sigma > 0$)

### Probability Density Function (PDF)

$$
f(x) = \frac{1}{\sigma \sqrt{2\pi}} \exp \left(-\frac{(x - \mu)^2}{2\sigma^2}\right)
$$

### Main Characteristics

- The graph is a symmetric bell-shaped curve centered at $\mu$.
- The **Standard Normal Distribution** is the case $\mu = 0, \sigma = 1$.

### Standardization ("Z-score")

To convert $X \sim N(\mu, \sigma^2)$ to a standard normal $Z$:
$$
Z = \frac{X - \mu}{\sigma}
$$

### Example

Heights of adult men in a city are normally distributed with mean $175$ cm and standard deviation $8$ cm.

Probability a randomly selected man is taller than 183 cm:

- $Z = (183 - 175)/8 = 1$
- Using normal tables or Python, $P(Z > 1) = 1 - P(Z \leq 1) \approx 0.1587$

### Python Example

```python
from scipy.stats import norm

mu = 175
sigma = 8
x = 183
prob = 1 - norm.cdf(x, mu, sigma)
print(f"Probability of height > 183 cm: {prob}")
```

---