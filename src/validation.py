"""Validation protocol (fixed for every method so comparisons are fair, NFR-02).

- StratifiedGroupKFold (5 folds) on label, grouped by normalised title so duplicate titles stay in one fold.
- Repeated with seeds 0, 1, 2  ->  15 folds.
- Models train on all training-fold papers (including iclp) but each fold is SCORED only on its non-iclp papers,
  because Test.csv contains no iclp (docs/05 §5). Each scored fold has ~400 papers (official splits: 298).
- `id` is not used as a feature (Q-10 unresolved).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

from src.data import title_key

N_SPLITS = 5
SEEDS = (0, 1, 2)


def folds(train: pd.DataFrame, seed: int, n_splits: int = N_SPLITS):
    groups = train["title"].map(title_key).to_numpy()
    skf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    yield from skf.split(np.zeros(len(train)), train["label"].to_numpy(), groups)


def scored_mask(df: pd.DataFrame) -> np.ndarray:
    return (df["venue"] != "iclp").to_numpy()
