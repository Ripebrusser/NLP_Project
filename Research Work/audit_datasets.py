#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reproducible audit of the two approved datasets.
Stdlib only: zipfile + xml.etree for XLSX, csv for CSV, unicodedata for scripts.

Outputs:
  Research Work/audit_output/dataset_audit.json   (all counts)
  stdout                                          (human summary)

No dataset file is modified. No labels are changed on disk.
"""
import csv, json, re, sys, unicodedata, zipfile, hashlib
from collections import Counter, defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
XLSX = ROOT / "Datasets" / "Spam Message Collection.xlsx"
CSV_PATH = ROOT / "Datasets" / "Dataset_5971.csv"
OUT = ROOT / "Research Work" / "audit_output"
OUT.mkdir(parents=True, exist_ok=True)

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
T = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"

MAL = re.compile(r"[\u0D00-\u0D7F]")
TAM = re.compile(r"[\u0B80-\u0BFF]")
LAT = re.compile(r"[A-Za-z]")
DEV = re.compile(r"[\u0900-\u097F]")
ARB = re.compile(r"[\u0600-\u06FF]")
HAN = re.compile(r"[\u4E00-\u9FFF]")
CYR = re.compile(r"[\u0400-\u04FF]")

# Documented heuristic lexicon for Romanised Malayalam (Manglish) screening.
# This is a SCREEN, not an annotation. It gives a lower bound on Latin-script
# messages that contain Malayalam-origin function/content words.
MANGlish_LEX = {
    "alle", "alla", "illa", "unde", "undo", "ente", "njan", "nee", "ningal",
    "avan", "aval", "avar", "athu", "ithu", "oru", "ennu", "enniku", "enikku",
    "sheriyano", "sheri", "okke", "pinne", "venda", "vendam", "chetta", "chechi",
    "mone", "mol", "kutta", "da", "edi", "poda", "podi", "machan", "machane",
    "sugham", "sugam", "evide", "eppo", "ippo", "inne", "nale", "innale",
    "ente", "ninakku", "ninne", "tharaam", "tharum", "parayu", "parayam",
    "kollam", "kidilam", "adipoli", "pwoli", "thakkeda", "thakka", "vittu",
    "aano", "aano?", "ano", "aanu", "anu", "aayirunnu", "ayirunnu", "kanunnu",
    "kandu", "kettu", "venam", "venamenkil", "pakshe", "athil", "athinte",
    "avante", "avante", "chaya", "chayakku", "vishakkunnu", "urakkam",
    "veettil", "veedu", "naadu", "nattil", "malayali", "malayalathil",
    "nannayi", "mosam", "budhimutt", "vayya", "maduthu", "thudangi",
}

# Normalisation used ONLY for duplicate / near-duplicate detection.
URL_RE = re.compile(r"(https?://\S+|www\.\S+|\b\S+\.(?:com|in|net|org|ly|co)\b\S*)", re.I)
NUM_RE = re.compile(r"\d+")
WS_RE = re.compile(r"\s+")
NONALNUM_RE = re.compile(r"[^\w\u0D00-\u0D7F\u0B80-\u0BFF]+", re.UNICODE)


def norm_key(text: str) -> str:
    """Aggressive normalisation for near-duplicate grouping (documented in report)."""
    s = unicodedata.normalize("NFKC", text).lower()
    s = URL_RE.sub(" <url> ", s)
    s = NUM_RE.sub(" <num> ", s)
    s = NONALNUM_RE.sub(" ", s)
    s = WS_RE.sub(" ", s).strip()
    return s


def script_bucket(text: str) -> str:
    has_mal = bool(MAL.search(text))
    has_tam = bool(TAM.search(text))
    has_lat = bool(LAT.search(text))
    has_dev = bool(DEV.search(text))
    has_arb = bool(ARB.search(text))
    has_han = bool(HAN.search(text))
    has_cyr = bool(CYR.search(text))
    if has_mal and has_tam:
        return "malayalam+tamil"
    if has_mal and has_lat:
        return "malayalam+latin"
    if has_mal:
        return "malayalam_only"
    if has_tam and has_lat:
        return "tamil+latin"
    if has_tam:
        return "tamil_only"
    if has_lat:
        return "latin_only"
    if has_dev:
        return "devanagari"
    if has_arb:
        return "arabic"
    if has_han:
        return "han"
    if has_cyr:
        return "cyrillic"
    return "no_letters"


def manglish_screen(text: str) -> bool:
    if MAL.search(text) or TAM.search(text) or not LAT.search(text):
        return False
    tokens = re.findall(r"[A-Za-z]+", text.lower())
    return any(t in MANGlish_LEX for t in tokens)


def char_health(text: str) -> dict:
    return {
        "replacement_char": text.count("\ufffd"),
        "control_chars": sum(1 for ch in text if ord(ch) < 32 and ch not in "\t\n\r"),
        "nbsp": text.count("\u00a0"),
        "zero_width": sum(1 for ch in text if ch in "\u200b\u200c\u200d\ufeff"),
        "starts_or_ends_space": text != text.strip(),
        "double_space": "  " in text,
    }


# ---------------------------------------------------------------- XLSX reader
def col_to_idx(ref: str) -> int:
    m = re.match(r"([A-Z]+)", ref or "")
    if not m:
        return 0
    n = 0
    for ch in m.group(1):
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def read_xlsx_rows(path: Path):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        shared = []
        if "xl/sharedStrings.xml" in names:
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.iter(f"{{{NS['m']}}}si"):
                shared.append("".join(t.text or "" for t in si.iter(T)))
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        relmap = {r.get("Id"): r.get("Target") for r in rels}
        out = []
        for sh in wb.find("m:sheets", NS):
            rid = sh.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
            target = relmap[rid]
            if not target.startswith("xl/"):
                target = "xl/" + target.lstrip("/")
            root = ET.fromstring(z.read(target))
            rows = []
            for row in root.iter(f"{{{NS['m']}}}row"):
                cells = {}
                for c in row.findall("m:c", NS):
                    idx = col_to_idx(c.get("r"))
                    t = c.get("t")
                    v = c.find("m:v", NS)
                    if t == "s" and v is not None:
                        val = shared[int(v.text)]
                    elif t == "inlineStr":
                        isel = c.find("m:is", NS)
                        val = "".join(x.text or "" for x in isel.iter(T)) if isel is not None else ""
                    elif v is not None:
                        val = v.text
                    else:
                        val = ""
                    cells[idx] = val
                rows.append({i: cells.get(i, "") for i in range(max(cells) + 1)} if cells else {})
            out.append({"name": sh.get("name"), "target": target, "rows": rows, "zip_names": names})
        return out


# ------------------------------------------------------------------ XLSX audit
def audit_dravidian():
    sheets = read_xlsx_rows(XLSX)
    sheet = sheets[0]
    all_rows = sheet["rows"]
    header = [all_rows[0].get(0, ""), all_rows[0].get(1, "")]
    data = []
    blank_row_elements = 0
    for r in all_rows[1:]:
        if not r or all(v == "" for v in r.values()):
            blank_row_elements += 1
            continue
        data.append((r.get(0, ""), r.get(1, "")))

    raw_label_counts = Counter(lbl for _, lbl in data)
    msg_missing = [i for i, (m, _) in enumerate(data) if str(m).strip() == ""]
    lbl_missing = [i for i, (_, l) in enumerate(data) if str(l).strip() == ""]

    # whitespace-only labels are distinct from empty
    ws_labels = Counter(repr(l) for _, l in data if str(l) != str(l).strip())

    norm_label = lambda l: str(l).strip()
    norm_counts = Counter(norm_label(l) for _, l in data)

    texts = [str(m) for m, _ in data]
    labels = [norm_label(l) for _, l in data]

    exact_groups = defaultdict(list)
    for i, t in enumerate(texts):
        exact_groups[t].append(i)
    exact_dup_groups = {k: v for k, v in exact_groups.items() if len(v) > 1}
    exact_excess = sum(len(v) - 1 for v in exact_dup_groups.values())

    near_groups = defaultdict(list)
    empty_key = 0
    for i, t in enumerate(texts):
        k = norm_key(t)
        if not k:
            empty_key += 1
        near_groups[k].append(i)
    near_dup_groups = {k: v for k, v in near_groups.items() if len(v) > 1 and k}
    near_excess = sum(len(v) - 1 for v in near_dup_groups.values())

    conflicts = []
    for k, idxs in near_groups.items():
        ls = {labels[i] for i in idxs}
        if len(ls) > 1:
            conflicts.append({"key": k[:120], "labels": sorted(ls), "n": len(idxs),
                              "samples": [texts[i][:160] for i in idxs[:3]]})

    script_counts = Counter(script_bucket(t) for t in texts)
    script_by_label = defaultdict(Counter)
    for t, l in zip(texts, labels):
        script_by_label[script_bucket(t)][l] += 1

    manglish = [i for i, t in enumerate(texts) if manglish_screen(t)]
    manglish_by_label = Counter(labels[i] for i in manglish)

    health = Counter()
    for t in texts:
        h = char_health(t)
        for k, v in h.items():
            if isinstance(v, bool) and v:
                health[k] += 1
            elif isinstance(v, int) and v:
                health[k] += v

    lengths = [len(t.split()) for t in texts]

    return {
        "file": XLSX.name,
        "sheet_names": [s["name"] for s in sheets],
        "header": header,
        "row_elements_including_blanks": len(all_rows),
        "blank_row_elements": blank_row_elements,
        "records": len(data),
        "raw_label_counts": {repr(k): v for k, v in raw_label_counts.most_common()},
        "normalised_label_counts": dict(norm_counts.most_common()),
        "whitespace_label_variants": {k: v for k, v in ws_labels.items() if k.count(" ") or "\\t" in k or "\\n" in k},
        "missing_message_records": len(msg_missing),
        "missing_label_records": len(lbl_missing),
        "exact_duplicate_groups": len(exact_dup_groups),
        "exact_duplicate_excess": exact_excess,
        "near_duplicate_groups": len(near_dup_groups),
        "near_duplicate_excess": near_excess,
        "empty_normalised_key": empty_key,
        "conflicting_label_groups": len(conflicts),
        "conflict_examples": conflicts[:8],
        "script_counts": dict(script_counts.most_common()),
        "script_by_label": {k: dict(v.most_common()) for k, v in script_by_label.items()},
        "manglish_screen_count": len(manglish),
        "manglish_screen_by_label": dict(manglish_by_label.most_common()),
        "char_health": dict(health),
        "tokens_mean": round(sum(lengths) / len(lengths), 2),
        "tokens_median": sorted(lengths)[len(lengths) // 2],
        "tokens_max": max(lengths),
        "tokens_min": min(lengths),
        "sha256": hashlib.sha256(XLSX.read_bytes()).hexdigest(),
        "distinct_exact_messages": len(exact_groups),
    }


# ------------------------------------------------------------------- CSV audit
def audit_mendeley():
    with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    header = rows[0]
    data = rows[1:]
    widths = Counter(len(r) for r in data)
    # keep only rows matching header width
    clean = [r for r in data if len(r) == len(header)]
    bad_width = [i for i, r in enumerate(data) if len(r) != len(header)]

    idx = {name: i for i, name in enumerate(header)}
    texts = [r[idx["TEXT"]] for r in clean]
    labels_raw = [r[idx["LABEL"]] for r in clean]
    raw_counts = Counter(labels_raw)
    norm = lambda l: l.strip().lower()
    labels = [norm(l) for l in labels_raw]
    norm_counts = Counter(labels)

    # metadata columns
    meta = {}
    for col in ("URL", "EMAIL", "PHONE"):
        if col in idx:
            vals = [r[idx[col]] for r in clean]
            vc = Counter(v.strip().lower() for v in vals)
            meta[col] = {"unique_values": len(vc),
                         "top": dict(vc.most_common(6)),
                         "non_no": sum(1 for v in vals if v.strip().lower() not in ("no", "", "0"))}

    missing_text = sum(1 for t in texts if t.strip() == "")
    missing_label = sum(1 for l in labels_raw if l.strip() == "")

    exact_groups = defaultdict(list)
    for i, t in enumerate(texts):
        exact_groups[t].append(i)
    exact_dup = {k: v for k, v in exact_groups.items() if len(v) > 1}
    exact_excess = sum(len(v) - 1 for v in exact_dup.values())

    near = defaultdict(list)
    for i, t in enumerate(texts):
        near[norm_key(t)].append(i)
    near_dup = {k: v for k, v in near.items() if len(v) > 1 and k}
    near_excess = sum(len(v) - 1 for v in near_dup.values())

    conflicts = []
    for k, ids in near.items():
        ls = {labels[i] for i in ids}
        if len(ls) > 1:
            conflicts.append({"key": k[:120], "labels": sorted(ls), "n": len(ids),
                              "samples": [texts[i][:160] for i in ids[:3]]})

    script = Counter(script_bucket(t) for t in texts)
    script_by_label = defaultdict(Counter)
    for t, l in zip(texts, labels):
        script_by_label[script_bucket(t)][l] += 1

    health = Counter()
    for t in texts:
        for k, v in char_health(t).items():
            if isinstance(v, bool) and v:
                health[k] += 1
            elif isinstance(v, int) and v:
                health[k] += v

    lengths = [len(t.split()) for t in texts]

    # duplicates vs the Dravidian dataset
    return {
        "file": CSV_PATH.name,
        "header": header,
        "row_width_distribution": dict(widths),
        "malformed_rows": len(bad_width),
        "records": len(clean),
        "raw_label_counts": dict(raw_counts.most_common()),
        "normalised_label_counts": dict(norm_counts.most_common()),
        "missing_text": missing_text,
        "missing_label": missing_label,
        "metadata_columns": meta,
        "exact_duplicate_groups": len(exact_dup),
        "exact_duplicate_excess": exact_excess,
        "near_duplicate_groups": len(near_dup),
        "near_duplicate_excess": near_excess,
        "conflicting_label_groups": len(conflicts),
        "conflict_examples": conflicts[:8],
        "script_counts": dict(script.most_common()),
        "script_by_label": {k: dict(v.most_common()) for k, v in script_by_label.items()},
        "char_health": dict(health),
        "tokens_mean": round(sum(lengths) / len(lengths), 2),
        "tokens_median": sorted(lengths)[len(lengths) // 2],
        "tokens_max": max(lengths),
        "tokens_min": min(lengths),
        "sha256": hashlib.sha256(CSV_PATH.read_bytes()).hexdigest(),
        "distinct_exact_messages": len(exact_groups),
        "_texts": texts,
    }


def cross_dataset(drav, mend):
    a = {}
    for m, _ in drav["_pairs"]:
        a.setdefault(norm_key(str(m)), []).append(m)
    b = {}
    for t in mend["_texts"]:
        b.setdefault(norm_key(t), []).append(t)
    inter = set(a) & set(b)
    return {
        "dravidian_normalised_keys": len(a),
        "mendeley_normalised_keys": len(b),
        "overlapping_keys": len(inter),
        "overlap_examples": [a[k][0][:160] for k in list(inter)[:5]],
        "dravidian_messages_in_overlap": sum(len(a[k]) for k in inter),
        "mendeley_messages_in_overlap": sum(len(b[k]) for k in inter),
    }


if __name__ == "__main__":
    d = audit_dravidian()
    m = audit_mendeley()

    # stash pairs for cross-dataset check
    sheets = read_xlsx_rows(XLSX)
    pairs = []
    for r in sheets[0]["rows"][1:]:
        if r and not all(v == "" for v in r.values()):
            pairs.append((r.get(0, ""), r.get(1, "")))
    d["_pairs"] = pairs
    x = cross_dataset(d, m)
    d.pop("_pairs", None)
    m.pop("_texts", None)

    result = {"dravidian": d, "mendeley": m, "cross_dataset": x}
    (OUT / "dataset_audit.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    def show(name, r):
        print(f"\n{'='*70}\n{name}  ({r['file']})  sha256={r['sha256'][:16]}...")
        for k in ("records", "raw_label_counts", "normalised_label_counts",
                  "missing_message_records", "missing_label_records", "missing_text",
                  "missing_label", "exact_duplicate_groups", "exact_duplicate_excess",
                  "near_duplicate_groups", "near_duplicate_excess",
                  "conflicting_label_groups", "script_counts", "script_by_label",
                  "char_health", "tokens_mean", "tokens_median", "tokens_max",
                  "manglish_screen_count", "manglish_screen_by_label"):
            if k in r:
                print(f"  {k}: {r[k]}")

    show("DRAVIDIAN XLSX", d)
    show("MENDELEY CSV", m)
    print("\nCROSS-DATASET:", json.dumps(x, ensure_ascii=False, indent=2))
    print("\nwrote", OUT / "dataset_audit.json")
