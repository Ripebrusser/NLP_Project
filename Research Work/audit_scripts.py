#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Corrected script census covering all Indic blocks + per-language label feasibility."""
import csv, json, sys, re
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_datasets import read_xlsx_rows, XLSX, CSV_PATH, manglish_screen

sys.stdout.reconfigure(encoding="utf-8")

BLOCKS = [
    ("malayalam", 0x0D00, 0x0D7F), ("tamil", 0x0B80, 0x0BFF),
    ("telugu", 0x0C00, 0x0C7F), ("kannada", 0x0C80, 0x0CFF),
    ("devanagari", 0x0900, 0x097F), ("bengali", 0x0980, 0x09FF),
    ("gujarati", 0x0A80, 0x0AFF), ("gurmukhi", 0x0A00, 0x0A7F),
    ("oriya", 0x0B00, 0x0B7F), ("sinhala", 0x0D80, 0x0DFF),
    ("arabic", 0x0600, 0x06FF), ("cyrillic", 0x0400, 0x04FF),
    ("han", 0x4E00, 0x9FFF), ("hangul", 0xAC00, 0xD7AF),
    ("thai", 0x0E00, 0x0E7F), ("hebrew", 0x0590, 0x05FF),
]
LATIN = (0x0041, 0x005A), (0x0061, 0x007A)


def scripts_in(t):
    found = set()
    for ch in t:
        o = ord(ch)
        if 0x41 <= o <= 0x5A or 0x61 <= o <= 0x7A:
            found.add("latin")
            continue
        for name, lo, hi in BLOCKS:
            if lo <= o <= hi:
                found.add(name)
                break
    return found


def bucket(t):
    s = scripts_in(t)
    if not s:
        return "no_letters"
    if s == {"latin"}:
        return "latin_only"
    if "latin" in s:
        base = sorted(x for x in s if x != "latin")
        return "+".join(base) + "+latin"
    if len(s) == 1:
        return next(iter(s)) + "_only"
    return "+".join(sorted(s))


def load_drav():
    rows = read_xlsx_rows(XLSX)[0]["rows"]
    out = []
    for r in rows[1:]:
        if not r or all(v == "" for v in r.values()):
            continue
        out.append((str(r.get(0, "")), str(r.get(1, "")).strip()))
    return out


drav = load_drav()
bc = Counter(bucket(m) for m, _ in drav)
print("### CORRECTED SCRIPT BUCKETS (Dravidian dataset, n=%d)" % len(drav))
for k, v in bc.most_common():
    print(f"  {k:<28} {v:5d}  {100*v/len(drav):5.1f}%")

print("\n### ANY DRAVIDIAN SCRIPT PRESENT")
DR = {"malayalam", "tamil", "telugu", "kannada"}
n_dr = sum(1 for m, _ in drav if scripts_in(m) & DR)
n_dr_nolatin = sum(1 for m, _ in drav if scripts_in(m) & DR and "latin" not in scripts_in(m))
n_dr_latin = sum(1 for m, _ in drav if scripts_in(m) & DR and "latin" in scripts_in(m))
print(f"  any Dravidian script: {n_dr} ({100*n_dr/len(drav):.1f}%)")
print(f"    Dravidian script only (no Latin): {n_dr_nolatin}")
print(f"    Dravidian script + Latin: {n_dr_latin}")
print(f"  Latin only: {bc['latin_only']}")
print(f"  no letters at all: {bc['no_letters']}")

print("\n### PER-SCRIPT LABEL DISTRIBUTION")
ct = defaultdict(Counter)
for m, l in drav:
    ct[bucket(m)][l] += 1
for k, v in sorted(ct.items(), key=lambda x: -sum(x[1].values())):
    tot = sum(v.values())
    print(f"  {k:<28} total={tot:5d} ham={v['Ham']:5d} spam={v['Spam']:4d} bad={v['Spa,']} spam%={100*v['Spam']/tot:5.1f}")

print("\n### MALAYALAM-SCRIPT SUBSET (script present, incl. mixed)")
mal = [(m, l) for m, l in drav if "malayalam" in scripts_in(m)]
print("  n=", len(mal), Counter(l for _, l in mal))
print("  token stats: mean=%.1f median=%d" % (sum(len(m.split()) for m, _ in mal)/len(mal), sorted(len(m.split()) for m, _ in mal)[len(mal)//2]))

print("\n### TAMIL SUBSET")
tam = [(m, l) for m, l in drav if "tamil" in scripts_in(m)]
print("  n=", len(tam), Counter(l for _, l in tam))

print("\n### TELUGU SUBSET")
tel = [(m, l) for m, l in drav if "telugu" in scripts_in(m)]
print("  n=", len(tel), Counter(l for _, l in tel))

print("\n### MENDELEY SCRIPT")
with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
    rd = list(csv.reader(f))
h = rd[0]
mend = [(r[h.index("TEXT")], r[h.index("LABEL")].strip().lower()) for r in rd[1:] if len(r) == len(h)]
mb = Counter(bucket(t) for t, _ in mend)
print(" ", dict(mb), " with any Indic script:", sum(1 for t, _ in mend if scripts_in(t) & DR))

print("\n### DRAVIDIAN SCRIPT x CLASS COUNTS FOR MODELLING FEASIBILITY")
for name in ("malayalam", "tamil", "telugu"):
    sub = [(m, l) for m, l in drav if name in scripts_in(m)]
    c = Counter(l for _, l in sub if l in ("Ham", "Spam"))
    print(f"  {name:<10} n={len(sub):5d} ham={c['Ham']:5d} spam={c['Spam']:4d}")

json.dump({
    "buckets": dict(bc.most_common()),
    "per_bucket_labels": {k: dict(v) for k, v in ct.items()},
    "dravidian_script_any": n_dr,
    "dravidian_script_only": n_dr_nolatin,
    "dravidian_plus_latin": n_dr_latin,
    "mendeley_indic_script": sum(1 for t, _ in mend if scripts_in(t) & DR),
}, open(Path(__file__).parent / "audit_output" / "script_census.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("\nwrote script_census.json")
