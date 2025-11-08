Not everything written in a computer program is intended for execution. In Python, anything on a line after the `#` character is ignored and is known as a **comment**. You can write whatever you want in a comment. Comments are intended to be used to explain what a snippet of code is intended for. It might, for example, explain the objective or provide a reference to the data or algorithm used. This is useful for you when you have to understand your code at some later stage, and indeed for whoever has to read and understand your code later.


```python
# Program for computing the height of a ball in vertical motion.
v0 = 5  # Set initial velocity in m/s.
g = 9.81  # Set acceleration due to gravity in m/s^2.
t = 0.6  # Time at which we want to know the height of the ball in seconds.
y = v0 * t - 0.5 * g * t**2  # Calculate the vertical position.
print(y)
```