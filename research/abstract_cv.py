"""How much would abstracts help?  TRAIN-ONLY cross-validation (no test data involved).

    .venv\\Scripts\\python.exe -m research.abstract_cv [model_key ...]      (default: minilm)

Text per paper = title + ". " + abstract  (fallback: S2 TLDR, then title only). Embeddings cached in
data/interim/emb_abs_<key>_train.npz. Compares, on seed-0 folds of the fixed protocol (non-iclp scored):
  A  exp003 (title embeddings only)            — the submitted model
  B  exp003 + abstract embeddings (concat)
  C  abstract embeddings replace title embeddings
Threshold: 'honest' = chosen on the other 4 folds; also fixed 0.55.
"""
from __future__ import annotations

import json
import sys
import time

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from src.data import ROOT, load_all
from src.embeddings import MODELS as EMB_MODELS
from src.embeddings import title_embeddings
from src.metric import score_arrays
from src.models import EmbedLogReg
from src.validation import folds, scored_mask

EXT = ROOT / "data" / "external" / "s2_train.jsonl"
CACHE = ROOT / "data" / "interim"
GRID = np.round(np.arange(0.30, 0.801, 0.025), 3)


MODE = "abstract"  # or "tldr": title + S2 TLDR only (short, more uniform)


def texts(tr: pd.DataFrame, sep: str = ". ") -> tuple[list[str], pd.DataFrame]:
    recs = {r["id"]: r for r in map(json.loads, EXT.read_text(encoding="utf-8").splitlines())}
    out, kind = [], []
    for i, t in zip(tr.id, tr.title):
        r = recs.get(int(i), {})
        if MODE == "abstract" and r.get("abstract"):
            out.append(f"{t}{sep}{r['abstract']}"); kind.append("abstract")
        elif r.get("tldr"):
            out.append(f"{t}{sep}{r['tldr']}"); kind.append("tldr")
        else:
            out.append(t); kind.append("title_only")
    return out, pd.DataFrame({"id": tr.id.values, "kind": kind, "label": tr.label.values, "venue": tr.venue.values})


def abs_embeddings(tr, key):
    path = CACHE / f"emb_{MODE}_{key}_train.npz" if MODE != "abstract" else CACHE / f"emb_abs_{key}_train.npz"
    if path.exists():
        z = np.load(path)
        return dict(zip(z["ids"].tolist(), z["emb"]))
    from sentence_transformers import SentenceTransformer
    import torch
    txt, _ = texts(tr, sep="[SEP]" if key == "specter" else ". ")  # SPECTER's documented input: title[SEP]abstract
    t0 = time.time()
    m = SentenceTransformer(EMB_MODELS[key], device="cpu", model_kwargs={"torch_dtype": torch.float32})
    parts = []
    for s in range(0, len(txt), 64):
        parts.append(m.encode(txt[s:s + 64], batch_size=64, normalize_embeddings=True, show_progress_bar=False))
        if (s // 64) % 8 == 0:
            print(f"  [abs {key}] {min(s + 64, len(txt))}/{len(txt)}  {time.time() - t0:.0f}s", flush=True)
    E = np.vstack(parts).astype(np.float32)
    np.savez(path, ids=tr.id.to_numpy(), emb=E)
    return dict(zip(tr.id.tolist(), E))


class AbsEmbedLogReg(EmbedLogReg):
    def __init__(self, abs_maps: dict, mode: str = "concat", **kw):
        super().__init__(**kw)
        self.abs_maps, self.mode = abs_maps, mode

    def _emb(self, df):
        blocks = [] if self.mode == "replace" else [title_embeddings(df, e) for e in self.embs]
        blocks += [np.vstack([mp[int(i)] for i in df.id]) for mp in self.abs_maps.values()]
        return np.hstack(blocks) / np.sqrt(len(blocks))


def oof(tr, make):
    parts = []
    for k, (a, v) in enumerate(folds(tr, 0)):
        f, t = tr.iloc[a], tr.iloc[v]
        t = t[scored_mask(t)].copy()
        eg, pb = make().fit(f).predict(t)
        t["fold"], t["eg"], t["pb"] = k, eg, pb
        parts.append(t)
    return pd.concat(parts)


def evaluate(o):
    def fs(g, t):
        return score_arrays(g.id, np.where(g.pb >= t, 1 + 9 * np.clip(g.eg, 0, 1), 0), g.label)
    hon, fix = [], []
    for k, g in o.groupby("fold"):
        others = [gg for kk, gg in o.groupby("fold") if kk != k]
        t = max(GRID, key=lambda t: np.mean([fs(gg, t)[0] for gg in others]))
        hon.append(fs(g, t)); fix.append(fs(g, 0.55))
    h, f = np.array(hon), np.array(fix)
    return dict(honest=h[:, 0].mean(), honest_std=h[:, 0].std(ddof=1), Q=h[:, 1].mean(), R=h[:, 2].mean(),
                fixed055=f[:, 0].mean(), auc=roc_auc_score(o.label > 1, o.pb))


def main():
    global MODE
    args = sys.argv[1:]
    if "--tldr" in args:
        MODE = "tldr"; args.remove("--tldr")
    keys = args or ["minilm"]
    print(f"text mode = {MODE}, embedding models = {keys}", flush=True)
    tr, _ = load_all()
    _, info = texts(tr)
    print("text source:", info.kind.value_counts().to_dict())
    print("worth-rate by text source:", info.groupby("kind").label.apply(lambda s: round(float((s > 1).mean()), 3)).to_dict())
    maps = {k: abs_embeddings(tr, k) for k in keys}
    res = {}
    t0 = time.time(); res["A exp003 (title only)"] = evaluate(oof(tr, lambda: EmbedLogReg(seed=0)))
    print(f"A done {time.time() - t0:.0f}s", flush=True)
    t0 = time.time(); res[f"B exp003 + abstract[{'+'.join(keys)}]"] = evaluate(oof(tr, lambda: AbsEmbedLogReg(maps, "concat", seed=0)))
    print(f"B done {time.time() - t0:.0f}s", flush=True)
    t0 = time.time(); res[f"C abstract[{'+'.join(keys)}] replaces title emb"] = evaluate(oof(tr, lambda: AbsEmbedLogReg(maps, "replace", seed=0)))
    print(f"C done {time.time() - t0:.0f}s", flush=True)
    print("\nseed-0 folds, non-iclp scored")
    for name, r in res.items():
        print(f"{name:45s} honest={r['honest']:.4f}±{r['honest_std']:.4f} Q={r['Q']:.4f} R={r['R']:.4f} fixed0.55={r['fixed055']:.4f} AUC={r['auc']:.4f}")
    out = ROOT / "outputs" / "research" / f"abstract_cv_{MODE}_{'_'.join(keys)}.json"
    out.write_text(json.dumps(res, indent=2), encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
