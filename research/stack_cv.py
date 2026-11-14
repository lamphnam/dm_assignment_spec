"""Score-plan P1 (2026-11-14, session 2): stacking/calibration of the selection components (P1a) and an ordering that
uses the ensemble's P(y>1) (P1b), on saved 15-fold research OOF. No encoder is retrained.

    .venv-gpu\\Scripts\\python.exe -m research.stack_cv

Inputs per (seed, fold, id), all out-of-fold (models trained on the fold's training papers only):
  A        exp003: binary-head P(y>1) and multinomial distribution (pm = P(y>1) of the multinomial head, recomputed
           here by refitting EmbedLogReg on the same folds -> outputs/research/oof_A5_s{seed}_f{k}.pkl; CPU, sklearn)
  CE x4    fine-tuned binary encoders of EXP-004 (MiniLM, MPNet, SPECTER, SciNCL)
  CE5 x2   fine-tuned 5-class encoders of EXP-004 (MiniLM, MPNet): P(y>1) and E[gain]

Pre-declared variants (fixed before looking at results; screened on seed 0, confirmed on seeds 1-2):
  selection (P1a), stacker fitted NESTED: for (seed s, fold k) a logistic regression is fitted on the OOF rows of the
  other 4 folds of seed s and applied to fold k (stacking on OOF predictions; a handful of weights)
    ST1  LR on the 5 logits (A + 4 CE)
    ST2  ST1 + logits of the 2 CE5 P(y>1)
    ST3  ST1 + venue one-hot (venue-specific intercepts = calibration per venue)
  ordering (P1b): E[gain] = P(y>1) * E[gain | y>1], with E_k[gain | y>1] = eg_k / P_k(y>1) of each 5-class model
    O1   pb_sel * mean(E_A[g|y>1], E_CE5mini[g|y>1], E_CE5mpnet[g|y>1])
    O2   pb_sel * E_A[g|y>1]                       (the score-plan's literal formula)
  where pb_sel is EXP-004's pb (ordering-only change) or the stacker's pb (combined).
Comparison: research/ens_compare.py::compare, paired with EXP-004 on the same folds.
"""
from __future__ import annotations

import json
import time

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from research.ens_compare import SEL_EXP004, compare, exp004, load_runs, restrict
from research.finetune_cv import OUT, logit
from src.data import load_all
from src.models import GAIN, EmbedLogReg
from src.validation import SEEDS, folds, scored_mask

EG5 = ["finetune_minilm_ce5+finetune_minilm_s12:CE5own", "finetune_mpnet_ce5+finetune_mpnet_s12:CE5own"]


def a5_oof() -> pd.DataFrame:
    """exp003's multinomial distribution per OOF row (cached per fold)."""
    tr, _ = load_all()
    parts = []
    for seed in SEEDS:
        for k, (ia, iv) in enumerate(folds(tr, seed)):
            path = OUT / f"oof_A5_s{seed}_f{k}.pkl"
            if not path.exists():
                t0 = time.time()
                f, t = tr.iloc[ia], tr.iloc[iv]
                t = t[scored_mask(t)]
                m = EmbedLogReg(seed=0).fit(f)
                P = m.multi_.predict_proba(m._transform(t, fitting=False))
                full = np.zeros((len(t), 5))
                for j, c in enumerate(m.multi_.classes_):
                    full[:, c - 1] = P[:, j]
                pb = m.bin_.predict_proba(m._transform(t, fitting=False))[:, 1]
                d = pd.DataFrame(full, columns=[f"p{c}" for c in range(1, 6)])
                d.insert(0, "id", t["id"].to_numpy()); d["eg"] = full @ GAIN; d["pb"] = pb
                d.to_pickle(path)
                print(f"A5 seed {seed} fold {k}: {time.time() - t0:.1f}s", flush=True)
            d = pd.read_pickle(path); d["seed"] = seed; d["fold"] = k
            parts.append(d)
    return pd.concat(parts, ignore_index=True).set_index(["seed", "fold", "id"]).sort_index()


def nested_stack(X: np.ndarray, y: np.ndarray, sf: pd.DataFrame, C: float = 1.0) -> tuple[np.ndarray, list]:
    """Out-of-fold stacker predictions: for each (seed, fold) fit on the other folds of the same seed."""
    out, coefs = np.zeros(len(y)), []
    for (s, k), _ in sf.groupby(["seed", "fold"]):
        te = ((sf.seed == s) & (sf.fold == k)).to_numpy()
        trn = ((sf.seed == s) & (sf.fold != k)).to_numpy()
        lr = LogisticRegression(C=C, max_iter=2000).fit(X[trn], y[trn])
        out[te] = lr.predict_proba(X[te])[:, 1]
        coefs.append(np.r_[lr.intercept_, lr.coef_.ravel()])
    return out, coefs


def main():
    A, E = exp004()
    idx = E.index
    sel = [load_runs(s, idx) for s in SEL_EXP004]
    eg5 = [load_runs(s, idx) for s in EG5]
    A5 = a5_oof().loc[idx]
    print(f"A5 vs cached A: max|d eg| {np.abs(A5.eg - A.eg).max():.2e}, max|d pb| {np.abs(A5.pb - A.pb).max():.2e}")
    y = (E.label > 1).to_numpy().astype(int)
    sf = idx.to_frame(index=False)[["seed", "fold"]]
    L = np.column_stack([logit(A.pb.to_numpy())] + [logit(p.pb.to_numpy()) for p in sel])
    L5 = np.column_stack([logit(p.pb.to_numpy()) for p in eg5])
    venues = pd.get_dummies(E.venue).to_numpy(float)

    # conditional gain given y>1 of each 5-class model (eg = P(y>1) * E[g | y>1] since gain(label 1) = 0)
    pmA = 1 - A5.p1.to_numpy()
    cA = A.eg.to_numpy() / np.clip(pmA, 1e-6, None)
    c5 = [p.eg.to_numpy() / np.clip(p.pb.to_numpy(), 1e-6, None) for p in eg5]
    c_mean = np.mean([cA] + c5, axis=0)

    pbs = {"E4": E.pb.to_numpy()}
    coefs = {}
    for name, X in {"ST1": L, "ST2": np.hstack([L, L5]), "ST3": np.hstack([L, venues])}.items():
        pbs[name], coefs[name] = nested_stack(X, y, sf)

    cands = {}
    for name in ("ST1", "ST2", "ST3"):
        c = E.copy(); c["pb"] = pbs[name]; cands[f"{name} (EXP-004 ordering)"] = c
    for sel_name in ("E4", "ST1", "ST2", "ST3"):
        for oname, cg in (("O1", c_mean), ("O2", cA)):
            c = E.copy(); c["pb"] = pbs[sel_name]; c["eg"] = pbs[sel_name] * cg
            cands[f"{oname} ordering, selection {sel_name}"] = c

    res = {}
    for part, seeds in (("seed0 (screening)", [0]), ("seeds12 (confirmation)", [1, 2]), ("15 folds", [0, 1, 2])):
        print(f"\n=== {part} ===")
        base = restrict(E, seeds)
        res[part] = {n: compare(n, restrict(c, seeds), base) for n, c in cands.items()}
    cal = {n: {"mean_pb": float(p.mean()), "rate": float(y.mean())} for n, p in pbs.items()}
    print("\ncalibration (mean pb vs positive rate):", json.dumps({n: round(v["mean_pb"], 4) for n, v in cal.items()}),
          f"rate {y.mean():.4f}")
    cnames = {"ST1": ["b", "A", "minilm", "mpnet", "specter", "scincl"]}
    cnames["ST2"] = cnames["ST1"] + ["ce5_minilm", "ce5_mpnet"]
    cnames["ST3"] = cnames["ST1"] + list(pd.get_dummies(E.venue).columns)
    cm = {n: dict(zip(cnames[n], np.mean(v, axis=0).round(3).tolist())) for n, v in coefs.items()}
    print("mean stacker coefficients:", json.dumps(cm))
    (OUT / "stack_cv.json").write_text(json.dumps({"results": res, "calibration": cal, "coef_mean": cm}, indent=2),
                                       encoding="utf-8")
    print("wrote", OUT / "stack_cv.json")


if __name__ == "__main__":
    from threadpoolctl import threadpool_limits

    with threadpool_limits(limits=1):  # same as run_experiment: exp003 refits byte-reproducible
        main()
