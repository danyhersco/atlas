The **Bernoulli distribution** is the simplest discrete probability distribution, modeling a single experiment (trial) that results in just one of two possible outcomes, commonly termed as "success" (1) and "failure" (0).

### Properties

- **Support**: $X \in \{0, 1\}$
- **Parameter**: $p$ = probability of success ($0 \leq p \leq 1$)

### Probability Mass Function (PMF)

$$
P(X = x) = p^x (1 - p)^{1 - x} \quad \text{for} \quad x \in \{0, 1\}
$$

### Mean and Variance

- **Mean** (Expected value): $E[X] = p$
- **Variance**: $Var(X) = p(1 - p)$

### Example

Suppose you toss a fair coin ($p = 0.5$) and define $X = 1$ if heads, $X = 0$ if tails.

- $P(X = 1) = 0.5$
- $P(X = 0) = 0.5$
- $E[X] = 0.5$
- $Var(X) = 0.25$

---