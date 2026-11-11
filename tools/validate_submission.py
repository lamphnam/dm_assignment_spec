#!/usr/bin/env python3
"""Validate a Kaggle submission file for assignment-data-mining-261 WITHOUT submitting it.

Usage:
    python validate_submission.py SUBMISSION.csv [--test data/raw/Test.csv]

Checks FR-01..FR-03 (docs/02-requirements.md) and prints the file's SHA-256 for the
submission tracker. Standard library only. This script never contacts Kaggle.

Exit code: 0 = valid (warnings allowed), 1 = invalid, 2 = file not found.
"""
from __future__ import annotations

import argparse
import collections as C
import csv
import hashlib
import math
import os
import sys


def test_ids(path: str) -> list[str]:
    # The id is always the first field even in the malformed Test.csv (docs/07-data-processing.md §2).
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh))
    if rows[0][:1] != ["id"]:
        raise SystemExit(f"{path}: unexpected header {rows[0][:3]}")
    return [r[0] for r in rows[1:] if r]


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("submission")
    ap.add_argument("--test", default="data/raw/Test.csv")
    a = ap.parse_args()
    for p in (a.submission, a.test):
        if not os.path.isfile(p):
            print(f"ERROR file not found: {p}")
            return 2

    errors, warnings = [], []
    with open(a.submission, "rb") as fh:
        raw = fh.read()
    if raw.startswith(b"\xef\xbb\xbf"):
        errors.append("file starts with a UTF-8 BOM; header would not be exactly 'id,priority'")
    with open(a.submission, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    header, body = (rows[0], rows[1:]) if rows else ([], [])
    if header != ["id", "priority"]:
        errors.append(f"header must be exactly ['id', 'priority'], got {header}")
    bad_width = [i + 2 for i, r in enumerate(body) if len(r) != 2]
    if bad_width:
        errors.append(f"rows without exactly 2 fields at lines {bad_width[:10]}")

    ids = [r[0].strip() for r in body if len(r) == 2]
    expected = test_ids(a.test)
    dup = [i for i, n in C.Counter(ids).items() if n > 1]
    if dup:
        errors.append(f"duplicate ids: {dup[:10]} (total {len(dup)})")
    missing, extra = set(expected) - set(ids), set(ids) - set(expected)
    if missing:
        errors.append(f"{len(missing)} test ids missing, e.g. {sorted(missing)[:5]}")
    if extra:
        errors.append(f"{len(extra)} ids not in Test.csv, e.g. {sorted(extra)[:5]}")
    if len(body) != len(expected):
        errors.append(f"expected {len(expected)} data rows, got {len(body)}")

    prios = []
    for r in body:
        if len(r) != 2:
            continue
        try:
            v = float(r[1])
        except ValueError:
            errors.append(f"id {r[0]}: priority not numeric ({r[1]!r})")
            continue
        if not math.isfinite(v):
            errors.append(f"id {r[0]}: priority not finite ({r[1]!r})")
        elif v < 0:
            errors.append(f"id {r[0]}: negative priority ({r[1]!r})")
        else:
            prios.append(v)
    positive = [v for v in prios if v > 0]
    if prios and not positive:
        errors.append("every priority is 0: empty recommendation list scores 0")
    tied = sum(n for v, n in C.Counter(positive).items() if n > 1)
    if tied:
        warnings.append(f"{tied} positive priorities share a value with another row; "
                        "ties are broken by id as TEXT (docs/08-methodology.md §1)")
    if positive and max(positive) > 10:
        warnings.append("priorities above 10: allowed, but [0, 10] is the recommended scale")

    print(f"file: {a.submission}")
    print(f"sha256: {hashlib.sha256(raw).hexdigest()}")
    print(f"rows: {len(body)}  selected (priority>0): {len(positive)}  share: "
          f"{(len(positive) / len(body)) if body else 0:.3f}")
    for w in warnings:
        print(f"WARNING: {w}")
    for e in errors[:30]:
        print(f"ERROR: {e}")
    if len(errors) > 30:
        print(f"... {len(errors) - 30} more errors")
    print("RESULT: VALID" if not errors else "RESULT: INVALID — do not submit")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
