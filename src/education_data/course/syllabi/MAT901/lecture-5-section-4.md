The **Poisson distribution** models the number of times an event occurs in an interval of time or space, when these events occur with a known constant mean rate and independently of the time since the last event.

### Properties

- **Support**: $X = 0, 1, 2, ...$
- **Parameter**: $\lambda$ (lambda) = mean number of events per interval ($\lambda > 0$)

### Probability Mass Function (PMF)

$$
P(X = k) = \frac{e^{-\lambda} \lambda^k}{k!}, \text{ for } k = 0, 1, 2, ...
$$

### Mean and Variance

- **Mean**: $E[X] = \lambda$
- **Variance**: $Var(X) = \lambda$

### Example

If a website receives on average $\lambda = 2$ messages per minute, the probability of receiving exactly 3 messages in a minute:

$$
P(X = 3) = \frac{e^{-2} 2^3}{3!} \approx \frac{0.1353 \cdot 8}{6} \approx 0.180
$$

### Python Example

```python
from scipy.stats import poisson

lam = 2
k = 3
prob = poisson.pmf(k, lam)
print(f"Probability of exactly 3 messages: {prob}")
```

---