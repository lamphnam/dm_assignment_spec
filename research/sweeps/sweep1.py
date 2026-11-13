"""Sweep 1: feature sets x model heads, same 15-fold protocol as src/validation.py."""
import sys, time
import numpy as np, pandas as pd
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression, Ridge
from src.data import load_all
from src.validation import folds, scored_mask, SEEDS
from src.metric import score_arrays, to_priority

tr, te = load_all()
GAIN = np.array([0, .25, .5, .75, 1])


def ident(x):
    return [t.lower() for t in x]


def author_te(fit_df, tgt_df, loo, m=3.0):
    """Smoothed author mean gain / worth-rate from fit_df; leave-one-out when tgt is the fit set."""
    g = ((fit_df.label - 1) / 4).to_numpy(); w = (fit_df.label > 1).to_numpy().astype(float)
    S, W, N = {}, {}, {}
    for auths, gi, wi in zip(fit_df.authors, g, w):
        for a in set(x.lower() for x in auths):
            S[a] = S.get(a, 0) + gi; W[a] = W.get(a, 0) + wi; N[a] = N.get(a, 0) + 1
    pg, pw = g.mean(), w.mean()
    feats = []
    for k, auths in enumerate(tgt_df.authors):
        gs, ws, ns = [], [], []
        for a in set(x.lower() for x in auths):
            s, ww, n = S.get(a, 0), W.get(a, 0), N.get(a, 0)
            if loo:
                s -= g[k]; ww -= w[k]; n -= 1
            if n > 0:
                gs.append((s + m * pg) / (n + m)); ws.append((ww + m * pw) / (n + m)); ns.append(n)
        feats.append([max(gs) if gs else pg, np.mean(gs) if gs else pg, max(ws) if ws else pw,
                      min(ws) if ws else pw, np.log1p(sum(ns)), len(gs) > 0, len(auths) == 0])
    return np.array(feats, float)


def features(fit_df, tgt_df, cfg):
    """returns X_fit, X_tgt (sparse)"""
    blocks_f, blocks_t = [], []
    tv = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, strip_accents="unicode")
    blocks_f.append(tv.fit_transform(fit_df.title)); blocks_t.append(tv.transform(tgt_df.title))
    if cfg.get("char"):
        cv = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=3, sublinear_tf=True, strip_accents="unicode", max_features=30000)
        blocks_f.append(cfg["char"] * cv.fit_transform(fit_df.title)); blocks_t.append(cfg["char"] * cv.transform(tgt_df.title))
    oh = OneHotEncoder(handle_unknown="ignore")
    cols = ["venue", "year"]
    f_cat = fit_df[cols].astype(str).copy(); t_cat = tgt_df[cols].astype(str).copy()
    if cfg.get("vy"):
        f_cat["vy"] = f_cat.venue + "_" + f_cat.year; t_cat["vy"] = t_cat.venue + "_" + t_cat.year
    blocks_f.append(oh.fit_transform(f_cat)); blocks_t.append(oh.transform(t_cat))
    if cfg.get("auth_bin", True):
        av = CountVectorizer(analyzer=ident, binary=True, min_df=2)
        blocks_f.append(av.fit_transform(fit_df.authors)); blocks_t.append(av.transform(tgt_df.authors))
    if cfg.get("te"):
        a_f, a_t = author_te(fit_df, fit_df, True), author_te(fit_df, tgt_df, False)
        mu, sd = a_f.mean(0), a_f.std(0) + 1e-9
        blocks_f.append(sparse.csr_matrix(cfg["te"] * (a_f - mu) / sd)); blocks_t.append(sparse.csr_matrix(cfg["te"] * (a_t - mu) / sd))
    return sparse.hstack(blocks_f).tocsr(), sparse.hstack(blocks_t).tocsr()


def run(cfg):
    out = []
    for seed in SEEDS:
        for a, v in folds(tr, seed):
            f, t = tr.iloc[a], tr.iloc[v]; t = t[scored_mask(t)]
            Xf, Xt = features(f, t, cfg)
            yf = f.label.to_numpy()
            multi = LogisticRegression(C=cfg.get("C", 1.0), max_iter=5000).fit(Xf, yf)
            P = multi.predict_proba(Xt); eg = P @ GAIN[multi.classes_ - 1]; pw = 1 - P[:, list(multi.classes_).index(1)]
            if cfg.get("bin_C"):
                b = LogisticRegression(C=cfg["bin_C"], max_iter=5000).fit(Xf, yf > 1)
                pw = b.predict_proba(Xt)[:, 1]
            if cfg.get("ridge"):
                r = Ridge(alpha=cfg["ridge"]).fit(Xf, (yf - 1) / 4); eg = r.predict(Xt)
            if cfg.get("order") == "pw":
                eg = pw
            out.append((t.id.to_numpy(), t.label.to_numpy(), eg, pw))
    return out


def evaluate(out):
    best = None
    for th in np.round(np.arange(0.3, 0.71, 0.025), 3):
        s = np.array([score_arrays(i, to_priority(np.clip(e, 0, 1), p, th), y) for i, y, e, p in out])
        r = (s[:, 0].mean(), s[:, 0].std(ddof=1), s[:, 1].mean(), s[:, 2].mean(), th)
        if best is None or r[0] > best[0]:
            best = r
    return best


CFGS = {
    "A exp002 (C=1)": dict(),
    "B C=0.3": dict(C=0.3),
    "C C=3": dict(C=3),
    "D +bin head C=1": dict(bin_C=1.0),
    "E +char": dict(char=1.0),
    "F +venue_year": dict(vy=True),
    "G +author TE": dict(te=1.0),
    "H +TE +bin": dict(te=1.0, bin_C=1.0),
    "I +TE +char +bin": dict(te=1.0, char=1.0, bin_C=1.0),
    "J +TE order=pw": dict(te=1.0, bin_C=1.0, order="pw"),
}
only = sys.argv[1:]
for name, cfg in (CFGS.items() if __name__ == "__main__" else []):
    if only and name.split()[0] not in only:
        continue
    t0 = time.time(); r = evaluate(run(cfg))
    print(f"{name:22s} Score={r[0]:.4f}±{r[1]:.4f} Q={r[2]:.4f} R={r[3]:.4f} th={r[4]:.3f}  ({time.time()-t0:.0f}s)", flush=True)
