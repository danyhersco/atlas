Consider the random mathematical expression:

$$ \frac{5}{9} + \frac{3a^4}{2} $$

implemented in Python as `5/9 + 3 * a**4 / 2`. The rules for evaluating the expression are the same as in mathematics: proceed term by term (additions/subtractions) from the left, compute powers first, then multiplication and division. Therefore in this example the order of evaluation will be:

1. `r1 = 5/9`
2. `r2 = a**4`
3. `r3 = 3*r2`
4. `r4 = r3/2`
5. `r5 = r1 + r4`

We use parenthesis to override these default rules. Indeed, many programmers use parenthesis for greater clarity.