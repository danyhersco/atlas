The construction of a confidence interval depends on:
- The parameter being estimated (mean, proportion, etc.)
- The sample size ($n$)
- Whether the population standard deviation is known
- The desired level of confidence (e.g., 90%, 95%, 99%)

**Let’s start with the most common case:**

### Confidence Interval for the Mean ($\mu$), Population Standard Deviation Known

If the population standard deviation ($\sigma$) is known, and:
- The population is normal *or* $n$ is large ($n \geq 30$; by the Central Limit Theorem)

The confidence interval for the mean is:
$$
\bar{x} \pm z^* \frac{\sigma}{\sqrt{n}}
$$

- $\bar{x}$: sample mean
- $z^*$: critical value from the standard normal distribution for the desired confidence level
    - 90% CI: $z^* \approx 1.645$
    - 95% CI: $z^* \approx 1.96$
    - 99% CI: $z^* \approx 2.576$
- $\frac{\sigma}{\sqrt{n}}$: standard error of the mean

**Example:**
Suppose $\bar{x} = 80$, $\sigma = 10$, $n = 25$. Compute a 95% confidence interval for the mean.

Calculation:
- Standard error: $SE = \frac{10}{\sqrt{25}} = 2$
- Margin of error: $ME = 1.96 \times 2 = 3.92$
- Confidence interval: $80 \pm 3.92$ or $(76.08, 83.92)$

### Confidence Interval for the Mean ($\mu$), Population Standard Deviation Unknown

Usually, $\sigma$ is unknown and is estimated by the *sample standard deviation* $s$.

Then, we use the **$t$-distribution** with $n-1$ degrees of freedom:

$$
\bar{x} \pm t^* \frac{s}{\sqrt{n}}
$$

- $t^*$: critical value from the $t$-distribution for the desired confidence level and degrees of freedom $n-1$

**How to find $t^*$:** Use tables or statistical software (e.g., for $n=10$, df=9, 95% CI gives $t^* \approx 2.262$).

**Example:**
Sample of $n=16$, $\bar{x}=50$, $s=8$. Find 95% CI for the mean.

- Degrees of freedom: $15$
- $t^* \approx 2.131$ (from table)
- $SE = \frac{8}{4} = 2$
- $ME = 2.131 \times 2 = 4.262$
- Confidence interval: $50 \pm 4.262$ or $(45.738, 54.262)$

### Confidence Interval for a Proportion ($p$)

For a sample proportion $\hat{p}$ based on $n$ observations:

$$
\hat{p} \pm z^* \sqrt{\frac{\hat{p}(1-\hat{p})}{n}}
$$

- This formula is reliable when $n\hat{p} \geq 10$ and $n(1-\hat{p}) \geq 10$

**Example:**
In a survey of 200 people, 56 favored a new policy. Compute a 95% CI for the true proportion.

- $\hat{p} = \frac{56}{200} = 0.28$
- Standard error: $SE = \sqrt{\frac{0.28 \times 0.72}{200}} \approx 0.0312$
- Margin of error: $1.96 \times 0.0312 \approx 0.0611$
- Confidence interval: $0.28 \pm 0.0611$ or $(0.2189, 0.3411)$

---