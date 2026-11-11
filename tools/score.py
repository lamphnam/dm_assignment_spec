#!/usr/bin/env python3
"""Reference implementation of the competition metric (docs/reference/competition-pages/evaluation.md).

Standard library only. Subcommands:

  selftest                         run the documented test cases T1-T8 (docs/11-testing-evaluation.md §1)
  score  --pred P.csv --labels L.csv [--split-size 298 --n-subsets 200 --seed 0]
                                   score a prediction file (id,priority) against LOCAL labels (id,Label),
                                   e.g. a validation fold built from train.csv. Never use hidden test labels.
  bounds --train train.csv [--split-size 298 --n-subsets 200 --seed 0]
                                   reproduce the reference points in .claude/skills/validation-and-scoring/references/interpretation.md.
                                   Rows marked ORACLE use true labels: they are UNREACHABLE upper bounds,
                                   not baselines.

Library use:  from score import score_split
"""
from __future__ import annotations

import argparse
import csv
import math
import random
import statistics as st
import sys


def order_ids(pred: dict[str, float]) -> list[str]:
    """Drop priority 0, sort by priority desc, ties by id ascending AS TEXT."""
    chosen = [(i, p) for i, p in pred.items() if p > 0]
    chosen.sort(key=lambda t: (-t[1], str(t[0])))
    return [i for i, _ in chosen]


def score_split(pred: dict[str, float], labels: dict[str, int]) -> tuple[float, float, float]:
    """Return (score, Q, R) for one split. `pred` and `labels` must cover the same ids."""
    if set(pred) != set(labels):
        raise ValueError("pred and labels must contain exactly the same ids")
    for i, p in pred.items():
        if not (isinstance(p, (int, float)) and math.isfinite(p) and p >= 0):
            raise ValueError(f"invalid priority for id {i}: {p!r}")
    ranked = order_ids(pred)
    if ranked:
        w = [1.0 / math.log2(r + 1) for r in range(1, len(ranked) + 1)]
        q = sum(wi * (labels[i] - 1) / 4 for wi, i in zip(w, ranked)) / sum(w)
    else:
        q = 0.0
    positives = sum(1 for y in labels.values() if y > 1)
    r = (sum(1 for i in ranked if labels[i] > 1) / positives) if positives else 0.0
    s = 0.0 if q == 0 or r == 0 else 2 * q * r / (q + r)
    return s, q, r


def _from_order(order_labels, split_labels):
    """Helper for tests: build pred/labels from labels listed in recommendation order."""
    labels, pred = {}, {}
    for k, y in enumerate(order_labels):
        labels[f"r{k:04d}"] = y
        pred[f"r{k:04d}"] = float(len(order_labels) - k)
    remaining = list(split_labels)
    for y in order_labels:
        remaining.remove(y)
    for k, y in enumerate(remaining):
        labels[f"x{k:04d}"] = y
        pred[f"x{k:04d}"] = 0.0
    return pred, labels


def selftest() -> int:
    cases = [
        ("T1", [5], [5], (1.0, 1.0, 1.0)),
        ("T2", [1], [1, 2], (0.0, 0.0, 0.0)),
        ("T3", [5, 1], [5, 1, 3], (0.550823, 0.613147, 0.5)),
        ("T4", [1, 5], [5, 1, 3], (0.436209, 0.386853, 0.5)),
        ("T5", [3, 3, 2], [3, 3, 2, 1, 1], (0.612403, 0.441340, 1.0)),
        ("T6", [], [2, 3], (0.0, 0.0, 0.0)),
    ]
    ok = True
    for name, order, split, (es, eq, er) in cases:
        s, q, r = score_split(*_from_order(order, split))
        good = all(abs(a - b) < 5e-7 for a, b in ((s, es), (q, eq), (r, er)))
        ok &= good
        print(f"{'PASS' if good else 'FAIL'} {name}: score={s:.6f} Q={q:.6f} R={r:.6f}")
    s7 = 2 * 0.8 * 0.6 / (0.8 + 0.6)
    good = abs(s7 - 0.685714) < 5e-7
    ok &= good
    print(f"{'PASS' if good else 'FAIL'} T7: harmonic mean(0.80, 0.60) = {s7:.6f}")
    got = order_ids({"10": 1.0, "9": 1.0, "1000": 1.0, "713": 1.0})
    good = got == ["10", "1000", "713", "9"]
    ok &= good
    print(f"{'PASS' if good else 'FAIL'} T8: tie-break order {got}")
    try:
        score_split({"a": -1.0}, {"a": 2})
        print("FAIL T9: negative priority accepted"); ok = False
    except ValueError:
        print("PASS T9: negative priority rejected")
    print("ALL PASS" if ok else "SOME TESTS FAILED")
    return 0 if ok else 1


def _read_pred(path):
    with open(path, encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        if rd.fieldnames != ["id", "priority"]:
            raise SystemExit(f"{path}: header must be exactly id,priority (got {rd.fieldnames})")
        out = {}
        for row in rd:
            if row["id"] in out:
                raise SystemExit(f"{path}: duplicate id {row['id']}")
            out[row["id"]] = float(row["priority"])
        return out


def _read_labels(path):
    with open(path, encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        col = "Label" if "Label" in rd.fieldnames else "label"
        return {row["id"]: int(row[col]) for row in rd}


def _subsets(ids, size, n, seed):
    rng = random.Random(seed)
    ids = sorted(ids)
    if size <= 0 or size >= len(ids):
        return [ids]
    return [rng.sample(ids, size) for _ in range(n)]


def _summ(rows):
    return {k: (st.mean(v), st.pstdev(v)) for k, v in zip(("score", "Q", "R"), zip(*rows))}


def cmd_score(a) -> int:
    pred, labels = _read_pred(a.pred), _read_labels(a.labels)
    if set(pred) != set(labels):
        raise SystemExit(f"id mismatch: {len(set(pred) - set(labels))} pred-only, {len(set(labels) - set(pred))} label-only")
    rows = [score_split({i: pred[i] for i in sub}, {i: labels[i] for i in sub})
            for sub in _subsets(labels, a.split_size, a.n_subsets, a.seed)]
    for k, (m, s) in _summ(rows).items():
        print(f"{k}: mean={m:.5f} std={s:.5f}")
    print(f"subsets={len(rows)} size={len(rows and _subsets(labels, a.split_size, 1, a.seed)[0])} seed={a.seed} "
          f"selected_share={sum(1 for p in pred.values() if p > 0)/len(pred):.3f}")
    return 0


def cmd_bounds(a) -> int:
    labels = _read_labels(a.train)
    rng = random.Random(a.seed)
    subs = _subsets(labels, a.split_size, a.n_subsets, a.seed)
    strategies = {
        "recommend-all, random order (achievable floor)": lambda ids: {i: rng.random() + 1e-9 for i in ids},
        "recommend-all, constant priority (id-text tie-break)": lambda ids: {i: 1.0 for i in ids},
        "ORACLE recommend-all sorted by true label (unreachable)": lambda ids: {i: float(labels[i]) for i in ids},
        "ORACLE drop label 1, sort by true label (unreachable)":
            lambda ids: {i: (float(labels[i]) if labels[i] > 1 else 0.0) for i in ids},
    }
    print(f"train-label subsets: n={len(subs)} size={len(subs[0])} seed={a.seed}  (estimates on TRAIN labels, not test)")
    for name, fn in strategies.items():
        rows = [score_split(fn(sub), {i: labels[i] for i in sub}) for sub in subs]
        s = _summ(rows)
        print(f"{name:58s} score={s['score'][0]:.4f}±{s['score'][1]:.4f}  Q={s['Q'][0]:.4f}  R={s['R'][0]:.4f}")
    return 0


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("selftest")
    for name in ("score", "bounds"):
        p = sp.add_parser(name)
        if name == "score":
            p.add_argument("--pred", required=True)
            p.add_argument("--labels", required=True)
        else:
            p.add_argument("--train", required=True)
        p.add_argument("--split-size", type=int, default=298, help="0 = score the whole file as one split")
        p.add_argument("--n-subsets", type=int, default=200)
        p.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    return {"selftest": lambda: selftest(), "score": lambda: cmd_score(a), "bounds": lambda: cmd_bounds(a)}[a.cmd]()


if __name__ == "__main__":
    sys.exit(main())
