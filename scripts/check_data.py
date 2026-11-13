"""Sanity-check the loader. Optionally compare cleaned text with the leader's copies if leader_csv_file/ exists.

    .venv\\Scripts\\python.exe -m scripts.check_data
"""
from __future__ import annotations

import csv

from src.data import ROOT, clean_text, load_all

train, test = load_all()
print(f"train {train.shape}, test {test.shape}; checksums OK")
print("train labels:", train["label"].value_counts().sort_index().to_dict())
print("test venues :", test["venue"].value_counts().to_dict())
print("empty authors train/test:", int((train["authors"].str.len() == 0).sum()), int((test["authors"].str.len() == 0).sum()))

lead = ROOT / "leader_csv_file"
if lead.exists():
    def rd(n):
        with open(lead / n, encoding="utf-8", newline="") as fh:
            return {int(r[0]): r for r in list(csv.reader(fh))[1:]}
    lt, ls = rd("train.csv"), rd("Test.csv")
    t1 = sum(clean_text(lt[i][1]) == t for i, t in zip(train["id"], train["title"]))
    t2 = sum(clean_text(ls[i][1]) == t for i, t in zip(test["id"], test["title"]))
    lab = sum(int(lt[i][6]) == y for i, y in zip(train["id"], train["label"]))
    print(f"vs leader: train titles {t1}/2494, test titles {t2}/596, train labels {lab}/2494")
