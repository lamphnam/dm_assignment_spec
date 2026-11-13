"""Combine saved OOF predictions of several research/finetune_cv.py runs (no retraining).

    .venv-gpu\\Scripts\\python.exe -m research.finetune_combine finetune_minilm:CE finetune_mpnet_ce:CE ...
    .venv-gpu\\Scripts\\python.exe -m research.finetune_combine finetune_minilm+finetune_minilm_ce_s12:CE ...  (15 folds)

Each argument is <run name>[+<run name>...]:<variant>; the selection probability of a combo is
    pb = sigmoid( mean_k logit(pb_k) )   over A (exp003) and the listed variants (equal weights, nothing tuned),
and eg (ordering) is A's. Also prints paired per-fold differences against A, because fold-to-fold variation
(std ~0.008) is shared by A and the combo, so the paired difference is the meaningful noise scale.
Caveat: choosing the best of many combos on the same folds is optimistic -> confirm on other seeds.
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from research.abstract_cv import GRID, evaluate
from research.finetune_cv import OUT, logit
from src.metric import score_arrays


def _read(runs: str) -> pd.DataFrame:
    """'runA+runB' -> concatenated OOF of several runs (e.g. seed 0 run + seeds 1,2 run of the same config)."""
    return pd.concat([pd.read_pickle(OUT / f"{r}_oof.pkl") for r in runs.split("+")], ignore_index=True)


def load(spec: str) -> tuple[str, pd.DataFrame]:
    runs, var = spec.split(":")
    o = _read(runs)
    return spec, o[o.variant == var].set_index(["seed", "fold", "id"]).sort_index()


def combo(base: pd.DataFrame, parts: list[pd.DataFrame], with_a: bool = True) -> pd.DataFrame:
    L = [logit(p.loc[base.index, "pb"].to_numpy()) for p in parts]
    if with_a:
        L.append(logit(base["pb"].to_numpy()))
    out = base.copy()
    out["pb"] = 1 / (1 + np.exp(-np.mean(L, axis=0)))
    return out


def per_fold_scores(o: pd.DataFrame) -> np.ndarray:
    """Honest per-fold scores (threshold from the other folds of the same seed), in (seed, fold) order."""
    o = o.reset_index()
    res = []
    for s, gs in o.groupby("seed"):
        gf = dict(list(gs.groupby("fold")))

        def fs(g, t):
            return score_arrays(g.id, np.where(g.pb >= t, 1 + 9 * np.clip(g.eg, 0, 1), 0), g.label)[0]
        for k, g in gf.items():
            t = max(GRID, key=lambda t: np.mean([fs(gg, t) for kk, gg in gf.items() if kk != k]))
            res.append(fs(g, t))
    return np.array(res)


def report(name: str, o: pd.DataFrame, base_scores: np.ndarray) -> dict:
    sc = per_fold_scores(o)
    d = sc - base_scores
    r = {"auc": float(roc_auc_score(o.label > 1, o.pb)), "honest": float(sc.mean()),
         "delta": float(d.mean()), "delta_se": float(d.std(ddof=1) / np.sqrt(len(d))),
         "folds_better": int((d > 0).sum()), "n_folds": len(d)}
    print(f"{name:60s} AUC={r['auc']:.4f} honest={r['honest']:.4f} d={r['delta']:+.4f} (se {r['delta_se']:.4f}, "
          f"better in {r['folds_better']}/{r['n_folds']} folds)", flush=True)
    return r


def with_eg(o: pd.DataFrame, A: pd.DataFrame, egs: list[pd.DataFrame]) -> pd.DataFrame:
    """Ordering = mean of A's expected gain and the listed models' expected gains."""
    out = o.copy()
    out["eg"] = np.mean([A["eg"].to_numpy()] + [e.loc[A.index, "eg"].to_numpy() for e in egs], axis=0)
    return out


def main():
    eg_specs = [s[3:] for s in sys.argv[1:] if s.startswith("eg=")]
    outs = [s[4:] for s in sys.argv[1:] if s.startswith("out=")]
    specs = [s for s in sys.argv[1:] if not s.startswith(("eg=", "out="))]
    loaded = dict(load(s) for s in specs)
    egs = [load(s)[1] for s in eg_specs]
    base_run = specs[0].split(":")[0]
    o0 = _read(base_run)
    A = o0[o0.variant == "A"].set_index(["seed", "fold", "id"]).sort_index()
    for s, p in list(loaded.items()) + list(zip(eg_specs, egs)):
        assert p.index.equals(A.index), f"{s}: folds/ids differ from {base_run}"
    base_scores = per_fold_scores(A)
    print(f"{A.reset_index().groupby(['seed', 'fold']).ngroups} folds, seeds {sorted(A.reset_index().seed.unique().tolist())}")
    res = {"A": report("A (exp003)", A, base_scores)}
    for s, p in loaded.items():
        res[f"A+{s}"] = report(f"A+{s}", combo(A, [p]), base_scores)
    if len(loaded) > 1:
        res["A+all"] = report("A+all listed", combo(A, list(loaded.values())), base_scores)
        res["all (no A)"] = report("mean of listed (no A)", combo(A, list(loaded.values()), with_a=False), base_scores)
    if egs:
        res["A, eg avg"] = report("A selection, eg averaged (ordering only)", with_eg(A, A, egs), base_scores)
        res["A+all, eg avg"] = report("A+all listed, eg averaged", with_eg(combo(A, list(loaded.values())), A, egs), base_scores)
        res["all (no A), eg avg"] = report("mean of listed (no A), eg averaged",
                                           with_eg(combo(A, list(loaded.values()), with_a=False), A, egs), base_scores)
    out = OUT / f"finetune_combine_{outs[0] if outs else 'last'}.json"
    out.write_text(json.dumps({"specs": specs, "eg_specs": eg_specs, "results": res}, indent=2), encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
