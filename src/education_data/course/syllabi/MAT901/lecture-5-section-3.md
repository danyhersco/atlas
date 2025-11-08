A **Binomial distribution** generalizes the Bernoulli by modeling the number of successes in a fixed number $n$ of independent Bernoulli trials, each with probability $p$ of success.

### Properties

- **Support**: $X \in \{0, 1, 2, ..., n\}$
- **Parameters**: $n$ = number of trials, $p$ = probability of success in each trial

### Probability Mass Function (PMF)

$$
P(X = k) = {n \choose k} p^k (1 - p)^{n - k}
$$

where ${n \choose k}$ is the binomial coefficient:
$$
{n \choose k} = \frac{n!}{k! (n - k)!}
$$

### Mean and Variance

- **Mean**: $E[X] = np$
- **Variance**: $Var(X) = np(1 - p)$

### Example

Tossing a fair coin 5 times, probability of getting exactly 3 heads:
- $n = 5, p = 0.5, k = 3$
- $P(X = 3) = {5 \choose 3} (0.5)^3 (0.5)^2 = 10 \cdot 0.125 \cdot 0.25 = 0.3125$

### Python Example

```python
from scipy.stats import binom

n = 5
p = 0.5
k = 3
prob = binom.pmf(k, n, p)
print(f"Probability of exactly 3 heads: {prob}")
```

---