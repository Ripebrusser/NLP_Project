# Review 2 Progress Report — Phase 2

> **AUDIT WORKING DOCUMENT.** This progress report records an earlier review stage, not the final statistical record. Authoritative sources: `CANONICAL_FINAL_RESULTS.md`, `FINAL_STATISTICAL_AUDIT.md` and `VERIFICATION_REPORT.md`.


> **CORRECTION NOTICE (6 Nov 2026):** Historical report preserved. “Block-held-out” / “source-block” means **leave-one-row-block-out stress test** on row-order proxies, not verified sources. The 6001 fold is **0.3685**; block counts are **630/991/371**; the zero-FP upper bound is **1.382%** (0/265 Ham), not 1.0%. MuRIL is complete and is not a performance improvement. See `Admin/CANONICAL_FINAL_RESULTS.md`.

## Classical and Multilingual Transformer Models for SMS Spam and Smishing Detection in Malayalam-Script and English Text

**Course:** 24AM3503 Natural Language Models  
**Department:** CSE (AI & ML), Dayananda Sagar University  
**Date:** 5 November 2026  
**Status:** statistical validation complete, final models selected, ready for prototype development; external validation not available; **D1 access provenance still undocumented**

> This report supersedes the pre-training Review 2 report. Dataset figures remain those verified in the audit; model figures are now actual outputs saved under `Research Work/phase2/`.

---

## 1. Executive summary

The project is now a two-task study, matching what the data can support:

1. **Primary — D1 Malayalam-script SMS: Ham vs Spam.** 1,992 Malayalam-containing records from the five-language Dravidian corpus. D1 has **no phishing labels**; no phishing claim is made.
2. **Secondary — D2 English SMS: Ham / Spam / Smishing.** 5,971 records, kept entirely separate.

Classical baselines are trained and evaluated. On the requested grouped random split:

| Experiment | Selected model | Accuracy | Macro-F1 | Key class metric |
|---|---|---|---|---|
| D1 Malayalam Ham/Spam | Linear SVM, char 2–4, C=0.5 | **98.66%** | **0.9650** | Spam recall 88.24%, precision 100% |
| D2 English 3-class | Logistic Regression, char 2–4, C=1.0 | **96.38%** | **0.8877** | Smishing recall 82.22%; Spam F1 0.803 |

**The D1 number is not a field-performance claim.** A leave-one-source-block-out check gives macro-F1 0.6964 and 0.3685 on the two evaluable blocks (the third block contains no Spam). D1’s Spam is concentrated in one 1,000-row block, so the random split measures within-source/template performance. This caveat is central, not cosmetic.

**MuRIL does not change that conclusion.** `google/muril-base-cased` reaches **0.9619 ± 0.0054** macro-F1 and **87.25%** Spam recall on the random split (three seeds) — within seed variation of, and slightly below, the SVM’s 0.9650/88.24%. Under leave-one-block-out it falls to **0.5028** pooled macro-F1 and **3.56%** Spam recall, against 0.5378/7.56% for the SVM, because it predicts Ham for all 213 Spam messages when block 6001–7000 is held out. The transformer reproduces the batch confound rather than removing it. See §10. Phase 2.3 completes the confidence intervals, paired comparison, threshold diagnosis and final model decision; see §11.

---

## 2. What was done

### 2.1 Dataset audit — COMPLETED

D1: **7,717** records (Ham 6,322 / Spam 1,394 / invalid `Spa,` 1), 2 empty messages, 1,154 exact and 1,245 near-duplicate groups, 28 conflict groups. D2: **5,971** (ham 4,844 / spam 489 / smishing 638), 22 exact and 179 near-duplicate groups, 37 conflict groups, **0 Indic-script records**. See `Admin/DATASET_AUDIT_REPORT.md`.

### 2.2 Malayalam subset — COMPLETED, discrepancy resolved

| Item | Value |
|---|---|
| Malayalam-containing | **1,992** |
| Labels | Ham 1,767 / Spam 225 (11.3% Spam) |
| Malayalam + Latin | 503 |
| Malayalam-only script | 1,489 (60 Spam) |
| Tamil/Telugu/Kannada co-occurrence | **0** |

The earlier count discrepancy was semantic: inclusive “contains” counts overlap (a message can contain Malayalam and Latin), while exclusive buckets sum to 7,717. The exclusive census is: Malayalam 1,489 + 503, Tamil 883 + 292, Telugu 747 + 322, Kannada 984 + 365, Latin-only 2,130, other/no letters 2.

### 2.3 Scope — ADOPTED FOR IMPLEMENTATION

The 5 November Phase 2 direction sets D1 as primary and D2 as secondary. Scope A is therefore in force. Datasets remain separate; Manglish is out (34 heuristic records, 0.44%); D1 is never called a phishing dataset; D2’s lack of Indic records is stated wherever D2 is discussed.

### 2.4 Literature — PARTIALLY COMPLETE

19 records retained, 1 excluded (P10). P06 is verified but covers six Indian languages and **excludes Malayalam**; FSSHAP is verified to abstract level only; **14 retained records remain bibliographic-only**. The Elangovan/Abirami series confirms Dravidian SMS spam is an active area, so no dataset or “first study” claim is made. See `Literature Review/LITERATURE_REVIEW_VERIFICATION.md`.

### 2.5 Preprocessing — COMPLETED

Scripts: `phase2/p2_extract.py`, `p2_duplicates.py`, `p2_split.py`. Steps: NFKC, zero-width/NBSP/control removal, whitespace collapse, URL/punctuation preservation, original row and message retained. No stemming, stopword removal, transliteration or translation. Duplicate grouping uses exact message, the audit’s normalised key, and a conservative fuzzy pass for D1 (char 3–5 TF-IDF cosine ≥ 0.90 plus token Jaccard ≥ 0.60). D1: 1,992 records → 1,824 groups (168 duplicate excess); no label conflicts. D2: 5,971 records → 5,700 pre-exclusion groups; excluding 37 conflict groups / 76 records leaves 5,895 rows and **5,663 experimental groups**.

### 2.6 Model development — CLASSICAL COMPLETE; MuRIL COMPLETE

Four feature configurations (word 1–1, word 1–2, char 2–4, char 2–5) × two families (Logistic Regression, Linear SVM) × C ∈ {0.5, 1, 2}. Selection used **validation macro-F1 only**; the test set was evaluated once after selection. Final models were refit on train+validation. Saved in `phase2/models/`.

### 2.7 Experiments — COMPLETED (classical baselines)

D1 test: 299 rows, 34 Spam. D2 test: 883 rows (ham 726 / spam 67 / smishing 90). Full tables in `phase2/reports/D1_RESULTS.md` and `D2_RESULTS.md`.

### 2.8 Leakage and splits — EXECUTED

70/15/15, seed 42, grouped and stratified. D1: 1,394 / 299 / 299 (157/34/34 Spam). D2: 4,127 / 885 / 883. Group and normalised-text overlap across splits is zero. Files and SHA-256 hashes: `phase2/splits/split_manifest.json`; report: `phase2/reports/SPLIT_INTEGRITY.md`.

**Source-block finding:** the split is group-safe but not block-safe. Malayalam rows occupy three populated 1,000-row blocks, with Spam concentrated in `6001–7000`. Holding out that block leaves only 12 Spam in training; the model reaches 6.6% Spam recall. This is documented as the main limitation and motivates a block-aware confirmatory design or external test set.

### 2.9 Documentation — COMPLETED for Phase 2

This report, the comparison, the split integrity report, results reports, error analysis, evidence register (§7) and readiness checklist are updated.

---

## 3. Progress inventory

| Component | Status | Evidence |
|---|---|---|
| Workspace/file audit | **COMPLETED** | Hashes + inventory |
| Dataset audit | **COMPLETED** | `DATASET_AUDIT_REPORT.md` |
| Scope/label decision | **COMPLETED — ADOPTED** | Phase 2 direction; `RESEARCH_SCOPE_AND_LABEL_DECISION.md` |
| Literature verification | **PARTIALLY COMPLETED** | 14 bibliographic-only |
| Preprocessing | **COMPLETED** | `phase2/p2_extract.py`, data CSVs |
| Duplicate/leakage control | **COMPLETED** | `phase2/p2_duplicates.py`, zero overlap |
| Splits + hashes | **COMPLETED** | `phase2/splits/split_manifest.json` |
| Classical models | **COMPLETED** | 4 saved models |
| Evaluation + errors | **COMPLETED** | Metrics JSON, reports |
| Block robustness | **COMPLETED** | `d1_block_robustness.json` |
| Transformers | **COMPLETED** | MuRIL seeds 42/43/44; random-split and block predictions saved |
| Literature full texts | **BLOCKED** | Publisher paywalls |

---

## 4. Corrections carried forward

| Earlier | Corrected | Cause |
|---|---|---|
| 7,980 records | 7,717 | Empty formatting rows |
| 7,718 | 7,717 data rows (+1 header) | Header counted |
| Malayalam 1,996 / Tamil 1,241 | Malayalam 1,992 / Tamil 1,175 / Telugu 1,068 / Kannada 1,345 | Incomplete Unicode coverage |
| “Malayalam-English corpus” | Five-language Dravidian corpus | Official record + census |
| “cybersecurity threat detection” | Spam + smishing only | No phishing labels |

---

## 5. Files produced

| File | Location |
|---|---|
| `REVIEW_2_PROGRESS_REPORT.md`, `REVIEW_2_PROGRESS_COMPARISON.md` | `Admin/` |
| `DATASET_AUDIT_REPORT.md`, `RESEARCH_SCOPE_AND_LABEL_DECISION.md`, `EVIDENCE_REGISTER.md`, `FINAL_AUDIT.md`, `BLOCKER_CLOSURE_REPORT.md` | `Admin/` |
| `LITERATURE_REVIEW_VERIFICATION.md`, `LITERATURE_COMPARISON_MATRIX.csv`, `VERIFIED_REFERENCES.md`, `RESEARCH_GAP_AND_NOVELTY_ANALYSIS.md` | `Literature Review/` |
| `DATA_LEAKAGE_AND_SPLIT_PLAN.md`, `MODEL_TRAINING_READINESS_CHECKLIST.md` | `Research Work/` |
| Phase 2 scripts | `Research Work/phase2/` |
| Derived data | `Research Work/phase2/data/` |
| Splits + manifest | `Research Work/phase2/splits/` |
| Models | `Research Work/phase2/models/` |
| Metrics/predictions/errors | `Research Work/phase2/metrics/` |
| Reports | `Research Work/phase2/reports/` |

---

## 6. Blockers

| Blocker | Status | Evidence needed |
|---|---|---|
| **B1 — D1 access provenance** | **OPEN** | Subscription receipt, download log or author permission |
| **B2 — Scope approval** | **CLOSED** | Phase 2 direction adopts Scope A |
| **B4 — Split execution** | **CLOSED** | Splits generated and hashed |
| **B7 — Literature full texts** | **OPEN** | Institutional access or explicit bibliographic-only acceptance |
| **B8 — Language identification** | **OPEN** | Verified Malayalam/Manglish LID source or script-only acceptance |

B1 does not block local experimentation under the project direction, but it blocks submission, publication and any claim that reuse permission is formally documented.

---

## 7. Actual results and interpretation

### D1 primary

| Model | Features | C | Accuracy | Macro-F1 | Spam P | Spam R | Spam F1 |
|---|---|---|---|---|---|---|---|
| Linear SVM | char 2–4 | 0.5 | 0.9866 | **0.9650** | 1.000 | 0.882 | 0.938 |
| Logistic Regression | char 2–4 | 1.0 | 0.9833 | 0.9556 | 1.000 | 0.853 | 0.921 |

Confusion matrix (SVM): Ham 265/265 correct, 0 false positives; Spam 30/34 correct, 4 false negatives. The four errors are two long Onam messages and two short one-liners. The majority-class floor is 88.6% accuracy but only ~0.47 macro-F1, so accuracy alone would be misleading.

Block-held-out check (same pipeline): macro-F1 **0.6964** (block 4001–5000), **0.4972** (block 5001–6000; no Spam in test), **0.3685** (block 6001–7000; train has only 12 Spam). The random split is optimistic because Spam lives predominantly in one block.

### D2 secondary

| Model | Features | C | Accuracy | Macro-F1 | Ham F1 | Spam F1 | Smishing F1 |
|---|---|---|---|---|---|---|---|
| Logistic Regression | char 2–4 | 1.0 | 0.9638 | **0.8877** | 0.990 | 0.803 | 0.871 |
| Linear SVM | char 2–4 | 0.5 | 0.9638 | 0.8825 | 0.990 | 0.776 | 0.881 |

Main confusions: smishing→spam 15, spam→ham 10, ham→smishing 4. D2 is English-only; its scores are not comparable with D1 and are not pooled.

---

## 8. Phase 2.1 — baseline validation and robustness (5 November 2026)

Full report: `Research Work/phase2/reports/BASELINE_VALIDATION_AND_ROBUSTNESS_REPORT.md`.

- **Artifacts verified.** All four models (D1/D2 × LR/SVM) load and reproduce their saved test predictions exactly. No missing experiment had to be run.
- **D1 source blocks.** Malayalam records occupy rows 4146–6371 in three blocks: 4001–5000 (630 rows, 12 Spam), 5001–6000 (991 rows, 0 Spam), 6001–7000 (371 rows, 213 Spam). 94.7% of Spam is in the last block.
- **Labels track source order.** Only 13 label runs where ~400 are expected (z = −43.2); a 1,662-row Ham run (4488–6158) is followed by a 213-row Spam run (6159–6371). A block-majority rule with no text reaches 91.5% accuracy / 0.832 macro-F1. A no-text structural model reaches 0.871 macro-F1, against 0.965 for the text model.
- **The random split is within-batch.** 95.5% of training Spam and 91.2% of test Spam come from block 6001–7000. Leave-one-block-out pooled macro-F1 falls to **0.538** (SVM) / **0.545** (LR), with Spam recall **7.6%** / **8.9%**. Per-fold: 0.696 (12 Spam test), 0.495 (0 Spam test; macro-F1 not a balanced estimate), 0.368 (only 12 Spam in train).
- **D2 unchanged and stable.** LR 0.8877 macro-F1; Spam remains weakest (F1 0.803) because it is the smallest class and its surface form is nearly identical to Smishing (centroid cosine 0.751). No classes were merged.
- **Manifest correction.** The D2 exclusion fields had been counted after filtering (0 instead of 37 groups / 76 records); fixed, with all split hashes byte-identical.

**Reliability verdict:** D1 is adequate for a within-source case study and for comparing transformers under a fixed protocol, but not for a generalisation claim. The 0.965 random-split score must always be paired with the pooled block-held-out 0.538.

---

## 9. Next step (executed as Phase 2.2 — see §10)

Run **MuRIL base** on D1 only as a within-source benchmark on the frozen split, and report the leave-one-source-block-out folds alongside it. Compare macro-F1 and Spam recall with the saved char-TF-IDF SVM using paired bootstrap intervals. Do not tune on the held-out block, do not create a new split, and do not claim real-world Malayalam SMS performance without an external, source-diverse test set. Resolve B1 (D1 access provenance) before any publication claim.

---

## 10. Phase 2.2 — confidence intervals and MuRIL benchmark (5 November 2026)

Full reports: `reports/CONFIDENCE_INTERVAL_REPORT.md`, `reports/MURIL_BENCHMARK_REPORT.md`, `reports/MODEL_COMPARISON.md`; machine tables in `reports/muril_tables.md`.

### 10.1 Part A — confidence intervals

- Nonparametric percentile bootstrap over duplicate groups, **2,000 replicates**, seed **42**, frozen test predictions only; no retraining and no split changes.
- **D1 SVM:** accuracy 0.9866 [0.9732, 0.9967], macro-F1 **0.9650 [0.9250, 0.9922]**, Spam precision 1.000 [1.000, 1.000], Spam recall 0.8824 [0.7600, 0.9730], Ham F1 0.9925, Spam F1 0.9375.
- **D1 LR:** accuracy 0.9833 [0.9666, 0.9967], macro-F1 0.9556 [0.9121, 0.9903], Spam recall 0.8529 [0.7222, 0.9655].
- **D2 LR:** macro-F1 0.8877 [0.8482, 0.9239], Spam P/R 0.7857/0.8209; **D2 SVM:** macro-F1 0.8825 [0.8408, 0.9196], Spam P/R 0.7761/0.7761.
- The D1 Spam precision interval is degenerate at 1.000 because there are zero false positives; the exact 95% upper bound on the false-positive rate is 1.382% (0/265 Ham), not 3/299. The intervals describe uncertainty **within** the existing test distribution. With only three source blocks, they do not estimate generalisation to new sources, and the block folds are reported individually rather than given a narrow CI.

### 10.2 Parts B and C — MuRIL

- **Data integrity:** all six frozen split hashes verified before training; test IDs unchanged; tokenizer preserves Malayalam exactly. Token lengths: median 31, p95 63, p99 90.09, max 127; `max_len=128` covers 100%.
- **Protocol:** `google/muril-base-cased`, lr 2e-5, batch 4 × 2-step accumulation (effective 8), max 6 epochs, patience 2 on validation macro-F1, fp16, class-weighted loss, seeds 42/43/44. Peak memory 4,779 MB on the 6 GB RTX 4050; 114–167 s per random-split run.
- **Random split:** 0.9866/0.9650, 0.9833/0.9556, 0.9866/0.9650 (accuracy/macro-F1) for seeds 42/43/44; mean **0.9619 ± 0.0054** macro-F1, **0.8725 ± 0.0170** Spam recall, zero false positives. Two seeds reproduce the SVM’s exact four errors.
- **Block-held-out:** pooled macro-F1 **0.4979 / 0.5006 / 0.5098** (mean 0.5028), Spam recall **3.11% / 3.11% / 4.44%** (mean 3.56%). Fold 4001–5000 improves to 0.815–0.848 macro-F1 (58–83% Spam recall); fold 6001–7000 collapses to **all 213 Spam predicted Ham** in every seed, because only 12 Spam remain for training. No held-out block was used for tuning.
- **Error analysis:** random-split errors are the same four batch-boundary messages the SVM misses (two Onam greetings, a road-safety message, a prayer), each at P(Spam) ≈ 0.055. In fold 4001, the same Onam campaign appears with both Ham and Spam labels, which is direct label inconsistency. In fold 6001, the model assigns P(Spam) ≈ 0.108 to the whole Spam batch.
- **Artifact verification:** saved model `models/muril_d1_seed42/` reloads and reproduces 299/299 test predictions with maximum probability difference 0.0.

### 10.3 Part D — comparison and verdict

| Model | Random-split Macro-F1 | Spam Recall | Block-held-out Macro-F1 |
|---|---|---|---|
| Logistic Regression | 0.9556 | 0.8529 | 0.5448 |
| Linear SVM | **0.9650** | **0.8824** | **0.5378** |
| MuRIL (3-seed mean) | 0.9619 ± 0.0054 | 0.8725 ± 0.0170 | 0.5028 ± 0.0062 |

**MuRIL does not genuinely improve the primary Malayalam experiment.** It ties the classical models within seed noise on the within-source split (and is 0.0031 below the SVM), then loses 0.0350 macro-F1 and more than half its Spam recall under source holdout. The only fold where it clearly wins is 4001–5000; the decisive 6001–7000 fold reverses the pooled result. No generalisation claim is made.

### 10.4 Part E — external validation

No external dataset was downloaded or collected. `MODEL_COMPARISON.md` §5 specifies what a valid one would require: independent collection and documented provenance/consent, double annotation with adjudication and a written codebook, human Malayalam verification including romanised Malayalam, overlap screening against D1/D2 at message and campaign level, and pre-registered source-stratified evaluation with clustered intervals. Until then, the defensible claim is about method behaviour on this corpus, not field performance.

### 10.5 Artifacts and preservation

- New: `p2_muril.py`, `p2_muril_report.py`, `p2_ci.py`, `models/muril_d1_seed42/` (913 MB), `metrics/muril_results.json`, 12 per-run prediction CSVs, `metrics/muril_artifact_verification.json`, `metrics/muril_error_examples.json`, `metrics/confidence_intervals.json/.csv`, three reports, `logs/muril_run2.log`.
- No previous model artifact was overwritten. The four `.joblib` classical models, the frozen splits and both original datasets are unchanged; split hashes are byte-identical.
- No git commit was made. This workspace has no `.git` directory, so the new artifacts exist only as files.

---

## 11. Phase 2.3 — statistical validation, threshold calibration and final selection (5 November 2026)

Full reports: `reports/CONFIDENCE_INTERVAL_REPORT.md` (complete), `reports/PAIRED_MODEL_COMPARISON.md`, `reports/THRESHOLD_CALIBRATION_REPORT.md`, `reports/FINAL_MODEL_SELECTION.md`, `reports/FINAL_EXPERIMENTAL_METHODOLOGY.md`.

### 11.1 Complete confidence intervals

- 2,000-replicate group bootstrap, seed 42, frozen predictions. Added MuRIL per-seed intervals and per-class precision/recall; D2 now includes Smishing precision and recall intervals.
- D1 SVM Macro-F1 0.9650 [0.9250, 0.9922], Spam recall 0.8824 [0.7600, 0.9730]; LR 0.9556 [0.9121, 0.9903], 0.8529 [0.7222, 0.9655].
- MuRIL per seed: 0.9650 [0.9250, 0.9922] (42), 0.9556 [0.9099, 0.9903] (43), 0.9650 [0.9250, 0.9922] (44). Across-seed mean 0.9619, SD 0.0054; this is reported separately from within-seed intervals, not combined with them.
- D2 LR Macro-F1 0.8877 [0.8482, 0.9239], Spam P/R 0.7857/0.8209, Smishing P/R 0.9250/0.8222; SVM 0.8825 [0.8408, 0.9196], Spam P/R 0.7761/0.7761, Smishing P/R 0.9487/0.8222.
- Block folds remain three descriptive cases; no population-level CI is presented.

### 11.2 Paired comparisons

- Paired group bootstrap, 2,000 replicates, same resample for both models. D1 seed-42 MuRIL and SVM predictions are **identical**: ΔMacro-F1 = 0.0000 [0.0000, 0.0000], ΔSpam recall = 0.0000 [0.0000, 0.0000].
- LR is 0.0094 Macro-F1 below SVM [−0.0321, 0.0000] and 0.0294 recall below [−0.0976, 0.0000] — one Spam message, below the pre-specified practical threshold (0.01 / 0.05).
- MuRIL seed 43 differs by one Spam message (SVM better by 0.0094 / 0.0294); seed 44 is again identical to SVM. Seed sensitivity does not create a transformer advantage.
- D2 LR vs SVM: ΔMacro-F1 0.0052 [−0.0121, 0.0244], ΔSpam recall 0.0448 [0.0000, 0.1000]. LR is the better point estimate, but this is not a decisive separation.
- Block pooled: LR vs SVM 0.0070 [−0.0043, 0.0217]; LR vs MuRIL42 0.0469 [0.0115, 0.0839]; SVM vs MuRIL42 0.0399 [0.0053, 0.0774]. The MuRIL deficit is a three-block robustness finding, not a population claim.

### 11.3 Threshold diagnosis

- Random split: validation-selected thresholds raise SVM from 0.9650/0.8824 to 0.9659/0.9118 (P 0.9688) and LR from 0.9556/0.8529 to 0.9650/0.8824 (P 1.0), changing one to two messages. These are sensitivity results, not the headline.
- Block 6001: classical ranking is strong (PR-AUC ≈ 0.980), but the default boundary is misplaced. A training-derived threshold raises SVM recall from 6.6% to 60.1% at precision 1.0 in the primary split. Across 20 inner splits, however, SVM recall is 44.3% ± 16.8 and the threshold ranges from −0.675 to −0.315; LR calibration fails. The cause is partly threshold, but it is **not reliably fixable with 12 training Spam**.
- MuRIL block 6001 is a representation failure, not a threshold problem: Spam and Ham probabilities differ by < 0.004 and are effectively constant (0.108/0.298/0.292 by seed). Any threshold labels all rows one class; no operating point exists.
- No held-out label was used to select a threshold.

### 11.4 Final model selection

| Model | Dataset | Random Macro-F1 | Spam Recall | Block-held-out Macro-F1 |
|---|---|---|---|---|
| Logistic Regression | D1 | 0.9556 | 0.8529 | 0.5448 |
| Linear SVM | D1 | **0.9650** | **0.8824** | 0.5378 |
| MuRIL (3-seed mean) | D1 | 0.9619 ± 0.0054 | 0.8725 ± 0.0170 | 0.5028 ± 0.0062 |
| Logistic Regression | D2 | **0.8877** | **0.8209** | N/A |
| Linear SVM | D2 | 0.8825 | 0.7761 | N/A |

- **Primary Malayalam model: Linear SVM** (char_wb 2–4, C=0.5, default boundary 0). Best random-split Macro-F1 and Spam recall, identical to MuRIL-42/44, tiny advantage over LR, and no GPU dependency. Report 0.9650 within-source **with** the 0.5378 block robustness result.
- **Secondary English model: Logistic Regression** (char_wb 2–4, C=1.0). Best Macro-F1 and Spam F1; the paired difference is suggestive, not decisive.
- **MuRIL** is retained as a documented comparator/negative result, not selected for deployment.
- Primary results are the random grouped splits; block-held-out is explicitly a robustness test; threshold-calibrated numbers are sensitivity analyses.

### 11.5 Literature status

No new literature search was run. The gap discussion was updated with the actual findings: the strongest supported gap is the absence of a source-diverse Malayalam evaluation corpus, and the project now provides a negative/limiting transformer result rather than a claimed improvement. Unresolved references are listed in `Literature Review/RESEARCH_GAP_AND_NOVELTY_ANALYSIS.md` §9; P10 remains excluded, and T01/P08/P09 still have incomplete bibliographic records.

### 11.6 Artifacts and decision

- New scripts: `p2_stats.py`, `p2_threshold.py`. New metrics: `confidence_intervals.json/.csv` (complete), `paired_model_comparison.json/.csv`, `block_paired_comparison.csv`, `muril_seed_variation.json/.csv`, `threshold_calibration.json/.csv`, `threshold_calibration_splits.csv`, `final_model_comparison.csv/.json`.
- New figures: `reports/figures/pr_random_d1.png`, `pr_block6001.png`, `scores_block6001.png`.
- No previous model artifact or frozen split was overwritten; the Phase 2.2 CI report is preserved as `CONFIDENCE_INTERVAL_REPORT.phase22.md`.
- **STATISTICAL VALIDATION COMPLETE — READY FOR PROTOTYPE DEVELOPMENT.** Remaining issues are data/provenance limitations (no external source-diverse test set; D1 access undocumented; block 6001 has 12 training Spam), not unresolved statistical analysis.

---

*All model numbers in this report are generated from saved predictions and metrics under `Research Work/phase2/metrics/`. They are not hand-entered.*
