"""Feasibility probe: can public APIs return abstracts for the papers' doi/S2 ids?  TRAIN PAPERS ONLY
(fetching external data for TEST papers is open question Q-07 — ask the lecturer first).

    .venv\\Scripts\\python.exe -m research.abstract_feasibility [n_sample]

Sources (both public, no key needed; cite if used — NFR-06):
- Semantic Scholar Academic Graph API, POST /graph/v1/paper/batch (Kinney et al., 2023, arXiv:2301.10140)
- OpenAlex API, /works?filter=doi:... (Priem et al., 2022, arXiv:2205.01833)
Sends only public paper identifiers. No email / personal data in requests.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request

import numpy as np

from src.data import load_all

UA = {"User-Agent": "course-assignment-feasibility-probe/0.1", "Content-Type": "application/json"}


def s2_id(doi: str) -> str | None:
    if doi.startswith("10."):
        return "DOI:" + doi
    m = re.search(r"semanticscholar\.org/paper/(?:[^/]+/)?([0-9a-f]{40})", doi)
    return m.group(1) if m else None


def s2_batch(ids):
    req = urllib.request.Request("https://api.semanticscholar.org/graph/v1/paper/batch?fields=title,abstract,year,venue,tldr,fieldsOfStudy,citationCount",
                                 data=json.dumps({"ids": ids}).encode(), headers=UA, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def openalex(dois):
    url = "https://api.openalex.org/works?per-page=50&select=doi,title,abstract_inverted_index&filter=doi:" + "|".join(dois)
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA["User-Agent"]}), timeout=60) as r:
        return json.loads(r.read())["results"]


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    tr, _ = load_all()
    smp = tr.sample(n, random_state=0)
    ids = [s2_id(d) for d in smp.doi]
    print(f"sample {n} train papers: doi10={sum(d.startswith('10.') for d in smp.doi)}, s2_url={sum('semanticscholar' in d for d in smp.doi)}, unparsable={ids.count(None)}")
    try:
        res = s2_batch([i for i in ids if i])
        found = [r for r in res if r]
        abst = [r for r in found if r.get("abstract")]
        tldr = [r for r in found if r.get("tldr")]
        print(f"Semantic Scholar: resolved {len(found)}/{len(res)}, with abstract {len(abst)}, with tldr {len(tldr)}")
        from difflib import SequenceMatcher
        titles = [t for t, i in zip(smp.title, ids) if i]  # aligned with the ids actually sent
        norm = lambda s: re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()
        sims = [SequenceMatcher(None, norm(r["title"]), norm(t)).ratio() for r, t in zip(res, titles) if r and r.get("title")]
        print(f"  returned title vs our title similarity: >=0.9 in {sum(s >= 0.9 for s in sims)}/{len(sims)}, min={min(sims):.2f}")
        if abst:
            print("  example abstract:", abst[0]["abstract"][:160].replace("\n", " "), "...")
    except Exception as e:  # rate limit (429) or network
        print("Semantic Scholar error:", repr(e))
    dois = [d for d in smp.doi if d.startswith("10.")]
    try:
        oa = openalex(dois)
        print(f"OpenAlex: {len(oa)}/{len(dois)} DOIs resolved, with abstract {sum(1 for w in oa if w.get('abstract_inverted_index'))}")
    except Exception as e:
        print("OpenAlex error:", repr(e))


if __name__ == "__main__":
    main()
