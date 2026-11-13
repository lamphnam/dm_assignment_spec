"""Sweep 3: multi-embedding concat, C tuning, and probability-averaging ensembles."""
import sys, time
import numpy as np
from sweep1 import evaluate
import sweep2
from sweep2 import run, EMB, tr

EMB["all3"] = np.hstack([EMB["minilm"], EMB["mpnet"], EMB["specter"]]) / np.sqrt(3)
base = dict(te=1.0, char=1.0, bin_C=1.0, ew=1.0, knn=20)
CFGS = {
    "S all3+knn": dict(base, emb="all3"),
    "T all3+knn C=0.5": dict(base, emb="all3", C=0.5, bin_C=0.5),
    "U all3+knn C=2": dict(base, emb="all3", C=2, bin_C=2),
    "V all3 ew2": dict(base, emb="all3", ew=2.0),
}
cache = {}
for name, cfg in CFGS.items():
    t0 = time.time(); cache[name] = o = run(cfg); r = evaluate(o)
    print(f"{name:20s} Score={r[0]:.4f}±{r[1]:.4f} Q={r[2]:.4f} R={r[3]:.4f} th={r[4]:.3f}  ({time.time()-t0:.0f}s)", flush=True)

for k in ("mpnet", "specter", "minilm"):
    cache[k] = run(dict(base, emb=k))


def avg(names):
    outs = [cache[n] for n in names]
    return [(o[0][0], o[0][1], np.mean([x[2] for x in o], 0), np.mean([x[3] for x in o], 0)) for o in zip(*outs)]


for names in (["mpnet", "specter"], ["mpnet", "specter", "minilm"], ["mpnet", "specter", "minilm", "S all3+knn"]):
    r = evaluate(avg(names))
    print(f"ENS {'+'.join(n.split()[0] for n in names):24s} Score={r[0]:.4f}±{r[1]:.4f} Q={r[2]:.4f} R={r[3]:.4f} th={r[4]:.3f}")
