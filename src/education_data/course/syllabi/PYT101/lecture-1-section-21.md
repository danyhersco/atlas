Suppose we want to make the following table of Celsius and Fahrenheit degrees:
```
 -20  -4.0
 -15   5.0
 -10  14.0
  -5  23.0
   0  32.0
   5  41.0
  10  50.0
  15  59.0
  20  68.0
  25  77.0
  30  86.0
  35  95.0
  40 104.0
```

How do we write a program that prints out such a table? We know that $F = \frac{9}{5}C + 32$, and a single line in this table is:


```python
C = -20
F = 9 / 5 * C + 32

print(C, F)
```

Now, we can just repeat these statements:


```python
C = -20
F = 9 / 5 * C + 32
print(C, F)
C = -15
F = 9 / 5 * C + 32
print(C, F)
C = -10
F = 9 / 5 * C + 32
print(C, F)
C = -5
F = 9 / 5 * C + 32
print(C, F)
C = 0
F = 9 / 5 * C + 32
print(C, F)
C = 5
F = 9 / 5 * C + 32
print(C, F)
C = 10
F = 9 / 5 * C + 32
print(C, F)
C = 15
F = 9 / 5 * C + 32
print(C, F)
C = 20
F = 9 / 5 * C + 32
print(C, F)
C = 25
F = 9 / 5 * C + 32
print(C, F)
C = 30
F = 9 / 5 * C + 32
print(C, F)
C = 35
F = 9 / 5 * C + 32
print(C, F)
C = 40
F = 9 / 5 * C + 32
print(C, F)
```

We can see that works but it is **very boring** to write and very easy to introduce a misprint.

**You really should not be doing boring repetitive tasks like this.** Spend your time instead looking for a smarter solution. When programming becomes boring, there is usually a construct that automates the writing. Computers are very good at performing repetitive tasks. For this purpose we use **loops**.