"""Sweep 2: add pretrained title embeddings (+ kNN preference features)."""
import sys, time
import numpy as np
from scipy import sparse
from sklearn.linear_model import LogisticRegression
from sweep1 import tr, features, evaluate, GAIN
from src.embeddings import title_embeddings
from src.validation import folds, scored_mask, SEEDS

EMB = {k: title_embeddings(tr, k) for k in ("minilm", "mpnet", "specter")}


def knn_feats(Ef, yf, Et, k=20, loo=False):
    S = Et @ Ef.T
    if loo:
        np.fill_diagonal(S, -np.inf)
    idx = np.argpartition(-S, k, axis=1)[:, :k]
    sims = np.take_along_axis(S, idx, 1); ys = yf[idx]
    w = np.maximum(sims, 0) + 1e-6
    g = (ys - 1) / 4
    out = [(w * g).sum(1) / w.sum(1), (w * (ys > 1)).sum(1) / w.sum(1), sims.mean(1)]
    for lab in (1, 5):  # mean of top-5 similarity to label-1 / label-5 papers
        Sl = np.where(yf[None, :] == lab, S, -np.inf)
        out.append(np.sort(Sl, axis=1)[:, -5:].mean(1))
    return np.column_stack(out)


def run(cfg):
    out = []
    E = EMB[cfg["emb"]] if cfg.get("emb") else None
    for seed in SEEDS:
        for a, v in folds(tr, seed):
            f, t = tr.iloc[a], tr.iloc[v]; keep = scored_mask(t); t = t[keep]
            if cfg.get("base", True):
                Xf, Xt = features(f, t, cfg)
            else:
                Xf, Xt = sparse.csr_matrix((len(f), 0)), sparse.csr_matrix((len(t), 0))
            yf = f.label.to_numpy()
            if E is not None:
                Ef, Et = E[a], E[v][keep]
                bf, bt = [Xf], [Xt]
                if cfg.get("ew"):
                    bf.append(sparse.csr_matrix(cfg["ew"] * Ef)); bt.append(sparse.csr_matrix(cfg["ew"] * Et))
                if cfg.get("knn"):
                    kf, kt = knn_feats(Ef, yf, Ef, cfg["knn"], loo=True), knn_feats(Ef, yf, Et, cfg["knn"])
                    mu, sd = kf.mean(0), kf.std(0) + 1e-9
                    bf.append(sparse.csr_matrix((kf - mu) / sd)); bt.append(sparse.csr_matrix((kt - mu) / sd))
                Xf, Xt = sparse.hstack(bf).tocsr(), sparse.hstack(bt).tocsr()
            m = LogisticRegression(C=cfg.get("C", 1.0), max_iter=5000).fit(Xf, yf)
            P = m.predict_proba(Xt); eg = P @ GAIN[m.classes_ - 1]; pw = 1 - P[:, list(m.classes_).index(1)]
            if cfg.get("bin_C"):
                pw = LogisticRegression(C=cfg["bin_C"], max_iter=5000).fit(Xf, yf > 1).predict_proba(Xt)[:, 1]
            out.append((t.id.to_numpy(), t.label.to_numpy(), eg, pw))
    return out


CFGS = {
    "K minilm only": dict(base=False, emb="minilm", ew=1.0, C=3),
    "L mpnet only": dict(base=False, emb="mpnet", ew=1.0, C=3),
    "M specter only": dict(base=False, emb="specter", ew=1.0, C=3),
    "N I+mpnet": dict(te=1.0, char=1.0, bin_C=1.0, emb="mpnet", ew=1.0),
    "O I+specter": dict(te=1.0, char=1.0, bin_C=1.0, emb="specter", ew=1.0),
    "P I+mpnet+knn": dict(te=1.0, char=1.0, bin_C=1.0, emb="mpnet", ew=1.0, knn=20),
    "Q I+specter+knn": dict(te=1.0, char=1.0, bin_C=1.0, emb="specter", ew=1.0, knn=20),
    "R E+mpnet ew2": dict(char=1.0, emb="mpnet", ew=2.0),
}
if __name__ == "__main__":
    only = sys.argv[1:]
    for name, cfg in CFGS.items():
        if only and name.split()[0] not in only:
            continue
        t0 = time.time(); r = evaluate(run(cfg))
        print(f"{name:20s} Score={r[0]:.4f}±{r[1]:.4f} Q={r[2]:.4f} R={r[3]:.4f} th={r[4]:.3f}  ({time.time()-t0:.0f}s)", flush=True)
