**Statement:**  
No matter the shape of the original population distribution, as the sample size $n$ **increases**, the sampling distribution of the sample mean $\bar{x}$ approaches a *normal distribution*, with mean $\mu$ and standard deviation $\sigma / \sqrt{n}$.

### Why Is This Amazing?

- It lets us use *normal probability* to make inferences about means, **even when the underlying population is not normal!**
- Often, $n \geq 30$ is "large enough" for the CLT to apply in practice.

### Visual Example

Suppose we have a population distribution that is skewed (not normal):

- Draw many samples of size $n=2$: Distribution of sample means is *less* skewed.
- Draw many samples of size $n=30$: Distribution of sample means is *almost normal*.

```python
import numpy as np
import matplotlib.pyplot as plt

# Skewed population
population = np.random.exponential(scale=2, size=100000)

# Draw many random samples, each of size 30, and compute sample means
sample_means = [np.mean(np.random.choice(population, size=30, replace=False)) for _ in range(5000)]

plt.hist(sample_means, bins=50, color="skyblue", edgecolor="k", density=True)
plt.title("Sampling distribution of the mean (n=30) from a skewed population")
plt.xlabel("Sample mean")
plt.ylabel("Density")
plt.show()
```

> This histogram will look almost normal, despite the population being skewed.

---