Below is a Python function to compute the CPI given two years of price data and fixed quantities for a basket of goods. Complete the function so that it works for any lists of prices and quantities.

```python
def calculate_cpi(prices_base, prices_current, quantities):
    """
    prices_base: list of prices in base year
    prices_current: list of prices in current year
    quantities: list of quantities for each good
    Returns: CPI (current year, base year = 100)
    """
    # Calculate total cost in base year
    cost_base = sum(p * q for p, q in zip(prices_base, quantities))
    # Calculate total cost in current year
    cost_current = sum(p * q for p, q in zip(prices_current, quantities))
    # Compute CPI
    cpi = (cost_current / cost_base) * 100
    return cpi

# Test with sample data: base prices = [2,3,1.5], current prices = [2.2,3.6,1.65], quantities = [10, 5, 4]
```
- Compute and print the CPI using the example from Exercise 3.1. 

---

End of Lecture 3.