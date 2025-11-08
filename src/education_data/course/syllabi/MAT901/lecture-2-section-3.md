Probability assigns a numerical measure (from 0 to 1) to the likelihood of an event $E$ occurring. We denote this as $P(E)$.

### *Definition of Probability (for Equally Likely Outcomes)*

If all outcomes in a sample space are equally likely,

$$
P(E) = \frac{\text{Number of favorable outcomes to } E}{\text{Total number of possible outcomes}}
$$

#### Example:

If you roll a fair 6-sided die, what is the probability of rolling a number less than 5?

- Favorable outcomes: $\{1, 2, 3, 4\}$ (4 outcomes)
- Total outcomes: 6

So,

$$
P(\text{less than 5}) = \frac{4}{6} = \frac{2}{3}
$$

---

### The Addition Rule

#### For Mutually Exclusive Events:

If $A$ and $B$ are mutually exclusive (cannot happen together), then

$$
P(A \cup B) = P(A) + P(B)
$$

Example: Rolling a die, event $A =$ rolling a 2, event $B =$ rolling a 5.

- $P(A) = 1/6$
- $P(B) = 1/6$
- Since $A$ and $B$ can't happen together: $P(A \cup B) = 1/6 + 1/6 = 1/3$

#### For Non-Mutually Exclusive Events:

$$
P(A \cup B) = P(A) + P(B) - P(A \cap B)
$$

$A \cap B$ is the event "both A and B occur."

*Example*: Drawing a card from a deck. Let $A =$ event "drawing a heart," $B =$ event "drawing a king."

- Number of hearts: 13, so $P(A) = 13/52$
- Number of kings: 4, so $P(B) = 4/52$
- Number of kings of hearts: 1, so $P(A \cap B) = 1/52$

$$
P(A \cup B) = \frac{13}{52} + \frac{4}{52} - \frac{1}{52} = \frac{16}{52} = \frac{4}{13}
$$

---

### The Multiplication Rule

#### For Independent Events:

If $A$ and $B$ are independent, then

$$
P(A \cap B) = P(A) \times P(B)
$$

*Example:* Tossing two coins, what is the probability both show heads?

$$
P(\text{first coin heads}) = 1/2 \
P(\text{second coin heads}) = 1/2 \
P(\text{both heads}) = 1/2 \times 1/2 = 1/4
$$

#### For Dependent Events:

If occurrence of $A$ affects $B$, then

$$
P(A \cap B) = P(A) \times P(B|A)
$$

where $P(B|A)$ is the probability of $B$ given $A$ has occurred.

*Example:* Drawing two cards from a deck without replacement. What is the probability both are aces?

- Probability first card is an ace: $4/52$
- Probability second card is an ace, given first was: $3/51$
- Therefore: $P(\text{2 aces}) = 4/52 \times 3/51 = 1/221$

---