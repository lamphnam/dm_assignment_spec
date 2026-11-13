"""Data-side ablations on the same 15 folds: cleaning, iclp in training, leader-filled authors, conflicting duplicates."""
import csv, time
import numpy as np
import sweep1, sweep2
from sweep1 import evaluate
from src.data import ROOT, RAW, split_authors, title_key
from src.validation import folds as base_folds

tr = sweep1.tr
orig_title, orig_auth = tr["title"].copy(), tr["authors"].copy()
I_CFG = dict(te=1.0, char=1.0, bin_C=1.0)                       # TF-IDF model (no embeddings)
V_CFG = dict(te=1.0, char=1.0, bin_C=1.0, ew=2.0, knn=20, emb="v")  # exp003 config
sweep2.EMB["v"] = np.hstack([sweep2.EMB[k] for k in ("minilm", "mpnet", "specter")]) / np.sqrt(3)


def show(name, out, t0):
    r = evaluate(out)
    print(f"{name:42s} Score={r[0]:.4f}±{r[1]:.4f} Q={r[2]:.4f} R={r[3]:.4f}  ({time.time()-t0:.0f}s)", flush=True)


def with_fit_filter(keep_fn):
    def f(train, seed, n_splits=5):
        for a, v in base_folds(train, seed, n_splits):
            yield a[keep_fn(train.iloc[a])], v
    return f


# 1) cleaning: raw train text (no entity unescape / NFC), TF-IDF model only (embeddings were computed on clean text)
with open(RAW / "train.csv", encoding="utf-8", newline="") as fh:
    raw = {int(r[0]): r for r in list(csv.reader(fh))[1:]}
t0 = time.time(); show("I  TF-IDF, cleaned text", sweep2.run(I_CFG), t0)
tr["title"] = [raw[i][1] for i in tr["id"]]
tr["authors"] = [[a.strip() for a in raw[i][4].split(",") if a.strip()] for i in tr["id"]]
t0 = time.time(); show("I  TF-IDF, RAW text (no cleaning)", sweep2.run(I_CFG), t0)
tr["title"], tr["authors"] = orig_title, orig_auth

# baseline V
t0 = time.time(); show("V  exp003 (as is)", sweep2.run(V_CFG), t0)

# 2) drop iclp from the training folds
sweep2.folds = with_fit_filter(lambda d: (d["venue"] != "iclp").to_numpy())
t0 = time.time(); show("V  train WITHOUT iclp", sweep2.run(V_CFG), t0)

# 4) drop conflicting duplicate-title rows from training folds
keys = tr["title"].map(title_key)
conf = set(tr.index[keys.isin(tr.groupby(keys)["label"].nunique().loc[lambda s: s > 1].index)])
sweep2.folds = with_fit_filter(lambda d: ~d.index.isin(conf))
t0 = time.time(); show(f"V  drop conflicting duplicates ({len(conf)} rows)", sweep2.run(V_CFG), t0)
sweep2.folds = base_folds

# 3) leader-filled authors
lead = ROOT / "leader_csv_file" / "train.csv"
if lead.exists():
    with open(lead, encoding="utf-8", newline="") as fh:
        la = {int(r[0]): r[4] for r in list(csv.reader(fh))[1:]}
    tr["authors"] = [split_authors(la[i]) if not a else a for i, a in zip(tr["id"], orig_auth)]
    print("   empty authors now:", int((tr["authors"].str.len() == 0).sum()))
    t0 = time.time(); show("V  + leader-filled authors", sweep2.run(V_CFG), t0)
    tr["authors"] = orig_auth
