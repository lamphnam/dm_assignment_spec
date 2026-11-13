"""Official metric. Re-uses tools/score.py (verified against test cases T1-T9) so there is one implementation."""
from __future__ import annotations

import sys

import numpy as np

from src.data import ROOT

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.score import score_split  # noqa: E402


def score_arrays(ids, priority, labels) -> tuple[float, float, float]:
    """(score, Q, R) for one evaluation split given aligned arrays."""
    pred = {str(i): float(p) for i, p in zip(ids, priority)}
    lab = {str(i): int(y) for i, y in zip(ids, labels)}
    return score_split(pred, lab)


def to_priority(expected_gain: np.ndarray, p_worth: np.ndarray, threshold: float) -> np.ndarray:
    """Select papers with P(label>1) >= threshold; order selected papers by expected gain on a [1, 10] scale."""
    eg = np.clip(np.asarray(expected_gain, dtype=float), 0.0, 1.0)
    return np.where(np.asarray(p_worth) >= threshold, 1.0 + 9.0 * eg, 0.0)
