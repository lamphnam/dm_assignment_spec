"""Models. Each model exposes fit(train_df) and predict(df) -> (expected_gain, p_worth).

expected_gain = E[(y-1)/4]   (the metric's gain)
p_worth       = P(y > 1)     (used for selection)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

GAIN = np.array([0.0, 0.25, 0.5, 0.75, 1.0])


class VenueMean:
    """Baseline (not a taught method): every paper gets its venue's train statistics."""

    name = "venue_mean"

    def __init__(self, seed: int = 0):
        self.seed = seed  # unused; uniform constructor

    def fit(self, df: pd.DataFrame) -> "VenueMean":
        g = (df["label"] - 1) / 4
        self.eg_ = g.groupby(df["venue"]).mean().to_dict()
        self.pw_ = (df["label"] > 1).groupby(df["venue"]).mean().to_dict()
        self.eg0_, self.pw0_ = g.mean(), (df["label"] > 1).mean()
        return self

    def predict(self, df: pd.DataFrame):
        eg = df["venue"].map(self.eg_).fillna(self.eg0_).to_numpy(float)
        pw = df["venue"].map(self.pw_).fillna(self.pw0_).to_numpy(float)
        return eg, pw


def _identity(tokens):
    return [t.lower() for t in tokens]


class LogRegText:
    """Classification (taught method, FR-04): multinomial logistic regression over labels 1..5.

    Features: TF-IDF of title (word 1-2 grams), venue one-hot, year one-hot, author indicators.
    Fitted on the training fold only (no test metadata used).
    """

    name = "logreg_text"

    def __init__(self, C: float = 1.0, seed: int = 0):
        self.C, self.seed = C, seed

    def _pipeline(self) -> Pipeline:
        feats = ColumnTransformer([
            ("title", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, strip_accents="unicode"), "title"),
            ("venue", OneHotEncoder(handle_unknown="ignore"), ["venue"]),
            ("year", OneHotEncoder(handle_unknown="ignore"), ["year"]),
            ("authors", CountVectorizer(analyzer=_identity, binary=True, min_df=2), "authors"),
        ])
        clf = LogisticRegression(C=self.C, max_iter=5000, random_state=self.seed)
        return Pipeline([("features", feats), ("clf", clf)])

    def fit(self, df: pd.DataFrame) -> "LogRegText":
        self.pipe_ = self._pipeline().fit(df[["title", "venue", "year", "authors"]], df["label"])
        return self

    def predict(self, df: pd.DataFrame):
        proba = self.pipe_.predict_proba(df[["title", "venue", "year", "authors"]])
        classes = list(self.pipe_.named_steps["clf"].classes_)
        full = np.zeros((len(df), 5))
        for j, c in enumerate(classes):
            full[:, c - 1] = proba[:, j]
        return full @ GAIN, 1.0 - full[:, 0]


def _author_stats(fit_df: pd.DataFrame):
    g = ((fit_df["label"] - 1) / 4).to_numpy()
    w = (fit_df["label"] > 1).to_numpy().astype(float)
    S, W, N = {}, {}, {}
    for auths, gi, wi in zip(fit_df["authors"], g, w):
        for a in sorted({x.lower() for x in auths}):
            S[a] = S.get(a, 0.0) + gi; W[a] = W.get(a, 0.0) + wi; N[a] = N.get(a, 0) + 1
    return S, W, N, g, w


def author_target_features(stats, tgt_df: pd.DataFrame, loo: bool, m: float = 3.0) -> np.ndarray:
    """Smoothed per-author mean gain / worth-rate learned from the training fold only.
    loo=True when tgt_df IS the fitting set: each paper's own label is removed (leave-one-out) to avoid leakage."""
    S, W, N, g, w = stats
    pg, pw = g.mean(), w.mean()
    rows = []
    for k, auths in enumerate(tgt_df["authors"]):
        gs, ws, ns = [], [], []
        # sorted(): set iteration order of str depends on per-process hash randomisation, which changed float
        # summation order and made outputs differ (~1e-5) between runs
        for a in sorted({x.lower() for x in auths}):
            s, ww, n = S.get(a, 0.0), W.get(a, 0.0), N.get(a, 0)
            if loo:
                s, ww, n = s - g[k], ww - w[k], n - 1
            if n > 0:
                gs.append((s + m * pg) / (n + m)); ws.append((ww + m * pw) / (n + m)); ns.append(n)
        rows.append([max(gs) if gs else pg, np.mean(gs) if gs else pg, max(ws) if ws else pw,
                     min(ws) if ws else pw, np.log1p(sum(ns)), float(bool(gs)), float(len(auths) == 0)])
    return np.array(rows, float)


def knn_features(E_fit: np.ndarray, y_fit: np.ndarray, E_tgt: np.ndarray, k: int = 20, loo: bool = False) -> np.ndarray:
    """Similarity-weighted label statistics of the k most similar TRAINING papers (cosine on normalised embeddings)."""
    S = E_tgt @ E_fit.T
    if loo:
        np.fill_diagonal(S, -np.inf)
    idx = np.argpartition(-S, k, axis=1)[:, :k]
    sims = np.take_along_axis(S, idx, 1); ys = y_fit[idx]
    wts = np.maximum(sims, 0) + 1e-6
    feats = [(wts * (ys - 1) / 4).sum(1) / wts.sum(1), (wts * (ys > 1)).sum(1) / wts.sum(1), sims.mean(1)]
    for lab in (1, 5):
        Sl = np.where(y_fit[None, :] == lab, S, -np.inf)
        feats.append(np.sort(Sl, axis=1)[:, -5:].mean(1))
    return np.column_stack(feats)


class EmbedLogReg:
    """Classification (FR-04): two logistic regressions on the same features.
    - multinomial over labels 1..5  -> expected gain (ordering)
    - binary label>1                -> P(worthwhile) (selection)
    Features: title word+char TF-IDF, venue/year one-hot, author indicators, author target stats (train fold only,
    leave-one-out), pretrained title embeddings (src/embeddings.py) and kNN label stats over embeddings.
    """

    def __init__(self, embs=("minilm", "mpnet", "specter"), ew: float = 2.0, k: int = 20, C: float = 1.0,
                 bin_C: float = 1.0, seed: int = 0):
        self.embs, self.ew, self.k, self.C, self.bin_C, self.seed = tuple(embs), ew, k, C, bin_C, seed
        self.name = f"embed_logreg[{'+'.join(self.embs)}]"

    def _emb(self, df):
        from src.embeddings import title_embeddings
        return np.hstack([title_embeddings(df, e) for e in self.embs]) / np.sqrt(len(self.embs))

    def _transform(self, df, fitting: bool):
        from scipy import sparse
        if fitting:
            self.word_ = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, strip_accents="unicode").fit(df["title"])
            self.char_ = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=3, sublinear_tf=True,
                                         strip_accents="unicode", max_features=30000).fit(df["title"])
            self.cat_ = OneHotEncoder(handle_unknown="ignore").fit(df[["venue", "year"]].astype(str))
            self.auth_ = CountVectorizer(analyzer=_identity, binary=True, min_df=2).fit(df["authors"])
            self.stats_ = _author_stats(df)
            self.E_fit_, self.y_fit_ = self._emb(df), df["label"].to_numpy()
        E = self._emb(df)
        dense = np.hstack([author_target_features(self.stats_, df, loo=fitting),
                           knn_features(self.E_fit_, self.y_fit_, E, self.k, loo=fitting)])
        if fitting:
            self.mu_, self.sd_ = dense.mean(0), dense.std(0) + 1e-9
        dense = (dense - self.mu_) / self.sd_
        return sparse.hstack([
            self.word_.transform(df["title"]), self.char_.transform(df["title"]),
            self.cat_.transform(df[["venue", "year"]].astype(str)), self.auth_.transform(df["authors"]),
            sparse.csr_matrix(dense), sparse.csr_matrix(self.ew * E),
        ]).tocsr()

    def fit(self, df: pd.DataFrame) -> "EmbedLogReg":
        X, y = self._transform(df, fitting=True), df["label"].to_numpy()
        self.multi_ = LogisticRegression(C=self.C, max_iter=5000, random_state=self.seed).fit(X, y)
        self.bin_ = LogisticRegression(C=self.bin_C, max_iter=5000, random_state=self.seed).fit(X, y > 1)
        return self

    def predict(self, df: pd.DataFrame):
        X = self._transform(df, fitting=False)
        P = self.multi_.predict_proba(X)
        full = np.zeros((len(df), 5))
        for j, c in enumerate(self.multi_.classes_):
            full[:, c - 1] = P[:, j]
        return full @ GAIN, self.bin_.predict_proba(X)[:, 1]


def _embed_v1(seed: int = 0):
    return EmbedLogReg(embs=("minilm", "mpnet", "specter"), ew=2.0, seed=seed)


def _logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


class FineTuneEnsemble:
    """Classification (FR-04) with fine-tuned sentence encoders (src/finetune.py), built on exp003.

    - selection  P(label>1) = sigmoid(mean of logits) of binary fine-tuned encoders `sel`
                 (+ exp003's binary head when use_a=True)
    - ordering   expected gain = mean of exp003's E[gain] and the E[gain] of 5-class fine-tuned encoders `eg`
    Every component is fitted on the data given to fit() only (a CV training fold, or the full train).
    Needs PyTorch; a CUDA GPU makes it practical (~2 min per fit on an RTX 3050 Laptop, much longer on CPU).
    """

    def __init__(self, sel=("minilm", "mpnet", "specter", "scincl"), eg=("minilm", "mpnet"), use_a: bool = True,
                 n_bag: int = 1, seed: int = 0):
        self.sel, self.eg, self.use_a, self.n_bag, self.seed = tuple(sel), tuple(eg), use_a, n_bag, seed
        self.name = (f"ft_ens[sel={'+'.join(self.sel)}{'+A' if use_a else ''} x{n_bag};"
                     f"eg=A+{'+'.join(self.eg)}]")

    def fit(self, df: pd.DataFrame) -> "FineTuneEnsemble":
        from src.finetune import FineTunedEncoder, texts_of
        self.a_ = EmbedLogReg(seed=0).fit(df)
        tx, y = texts_of(df), df["label"].to_numpy()
        # bag b uses fine-tuning seed  seed + 100*b  (different initialisation of the head and batch order)
        self.sel_ = [FineTunedEncoder(k, n_out=1, seed=self.seed + 100 * b).fit(tx, (y > 1).astype(int))
                     for k in self.sel for b in range(self.n_bag)]
        self.eg_ = [FineTunedEncoder(k, n_out=5, seed=self.seed).fit(tx, y - 1) for k in self.eg]
        return self

    def predict(self, df: pd.DataFrame):
        from src.finetune import texts_of
        eg_a, pb_a = self.a_.predict(df)
        tx = texts_of(df)
        logits = [_logit(m.predict(tx)) for m in self.sel_] + ([_logit(pb_a)] if self.use_a else [])
        pb = 1.0 / (1.0 + np.exp(-np.mean(logits, axis=0)))
        eg = np.mean([eg_a] + [m.predict(tx) @ GAIN for m in self.eg_], axis=0)
        return eg, pb


def _ft_ens_v1(seed: int = 0):
    """EXP-004 candidate C1: selection = exp003 + 4 fine-tuned binary encoders; ordering = exp003 + 2 CE5 encoders."""
    return FineTuneEnsemble(use_a=True, n_bag=1, seed=seed)


def _ft_ens_v1_bag2(seed: int = 0):
    """C1 with two fine-tuning seeds per selection encoder."""
    return FineTuneEnsemble(use_a=True, n_bag=2, seed=seed)


MODELS = {"venue_mean": VenueMean, "logreg_text": LogRegText, "embed_v1": _embed_v1,
          "ft_ens_v1": _ft_ens_v1, "ft_ens_v1_bag2": _ft_ens_v1_bag2}
