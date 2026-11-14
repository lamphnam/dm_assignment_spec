"""How much would Semantic Scholar METADATA (citation count, publication type) add?  TRAIN-ONLY measurement for Q-07.

    .venv-gpu\\Scripts\\python.exe -m research.citation_signal_cv

Data: data/external/s2_train.jsonl (TRAIN papers only, fetched earlier by research/fetch_s2.py). Test papers have no
such data and must not get any while Q-07 is unanswered: this script only quantifies what asking would be worth.
Features added to exp003 (fold-train statistics only): log1p(citationCount), missing flag, log1p(citations) minus the
fold-train mean of the same publication year (citations grow with age), one-hot of S2 publicationTypes.
Variants: A' vs A, and EXP-004 with A' in place of A (paired, seed 0 then seeds 1-2).
Caveat for the report/Q-07: citation counts are measured AFTER publication (2026); if the labels were derived from
impact, this would be close to the target, so the lecturer must decide whether it is admissible.
"""
from __future__ import annotations

import json
import time

import numpy as np
import pandas as pd

from research.ens_compare import SEL_EXP004, compare, exp004, load_runs, mean_logit_pb, restrict
from research.finetune_cv import OUT
from scripts.finalize_from_oof import COMPONENTS, _load
from src.data import ROOT, load_all
from src.models import EmbedLogReg
from src.validation import SEEDS, folds, scored_mask

S2 = {r["id"]: r for r in map(json.loads, (ROOT / "data" / "external" / "s2_train.jsonl").read_text(encoding="utf-8").splitlines())}
TYPES = ["Conference", "JournalArticle", "Review", "Book", "Editorial"]


class CiteEmbedLogReg(EmbedLogReg):
    def _transform(self, df, fitting: bool):
        from scipy import sparse
        X = super()._transform(df, fitting)
        rec = [S2.get(int(i), {}) for i in df["id"]]
        c = np.array([r.get("citationCount") if r.get("citationCount") is not None else np.nan for r in rec], float)
        lc = np.log1p(c)
        miss = np.isnan(lc).astype(float)
        yr = df["year"].to_numpy()
        if fitting:
            s = pd.Series(lc).groupby(yr).mean()
            self.yr_mean_, self.all_mean_ = s.to_dict(), float(np.nanmean(lc))
        ym = np.array([self.yr_mean_.get(y, self.all_mean_) for y in yr], float)
        ym = np.where(np.isnan(ym), self.all_mean_, ym)
        lc0 = np.where(miss > 0, self.all_mean_, lc)
        types = np.array([[float(t in (r.get("publicationTypes") or [])) for t in TYPES] for r in rec])
        dense = np.column_stack([lc0, miss, lc0 - ym, types])
        if fitting:
            self.cmu_, self.csd_ = dense.mean(0), dense.std(0) + 1e-9
        return sparse.hstack([X, sparse.csr_matrix((dense - self.cmu_) / self.csd_)]).tocsr()


def oof() -> pd.DataFrame:
    tr, _ = load_all()
    parts = []
    for seed in SEEDS:
        for k, (ia, iv) in enumerate(folds(tr, seed)):
            path = OUT / f"oof_Acite_s{seed}_f{k}.pkl"
            if not path.exists():
                t0 = time.time()
                f, t = tr.iloc[ia], tr.iloc[iv]
                t = t[scored_mask(t)]
                eg, pb = CiteEmbedLogReg(seed=0).fit(f).predict(t)
                pd.DataFrame({"id": t["id"].to_numpy(), "eg": eg, "pb": pb}).to_pickle(path)
                print(f"A_cite seed {seed} fold {k}: {time.time() - t0:.1f}s", flush=True)
            d = pd.read_pickle(path); d["seed"] = seed; d["fold"] = k
            parts.append(d)
    return pd.concat(parts, ignore_index=True).set_index(["seed", "fold", "id"]).sort_index()


def main():
    A, E = exp004()
    Ac = oof().loc[E.index]
    sel = [load_runs(s, E.index).pb.to_numpy() for s in SEL_EXP004]
    egs = [_load(s).loc[E.index].eg.to_numpy() for s in COMPONENTS["ft_ens_v1"]["eg"]]
    c = E.copy()
    c["pb"] = mean_logit_pb([Ac.pb.to_numpy()] + sel)
    c["eg"] = np.mean([Ac.eg.to_numpy()] + egs, axis=0)
    a_only = A.copy(); a_only[["eg", "pb"]] = Ac[["eg", "pb"]].to_numpy()
    for part, seeds in (("seed0", [0]), ("seeds12", [1, 2]), ("15 folds", [0, 1, 2])):
        print(f"=== {part} ===")
        compare("A' (exp003 + S2 metadata) vs A", restrict(a_only, seeds), restrict(A, seeds))
        compare("EXP-004 with A' in place of A", restrict(c, seeds), restrict(E, seeds))


if __name__ == "__main__":
    from threadpoolctl import threadpool_limits

    with threadpool_limits(limits=1):
        main()
