"""Research diagnostics on exp003 (EmbedLogReg) out-of-fold predictions — where is the score lost, how much headroom
does each direction have. Read-only w.r.t. data; writes outputs/research/.

    .venv\\Scripts\\python.exe -m research.analysis_exp003

Uses seed 0 of the fixed protocol (5 folds, scored on non-iclp papers). Runtime ~2 min on CPU.
"""
from __future__ import annotations

import json
import re
from collections import Counter

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

from src.data import ROOT, load_all
from src.metric import score_arrays
from src.models import GAIN, EmbedLogReg, author_target_features
from src.validation import folds, scored_mask

OUT = ROOT / "outputs" / "research"
OUT.mkdir(parents=True, exist_ok=True)
W = 1.0 / np.log2(np.arange(2, 4000))
GRID = np.round(np.arange(0.30, 0.801, 0.025), 3)
summary: dict = {}


def build_oof(tr: pd.DataFrame, seed: int = 0) -> pd.DataFrame:
    path = OUT / f"oof_exp003_seed{seed}.pkl"
    if path.exists():
        return pd.read_pickle(path)
    parts = []
    for k, (a, v) in enumerate(folds(tr, seed)):
        f, t = tr.iloc[a], tr.iloc[v].copy()
        m = EmbedLogReg(seed=0).fit(f)
        X = m._transform(t, fitting=False)
        P = m.multi_.predict_proba(X)
        full = np.zeros((len(t), 5))
        for j, c in enumerate(m.multi_.classes_):
            full[:, c - 1] = P[:, j]
        t["fold"], t["eg"], t["pm"] = k, full @ GAIN, 1 - full[:, 0]
        t["pb"] = m.bin_.predict_proba(X)[:, 1]
        t["known_author"] = author_target_features(m.stats_, t, loo=False)[:, 5]
        E = m._emb(t)
        S = E @ m.E_fit_.T
        j = S.argmax(1)
        t["nn_sim"], t["nn_label"] = S[np.arange(len(t)), j], m.y_fit_[j]
        parts.append(t)
        print(f"  fold {k} done", flush=True)
    oof = pd.concat(parts)
    oof.to_pickle(path)
    return oof


def priority(sel: np.ndarray, eg: np.ndarray) -> np.ndarray:
    return np.where(sel, 1 + 9 * np.clip(eg, 0, 1), 0.0)


def fold_score(g: pd.DataFrame, sel: np.ndarray, eg=None):
    return score_arrays(g.id, priority(sel, g.eg.to_numpy() if eg is None else eg), g.label)


def plugin(pb: np.ndarray, eg: np.ndarray):
    """Choose list length m maximising the plug-in expected score.
    E[Q] is exact given calibrated eg (denominator is deterministic); E[R] ~ sum(pb_selected)/sum(pb_all)."""
    order, tot, best = np.argsort(-pb, kind="stable"), pb.sum(), (-1.0, 0, 0.0, 0.0)
    for m in range(1, len(pb) + 1):
        S = order[:m]
        q = (W[:m] @ np.sort(eg[S])[::-1]) / W[:m].sum()
        r = pb[S].sum() / tot
        h = 2 * q * r / (q + r)
        if h > best[0]:
            best = (h, m, q, r)
    sel = np.zeros(len(pb), bool)
    sel[order[:best[1]]] = True
    return sel, best


def section(title):
    print(f"\n=== {title} ===", flush=True)


def main():
    tr, te = load_all()
    print("building OOF (seed 0) ...", flush=True)
    oof = build_oof(tr)
    o = oof[scored_mask(oof)].copy()
    y = o.label.to_numpy(); worth = y > 1

    # A1 ---------------------------------------------------------------- calibration
    section("A1 calibration of P(worthwhile) (pb), non-iclp OOF")
    bins = [0, .2, .3, .4, .5, .6, .7, .8, 1.01]
    o["bin"] = pd.cut(o.pb, bins, right=False)
    cal = o.groupby("bin", observed=True).agg(n=("pb", "size"), mean_pb=("pb", "mean"), actual=("label", lambda s: (s > 1).mean()))
    print(cal.round(3).to_string())
    pv = o.groupby("venue").agg(n=("pb", "size"), mean_pb=("pb", "mean"), actual=("label", lambda s: (s > 1).mean()),
                                auc=("pb", lambda s: roc_auc_score(o.loc[s.index, "label"] > 1, s)),
                                spearman_eg=("eg", lambda s: spearmanr(s, o.loc[s.index, "label"])[0]))
    print(pv.round(3).to_string())
    summary["A1_per_venue"] = pv.round(4).reset_index().to_dict("records")
    print(f"overall AUC(pb)={roc_auc_score(worth, o.pb):.3f}  AUC(pm)={roc_auc_score(worth, o.pm):.3f}  "
          f"AUC(avg)={roc_auc_score(worth, (o.pb + o.pm) / 2):.3f}  Spearman(eg,y)={spearmanr(o.eg, y)[0]:.3f}")

    # A2 ---------------------------------------------------------------- threshold curve
    section("A2 score vs threshold per fold (selection = pb >= t)")
    rows = []
    for k, g in o.groupby("fold"):
        sc = [fold_score(g, g.pb.to_numpy() >= t)[0] for t in GRID]
        rows.append(dict(fold=k, n=len(g), worth_rate=(g.label > 1).mean(), best_t=GRID[int(np.argmax(sc))], best=max(sc),
                         at_055=sc[list(GRID).index(0.55)], at_045=sc[list(GRID).index(0.45)], at_065=sc[list(GRID).index(0.65)]))
    a2 = pd.DataFrame(rows)
    print(a2.round(4).to_string(index=False))

    # A3 ---------------------------------------------------------------- plug-in expected-score cutoff
    section("A3 plug-in expected-score cutoff vs fixed threshold")
    res = []
    for k, g in o.groupby("fold"):
        pb, eg = g.pb.to_numpy(), g.eg.to_numpy()
        sel_pi, (h, m, q, r) = plugin(pb, eg)
        others = o[o.fold != k]
        t_h = max(GRID, key=lambda t: np.mean([fold_score(gg, gg.pb.to_numpy() >= t)[0] for _, gg in others.groupby("fold")]))
        res.append(dict(fold=k, fixed_055=fold_score(g, pb >= 0.55)[0], honest_t=t_h, honest=fold_score(g, pb >= t_h)[0],
                        plugin=fold_score(g, sel_pi)[0], plugin_m=m, plugin_expected=h, n_sel_055=int((pb >= .55).sum())))
    a3 = pd.DataFrame(res)
    print(a3.round(4).to_string(index=False))
    print("mean:", a3[["fixed_055", "honest", "plugin", "plugin_expected"]].mean().round(4).to_dict())
    summary["A3_plugin"] = a3[["fixed_055", "honest", "plugin", "plugin_expected"]].mean().round(4).to_dict()

    # A4 ---------------------------------------------------------------- headroom: selection AUC and ordering
    section("A4 headroom: score if selection AUC (or ordering) improved [simulation, re-tuned threshold]")
    lg = np.log(np.clip(o.pb, 1e-6, 1 - 1e-6) / (1 - np.clip(o.pb, 1e-6, 1 - 1e-6)))
    sim = []
    for beta in (0.0, 0.25, 0.5, 0.75, 1.0, 1.5):
        pb2 = 1 / (1 + np.exp(-(lg + beta * (2 * worth - 1))))
        o["pb2"] = pb2
        best = max(np.mean([fold_score(g, g.pb2.to_numpy() >= t)[0] for _, g in o.groupby("fold")]) for t in GRID)
        sim.append(dict(beta=beta, auc=roc_auc_score(worth, pb2), score=best))
    for gamma in (0.25, 0.5):
        o["eg2"] = o.eg + gamma * ((o.label - 1) / 4 - o.eg)
        best = max(np.mean([fold_score(g, g.pb.to_numpy() >= t, g.eg2.to_numpy())[0] for _, g in o.groupby("fold")]) for t in GRID)
        sim.append(dict(beta=f"order γ={gamma}", auc=roc_auc_score(worth, o.pb), score=best,
                        spearman=spearmanr(o.eg2, y)[0]))
    a4 = pd.DataFrame(sim)
    print(a4.round(4).to_string(index=False))
    summary["A4_headroom"] = a4.round(4).astype(str).to_dict("records")

    # A5 ---------------------------------------------------------------- authors / neighbours / year
    section("A5 known authors, nearest neighbour, year")
    for flag, g in o.groupby("known_author"):
        print(f"known_author={bool(flag)}: n={len(g)}, worth_rate={(g.label > 1).mean():.3f}, AUC(pb)={roc_auc_score(g.label > 1, g.pb):.3f}")
    o["sim_bin"] = pd.qcut(o.nn_sim, 5)
    nn = o.groupby("sim_bin", observed=True).apply(lambda g: pd.Series({
        "n": len(g), "same_label": (g.label == g.nn_label).mean(), "same_worth": ((g.label > 1) == (g.nn_label > 1)).mean()}), include_groups=False)
    print(nn.round(3).to_string())
    yr = tr[tr.venue != "iclp"].assign(w=lambda d: d.label > 1, period=lambda d: np.where(d.year <= 2019, "2016-19", "2020-26"))
    print(yr.pivot_table(index="venue", columns="period", values="w", aggfunc="mean").round(3).to_string())
    print("test year share <=2019:", round(float((te.year <= 2019).mean()), 3), "| train non-iclp:", round(float((yr.year <= 2019).mean()), 3))

    # A6 ---------------------------------------------------------------- words that separate label 1 vs worthwhile
    section("A6 log-odds (informative Dirichlet prior) of title tokens: worthwhile vs label 1, per venue [train]")
    tok = lambda s: re.findall(r"[a-z][a-z\-]+", s.lower())
    stop = set("a an the of for and in on with to by from via its is are as at or under using towards toward into".split())
    bg = Counter(w for t in tr.title for w in tok(t) if w not in stop)
    a0 = sum(bg.values())
    words = {}
    for ven in ("cav", "lics", "kr", "lpnmr"):
        d = tr[tr.venue == ven]
        c1 = Counter(w for t in d[d.label == 1].title for w in tok(t) if w not in stop)
        c2 = Counter(w for t in d[d.label > 1].title for w in tok(t) if w not in stop)
        n1, n2, z = sum(c1.values()), sum(c2.values()), {}
        for w in set(c1) | set(c2):
            if c1[w] + c2[w] < 4:
                continue
            aw = 10.0 * bg[w] / a0 * 1000
            l2 = np.log((c2[w] + aw) / (n2 + 1000 * 10 - c2[w] - aw)); l1 = np.log((c1[w] + aw) / (n1 + 1000 * 10 - c1[w] - aw))
            z[w] = (l2 - l1) / np.sqrt(1 / (c2[w] + aw) + 1 / (c1[w] + aw))
        top = sorted(z.items(), key=lambda kv: kv[1])
        words[ven] = {"label1": [w for w, _ in top[:10]], "worth": [w for w, _ in top[::-1][:10]]}
        print(f"{ven:6s} label-1 side: {', '.join(words[ven]['label1'])}\n       worthwhile  : {', '.join(words[ven]['worth'])}")
    summary["A6_words"] = words

    # A7 ---------------------------------------------------------------- external-data coverage
    section("A7 doi field types (for abstract lookup feasibility)")
    kind = lambda s: "doi10" if s.startswith("10.") else ("s2_url" if "semanticscholar.org" in s else "other_url")
    print("train:", dict(Counter(map(kind, tr.doi))), "| test:", dict(Counter(map(kind, te.doi))))

    # A8 ---------------------------------------------------------------- plug-in on the actual test predictions
    section("A8 full fit -> test: fixed t=0.55 vs plug-in")
    m = EmbedLogReg(seed=0).fit(tr)
    eg_t, pb_t = m.predict(te)
    sel_pi, (h, mm, q, r) = plugin(pb_t, eg_t)
    print(f"test mean pb={pb_t.mean():.3f} (train non-iclp worth rate {worth.mean():.3f}); selected t=0.55: {(pb_t >= .55).sum()} | "
          f"plug-in m={mm} expected Score={h:.4f} (Q={q:.3f}, R={r:.3f})")
    order = np.argsort(-pb_t); k55 = int((pb_t >= .55).sum())
    q55 = (W[:k55] @ np.sort(eg_t[order[:k55]])[::-1]) / W[:k55].sum(); r55 = pb_t[order[:k55]].sum() / pb_t.sum()
    print(f"expected Score of the submitted exp003 selection (t=0.55): {2 * q55 * r55 / (q55 + r55):.4f} (Q={q55:.3f}, R={r55:.3f})")
    summary["A8_test"] = dict(mean_pb=float(pb_t.mean()), n_sel_055=k55, plugin_m=int(mm), plugin_expected=float(h),
                              expected_055=float(2 * q55 * r55 / (q55 + r55)))
    (OUT / "summary_exp003.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    print(f"\nwrote {OUT / 'summary_exp003.json'}")


if __name__ == "__main__":
    main()
