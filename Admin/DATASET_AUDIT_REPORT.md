# Dataset Audit Report

**Project:** Malayalam / English SMS spam and smishing classification  
**Audit date:** 5 November 2026  
**Auditor:** project audit (automated, reproducible)  
**Files audited:**

| Dataset | Path | Bytes | SHA-256 |
|---|---|---|---|
| D1 Dravidian SMS | `Datasets/Spam Message Collection.xlsx` | 1,324,017 | `24ca099ac1ffabc0b02fd491f57d577c56afb932bc81c5964a40e32eab9a023b` |
| D2 Mendeley SMS | `Datasets/Dataset_5971.csv` | 595,987 | `649844f1c62a6b27e145eaf17a65f7010c56c390e11a794ea8329993a05ba71e` |

**Method:** Python 3.14 standard library only (`zipfile` + `xml.etree` for XLSX, `csv` for CSV, `unicodedata` for scripts). Scripts: `Research Work/audit_datasets.py`, `audit_forensics.py`, `audit_scripts.py`. Raw output: `Research Work/audit_output/dataset_audit.json`, `dataset_forensics.json`, `script_census.json`.

**No original file was modified. No label was changed on disk. No model was trained.**

---

## 0. Corrections to earlier reported figures

Earlier project documents (including the first draft of the Review 2 report) reported wrong counts. The verified values are:

| Earlier figure | Verified value | Why the earlier figure was wrong |
|---|---|---|
| 7,980 records (D1) | **7,717** | The earlier parser did not exclude empty/formatting `<row>` elements and mis-handled the sheet. The sheet contains 101,173 `<row>` elements, of which 93,456 are empty formatting rows. |
| 7,718 records (D1) | **7,717 data rows** | 7,718 is the spreadsheet row count **including the header**. |
| 7,715 records (D1) | **7,714 usable records** | 7,717 minus 2 empty messages minus 1 malformed label. |
| "missing label 1" (D1) | **0 empty labels; 1 invalid label `Spa,`** | `Spa,` is malformed, not absent. It is reported separately and excluded, never auto-corrected. |
| "missing messages 3" (D1) | **2 empty messages** | Only two records have no visible characters (indices 5121 and 5212; both labelled Ham). |
| Malayalam 1,996 / Tamil 1,241 (D1) | **Malayalam 1,992 / Tamil 1,175 / Telugu 1,068 / Kannada 1,345 / Latin-only 2,130** | The earlier regex covered only Malayalam and Tamil Unicode blocks; Kannada and Telugu were counted as "no letters". |
| "Malayalam + English dataset" (D1) | **Five-language Dravidian corpus** | The official record lists English, Tamil, Telugu, Kannada and Malayalam. |

These corrections supersede all earlier statements and are used throughout the Review 2 documents.

---

## 1. Dataset 1 — Spam Message Collection.xlsx

### A. Structure and integrity

| Property | Value |
|---|---|
| Format | Office Open XML workbook (`.xlsx`), 11 zip entries |
| Sheet name | **`Dravidian Dataset`** (the only sheet) |
| Header | `Message`, `Type` |
| Row elements in sheet XML | 101,173 |
| Empty formatting rows | 93,456 |
| Data records | **7,717** |
| Columns | 2 (both text) |
| Empty messages | **2** (`Ham`) |
| Empty labels | **0** |
| Invalid labels | **1** (`Spa,`) |
| Exact duplicate groups | **1,154** |
| Exact duplicate excess | **1,224** records (15.9%) |
| Near-duplicate groups | **1,245** |
| Near-duplicate excess | **1,375** records (17.8%) |
| Conflicting-label groups | **28** (58 records) |
| Distinct exact messages | 6,493 |
| Tokens per message | mean 12.47, median 10, max 80 |
| Encoding damage | 5 U+FFFD replacement characters |
| Invisible characters | 1,230 zero-width characters; 57 non-breaking spaces |
| Whitespace defects | 58 messages with leading/trailing spaces; 291 with double spaces |

**Near-duplicate definition (documented, not ad hoc):** NFKC normalisation → lowercase → URLs replaced by `<url>` → digit runs replaced by `<num>` → all non-alphanumeric characters (except Malayalam/Tamil/Telugu/Kannada ranges) replaced by a space → whitespace collapsed. This detects template SMS (e.g. the same promotional message with different phone numbers).

**Duplicate handling decision:** duplicates are **retained** in the dataset; they are grouped so that all members of a duplicate group fall in the same split. Reporting includes both full-corpus and group-aware results.

### B. Label audit

| Raw label | Count | Status |
|---|---|---|
| `Ham` | 6,322 | Valid |
| `Spam` | 1,394 | Valid |
| `Spa,` | 1 | **Invalid (typo)** |
| *empty* | 0 | — |

- No capitalisation variants exist (`Ham`/`Spam` are consistent).
- The single `Spa,` record is a **Telugu** Airtel 5G promotional message (row index 3749). Its content is consistent with Spam, but the label is malformed.
- **Decision:** the `Spa,` record is **excluded** from modelling (1 of 7,717 = 0.013%). It is not relabelled, because relabelling would invent ground truth. The raw file retains it.
- **Decision:** the 2 empty messages are excluded (no text to classify).
- **Usable dataset:** 7,714 records — **Ham 6,320 / Spam 1,394** (18.07% spam).

**Class definitions are documented by the creators:** Ham = normal messages; Spam = "business, annoying, and unnecessary messages an anonymous user sends". This is **not** a phishing or smishing definition.

### C. Language and script audit

Script detected by Unicode block per message (a message may contain several):

| Script composition | Records | Share |
|---|---|---|
| Latin only | 2,130 | 27.6% |
| Malayalam only | **1,489** | 19.3% |
| Malayalam + Latin | 503 | 6.5% |
| Tamil only | 883 | 11.4% |
| Tamil + Latin | 292 | 3.8% |
| Telugu only | 747 | 9.7% |
| Telugu + Latin | 321 | 4.2% |
| Kannada only | 980 | 12.7% |
| Kannada + Latin | 365 | 4.7% |
| Devanagari mixtures / other | 7 | 0.1% |
| No letters (emoji/number only) | 2 | 0.03% |

**Language totals (script present, including mixed messages):**

| Language | Records | Share | Ham | Spam | Spam rate |
|---|---|---|---|---|---|
| Malayalam | 1,992 | 25.8% | 1,767 | 225 | **11.3%** |
| Tamil | 1,175 | 15.2% | 963 | 212 | 18.0% |
| Telugu | 1,068 | 13.8% | 964 | 104 | 9.7% |
| Kannada | 1,345 | 17.4% | 1,014 | 331 | 24.6% |
| Latin only | 2,130 | 27.6% | 1,608 | 522 | 24.5% |

**Critical confound:** the spam rate depends strongly on the script of the message (4.0% for Malayalam-only, 32.8% for Malayalam+Latin, 59.7% for Kannada+Latin, 65.4% for Tamil+Latin). Script/language is therefore predictive of the label. Any random split will let a model exploit language rather than message content. This drives the stratified, script-aware split in `DATA_LEAKAGE_AND_SPLIT_PLAN.md` and must be reported as a limitation.

**Manglish:** a documented 100-word Romanised-Malayalam screening lexicon found only **34 records (0.44%)** containing at least one Malayalam-origin function/content word in Latin script. This is a lower-bound screen, not an annotation. **Manglish cannot be reliably isolated in this dataset.** Latin-script messages cannot be assumed to be Manglish; they are overwhelmingly English.

**Row-order / source-block structure:** the file is a concatenation of blocks with very different composition:

| Rows | Dominant script | Labels |
|---|---|---|
| 0–999 | Tamil | 922 Ham / 78 Spam |
| 1,000–1,999 | Latin + Tamil | 615 Ham / 385 Spam |
| 2,000–2,999 | Latin only | 816 Ham / 184 Spam |
| 3,000–3,999 | Latin + Telugu | 811 Ham / 188 Spam |
| 4,000–4,999 | Malayalam | 985 Ham / 15 Spam |
| 5,000–5,999 | Malayalam | **1,000 Ham / 0 Spam** |
| 6,000–6,999 | Telugu/Malayalam | 784 Ham / 216 Spam |
| 7,000–7,716 | Mixed | 389 Ham / 328 Spam |

A block of 1,000 consecutive records is 100% Ham. This is direct evidence of source-block structure and a serious leakage risk for random splits.

**English/UCI markers in D1:** `Txt STOP` (12), `FreeMsg` (3), `WINNER` (7), `www.` (82), `http` (314), `Nokia` (20). The corpus contains a substantial English SMS-spam component of the same kind as UCI, not only Dravidian-language messages.

### D. Class-by-language audit

| Subset | Records | Ham | Spam | Usable for evaluation? |
|---|---|---|---|---|
| Malayalam (any script) | 1,992 | 1,767 | 225 | Yes, with grouped split; spam test ≈ 34 |
| Malayalam-only script | 1,489 | 1,429 | 60 | Marginal; spam test ≈ 9–10 |
| Tamil | 1,175 | 963 | 212 | Yes |
| Telugu | 1,068 | 964 | 104 | Marginal |
| Kannada | 1,345 | 1,014 | 331 | Yes |
| Latin only | 2,130 | 1,608 | 522 | Yes |

The **Malayalam-only-script** subset has only 60 spam messages in total. A held-out test set will contain roughly 9–10 spam messages, which is too small for a stable per-class F1. The broader Malayalam subset (1,992 records, 225 spam) is the defensible minimum, and results must be reported with confidence intervals and support counts.

### E. Provenance and licence

| Property | Verified value |
|---|---|
| Dataset | "Spam SMS in Dravidian Languages" |
| Authors | Ramanujam Elangovan (NIT Silchar), Abirami A M (Thiagarajar College of Engineering) |
| Publisher | IEEE DataPort |
| Date | 2 June 2023 |
| DOI | **10.21227/dcym-pd69** |
| Official URL | https://ieee-dataport.org/documents/spam-sms-dravidian-languages |
| Languages (official) | English, Tamil, Telugu, Kannada, Malayalam |
| Size (official) | "Nearly 7700 messages" |
| Collection | Google Form sent to friends and contacts |
| Labelling | "Language experts (reading and writing skills)" |
| Labels | Ham / Spam |
| Label meaning | Ham = mostly normal; Spam = business, annoying, unnecessary messages from anonymous users |
| File listed | `Spam Message Collection.xlsx`, **1.26 MB** — matches the local file name and size |
| Access | **IEEE DataPort Subscription required** ("LOGIN TO ACCESS DATASET FILES") — Standard Dataset |
| Licence on record | **Not displayed** on the public dataset page |
| Platform licence | Terms of Use §2(g): uploaded Content is made available for viewing, downloading and **reuse**, and "Except as otherwise specifically permitted by IEEE …, Content will be made available subject to the terms of the **Creative Commons Attribution (CC-BY) License** [CC BY 3.0 US]" |
| Research use | Platform FAQ says research use is allowed with citation, but the dataset page itself displays **no licence** and requires a subscription. Dataset-specific research permission is therefore **not independently established**. |
| Redistribution | **Not established / do not redistribute.** Access is subscription-based; credentials are personal and non-transferable (§2a); public sharing is listed as misuse (§5a vii). No written permission is on file. |
| Related publication | "Multi-lingual Spam SMS detection using a hybrid deep learning technique" (IEEE, arnumber 10028936) |

**Provenance assessment:** the local file matches the official listing in file name, size, sheet layout (two columns), language mix and approximate record count. Provenance is therefore **strongly consistent**. The **licence and access question is NOT resolved**: the public dataset page displays no licence, states “Subscription Required,” and no subscription receipt, download log or author permission exists in the project. The platform-wide Terms of Use mention a CC BY 3.0 US default for uploaded content, but that is not a dataset-specific grant and does not establish this team’s authorisation to hold or redistribute the file. Treat research use as **unconfirmed pending written clarification**; do not redistribute raw messages, screenshots or examples. See `Admin/DATASET_PROVENANCE_AND_PERMISSIONS.md`.

### F. Verdict — Dataset 1

**BLOCKED — access provenance unverified.** Research use is permitted by the platform, but the project cannot document how the file was obtained. If a subscription receipt or author permission is produced, the dataset is **SUITABLE WITH RESTRICTIONS** for **multilingual Dravidian SMS spam/ham classification**, specifically:
- Malayalam-script ham vs spam (primary subset, 1,992 records);
- optionally Tamil/Telugu/Kannada as secondary language comparisons.

**NOT SUITABLE for:**
- phishing or smishing detection (no such labels; creator defines spam as business/annoying messages);
- Manglish-specific claims (34 heuristic hits only; Latin text is mostly English);
- any claim that the corpus is Malayalam-English only (it is five-language);
- any random-split evaluation (source blocks and duplicate clusters leak).

**Research questions it can support:** Malayalam-script spam detection; script-mixing effects; classical vs multilingual transformer comparison; language/script confound quantification.

**Research questions it cannot support:** Malayalam phishing detection; Manglish detection; URL/APK-based threat detection; cross-lingual smishing transfer.

---

## 2. Dataset 2 — Dataset_5971.csv

### A. Structure and integrity

| Property | Value |
|---|---|
| Format | CSV, UTF-8 with BOM, CRLF |
| Header | `LABEL, TEXT, URL, EMAIL, PHONE` |
| Data rows | **5,971** |
| Malformed rows | 0 |
| Empty text | 0 |
| Empty label | 0 |
| Exact duplicate groups / excess | **22 / 22** |
| Near-duplicate groups / excess | **179 / 270** (4.5%) |
| Conflicting-label groups | **37** (76 records) |
| Distinct exact messages | 5,949 |
| Tokens per message | mean 15.81, median 13, max 171 |
| Encoding damage | **185** U+FFFD replacement characters |
| Whitespace defects | 254 leading/trailing; 306 double spaces |

### B. Label audit

| Raw label | Count | Normalised |
|---|---|---|
| `ham` | 4,844 | ham 4,844 |
| `Smishing` | 616 | smishing 638 |
| `smishing` | 22 | (above) |
| `spam` | 466 | spam 489 |
| `Spam` | 23 | (above) |

- Capitalisation is inconsistent for **45 records** (23 `Spam`, 22 `smishing`). Normalisation is documented and applied **in analysis only**; the original file is unchanged.
- Normalised distribution: **ham 4,844 (81.1%) / spam 489 (8.2%) / smishing 638 (10.7%)** — matches the official Mendeley record exactly.
- **Decision: Spam and Smishing are kept separate.** They are not merged, because smishing is the cybersecurity-relevant class and merging would destroy the only phishing-adjacent signal in the project.
- 37 near-duplicate groups carry conflicting labels, mostly `spam` vs `smishing` (e.g. ringtone-subscription messages). This is genuine boundary noise in the source data and must be reported, not silently fixed.

### C. Language and script audit

| Script | Records |
|---|---|
| Latin only | 5,969 |
| Han + Latin | 1 |
| No letters | 2 |
| **Any Indic script (Malayalam/Tamil/Telugu/Kannada)** | **0** |

**Dataset 2 is English-only.** No Malayalam, Manglish, Tamil, Telugu or Kannada content exists in it. It cannot support any Malayalam or code-mixed claim.

### D. Class-by-language audit

Not applicable: one language (English). Class distribution as above.

### E. Provenance and licence

| Property | Verified value |
|---|---|
| Dataset | "SMS Phishing Dataset for Machine Learning and Pattern Recognition" |
| Authors | Sandhya Mishra, Devpriya Soni (Jaypee Institute of Information Technology, Noida) |
| Publisher | Mendeley Data, Version 1 |
| Published | 20 June 2022 |
| DOI | **10.17632/f45bkkt8pr.1** |
| Official URL | https://data.mendeley.com/datasets/f45bkkt8pr/1 |
| Licence | **CC BY 4.0** |
| Size | 5,971 messages: 4,844 ham, 489 spam, 638 smishing |
| Related record | UCI SMS Spam Collection (`dt.fee.unicamp.br/~tiago/smsspamcollection`) is linked from the dataset page — the ham/spam portion derives from Almeida's corpus |
| Companion paper | Mishra & Soni, "SMS Phishing Dataset for Machine Learning and Pattern Recognition", SoCPaR 2022, Springer, DOI 10.1007/978-3-031-27524-1_57 |
| Metadata columns | `URL`, `EMAIL`, `PHONE` are **binary yes/no flags**, not raw values (URL: 207 yes; EMAIL: 19 yes; PHONE: 844 yes) |

**Provenance assessment:** verified against the official Mendeley record; counts and label set match exactly. **Licence permits research use with attribution.**

### F. Verdict — Dataset 2

**SUITABLE WITH RESTRICTIONS** for **English three-class ham/spam/smishing classification**.

Restrictions:
- English only — no Malayalam/Manglish generalisation may be claimed;
- class imbalance (ham 81.1%);
- spam/smishing boundary is noisy (37 conflicting groups; prior work reports the same confusion);
- the `URL`/`EMAIL`/`PHONE` flags are derivable from the text and can act as shortcut features; the primary experiment must be text-only;
- the corpus is partly derived from UCI, so it is not independent of English SMS-spam benchmarks.

**Research questions it can support:** English three-class smishing detection; spam-vs-smishing separability; classical vs transformer comparison; class-wise error analysis.

**Research questions it cannot support:** Malayalam or Manglish detection; multilingual smishing; URL/APK behaviour analysis (only presence flags exist).

---

## 3. Cross-dataset audit

| Check | Result |
|---|---|
| Shared normalised-text keys | **773** |
| D1 records with a D2 twin | **1,555** (20.2% of 7,717) |
| D2 records with a D1 twin | **831** (13.9% of 5,971) |
| Byte-identical files | None |
| Duplicate copies on disk | None (hashes differ; only two dataset files exist) |

**Label agreement for overlapping messages:**

| D1 label | D2 label | Count |
|---|---|---|
| Ham | ham | 1,340 |
| **Spam** | **smishing** | **189** |
| Spam | spam | 87 |
| **Spam** | **ham** | **51** |
| Ham | spam | 6 |
| Ham | smishing | 1 |

**Interpretation:** the two datasets are **not independent**. A fifth of D1 overlaps D2, and the dominant overlap for D1 "Spam" is D2 "**smishing**" (189 vs 87 for "spam"), with 51 direct contradictions. The label semantics differ: D1's "Spam" includes messages that D2 treats as smishing, and some that D2 treats as ham.

**Consequence:** combining the datasets for training would (a) leak test messages across datasets, (b) inject contradictory labels, and (c) teach dataset-source artefacts. **Combined training is rejected.** Cross-dataset *evaluation* (train on one, test on the other) remains a legitimate domain-shift probe and must be labelled as such.

---

## 4. Duplicate-file check

- Two dataset files exist on disk; hashes are distinct, so they are two different datasets.
- No `Dataset_5971(1).csv` or second copy of the workbook was found.
- `Original Files/NLM_MiniProject_report.zip` is unrelated (SEMG/EMG neuromuscular report) and is excluded from the research workflow.

---

## 5. Summary verdict

| Dataset | Verdict | Permitted task | Forbidden claims |
|---|---|---|---|
| D1 Dravidian SMS | **Blocked on access provenance; otherwise suitable with restrictions** | Malayalam-script (and other Dravidian-script) ham vs spam | Phishing/smishing; Manglish; Malayalam-English-only corpus; random-split results |
| D2 Mendeley SMS | **Suitable with restrictions** | English ham/spam/smishing | Malayalam/Manglish; multilingual generalisation; URL/APK behaviour |
| Combined | **Not suitable** | None (cross-dataset evaluation only) | Any joint training result presented as a single system |

**Remaining unresolved items:**
1. D1 **access authorisation** is not documented (IEEE DataPort subscription required). The licence itself permits research use with citation. **BLOCKED pending receipt or author permission.**
2. D1's `Spa,` label cannot be repaired without inventing ground truth; it is excluded. Documented, no decision needed.
3. Malayalam-only-script spam support (60 records) is too small for a standalone claim; the Malayalam-any-script subset (225 spam) is the minimum viable.
