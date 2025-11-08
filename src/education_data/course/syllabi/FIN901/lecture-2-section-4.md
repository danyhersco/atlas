Let’s introduce two essential tools for tracking and planning your finances: the income statement and the budget.

### Income Statement

An income statement, also known as a profit and loss statement, summarizes income and expenses over a particular period (monthly, quarterly, yearly), allowing you to see if you are operating at a surplus or a deficit.

**Basic Structure:**

| Item        | Amount    |
| ----------- | --------- |
| Income      | $3,500    |
| Expenses    | $2,900    |
| ------------|-----------|
| Net Income  | $600      |

- **Formula:**  
  Net Income = Total Income - Total Expenses

#### Example

Suppose in April you earned:

- Salary: $2,800
- Freelance Work: $700

Total Income = $3,500

Your expenses:

- Rent: $1,200
- Utilities: $200
- Food: $500
- Transportation: $300
- Entertainment: $200
- Miscellaneous: $500

Total Expenses = $2,900

Net Income = $3,500 - $2,900 = $600

### Budget

A budget is a projection of your expected income and expenses for a future period. It is essential for planning and controlling spending.

**Steps to Create a Simple Budget:**

1. List all expected sources of income.
2. List all anticipated expenses (divide into "needs" and "wants" if possible).
3. Assign an amount to each item.
4. Calculate the difference to see if you expect a surplus or need to adjust spending.

**Sample Budget Table:**

| Category     | Budgeted Amount |
| ------------ | -------------- |
| Income       | $3,000         |
| Expenses     |                |
|   Rent       | $1,000         |
|   Food       | $400           |
|   Transport  | $200           |
|   Savings    | $200           |
|   Other      | $600           |
| Total Expenses | $2,400       |
| ------------ | -------------- |
| Surplus      | $600           |

#### Code Example: Simple Budget Calculation (Python)

```python
income = 3000
expenses = {
    "rent": 1000,
    "food": 400,
    "transport": 200,
    "savings": 200,
    "other": 600,
}
total_expenses = sum(expenses.values())
surplus = income - total_expenses
print("Surplus:", surplus)
```

---