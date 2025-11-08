Dispersion describes how spread out the data is. Two important measures are **variance** and **standard deviation**.

### Variance

Variance measures the average squared deviation from the mean:
$$
\text{Sample Variance (} s^2 \text{)} = \frac{1}{n-1} \sum_{i=1}^n (x_i - \bar{x})^2
$$

**Example:**
For [2, 4, 6]:
- Mean: $\bar{x} = 4$
- Variance: $((2-4)^2 + (4-4)^2 + (6-4)^2)/2 = (4 + 0 + 4)/2 = 4$

### Standard Deviation

The standard deviation is the square root of the variance:
$$
s = \sqrt{s^2}
$$

In the example above: $s = \sqrt{4} = 2$

### Range and Interquartile Range

- **Range:** Maximum value minus minimum value.
- **Interquartile Range (IQR):** Difference between the 75th and 25th percentile (Q3 - Q1).

#### Example Calculation

Data: [2, 4, 6, 8, 10]
- Range: 10 - 2 = 8
- For quartiles: Q1 = 4, Q3 = 8, so IQR = 8 - 4 = 4

---