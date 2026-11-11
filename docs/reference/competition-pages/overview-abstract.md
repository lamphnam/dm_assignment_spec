Your task is to build a method that recommends what researchers should read next by assigning a priority to every paper in the test collection.

A successful reading order should:

- Bring relevant papers forward: papers with higher reading relevance should appear earlier.

- Provide broad coverage: as researchers continue reading, the list should represent different parts of the collection rather than repeatedly presenting similar content.

You will receive 2,494 training papers with existing ratings from 1 to 5, where higher ratings indicate higher reading priority. You will also receive 596 test papers whose ratings are hidden. Available metadata includes the paper’s title, venue, publication year, authors, and DOI.

Submit a CSV containing the columns id,priority, with exactly one row for each test paper. Higher priority values mean earlier reading. You may use any finite numeric scale; evaluation uses the resulting order without converting your scores into predicted 1–5 labels.

The competition score combines relevance and coverage, with coverage measured through title similarity across all reading-list lengths. The Public and Private leaderboards each evaluate 298 hidden test papers independently. Final competition ranking uses the Private leaderboard.

Your solution must use at least one substantive approach taught in class: classification, regression, clustering, or itemset-based recommendation. Additional techniques are welcome when justified.

Teams may contain up to five members. Alongside your predictions, submit a report and GitHub repository explaining your data analysis, insights, solution design, evaluation, and how to reproduce your submission. Consult the Evaluation and Rules pages for the complete metric and grading requirements. 

For more details, please read the evaluation section and Rules page.
