"""Load the official competition files from data/raw.

- train.csv is standard RFC 4180 CSV.
- Test.csv is NOT quoted (commas inside title/authors split fields). Rows are parsed by anchoring on the
  unique (venue, 4-digit year) pair, see docs/07-data-processing.md §2.
- Text cleaning (deterministic, verified on 2026-11-14 to reproduce the leader's cleaned title/authors exactly):
  HTML-entity unescape, Unicode NFC, collapse whitespace; for Test titles re-insert the space after commas
  that Test.csv stripped ("A,B" -> "A, B"; this restoration is an inference, see docs/05 §6 Q1b).
"""
from __future__ import annotations

import csv
import hashlib
import html
import re
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
VENUES = ("cav", "iclp", "kr", "lics", "lpnmr")
SHA256 = {  # docs/05-dataset-overview.md §1
    "train.csv": "d591c126e1a7554895a72749f04ea95be199526d1b05ebe42803783d8be4822a",
    "Test.csv": "61d655b2512d8bd27ec593e8a149e172e0e3283e618e1ea0b5840e5f717399d6",
    "Submission.csv": "88a1d0ff0b3b00b8a380fe87d1b353e6cdf2045ef06a571c1149e2ffb8e38816",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_checksums(raw: Path = RAW) -> None:
    bad = {n: sha256(raw / n) for n, h in SHA256.items() if sha256(raw / n) != h}
    if bad:
        raise RuntimeError(f"Checksum mismatch (host may have changed files): {bad}")


def clean_text(s: str) -> str:
    return " ".join(unicodedata.normalize("NFC", html.unescape(s)).split())


def restore_comma_space(s: str) -> str:
    return re.sub(r",(?=\S)", ", ", s)


def split_authors(s: str) -> list[str]:
    return [a for a in (clean_text(t) for t in s.split(",")) if a]


def _rows(path: Path) -> list[list[str]]:
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.reader(fh))


def load_train(raw: Path = RAW) -> pd.DataFrame:
    rows = _rows(raw / "train.csv")
    assert rows[0] == ["id", "title", "venue", "year", "authors", "doi", "Label"], rows[0]
    df = pd.DataFrame({
        "id": [int(r[0]) for r in rows[1:]],
        "title": [clean_text(r[1]) for r in rows[1:]],
        "venue": [r[2] for r in rows[1:]],
        "year": [int(r[3]) for r in rows[1:]],
        "authors": [split_authors(r[4]) for r in rows[1:]],
        "doi": [r[5] for r in rows[1:]],
        "label": [int(r[6]) for r in rows[1:]],
    })
    assert len(df) == 2494 and df["id"].is_unique and set(df["venue"]) <= set(VENUES)
    assert df["label"].between(1, 5).all()
    return df


def load_test(raw: Path = RAW) -> pd.DataFrame:
    rows = _rows(raw / "Test.csv")
    assert rows[0] == ["id", "title", "venue", "year", "authors", "doi"], rows[0]
    recs = []
    for f in rows[1:]:
        idx = [i for i in range(2, len(f) - 2) if f[i] in VENUES and re.fullmatch(r"\d{4}", f[i + 1])]
        if len(idx) != 1:
            raise ValueError(f"cannot anchor-parse Test.csv row id={f[0]}: anchors={idx}")
        i = idx[0]
        recs.append({
            "id": int(f[0]),
            "title": restore_comma_space(clean_text(",".join(f[1:i]))),
            "venue": f[i],
            "year": int(f[i + 1]),
            "authors": [a for a in (clean_text(t) for t in f[i + 2:-1]) if a],
            "doi": f[-1],
        })
    df = pd.DataFrame(recs)
    assert len(df) == 596 and df["id"].is_unique
    assert df["venue"].value_counts().to_dict() == {"cav": 221, "lics": 187, "kr": 151, "lpnmr": 37}
    return df


def load_all(raw: Path = RAW, check: bool = True) -> tuple[pd.DataFrame, pd.DataFrame]:
    if check:
        verify_checksums(raw)
    train, test = load_train(raw), load_test(raw)
    assert not set(train["id"]) & set(test["id"])
    return train, test


def title_key(t: str) -> str:
    """Normalised title used to keep duplicate titles in the same CV fold."""
    return " ".join(re.sub(r"[^a-z0-9]+", " ", t.lower()).split())
