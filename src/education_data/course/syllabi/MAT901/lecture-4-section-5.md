A **Probability Density Function (PDF)** describes the probability distribution of a continuous random variable.

- The PDF itself is not a probability; instead, the area under the curve over an interval gives the probability that the variable falls within that interval.

#### Properties of a PDF

1. $f(y) \ge 0$ for all $y$
2. $\int_{-\infty}^{\infty} f(y) dy = 1$

### Example: Uniform Distribution on $[0,1]$

$$
f(y) = \begin{cases}
1 & \text{if } 0 \le y \le 1 \
0 & \text{otherwise}
\end{cases}
$$

To find the probability that $Y$ falls between $0.2$ and $0.5$:

$$
P(0.2 \le Y \le 0.5) = \int_{0.2}^{0.5} 1 dy = 0.3
$$

### Plotting a PDF Example

```python
import numpy as np
import matplotlib.pyplot as plt

y = np.linspace(0, 1, 100)
f = np.ones_like(y)

plt.plot(y, f, label='PDF')
plt.fill_between(y, f, alpha=0.3)
plt.xlabel('Value of Y')
plt.ylabel('Density')
plt.title('Uniform(0,1) PDF')
plt.ylim(0, 1.2)
plt.show()
```

---