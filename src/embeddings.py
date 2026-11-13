"""Pretrained sentence embeddings of titles (inference only, no fitting on test), cached in data/interim/.

External resources (NFR-06, cite in README/report):
- sentence-transformers library (Reimers & Gurevych, 2019), https://www.sbert.net
- models downloaded from the Hugging Face Hub, listed in MODELS below.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.data import ROOT

CACHE = ROOT / "data" / "interim"
MODELS = {
    "minilm": "sentence-transformers/all-MiniLM-L6-v2",
    "mpnet": "sentence-transformers/all-mpnet-base-v2",
    "specter": "sentence-transformers/allenai-specter",
    "bge_large": "BAAI/bge-large-en-v1.5",
    "e5_large": "intfloat/e5-large-v2",
    "gte_large": "thenlper/gte-large",
    "scincl": "malteos/scincl",
}
PREFIX = {"e5_large": "query: "}  # e5 expects an input prefix


def title_embeddings(df: pd.DataFrame, key: str = "minilm") -> np.ndarray:
    """L2-normalised embeddings aligned with df rows. Computes for all ids once and caches by id."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"emb_{key}.npz"
    if path.exists():
        z = np.load(path)
        lookup = dict(zip(z["ids"].tolist(), range(len(z["ids"]))))
        if all(i in lookup for i in df["id"]):
            return z["emb"][[lookup[i] for i in df["id"]]]
    import time

    import torch
    from sentence_transformers import SentenceTransformer

    t0 = time.time()
    print(f"[{key}] loading {MODELS[key]} (float32, cpu)", flush=True)
    # force float32: some checkpoints (e.g. gte-large) ship fp16 weights, which are extremely slow on CPU
    model = SentenceTransformer(MODELS[key], device="cpu", model_kwargs={"torch_dtype": torch.float32})
    print(f"[{key}] loaded in {time.time() - t0:.0f}s; dtype={next(model.parameters()).dtype}; encoding {len(df)} titles", flush=True)
    texts = [PREFIX.get(key, "") + t for t in df["title"]]
    bs, parts = 64, []
    for s in range(0, len(texts), bs):
        parts.append(model.encode(texts[s:s + bs], batch_size=bs, normalize_embeddings=True, show_progress_bar=False))
        if (s // bs) % 10 == 0 or s + bs >= len(texts):
            print(f"[{key}] {min(s + bs, len(texts))}/{len(texts)} titles  {time.time() - t0:.0f}s", flush=True)
    emb = np.vstack(parts)
    np.savez(path, ids=df["id"].to_numpy(), emb=emb.astype(np.float32))
    print(f"[{key}] done in {time.time() - t0:.0f}s -> {path.name}", flush=True)
    return emb


def all_titles() -> pd.DataFrame:
    from src.data import load_all
    tr, te = load_all()
    return pd.concat([tr[["id", "title"]], te[["id", "title"]]], ignore_index=True)


if __name__ == "__main__":
    import sys
    df = all_titles()
    for k in (sys.argv[1:] or list(MODELS)):
        e = title_embeddings(df, k)
        print(k, e.shape)
