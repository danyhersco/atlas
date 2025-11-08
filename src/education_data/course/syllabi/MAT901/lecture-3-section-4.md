Conditional probability allows us to update the likelihood of causes given observed evidence. This is the essence of **Bayes' Theorem.**

### Statement

Given events $A$ and $B$ with $P(B) > 0$,
$$
P(A\mid B) = \frac{P(B\mid A)P(A)}{P(B)}
$$

#### Where:
- $P(A)$: Prior probability of $A$
- $P(B\mid A)$: Likelihood of observing $B$ given $A$
- $P(B)$: Total probability of $B$
- $P(A\mid B)$: Posterior probability of $A$ given $B$

### Bayes' Theorem in Practice

Suppose a medical test is used to detect a rare disease. Let:
- $A$: Person has disease.
- $B$: Test is positive.

Suppose:
- 1% of people have the disease ($P(A) = 0.01$).
- Test correctly detects disease 99% of the time ($P(B\mid A) = 0.99$).
- Test gives a false positive 5% of the time ($P(B\mid A^c) = 0.05$, where $A^c$ is "no disease").

What is the probability a person actually has the disease if the test is positive ($P(A\mid B)$)?

Compute $P(B)$ using the law of total probability:

$$
P(B) = P(B\mid A)P(A) + P(B\mid A^c)P(A^c)\
= (0.99)(0.01) + (0.05)(0.99) = 0.0099 + 0.0495 = 0.0594
$$

Now,
$$
P(A\mid B) = \frac{0.99 \times 0.01}{0.0594} = \frac{0.0099}{0.0594} \approx 0.167
$$

Thus, even if you test positive, the probability you have the disease is only about 16.7%! This highlights the importance of considering the base rate of the disease.