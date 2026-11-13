"""Can the leader's cleaned text be reproduced from the OFFICIAL files alone with deterministic rules? (read-only)"""
import csv, html, re, sys, unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
root = Path(sys.argv[1]); OFF = root / "data/raw"; LEAD = root / "leader_csv_file"
VENUES = {"kr", "cav", "lics", "iclp", "lpnmr"}


def rows(p):
    with open(p, encoding="utf-8", newline="") as fh:
        return list(csv.reader(fh))


def parse_test(rs):
    out = {}
    for f in rs[1:]:
        i = [i for i in range(2, len(f) - 2) if f[i] in VENUES and re.fullmatch(r"\d{4}", f[i + 1])][0]
        out[f[0]] = dict(title=",".join(f[1:i]), authors=",".join(f[i + 2:-1]))
    return out


def clean(s):
    return unicodedata.normalize("NFC", html.unescape(s))


def restore_space(s):
    # deterministic rule: a comma followed by a non-space, non-digit-after-digit char gets ", " back
    return re.sub(r",(?=\S)", lambda m: ", ", s)


def restore_space_numsafe(s):
    # do not touch thousands separators like 1,000
    return re.sub(r"(?<!\d),(?=\S)|,(?=\D)", ", ", s)


O = {r[0]: r for r in rows(OFF / "train.csv")[1:]}
L = {r[0]: r for r in rows(LEAD / "train.csv")[1:]}
PO = parse_test(rows(OFF / "Test.csv")); PL = parse_test(rows(LEAD / "Test.csv"))

# TRAIN
t_ok = sum(clean(O[i][1]) == L[i][1] for i in O)
a_ok = sum(clean(O[i][4]).rstrip() == L[i][4].rstrip() for i in O if O[i][4].strip())
n_a = sum(1 for i in O if O[i][4].strip())
filled = [i for i in O if not O[i][4].strip() and L[i][4].strip()]
print(f"TRAIN title   : clean() == leader on {t_ok}/{len(O)} rows")
print(f"TRAIN authors : clean() == leader on {a_ok}/{n_a} rows that already have authors")
print(f"TRAIN authors : {len(filled)} rows empty in official but filled by leader -> NOT derivable from official data")

# TEST
for name, fn in (("naive  ',(?=\\S)'", restore_space), ("number-safe", restore_space_numsafe)):
    tt = sum(fn(clean(PO[i]["title"])) == PL[i]["title"] for i in PO)
    aa = sum(fn(clean(PO[i]["authors"])).rstrip(", ") == PL[i]["authors"].rstrip(", ") for i in PO if PO[i]["authors"].strip())
    print(f"TEST  [{name}] title exact match: {tt}/{len(PO)} | authors exact match (rows with authors): {aa}/{sum(1 for i in PO if PO[i]['authors'].strip())}")
bad = [(i, restore_space_numsafe(clean(PO[i]["title"])), PL[i]["title"]) for i in PO if restore_space_numsafe(clean(PO[i]["title"])) != PL[i]["title"]]
for i, a, b in bad[:6]:
    print(f"   title mismatch id={i}\n     rebuilt: {a[:110]!r}\n     leader : {b[:110]!r}")
filled_t = [i for i in PO if not PO[i]["authors"].strip() and PL[i]["authors"].strip()]
print(f"TEST  authors : {len(filled_t)} rows empty in official but filled by leader -> NOT derivable from official data")

# is_proceedings: can a title rule alone reproduce the leader's flag?
pr = rows(LEAD / "proceedings.csv"); H = pr[0]; d = [dict(zip(H, r)) for r in pr[1:]]
flag = {(x["split"].lower(), x["id"]) for x in d}
kw = re.compile(r"proceedings|front matter|preface", re.I)
mine = {("train", i) for i in O if kw.search(clean(O[i][1]))} | {("test", i) for i in PO if kw.search(clean(PO[i]["title"]))}
print(f"\nPROCEEDINGS flag: leader {len(flag)} | keyword rule {len(mine)} | overlap {len(flag & mine)} | leader-only {len(flag - mine)} | rule-only {len(mine - flag)}")
print("fields in proceedings.csv that need an external source (DBLP):", [h for h in H if h in ("volume_key", "volume_part", "editors", "source_url", "indexed_entry_count", "event_key", "topic_keys", "topic_title_counts")])
