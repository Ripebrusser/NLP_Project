#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Forensic follow-up: label conflicts, template clusters, source blocks, cross-dataset label agreement."""
import csv, json, re, sys, zipfile
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
XLSX = ROOT / "Datasets" / "Spam Message Collection.xlsx"
CSV_PATH = ROOT / "Datasets" / "Dataset_5971.csv"
OUT = ROOT / "Research Work" / "audit_output"

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
T = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_datasets import read_xlsx_rows, norm_key, script_bucket, MAL, TAM, LAT


def load_drav():
    rows = read_xlsx_rows(XLSX)[0]["rows"]
    out = []
    for r in rows[1:]:
        if not r or all(v == "" for v in r.values()):
            continue
        out.append((str(r.get(0, "")), str(r.get(1, "")).strip()))
    return out


def load_mend():
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        rd = list(csv.reader(f))
    h = rd[0]
    return [(r[h.index("TEXT")], r[h.index("LABEL")].strip().lower()) for r in rd[1:] if len(r) == len(h)]


drav = load_drav()
mend = load_mend()
print(f"drav records={len(drav)} mend records={len(mend)}")

print("\n### 1. PROBLEM RECORDS")
for i, (m, l) in enumerate(drav):
    if m.strip() == "" or l == "Spa,":
        print(f"  idx={i} label={l!r} msg={m!r} tokens={len(m.split())}")

print("\n### 2. LABEL CONFLICT GROUPS (Dravidian)")
g = defaultdict(list)
for i, (m, l) in enumerate(drav):
    g[norm_key(m)].append(i)
conf = [(k, v) for k, v in g.items() if k and len({drav[i][1] for i in v}) > 1]
print(f"  groups={len(conf)}  affected_records={sum(len(v) for _, v in conf)}")
for k, v in conf[:6]:
    print(f"  - labels={Counter(drav[i][1] for i in v)} key={k[:90]!r}")
    for i in v[:2]:
        print(f"      {drav[i][1]:<6} {drav[i][0][:110]!r}")

print("\n### 3. NEAR-DUP CLUSTER SIZES (Dravidian, top 8)")
sizes = sorted(((len(v), k) for k, v in g.items() if k and len(v) > 1), reverse=True)
print("  size distribution:", Counter(s for s, _ in sizes).most_common(8))
for s, k in sizes[:8]:
    print(f"  n={s} labels={Counter(drav[i][1] for i in g[k])} key={k[:100]!r}")

print("\n### 4. PER-CLASS DUPLICATE EXCESS")
for cls in ("Ham", "Spam", "Spa,"):
    idxs = [i for i, (_, l) in enumerate(drav) if l == cls]
    keys = {norm_key(drav[i][0]) for i in idxs}
    print(f"  {cls}: rows={len(idxs)} unique_norm={len(keys)} excess={len(idxs)-len(keys)}")

print("\n### 5. ROW-ORDER / SOURCE BLOCK STRUCTURE (Dravidian, per 1000-row block)")
for start in range(0, len(drav), 1000):
    blk = drav[start:start + 1000]
    sc = Counter(script_bucket(m) for m, _ in blk)
    lc = Counter(l for _, l in blk)
    print(f"  rows {start:5d}-{start+len(blk)-1:5d} labels={dict(lc)} scripts={dict(sc.most_common(4))}")

print("\n### 6. UCI / ENGLISH SMS MARKERS IN DRAVIDIAN DATASET")
markers = ["FreeMsg", "Txt STOP", "txtstop", "WINNER", "claim", "450ppm", "uk", "www.", "http",
           "Call", "prize", "Urgent", "customer service", "Nokia", "SMS"]
for mk in markers:
    n = sum(1 for m, _ in drav if mk.lower() in m.lower())
    if n:
        print(f"  {mk!r}: {n}")

print("\n### 7. CROSS-DATASET LABEL AGREEMENT (normalised-key overlap)")
md = defaultdict(list)
for m, l in mend:
    md[norm_key(m)].append(l)
pairs = Counter()
overlap_msgs = 0
for k, idxs in g.items():
    if k and k in md:
        for i in idxs:
            for ml in md[k]:
                pairs[(drav[i][1], ml)] += 1
        overlap_msgs += len(idxs)
print(f"  dravidian messages with a Mendeley twin: {overlap_msgs}")
for (dl, ml), c in pairs.most_common(12):
    print(f"  drav={dl:<5} mend={ml:<9} n={c}")

print("\n### 8. SCRIPT x LABEL CROSSTAB (Dravidian)")
ct = defaultdict(Counter)
for m, l in drav:
    ct[script_bucket(m)][l] += 1
for sc, c in sorted(ct.items(), key=lambda x: -sum(x[1].values())):
    tot = sum(c.values())
    print(f"  {sc:<16} total={tot:5d} ham={c['Ham']:5d} spam={c['Spam']:4d} other={c.get('Spa,',0)} spam%={100*c['Spam']/tot:5.1f}")

print("\n### 9. NO-LETTER RECORD SAMPLES")
nl = [(i, m) for i, (m, _) in enumerate(drav) if not MAL.search(m) and not TAM.search(m) and not LAT.search(m)]
print(f"  count={len(nl)}; samples:")
for i, m in nl[:6]:
    print(f"   idx={i} label={drav[i][1]} len={len(m)} repr={m[:70]!r}")

print("\n### 10. URL / CONTACT CONTENT")
for name, data, ti in (("dravidian", drav, 0), ("mendeley", mend, 0)):
    urls = sum(1 for t, _ in data if re.search(r"https?://|www\.", t, re.I))
    money = sum(1 for t, _ in data if re.search(r"[₹$€£]|\brs\.?\s?\d", t, re.I))
    phones = sum(1 for t, _ in data if re.search(r"\b\d{10}\b", t))
    print(f"  {name}: url={urls} currency={money} 10-digit={phones}")

print("\n### 11. MENDELEY METADATA COLUMNS")
with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
    rd = list(csv.reader(f))
h = rd[0]
for col in ("URL", "EMAIL", "PHONE"):
    j = h.index(col)
    vals = [r[j] for r in rd[1:]]
    vc = Counter(v.strip().lower() for v in vals)
    nonno = [v for v in vals if v.strip().lower() not in ("no", "")]
    print(f"  {col}: distinct={len(vc)} top={dict(vc.most_common(4))} non_no={len(nonno)} examples={nonno[:3]}")

print("\n### 12. MENDELEY CONFLICTS")
gm = defaultdict(list)
for i, (t, l) in enumerate(mend):
    gm[norm_key(t)].append(i)
cm = [(k, v) for k, v in gm.items() if k and len({mend[i][1] for i in v}) > 1]
print(f"  groups={len(cm)} affected={sum(len(v) for _, v in cm)}")
for k, v in cm[:5]:
    print(f"  - {Counter(mend[i][1] for i in v)} key={k[:80]!r}")

# persist
summary = {
    "dravidian_problem_records": [
        {"index": i, "label": l, "message": m} for i, (m, l) in enumerate(drav)
        if m.strip() == "" or l == "Spa,"
    ],
    "dravidian_conflict_groups": len(conf),
    "dravidian_conflict_records": sum(len(v) for _, v in conf),
    "dravidian_top_cluster_sizes": [s for s, _ in sizes[:20]],
    "overlap_message_count": overlap_msgs,
    "overlap_label_pairs": {f"{a}|{b}": c for (a, b), c in pairs.most_common()},
}
(OUT / "dataset_forensics.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print("\nwrote", OUT / "dataset_forensics.json")
