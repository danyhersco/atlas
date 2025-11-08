Here is a formula for the position of a ball, $y(t)$, in vertical motion, starting at ground level (i.e. at $y=0$) at time $t=0$:

$$ y(t) = v_{0}t- \frac{1}{2}gt^2, $$

where:

* $y(t)$ is the height (position) as a function of time $t$,
* $v_0$ is the initial velocity (at $t=0$), and
* $g$ is the acceleration due to gravity.

The computational task we want to solve is: given the values of $v_0$, $g$, and $t$, compute the height $y$. 

**How do we program this task?** A program is a sequence of instructions given to the computer. However, while a programming language is much **simpler** than a natural language, it is more **pedantic**. Programs must have correct syntax, i.e. correct use of the computer language grammar rules, and no misprints.

So let us execute a Python statement based on this example to evaluate $y(t) = v_0t- \frac{1}{2}gt^2$ for $v_0 = 5 \,\text{ms}^{-1}$, $g = 9.81 \,\text{ms}^{-2}$ and $t = 0.6 \,\text{s}$. If you were doing this on paper, you would probably write something like this: $$y = 5\cdot 0.6 - \frac{1}{2}\cdot 9.81 \cdot 0.6^2.$$ Happily, writing this in Python is very similar:


```python
# Comment: This is a 'code' cell within Jupyter notebook.
# Press Shift-Enter to execute the code within it,
# or click 'Run' in the Jupyter toolbar above.

print(5 * 0.6 - 0.5 * 9.81 * 0.6**2)
```

You probably noticed that, in the code cell we just wrote, the first few lines start with the hash (`#`) character. In Python, we use `#` to tell the Python interpreter to ignore everything that comes after `#`. We call those lines **comments**, and we write them to help us (humans) understand the code. Besides, we used `print` and we enclosed our calculation within parentheses to display the output. We will explain *comments* and *print function* in more detail later.