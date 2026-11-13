"""Run one experiment end to end (does NOT submit to Kaggle).

    .venv\\Scripts\\python.exe -m scripts.run_experiment --model logreg_text --name exp002_logreg_text

1. Load + verify data (src/data.py).
2. Cross-validate with the fixed protocol (src/validation.py); collect out-of-fold predictions per seed.
3. Choose the selection threshold on P(label>1) that maximises mean CV score (grid). Note: choosing it on the
   same folds makes the reported score slightly optimistic.
4. Fit on the full train, predict Test, write submissions/<name>.csv and outputs/<name>/report.json.
"""
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone

import numpy as np
import sklearn

from src.data import ROOT, load_all, sha256
from src.metric import score_arrays, to_priority
from src.models import MODELS
from src.validation import N_SPLITS, SEEDS, folds, scored_mask

THRESHOLDS = np.round(np.arange(0.0, 0.951, 0.05), 2)


def cross_validate(model_cls, train, seeds):
    """Return list of per-fold dicts holding OOF (expected_gain, p_worth) for the scored papers."""
    out = []
    for seed in seeds:
        for k, (tr, va) in enumerate(folds(train, seed)):
            m = model_cls(seed=seed)
            m.fit(train.iloc[tr])
            va_df = train.iloc[va]
            keep = scored_mask(va_df)
            eg, pw = m.predict(va_df[keep])
            out.append(dict(seed=seed, fold=k, ids=va_df["id"].to_numpy()[keep],
                            y=va_df["label"].to_numpy()[keep], eg=eg, pw=pw))
    return out


def _torch_env() -> dict:
    """torch version / device, only if the model imported torch (fine-tuned models)."""
    t = sys.modules.get("torch")
    if t is None:
        return {}
    return {"torch": t.__version__, "device": t.cuda.get_device_name(0) if t.cuda.is_available() else "cpu"}


def summarise(cv, threshold):
    s = np.array([score_arrays(f["ids"], to_priority(f["eg"], f["pw"], threshold), f["y"]) for f in cv])
    return {"score_mean": s[:, 0].mean(), "score_std": s[:, 0].std(ddof=1), "Q_mean": s[:, 1].mean(),
            "R_mean": s[:, 2].mean(), "n_folds": len(s), "fold_scores": s[:, 0].round(5).tolist()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=sorted(MODELS), required=True)
    ap.add_argument("--name", required=True, help="experiment id, e.g. exp002_logreg_text")
    ap.add_argument("--threshold", type=float, default=None, help="fix the selection threshold instead of tuning")
    a = ap.parse_args()

    train, test = load_all()
    model_cls = MODELS[a.model]
    cv = cross_validate(model_cls, train, SEEDS)

    grid = {float(t): summarise(cv, t) for t in THRESHOLDS}
    best_t = a.threshold if a.threshold is not None else max(grid, key=lambda t: grid[t]["score_mean"])
    best = summarise(cv, best_t)
    sel_all = grid[0.0]

    print(f"model={a.model}  folds={best['n_folds']} ({N_SPLITS}-fold x seeds {SEEDS}, scored on non-iclp)")
    print(f"{'threshold':>9} {'Score':>8} {'±std':>7} {'Q':>7} {'R':>7}")
    for t, r in grid.items():
        mark = "  <- chosen" if abs(t - best_t) < 1e-9 else ""
        print(f"{t:>9.2f} {r['score_mean']:8.4f} {r['score_std']:7.4f} {r['Q_mean']:7.4f} {r['R_mean']:7.4f}{mark}")

    model = model_cls(seed=0).fit(train)
    eg, pw = model.predict(test)
    priority = to_priority(eg, pw, best_t)

    sub_dir = ROOT / "submissions"; sub_dir.mkdir(exist_ok=True)
    out_dir = ROOT / "outputs" / a.name; out_dir.mkdir(parents=True, exist_ok=True)
    sub_path = sub_dir / f"{a.name}.csv"
    with open(sub_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("id,priority\n")
        for i, p in zip(test["id"], priority):
            fh.write(f"{i},{p:.6f}\n")

    report = {
        "name": a.name, "model": a.model, "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "protocol": {"n_splits": N_SPLITS, "seeds": list(SEEDS), "scored": "non-iclp papers of each fold",
                     "groups": "normalised title", "threshold_tuned_on_cv": a.threshold is None},
        "threshold": best_t, "cv_at_threshold": best, "cv_select_all": sel_all,
        "test": {"n_selected": int((priority > 0).sum()), "n_total": len(priority),
                 "selected_by_venue": test.loc[priority > 0, "venue"].value_counts().to_dict()},
        "submission": {"path": str(sub_path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(sub_path)},
        "env": {"python": platform.python_version(), "numpy": np.__version__, "sklearn": sklearn.__version__,
                **_torch_env()},
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"\nchosen threshold={best_t:.2f}  CV Score={best['score_mean']:.4f}±{best['score_std']:.4f} "
          f"(Q={best['Q_mean']:.4f}, R={best['R_mean']:.4f}); select-all CV Score={sel_all['score_mean']:.4f}")
    print(f"test: selected {report['test']['n_selected']}/596  by venue {report['test']['selected_by_venue']}")
    print(f"wrote {report['submission']['path']}  sha256={report['submission']['sha256'][:16]}...")
    rc = subprocess.call([sys.executable, "-I", str(ROOT / "tools" / "validate_submission.py"), str(sub_path),
                          "--test", str(ROOT / "data" / "raw" / "Test.csv")])
    return rc


if __name__ == "__main__":
    # Single-threaded BLAS: multi-threaded dense matmuls (kNN similarities) change float summation order with the
    # thread count, which made priorities differ by ~1e-5 between runs. One thread gives byte-identical CSVs.
    from threadpoolctl import threadpool_limits

    with threadpool_limits(limits=1):
        raise SystemExit(main())
