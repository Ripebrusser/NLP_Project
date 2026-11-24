# Data Leakage and Split Plan

**Status:** executed 5 November 2026; files and hashes recorded. Classical baselines trained; transformers not started.  
**Evidence:** `Research Work/audit_output/dataset_audit.json`, `dataset_forensics.json`, `split_simulation.json`.  
**Simulation script:** `Research Work/split_plan_simulation.py` (deterministic, seed 42).

> **Execution record (5 Nov 2026):** splits were generated under project direction. D1 Malayalam: 1,394 / 299 / 299 (Spam 157/34/34); D2: 4,127 / 885 / 883. Group and normalised-text overlap across splits is zero. SHA-256 hashes and the full manifest are in `Research Work/phase2/splits/split_manifest.json`; the integrity report is `Research Work/phase2/reports/SPLIT_INTEGRITY.md`. D1 access provenance remains undocumented.

---

## 1. Leakage inventory

### 1.1 Exact duplicates

| Dataset | Duplicate groups | Excess records | Share of corpus |
|---|---|---|---|
| D1 Dravidian | 1,154 | 1,224 | 15.9% of 7,717 |
| D2 Mendeley | 22 | 22 | 0.4% of 5,971 |

### 1.2 Near-duplicate / template duplicates

Normalisation: NFKC → lowercase → URLs → `<url>` → digits → `<num>` → punctuation removed → whitespace collapsed.

| Dataset | Groups | Excess records | Share |
|---|---|---|---|
| D1 | 1,245 | 1,375 | 17.8% |
| D2 | 179 | 270 | 4.5% |

Largest D1 clusters: "sorry i ll call later" (12 copies, all Ham); a Telugu template (10, Ham); a Tamil rummy spam template (6, Spam); "as per your request ... callertune" (5, Spam). These are template messages that would otherwise appear in both train and test.

### 1.3 Conflicting labels

| Dataset | Groups | Records | Examples |
|---|---|---|---|
| D1 | 28 | 58 | Identical English SMS labelled both Ham and Spam; identical Tamil road-safety message labelled both |
| D2 | 37 | 76 | Ringtone/subscription messages labelled both spam and smishing |

These are **source label noise**, not duplicates to delete. They stay in the data and are grouped together. Phase 2 excludes conflicting groups from supervised experiments: D1 Malayalam has 0; D2 excludes 37 groups / 76 records.

### 1.4 Cross-dataset leakage

| Measure | Value |
|---|---|
| Shared normalised keys | 773 |
| D1 records with a D2 twin | 1,555 (20.2%) |
| D2 records with a D1 twin | 831 (13.9%) |

**Consequence:** any experiment that pools D1 and D2 leaks. Pooling is prohibited (see `RESEARCH_SCOPE_AND_LABEL_DECISION.md` §9). Cross-dataset *evaluation* is allowed only with disjoint training and test files.

### 1.5 Source-block structure (D1)

The workbook is a concatenation of blocks. Rows 5,000–5,999 are **1,000 consecutive Ham messages**; rows 0–999 are 826 Tamil-only messages; rows 2,000–2,999 are 100% Latin. A random split would place near-identical source material on both sides.

### 1.6 Metadata shortcut (D2)

`URL`, `EMAIL`, `PHONE` are binary yes/no flags, not raw values (URL yes=207, EMAIL yes=19, PHONE yes=844). They are **derivable from the text by regex**, so they add no information a text model cannot learn — but they can act as a shortcut if used as separate features. The primary experiment is **text-only**; a metadata ablation is a secondary, explicitly reported experiment.

---

## 2. Split design

### 2.1 Rules

1. **Grouping unit:** the normalised-text key. Every record sharing a key goes to exactly one split.
2. **Stratification:** by class **and** language/script group (D1) or class only (D2).
3. **Proportions:** 70% train / 15% validation / 15% test.
4. **Seed:** 42, fixed in code and recorded with the split file.
5. **Test isolation:** the test split is written once, hashed, and not inspected until final evaluation. No tuning, threshold selection or feature choice may use it.
6. **Class imbalance:** handled with class weights only. **No SMOTE, no augmentation, no synthetic samples.**
7. **Minimum support:** a per-class result is reported only if the test split contains at least 30 examples of that class; otherwise the result is marked exploratory and reported with its support count.

### 2.2 Simulated split sizes (actual output, seed 42)

**D1 — all languages, Ham/Spam (7,714 records; 6,340 groups; 10 strata)**

| Split | Records | Ham | Spam |
|---|---|---|---|
| Train | 5,399 | 4,428 | 971 |
| Validation | 1,159 | 944 | 215 |
| Test | 1,156 | 948 | 208 |

**D1 — Malayalam subset, any script (1,992 records; 1,853 groups)**

| Split | Records | Ham | Spam |
|---|---|---|---|
| Train | 1,394 | 1,237 | 157 |
| Validation | 299 | 265 | 34 |
| Test | 299 | 265 | **34** |

34 spam in test meets the ≥30 rule, narrowly.

**D1 — Malayalam-only script (1,489 records; 1,379 groups)**

| Split | Records | Ham | Spam |
|---|---|---|---|
| Train | 1,042 | 1,000 | 42 |
| Validation | 224 | 215 | 9 |
| Test | 223 | 214 | **9** |

**9 spam in test fails the ≥30 rule.** This subset can be reported descriptively only; no per-class F1 claim.

**D2 — three-class (5,971 records; 5,700 groups)**

| Split | Records | Ham | Spam | Smishing |
|---|---|---|---|---|
| Train | 4,180 | 3,391 | 340 | 449 |
| Validation | 897 | 727 | 75 | 95 |
| Test | 894 | 726 | **74** | **94** |

**D2 — binary ham vs smishing (5,971 records)**

| Split | Records | Not smishing | Smishing |
|---|---|---|---|
| Train | 4,180 | 3,731 | 449 |
| Validation | 896 | 801 | 95 |
| Test | 895 | 801 | **94** |

### 2.3 Leakage self-check

The simulation asserts, for every case:

```
train_keys ∩ val_keys = ∅
train_keys ∩ test_keys = ∅
val_keys  ∩ test_keys = ∅
```

All five cases passed. The assertion is part of the script, so any future regeneration re-checks it.

### 2.4 What the simulation does **not** remove

- Near-duplicates that normalisation fails to catch (paraphrases, transliteration variants).
- Semantic templates across languages (e.g. the same promotional campaign in Malayalam and Tamil).
- The D1 source-block effect: stratification spreads blocks across splits, but block-level style remains.
- D1↔D2 overlap: only relevant if both datasets are used in one experiment; T4 keeps train and test files disjoint.

---

## 3. Cross-dataset evaluation design (T4)

**Purpose:** test whether a spam classifier survives a change of corpus. **Not** a combined model.

| Experiment | Train | Test | Caveat |
|---|---|---|---|
| T4a | D2 ham + spam (English) | D1 Latin-only ham + spam | Label definitions differ; D1 spam includes promotional messages |
| T4b | D1 Latin-only ham + spam | D2 ham + spam | D2 spam is UCI-derived; domain shift |
| T4c *(optional)* | D1 Malayalam | D1 Tamil/Telugu/Kannada | Script shift, same corpus family |

Rules: no target-side tuning; report in-domain vs cross-domain side by side; no claim of language generalisation from T4a/T4b (both are English/Latin).

---

## 4. Evaluation protocol

| Item | Decision |
|---|---|
| Primary metric | **Macro-F1** |
| Secondary | Per-class precision/recall/F1, confusion matrix, MCC, balanced accuracy |
| Supplementary | Accuracy (never alone) |
| Uncertainty | Bootstrap 95% CI, 1,000 resamples **by duplicate group**, not by record |
| Thresholds | Selected on validation only; frozen before test |
| Multiple seeds | 3 seeds for transformer runs if compute allows; report mean ± SD |
| Error analysis | Stratified sample of 50 errors per class; annotate script, length, URL presence, language |
| Reporting | Support counts beside every metric |

**Why macro-F1:** both datasets are imbalanced (D1 18.1% spam; D2 8.2% spam, 10.7% smishing). Accuracy would reward the majority class.

---

## 5. Split artefacts to be produced (not yet created)

| Artefact | Content | Status |
|---|---|---|
| `splits/d1_all_seed42.csv` | record index, group key, split | Not created |
| `splits/d1_malayalam_seed42.csv` | as above | Not created |
| `splits/d2_3class_seed42.csv` | as above | Not created |
| `splits/manifest.json` | seed, ratios, row counts, SHA-256 of each split file | Not created |

These are produced only after scope approval, by a script that reads the **original** files and writes derived copies. Original files are never modified.

---

## 6. Known limitations of this plan

1. **Malayalam-only-script test support is 9 spam** — below the reporting threshold.
2. **Grouping by normalised text cannot catch paraphrases or cross-script transliterations.**
3. **Label noise** (28 D1 / 37 D2 conflicting groups) is irreducible without re-annotation, which is prohibited.
4. **D1's source blocks** mean the test set is not a random sample of real SMS traffic; absolute scores will be optimistic.
5. **D2's ham/spam portion is UCI-derived** and near ceiling in prior work; high scores are expected and uninformative.
6. **No speaker/sender metadata** exists, so sender-level leakage cannot be checked.
7. **Temporal leakage** cannot be assessed because neither dataset has timestamps.

These limitations must appear in the final report; they are not fixable within the project's constraints.
