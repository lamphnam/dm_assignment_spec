## What to submit

Submit a CSV containing exactly the columns `id,priority`, with one row for each of the **596 test papers**:

```csv
id,priority
1488,9.25
2524,0
2344,7.12
997,8.50
```

These rows illustrate the format; your submission must include **every test ID exactly once**. Each priority must be a **finite, nonnegative number**:

- **Priority 0:** do not recommend the paper.
- **Positive priority:** recommend the paper; higher values mean earlier reading.

You may use any nonnegative numeric scale; **[0, 10] is recommended**. Submitted priorities determine selection and reading order. They are **not converted into predicted ratings 1–5**.

In this example, papers 1488, 997, and 2344 are recommended in that order if they belong to the same evaluation split. Paper 2524 is excluded.

## Competition evaluation

Submissions are evaluated using the **harmonic mean of relevance and coverage**. Scores range from **0 to 1**, and **higher is better**.

The hidden ground-truth ratings represent reading preferences: **rating 1 means “do not read,”** while ratings **2–5 indicate increasing reading priority**.

### Selection and reading order

The test papers are divided into a hidden **Public set of 298 papers** and a hidden **Private set of 298 papers**. Students do not need to know which papers belong to each set.

Within each set, the evaluator:

1. Excludes papers with priority 0.
2. Sorts the remaining papers by descending priority.
3. Resolves tied priorities by ascending paper ID, treated as text.
4. Assigns reading positions starting at 1 and calculates relevance and coverage.

There is **no fixed shortlist cutoff**: every positive-priority paper is included in the recommended list for its split.

### Relevance

Relevance measures the **usefulness of the recommended papers, with greater weight given to earlier positions**.

For a recommended paper at position \(r\), let \(y_r\) be its hidden true rating. Define its usefulness gain and position weight as:

\[
g_r=\frac{y_r-1}{4},
\qquad
w_r=\frac{1}{\log_2(r+1)}.
\]

The gains for ratings 1, 2, 3, 4, and 5 are respectively **0, 0.25, 0.50, 0.75, and 1**.

For \(m\) recommended papers, relevance is:

\[
Q=\frac{\sum_{r=1}^{m}w_rg_r}
{\sum_{r=1}^{m}w_r}.
\]

This means:

- Placing a higher-rated paper before a lower-rated paper improves relevance.
- A recommended rating-1 paper contributes zero gain but still contributes its position weight to the denominator.
- Swapping papers with equal true ratings does not change relevance.
- An empty recommendation list has relevance 0.

**Relevance measures both usefulness and reading order; it is not normalized against an ideal ground-truth ranking.** A perfectly ordered list containing ratings below 5 can therefore have relevance below 1.

### Coverage

Coverage measures **recall of worthwhile papers**, where worthwhile means a true rating of **2–5**:

\[
R=
\frac{\text{Number of recommended papers with true rating greater than 1}}
{\text{Total number of papers with true rating greater than 1 in the evaluated split}}.
\]

Worthwhile papers assigned priority 0 remain in the denominator. Recommending a rating-1 paper adds no coverage. Reordering the same selected papers does not change coverage.

If a split contains no worthwhile papers, coverage is defined as 0. Coverage uses paper IDs and hidden ratings; **title similarity is not part of the metric**.

### Final score

The final score combines relevance \(Q\) and coverage \(R\) with equal importance using their harmonic mean:

\[
\boxed{\text{Score}=\frac{2QR}{Q+R}}.
\]

If either component is zero, the final score is defined as 0.

For example, relevance of 0.80 and coverage of 0.60 produce:

\[
\text{Score}
=\frac{2(0.80)(0.60)}{0.80+0.60}
\approx 0.685714.
\]

This encourages useful, well-prioritized recommendations while recovering a substantial proportion of worthwhile papers.

### Public and Private leaderboards

The Public leaderboard provides feedback during the competition. **Final competition ranking uses the Private leaderboard.** Public and Private scores are calculated independently and are not averaged for the final ranking.

Course assignment grading, including the report grade, is calculated separately.