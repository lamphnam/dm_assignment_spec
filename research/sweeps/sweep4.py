"""Sweep 4: larger embedding models, singly and combined (config V style: ew=2, knn, TE, char, bin head)."""
import sys, time
import numpy as np
from sweep1 import evaluate
from sweep2 import run, EMB, tr
from src.embeddings import title_embeddings

new = sys.argv[1:] or ["bge_large", "e5_large", "gte_large", "scincl"]
for k in new:
    EMB[k] = title_embeddings(tr, k)
base = dict(te=1.0, char=1.0, bin_C=1.0, ew=2.0, knn=20)


def combo(keys):
    return np.hstack([EMB[k] for k in keys]) / np.sqrt(len(keys))


cfgs = {k: dict(base, emb=k) for k in new}
for name, keys in {"old3": ["minilm", "mpnet", "specter"], "new": new,
                   "all": ["minilm", "mpnet", "specter"] + new}.items():
    EMB[name] = combo(keys); cfgs["combo_" + name] = dict(base, emb=name)
for name, cfg in cfgs.items():
    t0 = time.time(); r = evaluate(run(cfg))
    print(f"{name:16s} Score={r[0]:.4f}±{r[1]:.4f} Q={r[2]:.4f} R={r[3]:.4f} th={r[4]:.3f}  ({time.time()-t0:.0f}s)", flush=True)
