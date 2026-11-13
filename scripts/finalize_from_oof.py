"""Make a submission for a fine-tuned ensemble WITHOUT re-running its 15-fold CV (does NOT submit to Kaggle).

    .venv-gpu\\Scripts\\python.exe -m scripts.finalize_from_oof --model ft_ens_v1 --name exp004_ft_ens_v1 [--parity]

Why: the 15-fold CV of the ensemble's components already exists as research OOF files (research/finetune_cv.py runs,
same folds/protocol as src/validation.py). Re-running it in scripts/run_experiment.py would repeat ~150 fine-tunings.
Steps:
  1. Build the ensemble's 15-fold OOF from the research files listed in COMPONENTS (same combination rule as
     src/models.py::FineTuneEnsemble: selection = sigmoid(mean logit), ordering = mean E[gain]).
  2. Choose the threshold exactly like run_experiment.py (same grid, same summarise(): best mean over 15 folds),
     and report exp003 (A) under the identical procedure for comparison.
  3. --parity: fit the PRODUCTION model (src/models.py) on seed-0 fold-0 training papers and compare its
     validation AUC/score with the research OOF of that fold (checks src/finetune.py reproduces the research code).
  4. Fit the production model on the full train, predict Test, write submissions/<name>.csv + outputs/<name>/report.json,
     run tools/validate_submission.py.
"""
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import sklearn
from sklearn.metrics import roc_auc_score

from scripts.run_experiment import THRESHOLDS, _torch_env, summarise
from src.data import ROOT, load_all, sha256
from src.metric import score_arrays, to_priority
from src.models import MODELS, _logit
from src.validation import folds, scored_mask

RES = ROOT / "outputs" / "research"
# research runs (seed 0 run + seeds 1,2 run) per component, matching FineTuneEnsemble's components
COMPONENTS = {
    "ft_ens_v1": {
        "sel": ["finetune_minilm+finetune_minilm_s12:CE", "finetune_mpnet_ce+finetune_mpnet_s12:CE",
                "finetune_specter_ce+finetune_specter_s12:CE", "finetune_scincl_ce+finetune_scincl_s12:CE"],
        "eg": ["finetune_minilm_ce5+finetune_minilm_s12:CE5own", "finetune_mpnet_ce5+finetune_mpnet_s12:CE5own"],
    },
}
COMPONENTS["ft_ens_v1_bag2"] = {
    "sel": COMPONENTS["ft_ens_v1"]["sel"] + [f"finetune_{e}_bag1:CE" for e in ("minilm", "mpnet", "specter", "scincl")],
    "eg": COMPONENTS["ft_ens_v1"]["eg"],
}


def _load(spec: str) -> pd.DataFrame:
    runs, var = spec.split(":")
    o = pd.concat([pd.read_pickle(RES / f"{r}_oof.pkl") for r in runs.split("+")], ignore_index=True)
    return o[o.variant == var].set_index(["seed", "fold", "id"]).sort_index()


def ensemble_oof(model: str) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    c = COMPONENTS[model]
    first = c["sel"][0].split(":")[0]
    o = pd.concat([pd.read_pickle(RES / f"{r}_oof.pkl") for r in first.split("+")], ignore_index=True)
    A = o[o.variant == "A"].set_index(["seed", "fold", "id"]).sort_index()
    sel, egs = [_load(s) for s in c["sel"]], [_load(s) for s in c["eg"]]
    for p in sel + egs:
        assert p.index.equals(A.index)
    E = A.copy()
    E["pb"] = 1 / (1 + np.exp(-np.mean([_logit(A.pb.to_numpy())] + [_logit(p.pb.to_numpy()) for p in sel], axis=0)))
    E["eg"] = np.mean([A.eg.to_numpy()] + [p.eg.to_numpy() for p in egs], axis=0)
    files = sorted({f"{r}_oof.pkl" for s in c["sel"] + c["eg"] for r in s.split(":")[0].split("+")})
    return A, E, files


def as_cv(o: pd.DataFrame) -> list[dict]:
    """research OOF -> the per-fold dict format of run_experiment.cross_validate()."""
    out = []
    for (s, k), g in o.reset_index().groupby(["seed", "fold"]):
        out.append(dict(seed=s, fold=k, ids=g.id.to_numpy(), y=g.label.to_numpy(), eg=g.eg.to_numpy(), pw=g.pb.to_numpy()))
    return out


def best_threshold(cv) -> tuple[float, dict]:
    grid = {float(t): summarise(cv, t) for t in THRESHOLDS}
    t = max(grid, key=lambda t: grid[t]["score_mean"])
    return t, grid[t]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=sorted(COMPONENTS), required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--parity", action="store_true")
    ap.add_argument("--sub-dir", default="submissions", help="where the CSV goes (e.g. outputs/<x> for a reproducibility re-run)")
    a = ap.parse_args()

    train, test = load_all()
    A, E, files = ensemble_oof(a.model)
    tA, cvA = best_threshold(as_cv(A))
    tE, cvE = best_threshold(as_cv(E))
    print(f"exp003 (A), run_experiment procedure on research OOF: t={tA:.2f} CV={cvA['score_mean']:.4f}±{cvA['score_std']:.4f}")
    print(f"{a.model}: t={tE:.2f} CV={cvE['score_mean']:.4f}±{cvE['score_std']:.4f} (Q={cvE['Q_mean']:.4f}, R={cvE['R_mean']:.4f}) "
          f"delta={cvE['score_mean'] - cvA['score_mean']:+.4f}; AUC {roc_auc_score(A.label > 1, A.pb):.4f} -> "
          f"{roc_auc_score(E.label > 1, E.pb):.4f}", flush=True)

    parity = None
    if a.parity:
        tr_idx, va_idx = next(iter(folds(train, 0)))
        f, v = train.iloc[tr_idx], train.iloc[va_idx]
        v = v[scored_mask(v)]
        eg, pb = MODELS[a.model](seed=0).fit(f).predict(v)
        r = E.loc[(0, 0)].loc[v["id"].to_numpy()]
        parity = {"prod_auc": float(roc_auc_score(v.label > 1, pb)), "research_auc": float(roc_auc_score(r.label > 1, r.pb)),
                  "prod_score_t": float(score_arrays(v.id, to_priority(eg, pb, tE), v.label)[0]),
                  "research_score_t": float(score_arrays(r.index, to_priority(r.eg, r.pb, tE), r.label)[0]),
                  "pb_corr": float(np.corrcoef(pb, r.pb)[0, 1])}
        print("parity (seed 0, fold 0):", json.dumps({k: round(x, 4) for k, x in parity.items()}), flush=True)

    model = MODELS[a.model](seed=0).fit(train)
    eg, pb = model.predict(test)
    priority = to_priority(eg, pb, tE)
    sub_path = ROOT / a.sub_dir / f"{a.name}.csv"
    sub_path.parent.mkdir(parents=True, exist_ok=True)
    with open(sub_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("id,priority\n")
        for i, p in zip(test["id"], priority):
            fh.write(f"{i},{p:.6f}\n")
    out_dir = ROOT / "outputs" / a.name; out_dir.mkdir(parents=True, exist_ok=True)
    np.savez(out_dir / "test_predictions.npz", id=test["id"].to_numpy(), eg=eg, pb=pb)
    report = {
        "name": a.name, "model": a.model, "model_desc": model.name,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "protocol": {"n_splits": 5, "seeds": [0, 1, 2], "scored": "non-iclp papers of each fold", "groups": "normalised title",
                     "threshold_tuned_on_cv": True,
                     "cv_source": "research OOF (research/finetune_cv.py), combined as in FineTuneEnsemble", "oof_files": files},
        "threshold": tE, "cv_at_threshold": cvE, "exp003_same_procedure": {"threshold": tA, **cvA}, "parity_check": parity,
        "test": {"n_selected": int((priority > 0).sum()), "n_total": len(priority), "mean_pb": float(pb.mean()),
                 "selected_by_venue": test.loc[priority > 0, "venue"].value_counts().to_dict()},
        "submission": {"path": str(sub_path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(sub_path)},
        "env": {"python": platform.python_version(), "numpy": np.__version__, "sklearn": sklearn.__version__, **_torch_env()},
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"test: selected {report['test']['n_selected']}/596 by venue {report['test']['selected_by_venue']}; mean pb {pb.mean():.3f}")
    print(f"wrote {report['submission']['path']} sha256={report['submission']['sha256'][:16]}...")
    return subprocess.call([sys.executable, "-I", str(ROOT / "tools" / "validate_submission.py"), str(sub_path),
                            "--test", str(ROOT / "data" / "raw" / "Test.csv")])


if __name__ == "__main__":
    # same as run_experiment.py: single-threaded BLAS so the exp003 component is byte-reproducible
    from threadpoolctl import threadpool_limits

    with threadpool_limits(limits=1):
        raise SystemExit(main())
