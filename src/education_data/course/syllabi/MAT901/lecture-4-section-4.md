A **Probability Mass Function (PMF)** describes the probability distribution of a discrete random variable.

- **Definition:** $p(x) = P(X = x)$ for all $x$ in the possible values of $X$.

#### Properties of a PMF

1. $p(x) \ge 0$ for all $x$
2. $\sum_x p(x) = 1$

### Example: Rolling a Fair Die

Let $X$ be the number rolled.

$$
p(x) = \begin{cases}
1/6 & \text{if } x = 1,2,3,4,5,6 \
0 & \text{otherwise}
\end{cases}
$$

### Visualizing a PMF

```python
import matplotlib.pyplot as plt

x_vals = [1, 2, 3, 4, 5, 6]
pmf = [1/6] * 6

plt.stem(x_vals, pmf, use_line_collection=True)
plt.xlabel('Value of X')
plt.ylabel('Probability')
plt.title('PMF of a Fair Six-Sided Die')
plt.show()
```

---