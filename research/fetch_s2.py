"""Fetch abstracts/TLDRs from the Semantic Scholar Academic Graph API (public, no key) into data/external/ (gitignored).

    .venv\\Scripts\\python.exe -m research.fetch_s2 train          # allowed: external public data for TRAIN papers
    .venv\\Scripts\\python.exe -m research.fetch_s2 test --i-asked-q07   # only after the lecturer answers Q-07

Cite: Kinney et al. (2023) "The Semantic Scholar Open Data Platform", arXiv:2301.10140. Sends only public paper ids.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request

from research.abstract_feasibility import UA, s2_id
from src.data import ROOT, load_all

OUT = ROOT / "data" / "external"
FIELDS = "title,abstract,tldr,year,venue,fieldsOfStudy,citationCount,publicationTypes"


def post(ids, tries=6):
    url = f"https://api.semanticscholar.org/graph/v1/paper/batch?fields={FIELDS}"
    for k in range(tries):
        try:
            req = urllib.request.Request(url, data=json.dumps({"ids": ids}).encode(), headers=UA, method="POST")
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and k < tries - 1:
                wait = 5 * 2 ** k
                print(f"  429 rate limited, retry in {wait}s", flush=True)
                time.sleep(wait)
                continue
            raise


def main():
    split = sys.argv[1] if len(sys.argv) > 1 else "train"
    if split == "test" and "--i-asked-q07" not in sys.argv:
        raise SystemExit("Refusing: external data for TEST papers is open question Q-07 (docs/13). Ask the lecturer first.")
    tr, te = load_all()
    df = tr if split == "train" else te
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"s2_{split}.jsonl"
    rows = [(int(i), s2_id(d)) for i, d in zip(df.id, df.doi)]
    todo = [(i, s) for i, s in rows if s]
    print(f"{split}: {len(rows)} papers, {len(todo)} with a usable id", flush=True)
    n_found = n_abs = n_tldr = 0
    with open(path, "w", encoding="utf-8") as fh:
        for b in range(0, len(todo), 500):
            chunk = todo[b:b + 500]
            res = post([s for _, s in chunk])
            for (i, s), r in zip(chunk, res):
                rec = {"id": i, "query": s, "found": r is not None}
                if r:
                    n_found += 1
                    n_abs += bool(r.get("abstract")); n_tldr += bool(r.get("tldr"))
                    rec.update({k: r.get(k) for k in ("title", "abstract", "year", "venue", "fieldsOfStudy", "citationCount", "publicationTypes")})
                    rec["tldr"] = (r.get("tldr") or {}).get("text")
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(f"  batch {b // 500 + 1}: {b + len(chunk)}/{len(todo)}", flush=True)
            time.sleep(3)
    print(f"done -> {path}: found {n_found}/{len(todo)}, abstract {n_abs}, tldr {n_tldr}, fetched {time.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
