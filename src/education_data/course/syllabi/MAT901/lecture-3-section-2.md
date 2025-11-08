Conditional probability gives us a way to extend the multiplication rule to any two events.

### The General Multiplication Rule

For any two events $A$ and $B$:
$$
P(A \cap B) = P(A\mid B)P(B)
$$
Alternatively:
$$
P(A \cap B) = P(B\mid A)P(A)
$$

#### Example

Suppose you roll two dice. Let:
- $A$: The first die shows a 3.
- $B$: The sum of the two dice is 5.

What is $P(A \cap B)$? 

First, $P(A) = 1/6$.

If the first die is 3, then the sum is 5 only if the second die is 2.

- $P(B \mid A) = P($Second die is 2$) = 1/6$
- $P(A \cap B) = P(B \mid A) \times P(A) = (1/6) \times (1/6) = 1/36$