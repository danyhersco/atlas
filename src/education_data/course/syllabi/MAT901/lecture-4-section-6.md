The **Cumulative Distribution Function (CDF)** gives the probability that a random variable is less than or equal to a certain value.

- **Discrete random variable:** $F(x) = P(X \le x) = \sum_{t \le x} p(t)$
- **Continuous random variable:** $F(y) = P(Y \le y) = \int_{-\infty}^{y} f(t) dt$

#### Properties of a CDF

1. $0 \le F(x) \le 1$
2. $F$ is non-decreasing
3. $\lim_{x \to -\infty} F(x) = 0$, $\lim_{x \to \infty} F(x) = 1$

### Example: Die Roll (Discrete)

$$
F(3) = P(X \le 3) = p(1) + p(2) + p(3) = \frac{1}{6} + \frac{1}{6} + \frac{1}{6} = 0.5
$$

### Example: Uniform(0,1) (Continuous)

$$
F(y) = 
\begin{cases}
0 & \text{if } y < 0 \
y & \text{if } 0 \le y \le 1 \
1 & \text{if } y > 1
\end{cases}
$$

---