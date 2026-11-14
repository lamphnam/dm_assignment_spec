"""Is the `doi` field's SOURCE / PUBLISHER SERIES a useful feature?  (never used as a feature before 2026-11-14)

    .venv-gpu\\Scripts\\python.exe -m research.doi_feature_cv

`doi` holds a DOI (10.x), a Semantic Scholar URL or another URL (docs/06). The DOI registrant prefix + the leading
letters of the suffix identify the publisher/series (e.g. 10.4204/eptcs = EPTCS workshop volumes, 10.24963/kr = KR
proceedings, 10.1109/lics = IEEE LICS). Feature: one-hot of that series (categories seen >= 5 times in the fold's
training papers; others ignored). Numbers inside the suffix (paper position in a volume) are NOT used: that is close
to the id/position artefact of Q-10.

One pre-declared variant: A' = exp003 + the one-hot, replacing A inside EXP-004 (selection logit average and ordering).
Paired with EXP-004 on the same folds (research/ens_compare.py); seed 0 and seeds 1-2 reported separately.
"""
from __future__ import annotations

import re
import time

import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder

from research.ens_compare import SEL_EXP004, compare, exp004, load_runs, mean_logit_pb, restrict
from research.finetune_cv import OUT
from scripts.finalize_from_oof import COMPONENTS, _load
from src.data import load_all
from src.models import EmbedLogReg
from src.validation import SEEDS, folds, scored_mask


def doi_series(s: str) -> str:
    if s.startswith("10."):
        pre, _, suf = s.partition("/")
        head = re.split(r"[./_\-;()]", suf)[0]
        return pre + "/" + re.sub(r"\d", "", head).lower()[:20]
    if "semanticscholar.org" in s:
        return "s2_url"
    return "ceur" if "ceur-ws" in s else "other_url"


class DoiEmbedLogReg(EmbedLogReg):
    def _transform(self, df, fitting: bool):
        from scipy import sparse
        X = super()._transform(df, fitting)
        ser = df[["doi"]].map(doi_series) if hasattr(df, "map") else df[["doi"]].applymap(doi_series)
        if fitting:
            self.doi_ = OneHotEncoder(handle_unknown="ignore", min_frequency=5).fit(ser)
        return sparse.hstack([X, self.doi_.transform(ser)]).tocsr()


def a_doi_oof() -> pd.DataFrame:
    tr, _ = load_all()
    parts = []
    for seed in SEEDS:
        for k, (ia, iv) in enumerate(folds(tr, seed)):
            path = OUT / f"oof_Adoi_s{seed}_f{k}.pkl"
            if not path.exists():
                t0 = time.time()
                f, t = tr.iloc[ia], tr.iloc[iv]
                t = t[scored_mask(t)]
                eg, pb = DoiEmbedLogReg(seed=0).fit(f).predict(t)
                pd.DataFrame({"id": t["id"].to_numpy(), "eg": eg, "pb": pb}).to_pickle(path)
                print(f"A_doi seed {seed} fold {k}: {time.time() - t0:.1f}s", flush=True)
            d = pd.read_pickle(path); d["seed"] = seed; d["fold"] = k
            parts.append(d)
    return pd.concat(parts, ignore_index=True).set_index(["seed", "fold", "id"]).sort_index()


def main():
    A, E = exp004()
    Ad = a_doi_oof().loc[E.index]
    sel = [load_runs(s, E.index).pb.to_numpy() for s in SEL_EXP004]
    egs = [_load(s).loc[E.index].eg.to_numpy() for s in COMPONENTS["ft_ens_v1"]["eg"]]
    c = E.copy()
    c["pb"] = mean_logit_pb([Ad.pb.to_numpy()] + sel)
    c["eg"] = np.mean([Ad.eg.to_numpy()] + egs, axis=0)
    a_only = A.copy(); a_only[["eg", "pb"]] = Ad[["eg", "pb"]].to_numpy()
    for part, seeds in (("seed0", [0]), ("seeds12", [1, 2]), ("15 folds", [0, 1, 2])):
        print(f"=== {part} ===")
        compare("A' (exp003 + doi series) vs A", restrict(a_only, seeds), restrict(A, seeds))
        compare("EXP-004 with A' in place of A", restrict(c, seeds), restrict(E, seeds))


if __name__ == "__main__":
    from threadpoolctl import threadpool_limits

    with threadpool_limits(limits=1):
        main()
