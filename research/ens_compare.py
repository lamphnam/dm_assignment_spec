"""Paired comparison of candidate ensembles against EXP-004 (`ft_ens_v1`) on saved research OOF (no retraining).

    .venv-gpu\\Scripts\\python.exe -m research.ens_compare add=finetune_e5_base_ce:CE [add=...] [seeds=0] [out=NAME]

Candidate built by the CLI: EXP-004 with extra CE components in the selection average, i.e.
    pb = sigmoid(mean logit over A + the 4 EXP-004 CE encoders + the added runs)   (equal weights, nothing tuned)
    eg = EXP-004's ordering (mean E[gain] of A, CE5 MiniLM, CE5 MPNet).
Other scripts (research/stack_cv.py) import compare() for their own candidates.

Two numbers per candidate, both PAIRED with EXP-004 on the same (seed, fold):
  honest   threshold chosen on the other folds of the same seed (research protocol, grid 0.30-0.80 step 0.025)
  run_exp  the procedure that produced EXP-004's reported CV 0.6302: one threshold for all 15 folds, grid 0.05
           (only when all 15 folds are present)
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from research.finetune_combine import per_fold_scores
from research.finetune_cv import OUT, logit
from scripts.finalize_from_oof import _load, as_cv, best_threshold, ensemble_oof

SEL_EXP004 = ["finetune_minilm+finetune_minilm_s12:CE", "finetune_mpnet_ce+finetune_mpnet_s12:CE",
              "finetune_specter_ce+finetune_specter_s12:CE", "finetune_scincl_ce+finetune_scincl_s12:CE"]


def exp004() -> tuple[pd.DataFrame, pd.DataFrame]:
    """(A = exp003 OOF, E = EXP-004 OOF), 15 folds, index (seed, fold, id)."""
    A, E, _ = ensemble_oof("ft_ens_v1")
    return A, E


def restrict(o: pd.DataFrame, seeds) -> pd.DataFrame:
    return o[o.index.get_level_values("seed").isin(list(seeds))]


def load_runs(spec: str, index: pd.Index) -> pd.DataFrame:
    """'runA+runB:VARIANT' restricted/aligned to `index` (which may cover fewer seeds than the run)."""
    p = _load(spec)
    missing = index.difference(p.index)
    assert len(missing) == 0, f"{spec}: {len(missing)} (seed, fold, id) rows missing"
    return p.loc[index]


def mean_logit_pb(parts: list[np.ndarray]) -> np.ndarray:
    return 1 / (1 + np.exp(-np.mean([logit(p) for p in parts], axis=0)))


def compare(name: str, cand: pd.DataFrame, base: pd.DataFrame, verbose: bool = True) -> dict:
    """Paired comparison of cand vs base (same index; columns label, eg, pb)."""
    cand = cand.loc[base.index]
    sc, sb = per_fold_scores(cand), per_fold_scores(base)
    d = sc - sb
    seeds = base.reset_index()[["seed", "fold"]].drop_duplicates().seed.to_numpy()
    r = {"auc": float(roc_auc_score(cand.label > 1, cand.pb)), "auc_base": float(roc_auc_score(base.label > 1, base.pb)),
         "honest": float(sc.mean()), "honest_base": float(sb.mean()), "delta": float(d.mean()),
         "delta_se": float(d.std(ddof=1) / np.sqrt(len(d))), "folds_better": int((d > 0).sum()), "n_folds": len(d),
         "delta_by_seed": {int(s): round(float(d[seeds == s].mean()), 5) for s in np.unique(seeds)},
         "mean_pb": float(cand.pb.mean())}
    if len(d) == 15:
        tc, cc = best_threshold(as_cv(cand))
        tb, cb = best_threshold(as_cv(base))
        r.update(run_exp=float(cc["score_mean"]), run_exp_std=float(cc["score_std"]), run_exp_t=tc,
                 run_exp_Q=float(cc["Q_mean"]), run_exp_R=float(cc["R_mean"]),
                 run_exp_base=float(cb["score_mean"]), run_exp_delta=float(cc["score_mean"] - cb["score_mean"]))
    if verbose:
        s = (f"{name:44s} AUC {r['auc']:.4f} (base {r['auc_base']:.4f})  honest {r['honest']:.4f} "
             f"d={r['delta']:+.4f} (se {r['delta_se']:.4f}, {r['folds_better']}/{r['n_folds']}) by seed {r['delta_by_seed']}")
        if "run_exp" in r:
            s += f"  | run_exp {r['run_exp']:.4f}±{r['run_exp_std']:.4f} t={r['run_exp_t']:.2f} d={r['run_exp_delta']:+.4f}"
        print(s, flush=True)
    return r


def main():
    swaps = [s[5:] for s in sys.argv[1:] if s.startswith("swap=")]  # swap=<i>/<spec>: replace EXP-004 CE component i
    if swaps:
        return main_swap(swaps)
    adds = [s[4:] for s in sys.argv[1:] if s.startswith("add=")]
    seeds = [int(x) for s in sys.argv[1:] if s.startswith("seeds=") for x in s[6:].split(",")] or [0, 1, 2]
    outs = [s[4:] for s in sys.argv[1:] if s.startswith("out=")]
    A, E = exp004()
    A, E = restrict(A, seeds), restrict(E, seeds)
    sel = [load_runs(s, E.index) for s in SEL_EXP004]
    new = {s: load_runs(s, E.index) for s in adds}
    base_parts = [A.pb.to_numpy()] + [p.pb.to_numpy() for p in sel]
    print(f"seeds {seeds}: {E.reset_index()[['seed', 'fold']].drop_duplicates().shape[0]} folds; base = EXP-004 (ft_ens_v1)")
    res = {"EXP-004": compare("EXP-004 (itself)", E, E)}
    for s, p in new.items():  # each added alone
        c = E.copy(); c["pb"] = mean_logit_pb(base_parts + [p.pb.to_numpy()])
        res[f"+{s}"] = compare(f"EXP-004 + {s}", c, E)
    if len(new) > 1:
        c = E.copy(); c["pb"] = mean_logit_pb(base_parts + [p.pb.to_numpy() for p in new.values()])
        res["+all"] = compare("EXP-004 + all added", c, E)
    if outs:
        path = OUT / f"ens_compare_{outs[0]}.json"
        path.write_text(json.dumps({"adds": adds, "seeds": seeds, "results": res}, indent=2), encoding="utf-8")
        print("wrote", path)


def main_swap(swaps: list[str]):
    """Each swap 'i/spec' separately: EXP-004 with its i-th CE component (0 MiniLM, 1 MPNet, 2 SPECTER, 3 SciNCL)
    replaced by `spec` (a variant of the same encoder, e.g. another input text), and with `spec` added instead."""
    seeds = [int(x) for s in sys.argv[1:] if s.startswith("seeds=") for x in s[6:].split(",")] or [0, 1, 2]
    A, E = exp004()
    A, E = restrict(A, seeds), restrict(E, seeds)
    sel = [load_runs(s, E.index).pb.to_numpy() for s in SEL_EXP004]
    print(f"seeds {seeds}; base = EXP-004 (ft_ens_v1)")
    for sw in swaps:
        i, spec = sw.split("/", 1)
        p = load_runs(spec, E.index).pb.to_numpy()
        parts = [A.pb.to_numpy()] + sel
        c = E.copy(); c["pb"] = mean_logit_pb(parts[:int(i) + 1] + [p] + parts[int(i) + 2:])
        compare(f"EXP-004, CE#{i} -> {spec}", c, E)
        c = E.copy(); c["pb"] = mean_logit_pb(parts + [p])
        compare(f"EXP-004 + {spec}", c, E)


if __name__ == "__main__":
    main()
