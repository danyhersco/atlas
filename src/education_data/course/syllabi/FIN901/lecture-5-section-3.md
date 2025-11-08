Let’s break down the process with pseudocode for both simple and compound interest for those who wish to implement calculations in Excel, a financial calculator, or a programming language like Python.

### Simple Interest in Python

```python
P = 1000  # principal
r = 0.05  # annual rate
t = 3     # years

simple_interest = P * r * t
print("Simple interest earned:", simple_interest)
```

### Compound Interest in Python

```python
P = 1000  # principal
r = 0.05  # annual rate
n = 12    # times compounded per year
t = 3     # years

A = P * (1 + r/n) ** (n * t)
print("Final amount with compound interest:", A)
```

---