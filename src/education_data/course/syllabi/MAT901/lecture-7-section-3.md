How we select our sample affects whether our results can be generalized to the population. There are several key sampling methods:

### 1. Simple Random Sampling

Every member of the population has an **equal chance** of being selected. No bias in selection.

**Example:** Assign a unique number to each member of the population and use a random number generator to pick your sample.

```python
import random

population = list(range(1, 101))  # population of size 100
sample_size = 10
sample = random.sample(population, sample_size)
print("Random sample:", sample)
```

### 2. Systematic Sampling

Every $k$-th member of the population is selected after a random start.

**Procedure:**
- Randomly select a starting point from the first $k$ members
- Select every $k$-th member thereafter

**Example:** If there are 1000 people and you want a sample of 100, select every 10th person.

### 3. Stratified Sampling

The population is divided into **strata** (subgroups) sharing a characteristic (e.g., age, gender), and random samples are taken from each subgroup.

- Ensures representation from each important subgroup

**Example:** Suppose a population is 60% women and 40% men. You divide the population accordingly, then sample proportionally from each.

### 4. Cluster Sampling

Population is divided into clusters (usually naturally occurring), some clusters are randomly selected, and **all members** of chosen clusters are sampled.

**Example:** Schools in a city are clusters; select 5 schools at random and survey all students in those schools.

### 5. Convenience Sampling (Not Recommended)

Samples are taken from a group that is easy to reach. This method is prone to bias.

**Example:** Standing outside the library and surveying passers-by.

---

### Properties of a "Good" Sample

- **Representative**: Accurately reflects the population.
- **Random**: Every member had a chance of being selected.
- **Free from bias**: No systematic tendency to over-represent or under-represent parts of the population.

---