Let's put the computation into code! Suppose we have the test scenario from earlier:

- $P($disease$)=0.01$
- $P($positive$\mid$disease$)=0.99$
- $P($positive$\mid$no disease$)=0.05$

Here's how you'd compute $P($disease$\mid$positive$)$ in Python:

```python
p_disease = 0.01
p_no_disease = 1 - p_disease
p_pos_given_disease = 0.99
p_pos_given_no_disease = 0.05

p_pos = p_pos_given_disease * p_disease + p_pos_given_no_disease * p_no_disease
p_disease_given_pos = p_pos_given_disease * p_disease / p_pos

print(f"Probability of disease given positive test: {p_disease_given_pos:.3f}")
```

---