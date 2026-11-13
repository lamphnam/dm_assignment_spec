"""Fine-tune a sentence encoder INSIDE each CV fold to improve the SELECTION step (P(label > 1)).

    .venv-gpu\\Scripts\\python.exe -m research.finetune_cv --enc minilm [--seeds 0] [--folds 0 1 2 3 4] [--tag NAME]

Why: research/analysis_exp003.py showed the score is lost mainly in selection (AUC 0.788; ~+0.004 Score per +0.01 AUC),
and frozen-embedding linear models look saturated (bigger encoders, abstracts, venue interactions: no gain).

Leakage control: for every fold the encoder is fine-tuned on the fold's TRAINING papers only. Validation labels and
Test are never seen; the validation fold plays the role of Test. Evaluation is the one of research/abstract_cv.py:
folds of src/validation.py, only non-iclp papers scored, threshold chosen honestly on the other folds of the same seed.

Variants per fold. A = exp003 (EmbedLogReg, the submitted model). Unless stated, eg (ordering) is A's, so a variant
changes only WHICH papers are selected:
  A        exp003 as submitted
  F0       frozen encoder + logistic head on (2*emb, venue, year)          -> pb
  SF       SetFit-style contrastive fine-tune (pairs by y>1) + same head    -> pb   (Tunstall et al., 2022)
  CE       supervised fine-tune: encoder + linear head, BCE on y>1          -> pb   (the network's own output)
  CE5      as CE but softmax over labels 1..5 -> pb = 1 - P(label 1); CE5own also uses its own eg = E[gain];
           A_eg5 = A's selection with ordering eg averaged with CE5's; A+CE5eg = both blended
  A+X      blend: mean of logit(pb_A) and logit(pb_X), fixed weight 0.5     -> pb
  A[X]     exp003 refitted with the `enc` embedding block replaced by X's fine-tuned embeddings (eg and pb refitted).
           Caveat: the fold-train embeddings come from an encoder that saw those labels, so the head sees
           over-separated training features; the validation estimate stays honest.
Text fed to the encoder: "<venue> <year>: <title>" (--no-prefix: title only).
"""
from __future__ import annotations

import argparse
import json
import math
import time

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import OneHotEncoder

from research.abstract_cv import evaluate
from src.data import ROOT, load_all
from src.embeddings import MODELS as EMB_MODELS
from src.embeddings import title_embeddings
from src.models import GAIN, EmbedLogReg
from src.validation import folds, scored_mask

OUT = ROOT / "outputs" / "research"


def texts_of(df: pd.DataFrame, prefix: bool) -> list[str]:
    if not prefix:
        return df["title"].tolist()
    return [f"{v} {y}: {t}" for v, y, t in zip(df["venue"], df["year"], df["title"])]


# ----------------------------------------------------------------------------------------------- encoder utils
def load_encoder(enc: str, device: str):
    import torch
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(EMB_MODELS[enc], device=device, model_kwargs={"torch_dtype": torch.float32})


def forward(model, texts, device):
    feats = model.preprocess(texts)
    feats = {k: (v.to(device) if hasattr(v, "to") else v) for k, v in feats.items()}
    return model(feats)["sentence_embedding"]


def encode(model, texts) -> np.ndarray:
    return model.encode(texts, batch_size=128, normalize_embeddings=True, show_progress_bar=False,
                        convert_to_numpy=True).astype(np.float32)


def _adamw(params, lr, device):
    """fused AdamW on CUDA: the default foreach implementation allocates parameter-sized temporaries, which ran a
    110M-parameter encoder (MPNet/SPECTER) out of the 4 GB of the RTX 3050."""
    import torch
    return torch.optim.AdamW(params, lr=lr, weight_decay=0.01, fused=device == "cuda")


def free_gpu():
    import gc

    import torch
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def _schedule(opt, total, warmup=0.1):
    import torch
    w = max(1, int(total * warmup))
    return torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min((s + 1) / w, max(0.0, (total - s) / max(1, total - w))))


def setfit_pairs(y: np.ndarray, iters: int, rng: np.random.Generator):
    """SetFit pair generation: per iteration, every sample gets one positive (same class) and one negative partner."""
    idx = {c: np.flatnonzero(y == c) for c in (0, 1)}
    a, b, t = [], [], []
    for _ in range(iters):
        for i in rng.permutation(len(y)):
            same, diff = idx[y[i]], idx[1 - y[i]]
            j = same[rng.integers(len(same))]
            if j == i:
                j = same[rng.integers(len(same))]
            a += [i, i]; b += [j, diff[rng.integers(len(diff))]]; t += [1.0, 0.0]
    p = rng.permutation(len(a))
    return np.array(a)[p], np.array(b)[p], np.array(t, np.float32)[p]


def train_setfit(model, texts, y, seed, device, iters=10, bs=32, lr=2e-5):
    import torch
    rng = np.random.default_rng(seed)
    a, b, t = setfit_pairs(y, iters, rng)
    steps = math.ceil(len(a) / bs)
    opt = _adamw(model.parameters(), lr, device)
    sch = _schedule(opt, steps)
    model.train()
    for s in range(steps):
        sl = slice(s * bs, (s + 1) * bs)
        batch = [texts[i] for i in a[sl]] + [texts[i] for i in b[sl]]
        with torch.autocast("cuda", dtype=torch.bfloat16, enabled=device == "cuda"):
            e = forward(model, batch, device).float()
        u, v = e[: len(e) // 2], e[len(e) // 2:]
        loss = torch.nn.functional.mse_loss(torch.nn.functional.cosine_similarity(u, v), torch.from_numpy(t[sl]).to(device))
        opt.zero_grad(set_to_none=True); loss.backward(); opt.step(); sch.step()
    model.eval()
    del opt, sch
    free_gpu()
    return steps


def train_ce(model, texts, y, seed, device, epochs=4, bs=32, lr=2e-5, head_lr=1e-3, scale=20.0, n_out=1):
    """Encoder + linear head on the (normalised) sentence embedding.
    n_out=1: binary cross-entropy on y (= label>1)  -> predict() gives P(y>1)
    n_out=5: softmax cross-entropy on y (= label-1) -> predict() gives the (n, 5) label distribution"""
    import torch
    torch.manual_seed(seed)
    dim = model.get_embedding_dimension()
    head = torch.nn.Linear(dim, n_out).to(device)
    opt = _adamw([{"params": model.parameters(), "lr": lr}, {"params": head.parameters(), "lr": head_lr}], lr, device)
    rng = np.random.default_rng(seed)
    steps = epochs * math.ceil(len(y) / bs)
    sch = _schedule(opt, steps)
    yt = torch.from_numpy(y.astype(np.float32 if n_out == 1 else np.int64)).to(device)
    model.train()
    for _ in range(epochs):
        order = rng.permutation(len(y))
        for s in range(0, len(y), bs):
            bi = order[s:s + bs]
            with torch.autocast("cuda", dtype=torch.bfloat16, enabled=device == "cuda"):
                e = forward(model, [texts[i] for i in bi], device).float()
            e = torch.nn.functional.normalize(e, dim=-1)
            out = head(scale * e)
            if n_out == 1:
                loss = torch.nn.functional.binary_cross_entropy_with_logits(out.squeeze(-1), yt[bi])
            else:
                loss = torch.nn.functional.cross_entropy(out, yt[bi])
            opt.zero_grad(set_to_none=True); loss.backward(); opt.step(); sch.step()
    model.eval()
    # optimizer <-> scheduler form a reference cycle: without an explicit delete + gc the Adam states (2x model size)
    # stayed on the GPU into the next training run and MPNet ran out of the 4 GB (ce + ce5 in one process)
    del opt, sch
    free_gpu()

    def predict(tx):
        with torch.no_grad():
            E = torch.from_numpy(encode(model, tx)).to(device)
            out = head(scale * E)
            p = torch.sigmoid(out.squeeze(-1)) if n_out == 1 else torch.softmax(out, dim=-1)
            return p.float().cpu().numpy()
    return predict, steps


# ----------------------------------------------------------------------------------------------- heads / blends
def head_pb(E_fit, f, E_val, t, C=1.0, seed=0):
    oh = OneHotEncoder(handle_unknown="ignore", sparse_output=False).fit(f[["venue", "year"]].astype(str))
    X = np.hstack([2 * E_fit, oh.transform(f[["venue", "year"]].astype(str))])
    Xv = np.hstack([2 * E_val, oh.transform(t[["venue", "year"]].astype(str))])
    lr = LogisticRegression(C=C, max_iter=5000, random_state=seed).fit(X, f["label"].to_numpy() > 1)
    return lr.predict_proba(Xv)[:, 1]


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def blend(p1, p2, w=0.5):
    return 1 / (1 + np.exp(-((1 - w) * logit(p1) + w * logit(p2))))


class ReplaceEmbLogReg(EmbedLogReg):
    """exp003 with one pretrained embedding block replaced (or appended) by a per-fold fine-tuned embedding map."""

    def __init__(self, emb_map: dict, slot: str, **kw):
        super().__init__(**kw)
        self.emb_map, self.slot = emb_map, slot

    def _emb(self, df):
        ft = np.vstack([self.emb_map[int(i)] for i in df["id"]])
        blocks = [ft if e == self.slot else title_embeddings(df, e) for e in self.embs]
        if self.slot not in self.embs:
            blocks.append(ft)
        return np.hstack(blocks) / np.sqrt(len(blocks))


# ----------------------------------------------------------------------------------------------- main loop
def a_oof_cached(tr, seed, k, f, t):
    """exp003 OOF for (seed, fold) — cached so several encoder runs share the same baseline numbers."""
    path = OUT / f"oof_A_s{seed}_f{k}.pkl"
    if path.exists():
        c = pd.read_pickle(path)
        if c["id"].tolist() == t["id"].tolist():
            return c["eg"].to_numpy(), c["pb"].to_numpy()
    eg, pb = EmbedLogReg(seed=0).fit(f).predict(t)
    pd.DataFrame({"id": t["id"].to_numpy(), "eg": eg, "pb": pb}).to_pickle(path)
    return eg, pb


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--enc", default="minilm", choices=sorted(EMB_MODELS))
    ap.add_argument("--seeds", type=int, nargs="+", default=[0])
    ap.add_argument("--folds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    ap.add_argument("--methods", nargs="+", default=["setfit", "ce"], choices=["setfit", "ce", "ce5"])
    ap.add_argument("--no-prefix", action="store_true")
    ap.add_argument("--no-refit", action="store_true", help="skip the A[X] refits (saves CPU time)")
    ap.add_argument("--sf-iters", type=int, default=10)
    ap.add_argument("--ce-epochs", type=int, default=4)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--seed-offset", type=int, default=0, help="changes the fine-tuning seed (for bagging runs)")
    ap.add_argument("--tag", default="")
    a = ap.parse_args()

    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    prefix = not a.no_prefix
    name = f"finetune_{a.enc}{'_' + a.tag if a.tag else ''}"
    print(f"{name}: device={device} ({torch.cuda.get_device_name(0) if device == 'cuda' else 'cpu'}), "
          f"torch {torch.__version__}, prefix={prefix}, args={vars(a)}", flush=True)

    tr, _ = load_all()
    frozen = load_encoder(a.enc, device)
    E_frozen = dict(zip(tr["id"].tolist(), encode(frozen, texts_of(tr, prefix))))
    del frozen
    free_gpu()

    rows, timing = [], []
    for seed in a.seeds:
        for k, (ia, iv) in enumerate(folds(tr, seed)):
            if k not in a.folds:
                continue
            t0 = time.time()
            f, t = tr.iloc[ia], tr.iloc[iv]
            t = t[scored_mask(t)].copy()
            tx_f, tx_t = texts_of(f, prefix), texts_of(t, prefix)
            yb = (f["label"].to_numpy() > 1).astype(int)
            P = {}
            P["A"] = a_oof_cached(tr, seed, k, f, t)
            eg_A, pb_A = P["A"]
            ta = time.time() - t0
            Ef = np.vstack([E_frozen[i] for i in f["id"]]); Et = np.vstack([E_frozen[i] for i in t["id"]])
            P["F0"] = (eg_A, head_pb(Ef, f, Et, t))
            fs = 1000 * seed + k + 100 * a.seed_offset
            info = {"seed": seed, "fold": k, "t_A": round(ta, 1)}
            if "setfit" in a.methods:
                torch.manual_seed(fs)
                m = load_encoder(a.enc, device)
                t1 = time.time(); steps = train_setfit(m, tx_f, yb, fs, device, iters=a.sf_iters, lr=a.lr)
                info.update(t_sf=round(time.time() - t1, 1), sf_steps=steps)
                Ef_sf, Et_sf = encode(m, tx_f), encode(m, tx_t)
                P["SF"] = (eg_A, head_pb(Ef_sf, f, Et_sf, t))
                if not a.no_refit:
                    emap = {**dict(zip(f["id"].tolist(), Ef_sf)), **dict(zip(t["id"].tolist(), Et_sf))}
                    P["A[SF]"] = ReplaceEmbLogReg(emap, a.enc, seed=0).fit(f).predict(t)
                del m
            if "ce" in a.methods:
                torch.manual_seed(fs)
                m = load_encoder(a.enc, device)
                t1 = time.time(); pred, steps = train_ce(m, tx_f, yb, fs, device, epochs=a.ce_epochs, lr=a.lr)
                info.update(t_ce=round(time.time() - t1, 1), ce_steps=steps)
                P["CE"] = (eg_A, pred(tx_t))
                if not a.no_refit:
                    emap = {**dict(zip(f["id"].tolist(), encode(m, tx_f))), **dict(zip(t["id"].tolist(), encode(m, tx_t)))}
                    P["A[CE]"] = ReplaceEmbLogReg(emap, a.enc, seed=0).fit(f).predict(t)
                del m, pred  # pred's closure holds the model
                free_gpu()
            if "ce5" in a.methods:
                torch.manual_seed(fs)
                m = load_encoder(a.enc, device)
                t1 = time.time()
                pred, steps = train_ce(m, tx_f, f["label"].to_numpy() - 1, fs, device, epochs=a.ce_epochs, lr=a.lr, n_out=5)
                info.update(t_ce5=round(time.time() - t1, 1), ce5_steps=steps)
                Pr = pred(tx_t)
                eg5, pb5 = Pr @ GAIN, 1.0 - Pr[:, 0]
                P["CE5"] = (eg_A, pb5)                                  # selection from CE5, ordering from A
                P["CE5own"] = (eg5, pb5)                                # CE5 alone (selection + ordering)
                P["A_eg5"] = ((eg_A + eg5) / 2, pb_A)                   # ordering-only change
                P["A+CE5eg"] = ((eg_A + eg5) / 2, blend(pb_A, pb5))     # selection + ordering blended
                del m, pred
            free_gpu()
            for x in [v for v in ("F0", "SF", "CE", "CE5") if v in P]:
                P[f"A+{x}"] = (eg_A, blend(pb_A, P[x][1]))
            if "SF" in P and "CE" in P:
                P["A+SF+CE"] = (eg_A, (blend(pb_A, P["SF"][1]) + blend(pb_A, P["CE"][1])) / 2)
            yv = t["label"].to_numpy() > 1
            aucs = {v: round(roc_auc_score(yv, pb), 4) for v, (_, pb) in P.items()}
            info.update(t_total=round(time.time() - t0, 1), auc=aucs)
            timing.append(info)
            print(f"[seed {seed} fold {k}] {json.dumps(info)}", flush=True)
            for v, (eg, pb) in P.items():
                rows.append(pd.DataFrame({"variant": v, "seed": seed, "fold": k, "id": t["id"].to_numpy(),
                                          "venue": t["venue"].to_numpy(), "label": t["label"].to_numpy(),
                                          "eg": eg, "pb": pb}))

    o = pd.concat(rows, ignore_index=True)
    o.to_pickle(OUT / f"{name}_oof.pkl")
    summarize(o, name, vars(a), timing)


def summarize(o: pd.DataFrame, name: str, args: dict, timing: list):
    res = {}
    for v, g in o.groupby("variant", sort=False):
        per_seed = []
        for s, gs in g.groupby("seed"):
            if gs["fold"].nunique() > 1:
                per_seed.append(evaluate(gs))
        venue_auc = {vn: round(roc_auc_score(gv.label > 1, gv.pb), 4) for vn, gv in g.groupby("venue")}
        r = {"auc": roc_auc_score(g.label > 1, g.pb), "venue_auc": venue_auc}
        if per_seed:
            r.update({key: float(np.mean([p[key] for p in per_seed])) for key in per_seed[0] if key != "auc"})
            r["honest_per_seed"] = [p["honest"] for p in per_seed]
        res[v] = r
    print(f"\n{name}  seeds={sorted(map(int, o.seed.unique()))} folds={sorted(map(int, o.fold.unique()))}  "
          f"(non-iclp scored, honest threshold, eg from A unless A[X])")
    base = res["A"].get("honest")
    for v, r in res.items():
        h = r.get("honest")
        hs = (f"honest={h:.4f}+-{r['honest_std']:.4f} d={h - base:+.4f} Q={r['Q']:.4f} R={r['R']:.4f} "
              f"fixed0.55={r['fixed055']:.4f}") if h is not None else "honest=n/a"
        print(f"{v:9s} AUC={r['auc']:.4f}  {hs}  venueAUC={r['venue_auc']}")
    (OUT / f"{name}.json").write_text(json.dumps({"args": args, "results": res, "timing": timing}, indent=2), encoding="utf-8")
    print("wrote", OUT / f"{name}.json", flush=True)


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3 and sys.argv[1] == "--summarize":  # re-summarise a saved run: --summarize finetune_minilm
        summarize(pd.read_pickle(OUT / f"{sys.argv[2]}_oof.pkl"), sys.argv[2], {"resummarized": True}, [])
    else:
        main()
