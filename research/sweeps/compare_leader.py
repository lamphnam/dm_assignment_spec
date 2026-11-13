"""Read-only comparison: official Kaggle files (data/raw) vs the group leader's files (leader_csv_file).
Usage: python -I compare_leader.py <repo_root>
"""
import csv, html, re, sys, hashlib
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
root = Path(sys.argv[1])
OFF = root / "data" / "raw"
LEAD = root / "leader_csv_file"
VENUES = {"kr", "cav", "lics", "iclp", "lpnmr"}


def rows(p):
    with open(p, encoding="utf-8", newline="") as fh:
        return list(csv.reader(fh))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def demojibake(s):
    for enc in ("cp1252", "latin-1"):
        try:
            return s.encode(enc).decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
    return s


def has_mojibake(s):
    return bool(re.search(r"[ÃÂâ][\x80-\xbf€‚ƒ„…†‡ˆ‰Š‹ŒŽ‘’“”•–—˜™š›œžŸ¡-¿©®]", s)) or "Ã" in s


def parse_test(rs):
    out, bad = {}, []
    for f in rs[1:]:
        idx = [i for i in range(2, len(f) - 2) if f[i] in VENUES and re.fullmatch(r"\d{4}", f[i + 1])]
        if len(idx) != 1:
            bad.append(f[:3]); continue
        i = idx[0]
        out[f[0]] = dict(id=f[0], title=",".join(f[1:i]), venue=f[i], year=f[i + 1],
                         authors=",".join(f[i + 2:-1]), doi=f[-1])
    return out, bad


def classify(a_off, a_lead):
    """how does the leader's text differ from the official text"""
    if a_off == a_lead:
        return "same"
    if demojibake(a_lead) == a_off:
        return "leader=mojibake of official"
    if demojibake(a_off) == a_lead:
        return "official=mojibake of leader"
    if a_off.replace(", ", ",") == a_lead.replace(", ", ","):
        return "only space-after-comma"
    if html.unescape(a_off) == html.unescape(a_lead):
        return "only html-entity"
    if " ".join(a_off.split()) == " ".join(a_lead.split()):
        return "only whitespace"
    return "other"


print("=== 0. raw files ===")
for n in ("train.csv", "Test.csv"):
    a, b = OFF / n, LEAD / n
    ba, bb = a.read_bytes(), b.read_bytes()
    print(f"{n}: official {len(ba)}B sha={sha(a)[:12]} | leader {len(bb)}B sha={sha(b)[:12]} | identical={ba == bb}")
    print(f"   CRLF: official={ba.count(b'\r\n')} leader={bb.count(b'\r\n')}; trailing newline: official={ba.endswith(b'\n')} leader={bb.endswith(b'\n')}")
    print(f"   identical after normalising CRLF->LF and stripping trailing newline: {ba.replace(b'\r\n', b'\n').rstrip(b'\n') == bb.replace(b'\r\n', b'\n').rstrip(b'\n')}")

# ---------------------------------------------------------------- train
print("\n=== 1. train.csv ===")
ro, rl = rows(OFF / "train.csv"), rows(LEAD / "train.csv")
print("header official:", ro[0]); print("header leader  :", rl[0], "| same:", ro[0] == rl[0])
print("rows official/leader:", len(ro) - 1, len(rl) - 1)
print("field counts leader:", Counter(len(r) for r in rl))
O = {r[0]: r for r in ro[1:]}; L = {r[0]: r for r in rl[1:] if len(r) == 7}
print("ids equal:", set(O) == set(L), "| same order:", [r[0] for r in ro[1:]] == [r[0] for r in rl[1:]])
print("only in official:", sorted(set(O) - set(L))[:10], "| only in leader:", sorted(set(L) - set(O))[:10])
cols = ro[0]
for ci, c in enumerate(cols):
    if c == "id":
        continue
    cnt, ex = Counter(), {}
    for i in O.keys() & L.keys():
        k = classify(O[i][ci], L[i][ci])
        cnt[k] += 1
        if k != "same":
            ex.setdefault(k, []).append((i, O[i][ci], L[i][ci]))
    print(f"-- {c}: {dict(cnt)}")
    for k, v in ex.items():
        for i, a, b in v[:3]:
            print(f"     [{k}] id={i}\n        official: {a[:110]!r}\n        leader  : {b[:110]!r}")
moj_l = sum(has_mojibake(r[1] + r[4]) for r in rl[1:]); moj_o = sum(has_mojibake(r[1] + r[4]) for r in ro[1:])
print(f"rows with mojibake markers (title/authors): official={moj_o} leader={moj_l}")
lab_diff = [(i, O[i][6], L[i][6]) for i in O.keys() & L.keys() if O[i][6] != L[i][6]]
print("Label differences:", len(lab_diff), lab_diff[:10])

# ---------------------------------------------------------------- test
print("\n=== 2. Test.csv ===")
to, tl = rows(OFF / "Test.csv"), rows(LEAD / "Test.csv")
print("header official:", to[0]); print("header leader  :", tl[0], "| same:", to[0] == tl[0])
print("rows official/leader:", len(to) - 1, len(tl) - 1)
print("raw field-count distribution official:", dict(sorted(Counter(len(r) for r in to[1:]).items())))
print("raw field-count distribution leader  :", dict(sorted(Counter(len(r) for r in tl[1:]).items())))
PO, bad_o = parse_test(to); PL, bad_l = parse_test(tl)
print("anchor-parse failures official/leader:", len(bad_o), len(bad_l))
print("ids equal:", set(PO) == set(PL), "| same order:", [r[0] for r in to[1:]] == [r[0] for r in tl[1:]])
print("only in official:", sorted(set(PO) - set(PL))[:10], "| only in leader:", sorted(set(PL) - set(PO))[:10])
# leader read the plain way (no custom parse)
plain_ok = all(len(r) == 6 for r in tl[1:])
print("leader Test.csv parses with plain csv.reader into exactly 6 fields on every row:", plain_ok)
for c in ("title", "venue", "year", "authors", "doi"):
    cnt, ex = Counter(), {}
    for i in PO.keys() & PL.keys():
        k = classify(PO[i][c], PL[i][c]); cnt[k] += 1
        if k != "same":
            ex.setdefault(k, []).append((i, PO[i][c], PL[i][c]))
    print(f"-- {c}: {dict(cnt)}")
    for k, v in ex.items():
        for i, a, b in v[:3]:
            print(f"     [{k}] id={i}\n        official: {a[:110]!r}\n        leader  : {b[:110]!r}")
print("leader Test contains ', ' (space after comma) occurrences:", sum(", " in r for r in [",".join(x) for x in tl]))
print("rows with mojibake markers (title/authors): official=%d leader=%d" % (
    sum(has_mojibake(v["title"] + v["authors"]) for v in PO.values()),
    sum(has_mojibake(v["title"] + v["authors"]) for v in PL.values())))
print("test venue dist official:", dict(Counter(v["venue"] for v in PO.values())), "| leader:", dict(Counter(v["venue"] for v in PL.values())))

# ---------------------------------------------------------------- extras
print("\n=== 3. extra files (not on Kaggle) ===")
pr = rows(LEAD / "proceedings.csv"); pc = rows(LEAD / "proceedings_contents.csv")
print("proceedings.csv header:", pr[0]); print("rows:", len(pr) - 1)
H = pr[0]
d = [dict(zip(H, r)) for r in pr[1:]]
print("split:", dict(Counter(x["split"] for x in d)), "| is_proceedings:", dict(Counter(x["is_proceedings"] for x in d)),
      "| author_status:", dict(Counter(x["author_status"] for x in d)))
print("source_venue:", dict(Counter(x["source_venue"] for x in d)))
# does the id/split claim match the official data?
m_ok = m_bad = 0
for x in d:
    pool = O if x["split"] == "train" else PO
    if x["id"] in pool:
        t_off = pool[x["id"]][1] if x["split"] == "train" else pool[x["id"]]["title"]
        if re.sub(r"\W+", "", t_off.lower()) == re.sub(r"\W+", "", x["title"].lower()): m_ok += 1
        else: m_bad += 1
    else:
        m_bad += 1
print(f"proceedings.csv rows whose (split,id,title) match the official files: {m_ok}/{len(d)} (mismatch {m_bad})")
tr_label = Counter(O[x["id"]][6] for x in d if x["split"] == "train" and x["id"] in O)
print("official train label of proceedings.csv train rows:", dict(tr_label))
print("proceedings_contents.csv header:", pc[0], "| rows:", len(pc) - 1,
      "| distinct volume_key:", len({r[0] for r in pc[1:]}), "| field counts:", dict(Counter(len(r) for r in pc[1:])))


def tn(t):
    return " ".join(re.sub(r"[^a-z0-9]+", " ", html.unescape(t).lower()).split())


ct = Counter(tn(r[1]) for r in pc[1:] if len(r) >= 2)
tr_titles = [tn(r[1]) for r in ro[1:]]
te_titles = [tn(v["title"]) for v in PO.values()]
print(f"official train titles found in proceedings_contents: {sum(t in ct for t in tr_titles)}/{len(tr_titles)}")
print(f"official test  titles found in proceedings_contents: {sum(t in ct for t in te_titles)}/{len(te_titles)}")
