# Research Loophole Register

> **AUDIT WORKING DOCUMENT.** This register records earlier loophole findings. It is not a current results authority. Authoritative sources: `CANONICAL_FINAL_RESULTS.md`, `FINAL_STATISTICAL_AUDIT.md` and `VERIFICATION_REPORT.md`.


**Purpose:** reviewer-facing list of weaknesses, severity, evidence, resolution and residual risk. Severity reflects threat to the paper’s claims, not implementation effort.

| # | Severity | Loophole | Evidence | Resolution / residual risk |
|---:|---|---|---|---|
| L1 | **Critical** | D1 access provenance is undocumented | `Admin/FINAL_AUDIT.md` B1; IEEE DataPort page requires subscription; no receipt/permission in project | Cannot be solved statistically. Obtain subscription receipt, author permission or institutional confirmation. Until then, do not publish D1-derived examples or claim authorised access; D2-only fallback. |
| L2 | **Critical** | No external, source-diverse Malayalam test set | Only three workbook blocks; all evaluation is within the same workbook | Cannot be solved with current data. Frame results as within-corpus plus row-block stress test. Do not claim field/generalisation performance. New independently collected data would require approval. |
| L3 | **Critical** | Row-order/source-block confound | 213/225 Spam (94.7%) in block 6001–7000; χ²=969.15, df=2, p≈3.56×10⁻²¹¹, Cramér’s V=0.6975 | Random-split score is within-batch. Always pair 0.9650 with pooled block 0.5378. Blocks are **row-order proxies**, not documented sources; cause (campaign, collection order, language organisation) is unidentified. |
| L4 | **Critical** | “Malayalam” is script detection, not language identification | `MAL = [\u0D00-\u0D7F]`; 503/1,992 are Malayalam+Latin; 1,489 are Malayalam-only script; no LID model | Rename to “Malayalam-containing subset” and “Malayalam Unicode script filter.” No Manglish claim; mixed-script messages are not automatically Manglish. |
| L5 | **Major** | Perfect D1 Spam precision is over-interpreted | 30/30 (SVM) or 29/29 (LR) predicted Spam; zero FP among 265 Ham; exact lower bounds 88.4%/88.0%; FPR upper 1.38% | Corrected in canonical results. Never write “100% precision proves no false positives.” Report exact and Wilson intervals, positive count and zero-FP upper bound. |
| L6 | **Major** | D1 test positives are campaign-concentrated | 29/30 SVM predicted Spam in block 6001; LR 29/29 there; only one block-4001 predicted Spam | Precision/recall are within the dominant campaign. Report block composition of test and predictions; no source-generalisation claim. |
| L7 | **Major** | Structure/script shortcuts can inflate performance | Structure-only diagnostic Macro-F1 0.8706 (no text, no block ID); block-only 0.8423; structure+block 0.9009 | These are diagnostics, not competing models. Char n-grams can exploit Latin letters, URLs, digits and length. Do not claim semantic Malayalam learning; an ablation would require retraining/approval. |
| L8 | **Major** | MuRIL comparison has only three seeds and one split | Seed Macro-F1 0.9650/0.9556/0.9650; seed SD 0.0054; per-seed intervals overlap | Report seed-level results and cross-seed SD; do not treat seeds as independent test sets. Three seeds cannot estimate a training-run population. |
| L9 | **Major** | MuRIL three-seed “CI” is conditional | Per-seed bootstrap intervals exist; no population interval for new seeds | Report conditional mean interval [0.9211, 0.9909] and label it as test-sample uncertainty for the three fixed seeds. Do not claim a 95% interval for future fine-tuning. |
| L10 | **Major** | Block stress test is underpowered and asymmetric | Block 5001 has 0 Spam; block 6001 training has 12 Spam; three blocks only | Do not compute a conventional CI over blocks. Mark 5001 Macro-F1 as an absent-class artefact; report fold-level support. Treat 6001 as a stress case, not a population estimate. |
| L11 | **Major** | D2 has no source metadata and 76 ambiguous records excluded | 37 conflict groups/76 records; 5,971 → 5,895; test 883 | Always state both denominators. No block-held-out claim. D2 is secondary and English/Latin-only; LR vs SVM difference is not decisive. |
| L12 | **Major** | D2 is not independent of UCI/D1 | `DATASET_AUDIT_REPORT.md`: shared 773 normalised keys; 1,555 D1 / 831 D2 records have a twin; D2 ham/spam derives from UCI | Keep D1/D2 separate; no pooled training. Report overlap as a limitation; no “independent external validation.” |
| L13 | **Major** | Label boundary noise | D2 37 spam↔smishing conflict groups; D1 full corpus 28 conflict groups (0 in Malayalam subset) | Conflicts excluded, not relabelled. Report source label ambiguity; do not claim a clean three-class ground truth. |
| L14 | **Major** | Hyperparameter/test reuse and exploratory analyses | Validation-only selection is documented, but threshold, block, CI and paired analyses reuse the same frozen test | Test was evaluated once for the selected models, but the paper reports multiple post-hoc analyses. Label them exploratory/sensitivity; no new “significant” claims. No evidence of test-set hyperparameter tuning in `p2_modeling.py`. |
| L15 | **Major** | No calibrated probabilities / deployment threshold | Linear SVM decision scores; D1 no calibration; threshold sensitivity unstable under block 6001 | Do not show percentages as probabilities. Default boundary is a research operating point, not a deployment threshold. Report threshold sensitivity only. |
| L16 | **Minor** | Macro-F1 can be distorted by absent classes | `zero_division=0`; block 5001 has no Spam | Mark absent-class folds invalid for Macro-F1; use Ham false positives there. Random-test bootstrap had 0 missing-Spam replicates. |
| L17 | **Minor** | CI method is percentile, not BCa; no source clustering | `p2_stats.py`; 2,000 replicates, seed 42; groups singleton | Percentile intervals are transparent and reproducible. They do not capture source uncertainty. BCa would not fix the three-block design. |
| L18 | **Minor** | Practical-significance threshold is not independently documented | `PAIRED_MODEL_COMPARISON.md` says “fixed before looking”; no timestamped protocol | Describe as an interpretive convention, not a pre-registered analysis, unless a dated protocol is produced. |
| L19 | **Minor** | Literature status was inconsistent | `LITERATURE_REVIEW_VERIFICATION.md` says only B01 full text, but MuRIL and Almeida 2013 details are used; FSSHAP paywalled | Use the corrected status table: B01/MuRIL full text; Almeida 2011 PDF/2013 expanded; FSSHAP abstract only; no numeric FSSHAP claim. |
| L20 | **Minor** | Documentation drift | Stale 631/370, 0.3677, “Transformers — NOT STARTED,” 1,486 typo, missing `VERIFICATION_REPORT.md`, “no source-block structure” | Canonical results and corrected reports now supersede old values. Preserve old files with correction notices. |
| L21 | **Minor** | Prototype does not prove generalisation | 299/299 and 883/883 parity is artifact parity only | Say “reproducible demonstration,” not validation. Model selection/limitations are documented; no deployment. |
| L22 | **Minor** | No Git history / provenance for changed files | No `.git` | Keep hashes and manifests; cannot prove the exact nine-file diff. |

## Cannot be resolved with current data

- External-source generalisation.
- D1 access authorisation.
- A population-level interval over collection sources (only three blocks).
- True Malayalam/Manglish language identification (only Unicode script detection).
- A clean spam/smishing ground truth in D2 (76 records excluded).
- Causal attribution of row-order association to campaign vs collection method.

## What duplicate controls do and do not prevent

**Prevent:** exact copies, normalised copies (URLs/numbers/punctuation), conservative fuzzy templates in D1, and group leakage across train/validation/test.

**Do not prevent:** same-campaign messages that fall below the fuzzy threshold, source-block label bias, script/language shortcuts, label noise, or cross-dataset overlap. Duplicate control is necessary but not sufficient.
