### One-sample Test

Used when you are comparing a single sample to a known value (e.g., population mean).

- **Example:** Is the mean weight of apples from an orchard different from 150 grams?

#### One-sample Z-test for the Mean

If the population variance is known and the sample is large:

$$
Z = \frac{\bar{x} - \mu_0}{\sigma / \sqrt{n}}
$$

Where:
- $\bar{x}$: sample mean
- $\mu_0$: hypothesized mean (from $H_0$)
- $\sigma$: population standard deviation
- $n$: sample size

#### One-sample t-test

If population variance is unknown:

$$
t = \frac{\bar{x} - \mu_0}{s / \sqrt{n}}
$$

Where $s$ is the sample standard deviation.

---

### Two-sample Test

Used when you compare two independent samples.

- **Example:** Is the average exam score different between two classes?

#### Two-sample t-test (Equal Variances Assumed)

$$
t = \frac{\bar{x}_1 - \bar{x}_2}{s_p \sqrt{\frac{1}{n_1} + \frac{1}{n_2}}}
$$

Where:
- $\bar{x}_1$, $\bar{x}_2$: sample means
- $n_1$, $n_2$: sample sizes
- $s_p$: pooled standard deviation:

$$
s_p = \sqrt{ \frac{ (n_1-1)s_1^2 + (n_2-1)s_2^2 }{n_1 + n_2 - 2} }
$$

**If variances are unequal, use Welch's t-test (adjusts for inequality).**

---