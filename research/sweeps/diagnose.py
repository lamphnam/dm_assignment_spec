"""OOF diagnostics for exp002 (logreg_text): where is the score lost?"""
import numpy as np, pandas as pd, re
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score
from src.data import load_all
from src.models import LogRegText
from src.validation import folds, scored_mask
from src.metric import score_arrays, to_priority

tr, te = load_all()
rows = []
for k, (a, v) in enumerate(folds(tr, 0)):
    m = LogRegText(seed=0).fit(tr.iloc[a])
    d = tr.iloc[v][scored_mask(tr.iloc[v])].copy()
    d["eg"], d["pw"], d["fold"] = *m.predict(d), k
    rows.append(d)
o = pd.concat(rows)
y = o.label.to_numpy()
print(f"OOF (seed 0, non-iclp, n={len(o)}): Spearman(eg,y)={spearmanr(o.eg, y)[0]:.3f}  AUC(pw, y>1)={roc_auc_score(y > 1, o.pw):.3f}  AUC(eg, y>=4)={roc_auc_score(y >= 4, o.eg):.3f}")
print("\nper venue: n, mean y, Spearman, AUC(y>1)")
for vn, g in o.groupby("venue"):
    print(f"  {vn:6s} {len(g):4d} {g.label.mean():.2f} {spearmanr(g.eg, g.label)[0]:.3f} {roc_auc_score(g.label > 1, g.pw):.3f}")
print("\nmean predicted eg by true label:", o.groupby("label").eg.mean().round(3).to_dict())
print("mean predicted pw by true label:", o.groupby("label").pw.mean().round(3).to_dict())

# decompose: oracle ordering with model selection, and model ordering with oracle selection
s = {"model": [], "model_sel+oracle_order": [], "oracle_sel+model_order": []}
for k, g in o.groupby("fold"):
    yy = g.label.to_numpy(); gt = (yy - 1) / 4
    sel = g.pw.to_numpy() >= 0.5
    s["model"].append(score_arrays(g.id, to_priority(g.eg, g.pw, 0.5), yy))
    s["model_sel+oracle_order"].append(score_arrays(g.id, np.where(sel, 1 + 9 * gt + 1e-6 * g.eg, 0), yy))
    s["oracle_sel+model_order"].append(score_arrays(g.id, np.where(yy > 1, 1 + 9 * g.eg, 0), yy))
for k, v in s.items():
    v = np.array(v); print(f"{k:24s} Score={v[:,0].mean():.4f} Q={v[:,1].mean():.4f} R={v[:,2].mean():.4f}")

kw = re.compile(r"proceedings|front matter|preface|workshop", re.I)
pk = o.title.str.contains(kw)
print(f"\nkeyword proceedings/front matter/preface/workshop rows: n={pk.sum()}, labels={o[pk].label.value_counts().to_dict()}, mean pw={o[pk].pw.mean():.3f}, selected@0.5={int((o[pk].pw>=0.5).sum())}")
print("test rows with keyword:", int(te.title.str.contains(kw).sum()))
fp = o[(o.pw >= 0.5) & (o.label == 1)].sort_values("eg", ascending=False).head(8)
print("\nTop-ranked label-1 papers (false positives):")
for _, r in fp.iterrows():
    print(f"  eg={r.eg:.2f} pw={r.pw:.2f} {r.venue} {r.year} | {r.title[:80]}")
