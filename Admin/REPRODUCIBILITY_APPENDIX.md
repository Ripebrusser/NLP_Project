# Reproducibility Appendix (manuscript version)

**This is the condensed, paper-ready appendix.** The authoritative, complete appendix is `Admin/IEEE_REPRODUCIBILITY_APPENDIX.md`; where the two differ, the full appendix governs. Artifact locations and hashes are listed in `Admin/IEEE_REPRODUCIBILITY_ARTIFACT_INDEX.md`, and the claim-by-claim evidence check is in `Admin/REPRODUCIBILITY_APPENDIX_VALIDATION.md`.

## A. Environment

Windows 11 (10.0.26300), Python 3.14.3, 16 logical CPUs. Classical models: scikit-learn 1.9.1, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, joblib 1.6.0. Transformer models: torch 2.11.0+cu128 (CUDA 12.8), transformers 5.22.1, accelerate 1.15.0, on an NVIDIA RTX 4050 Laptop GPU (6,141 MiB). Prototype: Streamlit 1.67.0. All runs executed locally; no cloud services were used. Pinned requirements are in `Research Work/requirements-verification.txt` and `Research Work/prototype/requirements.txt`. A clean-virtualenv installation was not performed, and training-time GPU driver and library versions beyond torch/CUDA were not recorded.

## B. Data

**D1** (primary, Malayalam): *Spam Message Collection*, IEEE DataPort, DOI `10.21227/dcym-pd69`, released 2 June 2023. The workbook has 7,718 physical rows; 7,717 candidate records; after removing 1 invalid label and 2 empty messages, 7,714 usable records (7,322 Ham / 1,394 Spam at raw label level). The Malayalam subset used for modelling contains **1,992 messages (1,767 Ham / 225 Spam)**: 1,489 Malayalam-only (1,429 / 60) and 503 Malayalam plus Latin script (338 / 165). Workbook SHA-256 `24ca099ac1ffabc0b02fd491f57d577c56afb932bc81c5964a40e32eab9a023b`.

**D2** (secondary, English/Latin): Mendeley, DOI `10.17632/f45bkkt8pr.1`, 20 June 2022, CC BY 4.0. 5,971 records (4,844 Ham / 489 Spam / 638 Smishing); 37 conflicting-duplicate groups covering 76 records were excluded, leaving **5,895 (4,844 / 450 / 601)**. File SHA-256 `649844f1c62a6b27e145eaf17a65f7010c56c390e11a794ea8329993a05ba71e`.

**Access and redistribution.** D2 may be redistributed under CC BY 4.0 with attribution. D1 is behind subscriber access with no displayed licence, and written permission from the authors has **not** been obtained at the time of writing (status: pending). D1 is therefore neither redistributed nor reproduced here, and no raw message text appears in this appendix. The two corpora share 773 normalised message keys; they are not independent samples.

## C. Preprocessing

NFKC normalisation; removal of zero-width and BOM characters; non-breaking spaces and C0 controls replaced by spaces; whitespace collapsed. URLs, punctuation, digits and Malayalam combining marks are preserved; no transliteration, stemming or stop-word removal. Cleaning is idempotent, and the longest frozen message is 910 characters. Script is decided by Unicode ranges (Malayalam U+0D00–0D7F, Tamil, Telugu, Kannada, and `[A-Za-z]`), and a record is Malayalam if it contains any Malayalam character.

Duplicates were controlled before splitting. D1: character 3–5-gram TF-IDF cosine ≥ 0.90 together with token Jaccard ≥ 0.60, or cosine ≥ 0.97. D2: exact and normalised-key matching only. No D1 group contained conflicting labels; 37 D2 groups (76 records) did and were removed. D1 retains 1,824 groups over 1,992 rows; D2 retains 5,663 groups over 5,895 rows.

## D. Splits

70/15/15, seed 42, group-stratified assignment. D1: 1,394 train (1,237 / 157), 299 validation (265 / 34), 299 test (265 / 34). D2: 4,127 train (3,391 / 315 / 421), 885 validation (727 / 68 / 90), 883 test (726 / 67 / 90). All six splits are frozen by SHA-256 in `split_manifest.json`; a post-hoc audit confirms zero group overlap and zero shared normalised keys between every pair of splits. Hyperparameters were chosen on validation macro-F1, models refit on train+validation, and the test split scored once.

**Known structural limitation.** 213 of the 225 D1 Spam messages (94.7%) fall in one journalist-collected row block. Random splitting therefore places near-duplicate campaign material on both sides of the split, so D1 scores measure within-campaign recognition. Sections G and K report the block-controlled results and this limitation explicitly.

## E. Models

**Classical.** Word-boundary character 2–4-gram TF-IDF, `min_df=2`, sublinear term frequency, 300,000 features. Per task, 4 configurations × 3 regularisation strengths were compared for logistic regression (`class_weight="balanced"`, `max_iter=5000`, liblinear for binary and lbfgs for multiclass) and a linear SVM (`max_iter=10000`, squared hinge). Selected: D1 Linear SVM (C = 0.5, validation macro-F1 0.9830) and D1 Logistic Regression (C = 1.0, 0.9748); D2 Logistic Regression (C = 1.0, 0.9048) and D2 Linear SVM (C = 0.5, 0.9030).

**MuRIL.** `google/muril-base-cased` (12 layers, hidden 768, 12 heads, vocabulary 197,285), max length 128, learning rate 2e-5, AdamW with weight decay 0.01, 10% warm-up, batch 4 with 2-step accumulation, at most 6 epochs, patience 2, class-weighted loss with a weight cap of 10, FP16. Seeds 42, 43 and 44; only run 42 trained to completion under the early-stopping rule (4 epochs, selected epoch 2, 167.09 s, peak 4,779.3 MiB). The base checkpoint revision is not recorded, and MuRIL was not applied to D2.

## F. Metrics and statistics

Primary metric: test Macro-F1, alongside accuracy, macro-precision, macro-recall, per-class precision/recall/F1 and confusion matrices. Intervals use the Clopper–Pearson exact method (Wilson reported alongside). Paired model comparisons use 2,000 group-level bootstrap resamples (seed 42) with shared resamples across models and percentile intervals, plus exact McNemar tests.

D1 (n = 299) test Macro-F1: MuRIL seed 42 0.9650, seed 43 0.9556, seed 44 0.9650 (mean 0.9619, SD 0.0054), Linear SVM 0.9619, Logistic Regression 0.9525. Linear SVM reaches 0.9967 accuracy, 0.9444 precision and 0.9804 recall with a 95% recall interval of [0.9372, 0.9968]; its false-positive rate is at most 1.382% (0.2% observed, Wilson upper bound 1.429%). D2 (n = 883) Macro-F1: Logistic Regression 0.9272, Linear SVM 0.9220.

No D1 paired difference is statistically resolved: Logistic Regression − Linear SVM = −0.00936 [−0.03214, 0], and Linear SVM − MuRIL(seed 42) = +0.00312 [0, 0.01010]. The LR/SVM difference rests on a single discordant message, 36.85% of bootstrap resamples tie, and the exact McNemar p-value is 1.0. MuRIL's advantage over each classical model is a single message and is not established.

## G. Row-block experiment

D1 rows were grouped by source-block position (`block = (row − 1) // 1000 + 1`, inferred from the workbook layout, not verified against collection metadata): rows 1–1000 → 630 messages (618 Ham / 12 Spam), 1001–2000 → 991 (991 / 0), 2001–3000 → 371 (158 / 213). Under three-fold leave-one-block-out evaluation, pooled accuracy is 0.5448 (LR), 0.5378 (SVM) and 0.5028 (MuRIL mean), with Spam recall of 8.89%, 7.56% and 3.56%. The pooled LR − SVM difference is +0.00695 [−0.00425, 0.02170]. The block containing no Spam makes its fold Macro-F1 structurally meaningless, and is reported rather than suppressed. These results do not establish that the row blocks correspond to distinct collection campaigns.

## H. Verification

Every reported value can be regenerated with one command:

```
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe "Research Work/run_full_audit.py"
```

The audit runs 15 checks (14 required, 1 informational): environment, required files, dataset integrity, split hashes, model hashes, baseline hashes for 39 frozen artifacts, the 125-test suite, frozen-prediction metric recomputation, statistical audit, prototype verification, literature validation, browser evidence, static code-risk invariants, pre/post metric stability, and post-run hash stability. The last executed run (`20261108T171120Z`) returned **15/15 PASS, 125/125 tests, 39/39 artifacts byte-identical, exit code 0, 34.9 s**. Verification never rewrites predictions or metrics, and the three derived verification outputs are restored byte-for-byte.

## I. Prototype

A local Streamlit application serves the D1 Linear SVM and D2 Logistic Regression with hash-checked loading. It reproduces frozen test predictions with 299/299 and 883/883 agreement in both batch and single-message paths, and rejects empty, non-string, control-character-only, over-length (>5,000 characters) and wrong-script input. Sixteen browser cases passed with zero console errors and no non-loopback requests after telemetry was disabled, driven by a synthetic DOM-event sequence rather than native key events. The prototype binds to loopback only and was never deployed publicly.

## J. Artifact integrity

Thirty-nine artifacts are frozen under SHA-256: 2 source datasets, 7 split files, 4 classical model files, 4 MuRIL files, 17 prediction files, 2 manifests and 3 verification outputs. Their digests are listed in the artifact index; all 39 were byte-identical before and after the final audit. Any modification to a frozen artifact fails the baseline check.

## K. Limitations

1. D1 written permission is pending; D1 data are not redistributed.
2. D1 scores measure within-campaign recognition: 94.7% of Spam sits in one row block.
3. The block experiment, not the random split, is the honest estimate of performance on unseen campaigns, and it is close to chance.
4. MuRIL is a single completed fine-tuning run under an unrecorded base-checkpoint revision.
5. The 0.90/0.60 duplicate threshold is a judgement call; tightening it would reduce the D1 sample further.
6. The `norm_key` placeholder substitutes `url` and `num` tokens, which is documented but not corrected.
7. `d1_block_robustness.json` and the manifest's descriptive block table predate the corrected block formula and are historical only.
8. The UI audit covers functional behaviour, not layout, accessibility or concurrency.
9. No clean-environment installation was verified.
10. The corpora are not independent and the shared 773 keys mean cross-corpus comparisons are not independent evidence.
11. Manglish and Romanised Malayalam are represented only as 503 mixed-script messages.
12. Probabilities are uncalibrated and should not be read as risk estimates.

## L. Reproducibility level

- **Level 1 — available:** artifact-level verification. Hashes, splits, predictions, metrics, intervals, statistics and prototype parity are all checkable with one command, offline, on the frozen artifacts.
- **Level 2 — partial:** classical retraining from the documented configuration. Implemented and documented but not re-executed here; it would overwrite frozen artifacts and must be run in a copy.
- **Level 3 — unavailable:** independent external validation. No external corpus, no second-hardware rerun and no third-party assessment exist, and none is claimed. MuRIL fine-tuning cannot be reproduced bitwise.

## M. Reproduction checklist

1. Install the pinned requirements into a fresh environment.
2. Obtain D1 from IEEE DataPort under its access terms and D2 from Mendeley under CC BY 4.0.
3. Confirm both source hashes against Section B.
4. Without retraining, run the verification command in Section H and confirm 15/15 PASS and exit code 0.
5. Optionally, in a copy of the project, rerun the fixed-seed split and training steps and compare against the frozen hashes in the artifact index.
