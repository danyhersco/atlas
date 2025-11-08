Statistics becomes much clearer with effective visualizations. Two common methods: **histograms** and **boxplots**.

### Histograms

A **histogram** shows the distribution of a quantitative variable by grouping data into bins and plotting the frequency of each bin.

**Example (Python):**
```python
import matplotlib.pyplot as plt

data = [2, 4, 4, 5, 6, 6, 6, 7, 8, 10]
plt.hist(data, bins=5, edgecolor='black')
plt.title('Histogram Example')
plt.xlabel('Value')
plt.ylabel('Frequency')
plt.show()
```

**Interpretation:**  
Histograms reveal the shape of the distribution (e.g., skewed, symmetric, multimodal).

### Boxplots

A **boxplot** (or box-and-whisker plot) summarizes:

- Minimum
- First Quartile (Q1, 25th percentile)
- Median
- Third Quartile (Q3, 75th percentile)
- Maximum

Boxplots are effective for visualizing spread and detecting outliers.

**Example (Python):**
```python
plt.boxplot(data, vert=False)
plt.title('Boxplot Example')
plt.xlabel('Value')
plt.show()
```

**Interpretation:**  
- The box shows the IQR.
- The line inside the box is the median.
- Whiskers extend to min and max (excluding outliers).

---