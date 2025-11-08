### Definition

Two events $A$ and $B$ are called **independent** if knowing that one event occurs does **not** affect the probability of the other:

$$
P(A\mid B) = P(A)
$$

This also means:
$$
P(A \cap B) = P(A) \cdot P(B)
$$

### Examples

#### Example 1: Coin Toss

If you toss a fair coin twice:
- $A$: First toss is heads.
- $B$: Second toss is heads.

These are independent. Knowing the result of the first toss does *not* affect the probability of the second.

$P(A) = 1/2$, $P(B) = 1/2$, $P(A \cap B) = 1/4$.

Indeed, $P(A \cap B) = (1/2) \times (1/2) = 1/4$.

#### Example 2: Dependent Events

Suppose in a bag you have 2 red and 3 blue balls. You draw 2 balls one after another *without replacement*. Let:
- $A$: First ball is red.
- $B$: Second ball is red.

$A$ and $B$ are not independent:

- $P(A) = 2/5$
- If first ball is red (one less red in bag), remaining: 1 red and 3 blue. So $P(B\mid A) = 1/4$
- $P(A \cap B) = (2/5) \times (1/4) = 2/20 = 1/10$

But $P(B) = $ probability that the second ball is red without any knowledge of the first draw.

- Total possible pairs: $5 \times 4 = 20$.
- Ways both are red: $2 \times 1 = 2$.
- $P(B) = (2/20) + (3/20) = 5/20 = 1/4$ (as per the law of total probability).

So $P(B\mid A) = 1/4$ but $P(B) = 1/4$: Here, weirdly, they numerically match because of the drawn ball, but generally with more balls, $P(B\mid A)$ would not equal $P(B)$. Hence, most draws "without replacement" are **not independent**.