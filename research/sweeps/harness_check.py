import numpy as np
from src.data import load_all
from src.validation import folds, scored_mask, SEEDS
from src.metric import score_arrays, to_priority

tr, te = load_all()
rng = np.random.default_rng(0)
res = {"oracle_drop1": [], "oracle_all": [], "random_all": []}
for s in SEEDS:
    for a, v in folds(tr, s):
        d = tr.iloc[v][scored_mask(tr.iloc[v])]
        y = d["label"].to_numpy(); g = (y - 1) / 4
        res["oracle_drop1"].append(score_arrays(d["id"], to_priority(g, (y > 1).astype(float), 0.5), y)[0])
        res["oracle_all"].append(score_arrays(d["id"], to_priority(g, np.ones(len(y)), 0.0), y)[0])
        res["random_all"].append(score_arrays(d["id"], to_priority(rng.random(len(y)), np.ones(len(y)), 0.0), y)[0])
for k, v in res.items():
    print(f"{k:13s} {np.mean(v):.4f} +- {np.std(v, ddof=1):.4f}")
print("scored fold size ~", len(d), "| worthwhile share non-iclp train:", round(float((tr[tr.venue != "iclp"].label > 1).mean()), 3),
      "| all train:", round(float((tr.label > 1).mean()), 3))
