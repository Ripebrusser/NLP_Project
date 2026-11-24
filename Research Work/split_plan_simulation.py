#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deterministic grouped-stratified split simulation + leakage self-check.
No model training. Establishes whether the proposed split is feasible."""
import csv, random, sys, json, re
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_datasets import read_xlsx_rows, XLSX, CSV_PATH, norm_key

sys.stdout.reconfigure(encoding="utf-8")
OUT = Path(__file__).resolve().parent / "audit_output"

BLOCKS = [("malayalam", 0x0D00, 0x0D7F), ("tamil", 0x0B80, 0x0BFF),
          ("telugu", 0x0C00, 0x0C7F), ("kannada", 0x0C80, 0x0CFF)]

def indic_scripts(t):
    found = set()
    for ch in t:
        o = ord(ch)
        for name, lo, hi in BLOCKS:
            if lo <= o <= hi:
                found.add(name)
                break
    return found

DR = {"malayalam", "tamil", "telugu", "kannada"}

def has_latin(t):
    return any(("A" <= c <= "Z") or ("a" <= c <= "z") for c in t)

def lang_group(t):
    s = indic_scripts(t) & DR
    return "+".join(sorted(s)) if s else "latin_or_other"

def load():
    rows = read_xlsx_rows(XLSX)[0]["rows"]
    drav = []
    for r in rows[1:]:
        if not r or all(v == "" for v in r.values()):
            continue
        drav.append((str(r.get(0, "")), str(r.get(1, "")).strip()))
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        rd = list(csv.reader(f))
    h = rd[0]
    mend = [(r[h.index("TEXT")], r[h.index("LABEL")].strip().lower())
            for r in rd[1:] if len(r) == len(h)]
    return drav, mend

drav_all, mend = load()

invis = [i for i, (m, _) in enumerate(drav_all)
         if re.sub(r"[\u200b\u200c\u200d\ufeff\u00a0\s]", "", m) == ""]
print("records with no visible characters:", len(invis))
drav = [(m, l) for m, l in drav_all if m.strip() != "" and l in ("Ham", "Spam")]
print(f"dravidian usable after exclusions: {len(drav)} (removed {len(drav_all)-len(drav)})")
print("  class counts:", dict(Counter(l for _, l in drav)))


def grouped_split(records, strata_fn, ratios=(0.70, 0.15, 0.15), seed=42):
    groups = defaultdict(list)
    for m, l in records:
        groups[norm_key(m)].append((m, l))
    strata = defaultdict(list)
    for k, items in groups.items():
        l = Counter(x[1] for x in items).most_common(1)[0][0]
        strata[strata_fn(k, l)].append(k)

    rng = random.Random(seed)
    parts = ("train", "val", "test")
    assign = {}
    for s, keys in sorted(strata.items()):
        rng.shuffle(keys)
        keys.sort(key=lambda k: -len(groups[k]))
        total = sum(len(groups[k]) for k in keys)
        targets = {p: ratios[i] * total for i, p in enumerate(parts)}
        counts = {p: 0 for p in parts}
        for k in keys:
            # largest absolute deficit relative to this stratum's target
            p = max(parts, key=lambda q: targets[q] - counts[q])
            assign[k] = p
            counts[p] += len(groups[k])
        # guarantee val/test representation when the stratum allows it
        if len(keys) >= 3:
            for q in ("val", "test"):
                if counts[q] == 0:
                    cands = [k for k in keys if assign[k] == "train"]
                    if len(cands) > 1:
                        k = min(cands, key=lambda x: len(groups[x]))
                        assign[k] = q
                        counts["train"] -= len(groups[k])
                        counts[q] += len(groups[k])

    out = {p: [] for p in parts}
    for k, items in groups.items():
        out[assign[k]].extend(items)
    sets = {p: {norm_key(m) for m, _ in v} for p, v in out.items()}
    assert not (sets["train"] & sets["val"])
    assert not (sets["train"] & sets["test"])
    assert not (sets["val"] & sets["test"])
    return out, len(groups), len(strata)


CASES = [
    ("dravidian_all", drav, lambda m, l: (l, lang_group(m))),
    ("dravidian_malayalam", [(m, l) for m, l in drav if "malayalam" in indic_scripts(m)],
     lambda m, l: (l, "malayalam")),
    ("dravidian_malayalam_only_script",
     [(m, l) for m, l in drav if "malayalam" in indic_scripts(m) and not has_latin(m)],
     lambda m, l: (l, "malayalam")),
    ("mendeley_3class", mend, lambda m, l: (l, "en")),
    ("mendeley_binary_smishing",
     [(m, ("smishing" if l == "smishing" else "not_smishing")) for m, l in mend],
     lambda m, l: (l, "en")),
]

results = {}
for name, recs, fn in CASES:
    out, ngroups, nstrata = grouped_split(recs, fn)
    row = {"records": len(recs), "groups": ngroups, "strata": nstrata}
    for p in ("train", "val", "test"):
        row[p] = {"n": len(out[p]), "labels": dict(Counter(l for _, l in out[p]).most_common())}
    results[name] = row
    print(f"\n{name}: records={len(recs)} groups={ngroups} strata={nstrata}")
    for p in ("train", "val", "test"):
        print(f"  {p}: n={row[p]['n']} {row[p]['labels']}")

json.dump(results, open(OUT / "split_simulation.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("\nwrote split_simulation.json")
