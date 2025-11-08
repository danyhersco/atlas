In the last lecture, we discussed fundamental probability rules and the idea of events. Today, we will extend these concepts by introducing *conditional probability* and examine how the probability of an event may change when we know that another event has occurred.

### What is Conditional Probability?

**Conditional probability** is the probability of event $A$ occurring given that event $B$ has occurred. It is denoted by $P(A\mid B)$, read as "the probability of $A$ given $B$.”

#### Mathematical Definition

Suppose $A$ and $B$ are two events, and $P(B) > 0$. The conditional probability of $A$ given $B$ is:
$$
P(A\mid B) = \frac{P(A \cap B)}{P(B)}
$$
where $P(A \cap B)$ is the probability that both $A$ and $B$ happen.

#### Example

Suppose we have a standard deck of 52 cards. Let:
- $A$ = event that a randomly drawn card is a king,
- $B$ = event that the card is a face card (jack, queen, or king).

- $P(A) = \frac{4}{52} = \frac{1}{13}$
- $P(B) = \frac{12}{52} = \frac{3}{13}$
- $P(A \cap B) = P(\text{card is a king}) = \frac{4}{52}$ (since all kings are face cards)

So,
$$
P(A \mid B) = \frac{P(A \cap B)}{P(B)} = \frac{4/52}{12/52} = \frac{4}{12} = \frac{1}{3}
$$
Thus, if you know you've drawn a face card, the probability it's a king is 1/3.

### Properties of Conditional Probability

- $P(A\mid B)$ is only defined if $P(B) > 0$.
- $P(A\mid B)$ may not equal $P(A)$; the knowledge that $B$ has occurred may affect the probability of $A$.