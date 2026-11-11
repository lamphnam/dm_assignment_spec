#!/usr/bin/env python3
"""Read-only integrity inspection for the assignment-data-mining-261 competition files.

Usage:
    python inspect_data.py [DATA_DIR] [--json OUT.json] [--no-expect]

DATA_DIR must contain train.csv, Test.csv, Submission.csv (default: data/raw).
The script never modifies input files. Standard library only (Python >= 3.9).

Exit code: 0 if every check PASSes, 1 if any FAIL, 2 if files are missing.
Expected values come from docs/05-dataset-overview.md (snapshot 2026-11-11).
Use --no-expect to skip comparisons with that snapshot (e.g. after the host updates data).
"""
from __future__ import annotations

import argparse
import collections as C
import csv
import hashlib
import html
import json
import math
import os
import re
import sys

VENUES = {"kr", "cav", "lics", "iclp", "lpnmr"}
EXPECTED = {
    "sha256": {
        "train.csv": "d591c126e1a7554895a72749f04ea95be199526d1b05ebe42803783d8be4822a",
        "Test.csv": "61d655b2512d8bd27ec593e8a149e172e0e3283e618e1ea0b5840e5f717399d6",
        "Submission.csv": "88a1d0ff0b3b00b8a380fe87d1b353e6cdf2045ef06a571c1149e2ffb8e38816",
    },
    "n_train": 2494,
    "n_test": 596,
    "labels": {1: 903, 2: 514, 3: 438, 4: 367, 5: 272},
    "test_venues": {"cav": 221, "lics": 187, "kr": 151, "lpnmr": 37},
    "empty_authors": {"train": 192, "test": 41},
}

results: list[dict] = []  # {"check", "status", "detail"}


def record(check: str, ok: bool | None, detail: str = "") -> None:
    status = "PASS" if ok else ("INFO" if ok is None else "FAIL")
    results.append({"check": check, "status": status, "detail": detail})
    print(f"[{status}] {check}" + (f" — {detail}" if detail else ""))


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def read_rows(path: str) -> list[list[str]]:
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.reader(fh))


def parse_test_rows(rows: list[list[str]]):
    """Anchor on the unique (venue, 4-digit year) pair; see docs/07-data-processing.md §2."""
    parsed, bad = [], []
    for f in rows:
        idx = [i for i in range(2, len(f) - 2) if f[i] in VENUES and re.fullmatch(r"\d{4}", f[i + 1])]
        if len(idx) != 1:
            bad.append((f[:3], idx))
            continue
        i = idx[0]
        parsed.append({
            "id": f[0], "title": ",".join(f[1:i]), "venue": f[i], "year": f[i + 1],
            "authors_raw": ",".join(f[i + 2:-1]), "author_tokens": f[i + 2:-1], "doi": f[-1], "n_fields": len(f),
        })
    return parsed, bad


def title_norm(t: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", html.unescape(t).lower()).split())


def authors_list(s: str) -> list[str]:
    return [a.strip() for a in html.unescape(s).split(",") if a.strip()]


def spearman(x: list[float], y: list[float]) -> float | None:
    def ranks(v):
        order = sorted(range(len(v)), key=lambda k: v[k])
        r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2
            i = j + 1
        return r
    if len(x) < 3:
        return None
    rx, ry = ranks(x), ranks(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sxx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    syy = math.sqrt(sum((b - my) ** 2 for b in ry))
    return None if sxx == 0 or syy == 0 else sxy / (sxx * syy)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("data_dir", nargs="?", default="data/raw")
    ap.add_argument("--json", dest="json_out")
    ap.add_argument("--no-expect", action="store_true", help="skip comparisons with the 2026-11-11 snapshot")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    exp = not a.no_expect
    paths = {n: os.path.join(a.data_dir, n) for n in ("train.csv", "Test.csv", "Submission.csv")}
    missing = [n for n, p in paths.items() if not os.path.isfile(p)]
    if missing:
        print(f"Missing files in {a.data_dir}: {missing}. See docs/10-development-guide.md §3.")
        return 2

    print("== 1. Checksums ==")
    for n, p in paths.items():
        h = sha256(p)
        record(f"sha256 {n}", (h == EXPECTED["sha256"][n]) if exp else None, h)

    print("\n== 2. train.csv schema ==")
    tr = read_rows(paths["train.csv"])
    th, tb = tr[0], tr[1:]
    record("train header", th == ["id", "title", "venue", "year", "authors", "doi", "Label"], str(th))
    record("train every row has 7 fields", all(len(r) == 7 for r in tb), str(C.Counter(len(r) for r in tb)))
    T = [dict(zip(th, r)) for r in tb if len(r) == 7]
    record("train row count", (len(T) == EXPECTED["n_train"]) if exp else None, str(len(T)))
    record("train id/year integers", all(r["id"].isdigit() and re.fullmatch(r"\d{4}", r["year"]) for r in T))
    labels = C.Counter(int(r["Label"]) for r in T if r["Label"] in {"1", "2", "3", "4", "5"})
    record("train Label in 1..5", sum(labels.values()) == len(T), str(dict(sorted(labels.items()))))
    if exp:
        record("train Label distribution matches snapshot", dict(labels) == EXPECTED["labels"])
    record("train venues subset of known 5", {r["venue"] for r in T} <= VENUES, str(sorted({r['venue'] for r in T})))
    ids_tr = [int(r["id"]) for r in T]
    record("train ids unique", len(set(ids_tr)) == len(ids_tr))
    record("train file sorted by id", ids_tr == sorted(ids_tr))
    empty_tr = sum(1 for r in T if not r["authors"].strip())
    record("train empty authors", (empty_tr == EXPECTED["empty_authors"]["train"]) if exp else None, str(empty_tr))

    print("\n== 3. Test.csv parsing and field boundaries ==")
    te = read_rows(paths["Test.csv"])
    teh, teb = te[0], te[1:]
    raw = open(paths["Test.csv"], "rb").read()
    record("test header", teh == ["id", "title", "venue", "year", "authors", "doi"], str(teh))
    record("test raw field-count distribution", None, str(dict(sorted(C.Counter(len(r) for r in teb).items()))))
    record("test contains no ', ' (spaces after commas stripped)", None, f"count={raw.count(b', ')}")
    crlf, trailing_nl = raw.count(b"\r\n"), raw.endswith(b"\n")
    record("test line endings", None, f"CRLF={crlf}, trailing newline={trailing_nl}")
    P, bad = parse_test_rows(teb)
    record("test anchor-parse: every row has exactly one (venue, year) anchor", not bad, f"ok={len(P)} bad={bad[:3]}")
    record("test row count", (len(P) == EXPECTED["n_test"]) if exp else None, str(len(P)))
    ids_te = [int(r["id"]) for r in P]
    record("test ids unique", len(set(ids_te)) == len(ids_te))
    record("test ids disjoint from train", not (set(ids_te) & set(ids_tr)))
    record("test doi field looks like DOI/URL", all(re.match(r"10\.|https?://", r["doi"]) for r in P),
           str([r["id"] for r in P if not re.match(r"10\.|https?://", r["doi"])][:5]))
    record("test year in 2016..2025", all(2016 <= int(r["year"]) <= 2025 for r in P))
    vc = C.Counter(r["venue"] for r in P)
    record("test venue distribution", (dict(vc) == EXPECTED["test_venues"]) if exp else None, str(dict(vc)))
    tok = [t for r in P for t in r["author_tokens"] if t.strip()]
    # Empty author segments (e.g. ", Yushi Cao") also exist in train.csv: a source-data artefact, not a parser error.
    seg_te = sum(1 for r in P if r["authors_raw"].strip() and any(not t.strip() for t in r["author_tokens"]))
    seg_tr = sum(1 for r in T if r["authors"].strip() and any(not t.strip() for t in r["authors"].split(",")))
    record("non-empty authors containing empty segments (train vs test; source artefact)", None,
           f"train={seg_tr} test={seg_te}")
    record("author tokens: none contain digits", not any(re.search(r"\d", t) for t in tok),
           str([t for t in tok if re.search(r"\d", t)][:5]))
    record("author tokens: none equal a venue token", not any(t in VENUES for t in tok))
    suffix = [t for t in tok if re.fullmatch(r"(Jr|Sr|II|III|IV)\.?", t.strip())]
    record("author tokens: no standalone name suffixes (would indicate split names)", not suffix, str(suffix[:5]))
    single = [t for t in tok if len(t.split()) == 1]
    record("author tokens: single-word tokens (inspect manually)", None, f"{len(single)}: {single[:8]}")
    record("test titles: share ending with '.'", None,
           f"{sum(r['title'].endswith('.') for r in P)}/{len(P)} (train {sum(r['title'].endswith('.') for r in T)}/{len(T)})")
    record("test titles containing ',' (commas inside title)", None, str(sum("," in r["title"] for r in P)))
    empty_te = sum(1 for r in P if not r["authors_raw"].strip())
    record("test empty authors", (empty_te == EXPECTED["empty_authors"]["test"]) if exp else None, str(empty_te))
    na_tr = C.Counter(min(len(authors_list(r["authors"])), 8) for r in T)
    na_te = C.Counter(min(len(authors_list(r["authors_raw"])), 8) for r in P)
    record("#authors distribution train vs test (8 = 8+)", None,
           f"train={dict(sorted(na_tr.items()))} test={dict(sorted(na_te.items()))}")

    print("\n== 4. Submission template ==")
    sb = read_rows(paths["Submission.csv"])
    record("template header", sb[0] == ["id", "priority"], str(sb[0]))
    record("template ids == Test.csv ids in same order", [r[0] for r in sb[1:]] == [r["id"] for r in P])
    record("template priorities all zero (template only; scores 0)", all(r[1] == "0" for r in sb[1:]))

    print("\n== 5. Duplicates ==")
    groups = C.defaultdict(list)
    for r in T:
        groups[title_norm(r["title"])].append(r)
    dups = {k: g for k, g in groups.items() if len(g) > 1}
    conflict = [[(x["id"], x["Label"]) for x in g] for g in dups.values() if len({x["Label"] for x in g}) > 1]
    record("train duplicate title groups", None, f"groups={len(dups)} rows={sum(len(g) for g in dups.values())}")
    record("train duplicate groups with conflicting labels", None, str(conflict))
    tg = C.Counter(title_norm(r["title"]) for r in P)
    record("test internal duplicate titles", None, str(sum(1 for v in tg.values() if v > 1)))
    record("train/test shared normalized titles", None, str(len(set(groups) & set(tg))))
    dd = C.Counter(r["doi"] for r in T)
    record("train doi values shared by >1 paper", None, f"{sum(1 for v in dd.values() if v > 1)} (max group {max(dd.values())})")
    record("train/test shared doi values (different papers; never copy labels)", None,
           str(sorted(set(dd) & {r['doi'] for r in P}))[:300])

    print("\n== 6. Train/test shift ==")
    vt = C.Counter(r["venue"] for r in T)
    record("venue share train vs test", None,
           ", ".join(f"{v}: {vt[v]/len(T):.1%} vs {vc[v]/len(P):.1%}" for v in sorted(VENUES)))
    yt, yp = C.Counter(r["year"] for r in T), C.Counter(r["year"] for r in P)
    record("year counts train vs test", None, ", ".join(f"{y}: {yt[y]}/{yp[y]}" for y in sorted(set(yt) | set(yp))))
    p1 = {v: sum(1 for r in T if r["venue"] == v and r["Label"] == "1") / vt[v] for v in vt}
    est = sum(vc[v] * p1.get(v, 0) for v in vc) / len(P)
    record("label-1 share train; venue-reweighted estimate for test [inference]", None,
           f"train={labels[1]/len(T):.3f} test_est={est:.3f}")

    print("\n== 7. Leakage probes ==")
    by_v = C.defaultdict(list)
    for r in T:
        by_v[r["venue"]].append(int(r["id"]))
    ranges = {v: (min(x), max(x)) for v, x in by_v.items()}
    record("train id ranges per venue (ids encode venue)", None, str(dict(sorted(ranges.items(), key=lambda kv: kv[1]))))
    nonincr = []
    for v in by_v:
        seq = [int(r["year"]) for r in sorted(T, key=lambda r: int(r["id"])) if r["venue"] == v]
        nonincr.append(all(b <= a for a, b in zip(seq, seq[1:])))
    record("within each venue, year is non-increasing in id (ids encode year)", None, str(all(nonincr)))
    num = den = 0.0
    per = []
    gv = C.defaultdict(list)
    for r in T:
        gv[(r["venue"], r["year"])].append((int(r["id"]), int(r["Label"])))
    for key, g in gv.items():
        rho = spearman([x for x, _ in g], [y for _, y in g])
        if rho is not None:
            num += rho * len(g); den += len(g); per.append((key, len(g), round(rho, 3)))
    pooled = num / den if den else float("nan")
    strongest = sorted(per, key=lambda t: -abs(t[2]))[:3]
    record("within (venue, year): Spearman(id, Label), size-weighted mean", None,
           f"{pooled:.3f}; strongest groups={strongest}")

    fails = [r for r in results if r["status"] == "FAIL"]
    print(f"\nSummary: {len(results)} checks, {len(fails)} FAIL, "
          f"{sum(r['status']=='PASS' for r in results)} PASS, {sum(r['status']=='INFO' for r in results)} INFO")
    if a.json_out:
        with open(a.json_out, "w", encoding="utf-8") as fh:
            json.dump(results, fh, ensure_ascii=False, indent=2)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
