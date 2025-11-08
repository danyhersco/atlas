This is very important:

- A 95% confidence interval generated from a sample does **not** mean there is a 95% probability that the population parameter is in the interval. 
- Instead, **if we repeated the study many times**, approximately 95% of the calculated intervals would contain the true parameter.

**Common Errors:**
- Don’t say "There’s a 95% chance that μ is between X and Y." Once the interval is computed, μ is fixed; the interval either contains μ or it does not.

---

**Effect of Confidence Level and Sample Size:**
- Higher confidence $\rightarrow$ wider interval (more certainty demands a larger margin)
- Larger sample size $\rightarrow$ narrower interval (more precision)

**Visual Example (in Python):**

Suppose we want to visualize intervals for repeated samples:

```python
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(0)
population_mean = 100
population_sd = 15
n = 25
num_intervals = 30
intervals = []

for _ in range(num_intervals):
    sample = np.random.normal(population_mean, population_sd, n)
    mean_sample = np.mean(sample)
    se = population_sd / np.sqrt(n)
    conf_int = (mean_sample - 1.96 * se, mean_sample + 1.96 * se)
    intervals.append(conf_int)

plt.hlines(range(num_intervals), [l for l, u in intervals], [u for l, u in intervals])
plt.vlines(population_mean, -1, num_intervals, color='red', linestyles='dashed')
plt.xlabel('Mean')
plt.ylabel('Sample')
plt.title('Confidence Intervals for Multiple Samples')
plt.show()
```

---