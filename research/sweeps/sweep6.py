"""Sweep 6: selection improvements on top of exp003 features, with HONEST threshold selection
(threshold for fold k chosen on the other 4 folds of the same seed)."""
import time
import numpy as np
from scipy import sparse
from sklearn.linear_model import LogisticRegression
from sklearn.decomposition import TruncatedSVD
from sklearn.ensemble import HistGradientBoostingClassifier
from sweep1 import tr, features, GAIN
from sweep2 import knn_feats, EMB
from src.validation import folds, scored_mask, SEEDS
from src.metric import score_arrays, to_priority

E = np.hstack([EMB[k] for k in ("minilm", "mpnet", "specter")]) / np.sqrt(3)
VEN = dict(zip(tr.id, tr.venue))
CFG = dict(te=1.0, char=1.0)
GRID = np.round(np.arange(0.3, 0.76, 0.025), 3)


def oof(hgb=False):
    """per fold: ids, y, venue, eg_multi, pw_multi, pw_bin, [pw_hgb]"""
    out = []
    for seed in SEEDS:
        for a, v in folds(tr, seed):
            f, t = tr.iloc[a], tr.iloc[v]; keep = scored_mask(t); t = t[keep]
            Xf, Xt = features(f, t, CFG)
            yf = f.label.to_numpy(); Ef, Et = E[a], E[v][keep]
            kf, kt = knn_feats(Ef, yf, Ef, 20, loo=True), knn_feats(Ef, yf, Et, 20)
            mu, sd = kf.mean(0), kf.std(0) + 1e-9
            Xf = sparse.hstack([Xf, sparse.csr_matrix((kf - mu) / sd), sparse.csr_matrix(2 * Ef)]).tocsr()
            Xt = sparse.hstack([Xt, sparse.csr_matrix((kt - mu) / sd), sparse.csr_matrix(2 * Et)]).tocsr()
            m = LogisticRegression(max_iter=5000).fit(Xf, yf)
            P = m.predict_proba(Xt); eg = P @ GAIN[m.classes_ - 1]; pm = 1 - P[:, 0]
            pb = LogisticRegression(max_iter=5000).fit(Xf, yf > 1).predict_proba(Xt)[:, 1]
            d = dict(seed=seed, ids=t.id.to_numpy(), y=t.label.to_numpy(), ven=t.venue.to_numpy(), eg=eg, pm=pm, pb=pb)
            if hgb:
                svd = TruncatedSVD(64, random_state=0).fit(Ef)
                Df = np.hstack([svd.transform(Ef), (kf - mu) / sd, f[["year"]].to_numpy(), (f.venue.to_numpy()[:, None] == np.array(["cav", "iclp", "kr", "lics", "lpnmr"]))])
                Dt = np.hstack([svd.transform(Et), (kt - mu) / sd, t[["year"]].to_numpy(), (t.venue.to_numpy()[:, None] == np.array(["cav", "iclp", "kr", "lics", "lpnmr"]))])
                h = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=15, l2_regularization=1.0, random_state=seed)
                d["ph"] = h.fit(Df, yf > 1).predict_proba(Dt)[:, 1]
            out.append(d)
    return out


def sc(d, sel_score, order_score, th):
    thv = np.array([th[v] for v in d["ven"]]) if isinstance(th, dict) else th
    pr = np.where(sel_score >= thv, 1 + 9 * np.clip(order_score, 0, 1), 0)
    return score_arrays(d["ids"], pr, d["y"])


def honest(out, sel, order, per_venue=False):
    """threshold(s) for each fold chosen on the other folds of the same seed"""
    res = []
    for k, d in enumerate(out):
        others = [o for j, o in enumerate(out) if o["seed"] == d["seed"] and j != k]
        mean = lambda th: np.mean([sc(o, sel(o), order(o), th)[0] for o in others])
        tg = max(GRID, key=mean)
        th = tg
        if per_venue:
            th = {v: tg for v in ("cav", "kr", "lics", "lpnmr", "iclp")}
            for _ in range(2):
                for v in ("cav", "kr", "lics", "lpnmr"):
                    th[v] = max(GRID, key=lambda t_: mean({**th, v: t_}))
        res.append(sc(d, sel(d), order(d), th))
    r = np.array(res)
    return r[:, 0].mean(), r[:, 0].std(ddof=1), r[:, 1].mean(), r[:, 2].mean()


t0 = time.time(); out = oof(hgb=True); print(f"OOF built in {time.time()-t0:.0f}s", flush=True)
variants = {
    "exp003  sel=pb order=eg global": (lambda d: d["pb"], lambda d: d["eg"], False),
    "per-venue thresholds": (lambda d: d["pb"], lambda d: d["eg"], True),
    "sel=avg(pb,pm)": (lambda d: (d["pb"] + d["pm"]) / 2, lambda d: d["eg"], False),
    "sel=avg(pb,pm,hgb)": (lambda d: (d["pb"] + d["pm"] + d["ph"]) / 3, lambda d: d["eg"], False),
    "sel=avg(pb,hgb)": (lambda d: (d["pb"] + d["ph"]) / 2, lambda d: d["eg"], False),
    "sel=hgb only": (lambda d: d["ph"], lambda d: d["eg"], False),
    "order=eg*pb": (lambda d: d["pb"], lambda d: d["eg"] * d["pb"], False),
    "order=avg(eg,pb)": (lambda d: d["pb"], lambda d: (d["eg"] + d["pb"]) / 2, False),
    "avg(pb,pm,hgb) + per-venue": (lambda d: (d["pb"] + d["pm"] + d["ph"]) / 3, lambda d: d["eg"], True),
}
for name, (s, o, pv) in variants.items():
    t0 = time.time(); r = honest(out, s, o, pv)
    print(f"{name:30s} Score={r[0]:.4f}±{r[1]:.4f} Q={r[2]:.4f} R={r[3]:.4f}  ({time.time()-t0:.0f}s)", flush=True)
