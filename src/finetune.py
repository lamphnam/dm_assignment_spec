"""Supervised fine-tuning of pretrained sentence encoders on paper titles (classification, FR-04).

Used by `FineTuneEnsemble` (model `ft_ens_v1` in src/models.py). The training procedure mirrors
research/finetune_cv.py::train_ce, which produced the CV evidence (experiments/EXPERIMENTS.md, EXP-004):
  input text  "<venue> <year>: <title>"
  network     pretrained encoder (sentence-transformers) -> L2-normalised sentence embedding -> linear head
  loss        binary cross-entropy on label>1 (n_out=1) or softmax cross-entropy on labels 1..5 (n_out=5)
  optimiser   AdamW (lr 2e-5 encoder, 1e-3 head, weight decay 0.01), 4 epochs, batch 32, linear warmup 10% + decay,
              bf16 autocast on CUDA.
Fitting only ever sees the training data passed to fit() (a CV training fold, or the full train for the final model).

External resources (NFR-06): sentence-transformers (Reimers & Gurevych, 2019); PyTorch; pretrained checkpoints
listed in src/embeddings.py::MODELS, downloaded from the Hugging Face Hub.
"""
from __future__ import annotations

import math
import os

import numpy as np
import pandas as pd

# deterministic cuBLAS (must be set before CUDA initialises); see torch docs "Reproducibility"
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")


def texts_of(df: pd.DataFrame) -> list[str]:
    return [f"{v} {y}: {t}" for v, y, t in zip(df["venue"], df["year"], df["title"])]


def _device() -> str:
    import torch
    return "cuda" if torch.cuda.is_available() else "cpu"


def _free_gpu():
    import gc

    import torch
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


class FineTunedEncoder:
    """One encoder + linear head fine-tuned on (texts, y). Kept on CPU between calls so several fit in memory."""

    def __init__(self, key: str, n_out: int = 1, epochs: int = 4, bs: int = 32, lr: float = 2e-5,
                 head_lr: float = 1e-3, scale: float = 20.0, seed: int = 0):
        self.key, self.n_out, self.epochs, self.bs, self.lr = key, n_out, epochs, bs, lr
        self.head_lr, self.scale, self.seed = head_lr, scale, seed

    def fit(self, texts: list[str], y: np.ndarray) -> "FineTunedEncoder":
        import torch
        from sentence_transformers import SentenceTransformer

        from src.embeddings import MODELS
        dev = _device()
        torch.manual_seed(self.seed)
        torch.use_deterministic_algorithms(True, warn_only=True)
        model = SentenceTransformer(MODELS[self.key], device=dev, model_kwargs={"torch_dtype": torch.float32})
        head = torch.nn.Linear(model.get_embedding_dimension(), self.n_out).to(dev)
        opt = torch.optim.AdamW([{"params": model.parameters(), "lr": self.lr},
                                 {"params": head.parameters(), "lr": self.head_lr}],
                                lr=self.lr, weight_decay=0.01, fused=dev == "cuda")
        steps = self.epochs * math.ceil(len(y) / self.bs)
        warm = max(1, int(steps * 0.1))
        sch = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min((s + 1) / warm, max(0.0, (steps - s) / max(1, steps - warm))))
        yt = torch.from_numpy(y.astype(np.float32 if self.n_out == 1 else np.int64)).to(dev)
        rng = np.random.default_rng(self.seed)
        model.train()
        for _ in range(self.epochs):
            order = rng.permutation(len(y))
            for s in range(0, len(y), self.bs):
                bi = order[s:s + self.bs]
                feats = model.preprocess([texts[i] for i in bi])
                feats = {k: (v.to(dev) if hasattr(v, "to") else v) for k, v in feats.items()}
                with torch.autocast("cuda", dtype=torch.bfloat16, enabled=dev == "cuda"):
                    e = model(feats)["sentence_embedding"].float()
                out = head(self.scale * torch.nn.functional.normalize(e, dim=-1))
                if self.n_out == 1:
                    loss = torch.nn.functional.binary_cross_entropy_with_logits(out.squeeze(-1), yt[bi])
                else:
                    loss = torch.nn.functional.cross_entropy(out, yt[bi])
                opt.zero_grad(set_to_none=True); loss.backward(); opt.step(); sch.step()
        model.eval()
        # optimizer <-> scheduler form a reference cycle; delete both and collect so the Adam states leave the GPU
        del opt, sch
        self.model_, self.head_ = model.to("cpu"), head.to("cpu")
        _free_gpu()
        return self

    def predict(self, texts: list[str]) -> np.ndarray:
        """n_out=1: P(label>1), shape (n,);  n_out=5: label distribution, shape (n, 5)."""
        import torch
        dev = _device()
        self.model_.to(dev); self.head_.to(dev)
        with torch.no_grad():
            E = self.model_.encode(texts, batch_size=128, normalize_embeddings=True, show_progress_bar=False,
                                   convert_to_tensor=True).float().to(dev)
            out = self.head_(self.scale * E)
            p = torch.sigmoid(out.squeeze(-1)) if self.n_out == 1 else torch.softmax(out, dim=-1)
            p = p.float().cpu().numpy()
        self.model_.to("cpu"); self.head_.to("cpu")
        _free_gpu()
        return p
