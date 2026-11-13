"""Hypothesis (from analysis A6): topic preferences differ by venue (cav likes neural/ML, lics likes probabilistic/graph and
dislikes quantum/homotopy). A single linear model on embeddings cannot express venue-specific topic weights.
Test: add embedding x venue interaction block (one copy of the embedding per venue, zeros elsewhere).

    .venv\\Scripts\\python.exe -m research.venue_interaction_cv

Seed-0 folds of the fixed protocol, honest threshold (chosen on the other 4 folds). Same evaluation as abstract_cv.py.
"""
from __future__ import annotations

import json

import numpy as np
from scipy import sparse

from research.abstract_cv import evaluate, oof
from src.data import ROOT, VENUES, load_all
from src.models import EmbedLogReg


class VenueInteractionLogReg(EmbedLogReg):
    def __init__(self, iw: float = 1.0, **kw):
        super().__init__(**kw)
        self.iw = iw

    def _transform(self, df, fitting: bool):
        X = super()._transform(df, fitting)
        E = self._emb(df)
        blocks = [sparse.csr_matrix(self.iw * E * (df["venue"].to_numpy() == v)[:, None]) for v in VENUES]
        return sparse.hstack([X] + blocks).tocsr()


def main():
    tr, _ = load_all()
    res = {"A exp003": evaluate(oof(tr, lambda: EmbedLogReg(seed=0)))}
    print("A done", flush=True)
    for iw in (1.0, 2.0):
        res[f"D exp003 + emb x venue (w={iw})"] = evaluate(oof(tr, lambda iw=iw: VenueInteractionLogReg(iw=iw, seed=0)))
        print(f"D w={iw} done", flush=True)
    for name, r in res.items():
        print(f"{name:34s} honest={r['honest']:.4f}±{r['honest_std']:.4f} Q={r['Q']:.4f} R={r['R']:.4f} fixed0.55={r['fixed055']:.4f} AUC={r['auc']:.4f}")
    (ROOT / "outputs" / "research" / "venue_interaction_cv.json").write_text(json.dumps(res, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
