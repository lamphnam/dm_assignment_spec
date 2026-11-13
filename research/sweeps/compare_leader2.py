import csv, html, re, sys, unicodedata
from collections import Counter
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
        out[f[0]] = dict(title=",".join(f[1:i]), venue=f[i], year=f[i + 1], authors=",".join(f[i + 2:-1]), doi=f[-1])
    return out


def toks(s):  # author tokens, empty segments dropped, entities unescaped, NFC, spaces collapsed
    return [" ".join(unicodedata.normalize("NFC", html.unescape(a)).split()) for a in s.split(",") if a.strip()]


def cat(a_off, a_lead):
    if a_off == a_lead: return "identical"
    to, tl = toks(a_off), toks(a_lead)
    if not to and tl: return "FILLED (official empty -> leader has authors)"
    if to and not tl: return "EMPTIED (leader empty)"
    if to == tl:
        if unicodedata.normalize("NFC", a_off) != a_off or unicodedata.normalize("NFC", a_lead) != a_lead:
            return "same tokens; differ by unicode NFC/NFD"
        return "same tokens; differ by entity/space/empty-segment"
    return "DIFFERENT author lists"


O = {r[0]: r for r in rows(OFF / "train.csv")[1:]}
L = {r[0]: r for r in rows(LEAD / "train.csv")[1:]}
PO, PL = parse_test(rows(OFF / "Test.csv")), parse_test(rows(LEAD / "Test.csv"))

print("== authors, TRAIN ==")
c = Counter(); ex = {}
for i in O:
    k = cat(O[i][4], L[i][4]); c[k] += 1; ex.setdefault(k, []).append(i)
print(dict(c))
for k in c:
    if k.startswith(("DIFFERENT", "EMPTIED", "same tokens; differ by unicode")):
        for i in ex[k][:4]:
            print(f"  [{k}] id={i}\n     official: {O[i][4][:100]!r}\n     leader  : {L[i][4][:100]!r}")
print("empty authors train: official=%d leader=%d" % (sum(not r[4].strip() for r in O.values()), sum(not r[4].strip() for r in L.values())))

print("\n== authors, TEST ==")
c = Counter(); ex = {}
for i in PO:
    k = cat(PO[i]["authors"], PL[i]["authors"]); c[k] += 1; ex.setdefault(k, []).append(i)
print(dict(c))
for k in c:
    if k.startswith(("DIFFERENT", "EMPTIED", "same tokens; differ by unicode", "same tokens")):
        for i in ex[k][:3]:
            print(f"  [{k}] id={i}\n     official: {PO[i]['authors'][:100]!r}\n     leader  : {PL[i]['authors'][:100]!r}")
print("empty authors test: official=%d leader=%d" % (sum(not v["authors"].strip() for v in PO.values()), sum(not v["authors"].strip() for v in PL.values())))
print("NFD strings in official train authors/title:", sum(unicodedata.normalize("NFC", r[1] + r[4]) != r[1] + r[4] for r in O.values()),
      "| leader:", sum(unicodedata.normalize("NFC", r[1] + r[4]) != r[1] + r[4] for r in L.values()))

print("\n== filled-author effect on label (train): rows FILLED by leader ==")
filled = [i for i in O if cat(O[i][4], L[i][4]).startswith("FILLED")]
print("n filled:", len(filled), "| label dist of those rows:", dict(sorted(Counter(O[i][6] for i in filled).items())))
print("by venue:", dict(Counter(O[i][2] for i in filled)))

print("\n== proceedings.csv ==")
pr = rows(LEAD / "proceedings.csv"); H = pr[0]; d = [dict(zip(H, r)) for r in pr[1:]]
norm = lambda s: re.sub(r"\W+", "", html.unescape(s).lower())
for x in d:
    pool_t = O.get(x["id"], [None, None])[1] if x["split"].lower() == "train" else PO.get(x["id"], {}).get("title")
    if pool_t is None or norm(pool_t) != norm(x["title"]):
        print(" MISMATCH:", x["split"], x["id"], "| leader title:", x["title"][:90], "| official:", (pool_t or "<id not in that split>")[:90])
tr = [x for x in d if x["split"].lower() == "train"]; te = [x for x in d if x["split"].lower() == "test"]
print("train rows:", len(tr), "labels:", dict(Counter(O[x["id"]][6] for x in tr if x["id"] in O)), "| test rows:", len(te))
print("test ids flagged:", sorted(int(x["id"]) for x in te))
# how many official train/test titles look like proceedings by keyword, and are they covered by the leader's flag?
kw = re.compile(r"proceedings|front matter|preface", re.I)
tr_kw = [i for i in O if kw.search(O[i][1])]; te_kw = [i for i in PO if kw.search(PO[i]["title"])]
flag_tr = {x["id"] for x in tr}; flag_te = {x["id"] for x in te}
print(f"official train titles matching proceedings|front matter|preface: {len(tr_kw)}; flagged by leader: {sum(i in flag_tr for i in tr_kw)}; leader-flagged but not keyword: {len(flag_tr - set(tr_kw))}")
print(f"official test  titles matching same keywords: {len(te_kw)}; flagged by leader: {sum(i in flag_te for i in te_kw)}; leader-flagged but not keyword: {len(flag_te - set(te_kw))}")
print("train labels of keyword-matching rows:", dict(Counter(O[i][6] for i in tr_kw)))
print("sample columns of one row:", {k: (v[:70] if isinstance(v, str) else v) for k, v in list(d[0].items())[:16]})
pc = rows(LEAD / "proceedings_contents.csv")
vk_p = {x["volume_key"] for x in d}; vk_c = {r[0] for r in pc[1:]}
print("volume_key sets equal between proceedings.csv and proceedings_contents.csv:", vk_p == vk_c, len(vk_p), len(vk_c))
print("source domains in proceedings.csv:", dict(Counter(re.match(r"https?://([^/]+)/", x["source_url"]).group(1) if re.match(r"https?://([^/]+)/", x["source_url"]) else "?" for x in d)))
print("source domains in proceedings_contents.csv:", dict(Counter(re.match(r"https?://([^/]+)/", r[3]).group(1) if re.match(r"https?://([^/]+)/", r[3]) else "?" for r in pc[1:])))
