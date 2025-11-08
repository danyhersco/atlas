Suppose we simulate flipping a fair coin 100 times and count how many times it lands heads up. This illustrates how probability predicts outcomes, and how statistics helps us summarize results.

```python
import random

heads = 0
n_flips = 100
for _ in range(n_flips):
    if random.choice(['H', 'T']) == 'H':
        heads += 1
print("Number of heads:", heads)
print("Proportion of heads:", heads / n_flips)
```

- Run this code several times. How does the proportion of heads compare to what you’d *expect*? Why does it vary?

---

**For Next Time:**  
Next lecture, we’ll delve deeper into the rules of probability and how to calculate probabilities for combined and conditional events. Please attempt all exercises before then and bring your questions to class!