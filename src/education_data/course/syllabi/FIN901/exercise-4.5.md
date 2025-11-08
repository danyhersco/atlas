Write (or code) a function in Python that takes the following inputs:

- Emergency fund goal
- Number of months to achieve it

The function should output how much must be saved each month.

*Bonus: Modify your function to add an optional interest rate parameter and account for monthly savings growth.*

```python
def calculate_monthly_savings(goal_amount, months):
    return goal_amount / months

# Example usage:
monthly_needed = calculate_monthly_savings(1200, 12)
print(f"You need to save ${monthly_needed:.2f} each month.")
```

---