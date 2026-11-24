# Reproducibility Appendix — Validation Record

**Document validated:** `Admin/IEEE_REPRODUCIBILITY_APPENDIX.md`
**Companion documents:** `Admin/IEEE_REPRODUCIBILITY_ARTIFACT_INDEX.md`, `Admin/REPRODUCIBILITY_APPENDIX.md`
**Validation date:** 8 November 2026
**Audit receipt:** `Research Work/phase2/metrics/full_audit_results.json`, run `20261108T171120Z`
**Final status: PASS — every quantitative claim traced to an artifact; limitations disclosed; no unsupported claim retained.**

---

## 1. Method

Each statement in the appendix was classified and checked against machine-readable evidence rather than against earlier narrative reports:

1. **Counts and splits** were read from `phase2/splits/split_manifest.json` and `phase2/metrics/subset_audit.json`, not from prose.
2. **Metrics, intervals and paired differences** were read from `phase2/metrics/final_verification.json` and `phase2/metrics/final_audit_stats.json`, and cross-checked against the canonical table in `Admin/CANONICAL_FINAL_RESULTS.md`.
3. **Model configurations** were read from `phase2/p2_modeling.py`, `phase2/metrics/d1_malayalam_results.json`, `d2_results.json` and `phase2/metrics/muril_results.json`.
4. **Hashes** were read from `phase2/metrics/audit_hash_baseline.json`, `split_manifest.json`, `model_manifest.json` and the saved MuRIL artifact directory.
5. **Environment values** were obtained by executing the interpreter and `nvidia-smi` in the project environment.
6. **The verification command was executed** during validation; its exit status, run identifier and per-check durations were taken from the JSON it wrote.
7. Arithmetic consistency of every derived total was checked independently (Section 3).

No file was modified to make a statement true. The only artifact changed by validation is `full_audit_results.json`, which the audit always rewrites and which is not a frozen artifact.

---

## 2. Claim-by-claim verification

### 2.1 Environment (Appendix A)

| Claim | Evidence | Status |
|---|---|---|
| Windows 11, build 10.0.26300 | `full_audit_results.json` → `platform`; `platform.platform()` executed during validation | Verified |
| Python 3.14.3, MSC v.1944 64-bit | `full_audit_results.json` → `python` | Verified |
| Intel64 Family 6 Model 191 Stepping 2, 16 logical processors | `os.cpu_count()` and `PROCESSOR_IDENTIFIER` executed during validation | Verified; no vendor model string exists, so none is claimed |
| RTX 4050 Laptop GPU, 6,141 MiB, driver 617.42 | `nvidia-smi` executed during validation | Verified as the **current** driver; the training-time driver is not recorded (disclosed) |
| CUDA 12.8, torch 2.11.0+cu128, transformers 5.22.1, accelerate 1.15.0 | `muril_results.json` → `versions`; `torch.__version__` executed | Verified |
| numpy 2.5.4, pandas 3.1.1, scikit-learn 1.9.1, scipy 1.18.1, joblib 1.6.0, openpyxl 3.1.5, streamlit 1.67.0 | `requirements-verification.txt`, `prototype/requirements.txt`, audit `environment` check | Verified |
| Peak MuRIL memory 4,779.3 MiB; 167.09 s for seed 42 | `muril_results.json` → `random_split.runs[0]` | Verified |
| System RAM unknown | No artifact records it | Correctly marked "not recoverable" |
| Clean-environment installation not performed | No clean-venv evidence exists; `FINAL_CODE_RISK_REGISTER.md` R-13 | Verified as a true limitation |

### 2.2 Dataset provenance (Appendix B)

| Claim | Evidence | Status |
|---|---|---|
| D1 authors, IEEE DataPort, 2 June 2023, DOI `10.21227/dcym-pd69` | `DATASET_PROVENANCE_AND_PERMISSIONS.md` | Verified |
| D1 workbook SHA-256 `24ca099a…a023b` | `audit_hash_baseline.json`; full digest in `FINAL_TECHNICAL_VERIFICATION.md` | Verified |
| D1 access subscription-gated; no licence displayed | Provenance record; audit check `dataset_integrity` only tests hashes | Verified; permission held as PENDING |
| 7,718 physical rows, one blank; 7,717 candidate records; 1 invalid label; 2 empty; 7,714 usable; 6,322 Ham / 1,394 Spam | `subset_audit.json` (`records`, `raw_label_counts`, `invalid_labels`, `empty_messages`); audit check reports the same figures | Verified |
| D1 Malayalam subset 1,992 = 1,767 Ham / 225 Spam | `subset_audit.json` → `d1.malayalam`; `split_manifest.json` → `d1.classes` | Verified |
| Script composition 1,489 Malayalam-only (1,429/60) and 503 mixed (338/165) | `subset_audit.json` → `script_categories`; `FINAL_STATISTICAL_AUDIT.md` §7.1 | Verified; sums to 1,992 / 1,767 / 225 |
| D2 authors, Mendeley, 20 June 2022, DOI `10.17632/f45bkkt8pr.1`, CC BY 4.0 | `DATASET_PROVENANCE_AND_PERMISSIONS.md` | Verified |
| D2 5,971 = 4,844 / 489 / 638; 37 conflicting groups / 76 records excluded; 5,895 = 4,844 / 450 / 601 | `split_manifest.json` → `d2.classes`, `exclusions`; `CANONICAL_FINAL_RESULTS.md` §5 | Verified; 5,971 − 76 = 5,895 |
| 773 shared normalised keys; 1,555 D1 and 831 D2 records with a twin | `DATASET_PROVENANCE_AND_PERMISSIONS.md` §3 | Verified |
| No raw D1 text appears in the appendix or index | Manual inspection of both documents | Verified |

### 2.3 Preprocessing and duplicate control (Appendix C)

| Claim | Evidence | Status |
|---|---|---|
| NFKC; ZWSP/ZWNJ/ZWJ/BOM removed; NBSP to space; C0 controls to space; whitespace collapsed | `p2_common.clean_text` source | Verified |
| URLs, punctuation, digits and Malayalam marks preserved; no transliteration | `clean_text` source; `test_unicode.py` | Verified |
| Cleaning idempotent; maximum frozen message length 910 characters | `FINAL_CODE_FIX_REGISTER.md` F-05; `test_unicode.py` | Verified |
| Script ranges U+0D00–0D7F, U+0B80–0BFF, U+0C00–0C7F, U+0C80–0CFF, `[A-Za-z]` | `p2_common.py` regexes | Verified |
| `norm_key` lower-cases, substitutes URLs and digit runs, strips punctuation; markers become `url` and `num` | `audit_datasets.norm_key`; F-08 | Verified |
| D1 fuzzy rule: `char_wb` 3–5, cosine ≥ 0.90 with Jaccard ≥ 0.60, or cosine ≥ 0.97 | `p2_duplicates.py`; `duplicates.json` note | Verified |
| D2 exact and normalised grouping only | `duplicates.json` note | Verified |
| D1: 0 conflicting groups; D2: 37 groups / 76 records | `split_manifest.json` → `exclusions` | Verified |
| D1 1,824 groups / 1,992 rows; D2 5,663 groups / 5,895 rows | `split_manifest.json`; `test_duplicates.py` | Verified |

### 2.4 Splits and leakage (Appendix D)

| Claim | Evidence | Status |
|---|---|---|
| 70/15/15, seed 42, group-stratified deficit assignment | `split_manifest.json` → `seed`, `ratios`, `algorithm`; `p2_common.split_grouped` | Verified |
| D1 1,394 / 299 / 299 with class counts | `split_manifest.json` → `d1.files` | Verified |
| D2 4,127 / 885 / 883 with class counts | `split_manifest.json` → `d2.files` | Verified |
| Test groups 299 and 883, maximum group size 1 | `split_manifest.json`; `FINAL_TECHNICAL_VERIFICATION.md` §4 | Verified |
| Zero group and normalised-key overlap for all split pairs | `split_manifest.json` → `checks.ok = true`, six zero counts | Verified |
| Six split hashes | `split_manifest.json`, `model_manifest.json`, baseline | Verified, all three sources agree |
| 94.7% of D1 Spam in one block | 213 / 225 = 0.9467 | Verified arithmetically |
| Selection on validation macro-F1; refit on train+validation; single test evaluation | `p2_modeling.fit_and_evaluate` source | Verified |
| Script, length and block association quantified in §7 of the statistical audit | `validation_summary.json` via `FINAL_STATISTICAL_AUDIT.md` | Verified |

### 2.5 Models (Appendix E)

| Claim | Evidence | Status |
|---|---|---|
| TF-IDF `char_wb` 2–4, `min_df=2`, `sublinear_tf`, `max_features=300,000` | `p2_modeling.make_pipeline`; `test_models.py` | Verified |
| Grid of 4 configurations × 3 C values × 2 families per task | `p2_modeling.CONFIGS`, `FAMILIES`, `c_grid`; `*_validation_grid.csv` (24 rows per task) | Verified |
| LR `class_weight="balanced"`, `max_iter=5000`, `liblinear` binary / `lbfgs` multiclass | `p2_modeling.FAMILIES` | Verified |
| Linear SVM `max_iter=10000`, `dual="auto"`, squared hinge | `p2_modeling.FAMILIES` (squared hinge is the scikit-learn default) | Verified |
| Selected configurations and C values | `d1_malayalam_results.json`, `d2_results.json` → `models.*.selected_config`, `C` | Verified: SVM 0.5 / LR 1.0 (D1); LR 1.0 / SVM 0.5 (D2) |
| Validation macro-F1 0.9830, 0.9748, 0.9048, 0.9030 | Same JSON → `val.val_macro_f1` | Verified |
| Feature counts 20,629 and 24,293 | `browser_ui_test_results.json` → model cards | Verified as displayed by the deployed prototype |
| MuRIL architecture 12 layers / 768 / 12 heads / 197,285 vocabulary | `muril_d1_seed42/config.json`; `muril_results.json` | Verified |
| MuRIL hyperparameters (lr 2e-5, AdamW wd 0.01, warm-up 10%, batch 4 × accum 2, 6 epochs, patience 2, weight cap 10, FP16, eval batch 32) | `muril_results.json` → `hyperparameters`; `p2_muril.py` argument defaults and optimiser construction | Verified |
| Class weights 0.5635 / 4.4395 for seed 42 | `muril_results.json` → `random_split.runs[0].class_weights` | Verified |
| Seed 42 ran 4 epochs, selected epoch 2 | `muril_results.json` → `epochs_run`, `selected_epoch` | Verified |
| MuRIL not evaluated on D2 | No D2 MuRIL artifacts exist; `d2_results.json` has only two families | Verified |
| Checkpoint revision, training-time driver, tokenizers version, cuDNN flags, optimiser state unrecoverable | No artifact records them | Verified as absent; disclosed, not guessed |

### 2.6 Metrics and statistics (Appendix F)

| Claim | Evidence | Status |
|---|---|---|
| All D1 and D2 values in the two result tables | `final_verification.json`; `CANONICAL_FINAL_RESULTS.md` §2 and §5 | Verified value-for-value |
| Confusion matrices | Same two sources | Verified; row sums equal class supports (299 and 883) |
| CP/Wilson precision and recall intervals | `final_verification.json` → exact checks; `FINAL_TECHNICAL_VERIFICATION.md` §5 | Verified |
| FPR upper bound 1.382% (exact) and 1.429% (Wilson) | `final_audit_stats.json`; `FINAL_STATISTICAL_AUDIT.md` §4.2 | Verified |
| Bootstrap 2,000 replicates, seed 42, group unit, shared resamples, 2.5/97.5 percentiles | `p2_stats.py`; `FINAL_STATISTICAL_AUDIT.md` §5.1 | Verified |
| Every test group singleton, so bootstrap is numerically message-level | `split_manifest.json`; §5.1 | Verified |
| LR−SVM −0.0093601 [−0.0321432, 0]; SVM−LR exact negation; 36.85% tied resamples; p = 1.0 | `paired_model_comparison.json`; `final_audit_stats.json`; `test_statistics.py` | Verified |
| SVM−MuRIL +0.0031200 [0, 0.0101002]; accuracy +0.0011148; recall +0.0098039 | `final_verification.json`; §3.2 | Verified |
| D2 LR−SVM +0.0052393 [−0.0120572, 0.0244165] | `final_audit_stats.json`; §8 | Verified |
| Seed values 0.9650 / 0.9556 / 0.9650; mean 0.9619; SD 0.0054 | `muril_seed_variation.json`; `CANONICAL_FINAL_RESULTS.md` §2 | Verified |
| Conditional mean interval [0.9211, 0.9909] etc. | `final_verification.json` | Verified |
| Seeds 42 and 44 identical to SVM; seed 43 one Spam false negative | `FINAL_STATISTICAL_AUDIT.md` §3.3; prediction files | Verified |

### 2.7 Row blocks (Appendix G)

| Claim | Evidence | Status |
|---|---|---|
| 630 (618/12), 991 (991/0), 371 (158/213) | `FINAL_STATISTICAL_AUDIT.md` §6.1; `d1.blocks` recomputation; `test_blocks.py` | Verified; sums to 1,992 / 1,767 / 225 |
| `block_number = (source_row − 1) // 1000 + 1` | `p2_common.block_number` | Verified |
| Pooled accuracy / Macro-F1 / precision / recall for five model rows and the MuRIL mean | `final_audit_stats.json`; `CANONICAL_FINAL_RESULTS.md` §4 | Verified |
| Per-block Macro-F1 values and fold supports | `CANONICAL_FINAL_RESULTS.md` §4 | Verified |
| LR−SVM pooled difference +0.00695 [−0.00425, 0.02170] | `FINAL_STATISTICAL_AUDIT.md` §6.3 | Verified |
| 5001–6000 fold has no Spam; its Macro-F1 is an artefact | Block counts and §6.3 | Verified |
| Structure-only 0.8706, block-only 0.8423, structure+block 0.9009 | §7.2, arithmetic checked against saved confusion matrices | Verified |
| Row blocks are not verified collection sources | No source metadata exists | Verified as a limitation |

### 2.8 Verification procedure (Appendix H)

| Claim | Evidence | Status |
|---|---|---|
| Single command, audit exits 0, 15/15 checks | Executed during validation; `full_audit_results.json` run `20261108T171120Z` | Verified: exit 0, 15 passed, 0 failed |
| Per-check durations in the table | Same JSON → `checks[].duration_seconds` | Verified; 34.9 s total |
| 125/125 tests, 0 failures, 0 errors, 0 skipped | `code_audit_test_results.json`; audit `regression_tests` | Verified |
| 39/39 artifacts byte-identical before and after | `baseline_hashes` (0.87 s) and `post_run_hash_stability` | Verified |
| Three verification outputs restored byte-for-byte | Audit restore logic; post-run hash equality | Verified |
| Audit checks environment, files, datasets, splits, model hashes, prediction alignment, statistics, parity, literature, static risks, hash stability | `run_full_audit.py`; `ONE_COMMAND_AUDIT_REPORT.md` §2 | Verified |
| `--write-baseline` and `--skip-tests` behaviour | Script argument parser and help text | Verified |
| Audit cannot establish permission, source independence or field performance | Design: no network, no permission check, no external data | Verified |

**Note on durations.** The first validated run recorded 32.6 s and an earlier draft quoted those per-check times. Validation re-executed the command, so the appendix now reports the run actually inspected (34.9 s). Durations vary with machine load and are explicitly not a performance claim.

### 2.9 Prototype (Appendix I)

| Claim | Evidence | Status |
|---|---|---|
| Streamlit 1.67.0; D1 Linear SVM; D2 Logistic Regression | `inference.MODEL_FILES`; `prototype/requirements.txt`; browser model cards | Verified |
| SHA-256 verified before `joblib.load` | `inference.verify_artifact_hash`; `FINAL_CODE_RISK_REGISTER.md` R-10 | Verified |
| 299/299 and 883/883 batch and API parity; cleaning parity equal | `verification_results.json`; audit `prototype_verification` | Verified |
| Guards: None, empty, bytes, control-only, >5,000 chars, wrong script | `inference.validate_input`; `test_inference.py`, `test_unicode.py` | Verified |
| 5,000-character cap vs 910-character frozen maximum | F-05 | Verified |
| 11 `AppTest` widget tests | `test_streamlit_app.py`; `FINAL_TEST_REPORT.md` §4 | Verified |
| 16 browser cases, all PASS; zero console errors; zero non-loopback requests after telemetry disabled | `browser_ui_test_results.json` | Verified |
| Dashboard 5 tabs / 6 metrics / 10 tables / 11 charts | `browser_ui_test_results.json` | Verified |
| Loopback only, never deployed | Browser record → `deployment: none`; server command bound to 127.0.0.1 | Verified |
| DOM-event driver caveat | Recorded verbatim in the browser JSON `driver.note` | Verified and disclosed |

### 2.10 Integrity (Appendix J, artifact index)

| Claim | Evidence | Status |
|---|---|---|
| Baseline of 39 artifacts created 2026-11-08T16:16:45Z | `audit_hash_baseline.json` | Verified |
| Category composition 2 + 7 + 4 + 4 + 17 + 2 + 3 = 39 | Baseline key prefixes | Verified |
| Every listed digest | Baseline, `split_manifest.json`, `model_manifest.json` | Verified; all copied verbatim, none invented |
| 39/39 unchanged after the final run | Audit post-run check | Verified |
| No raw D1 artifact marked publicly shareable | Artifact index sharing column | Verified |

### 2.11 Limitations and levels (Appendix K, L)

| Claim | Evidence | Status |
|---|---|---|
| Twelve limitations listed, including permission, external validity, blocks, MuRIL settings, fuzzy threshold, URL placeholder, historical artifacts, UI audit, clean install, corpus overlap, Manglish, calibration | Corresponding evidence in Sections 2.1–2.10 and `FINAL_CODE_RISK_REGISTER.md` | Verified |
| Level 1 supported; Level 2 partial; Level 3 unavailable | Verification executed; classical retraining not re-executed; no external corpus exists | Verified |
| Internal verification never described as external validation | Full-text check of both documents | Verified |

---

## 3. Independent arithmetic checks

| Check | Result |
|---|---|
| 1,489 + 503 = 1,992 | Pass |
| 1,429 + 338 = 1,767; 60 + 165 = 225 | Pass |
| 1,394 + 299 + 299 = 1,992 | Pass |
| 1,237 + 265 + 265 = 1,767; 157 + 34 + 34 = 225 | Pass |
| 630 + 991 + 371 = 1,992; 618 + 991 + 158 = 1,767; 12 + 0 + 213 = 225 | Pass |
| 4,127 + 885 + 883 = 5,895 | Pass |
| 3,391 + 727 + 726 = 4,844; 315 + 68 + 67 = 450; 421 + 90 + 90 = 601 | Pass |
| 5,971 − 76 = 5,895; 489 − 39 = 450 (76 records: 39 Spam, 37 Smishing) | Pass (implied by class totals) |
| 213 / 225 = 94.67% ≈ 94.7% | Pass |
| Confusion-matrix row sums: 265 + 0 + 5 + 29 = 299; 722+0+4+10+55+2+1+15+74 = 883 | Pass |
| 36.85% + 63.15% = 100% of resamples | Pass |
| 2 + 7 + 4 + 4 + 17 + 2 + 3 = 39 artifacts | Pass |

---

## 4. Commands executed during validation

| Command | Exit | Result |
|---|---:|---|
| `.venv/Scripts/python.exe -c "import sys, platform; …"` | 0 | Python 3.14.3, Windows-11-10.0.26300 |
| `nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv` | 0 | RTX 4050 Laptop GPU, 6,141 MiB, 617.42 |
| `torch.__version__`, `torch.cuda.is_available()` | 0 | 2.11.0+cu128, True, CUDA 12.8 |
| `PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe "Research Work/run_full_audit.py"` | **0** | 15/15 PASS, 125 tests, 34.9 s, run `20261108T171120Z` |

The audit's own child processes (test suite, metric recomputation, statistical audit, prototype verifier, literature validator) all returned exit code 0 inside that run, which is recorded per check in `full_audit_results.json`.

---

## 5. Issues found while validating, and their resolution

| Item | Resolution |
|---|---|
| First draft quoted per-check durations from an earlier run (32.6 s total) | Re-executed the command; table and total replaced with the inspected run (34.9 s). No claim depends on timing |
| Run identifier in the draft pointed to run `20261108T163352Z` | Updated to `20261108T171120Z` in the appendix body and the reproduction checklist |
| "7,717 records" is ambiguous between workbook rows and labelled records | Appendix states 7,718 physical rows, 7,717 candidate records, 7,714 usable after 1 invalid label and 2 empty messages, matching `subset_audit.json` |
| MuRIL "hyperparameters" could be overstated as a full training record | Appendix explicitly lists unrecoverable items (checkpoint revision, driver at training time, tokenizers version, cuDNN flags, optimiser state) and withholds a bitwise-reproduction claim |
| Artifact sharing could imply derived files are safe to publish | Index states that split and prediction files embed message text and therefore inherit D1/D2 restrictions |

No unsupported claim required deletion beyond these corrections; no figure was changed to differ from its artifact.

---

## 6. Data that is missing and explicitly marked as such

| Missing item | Where it would have come from | Handling in the appendix |
|---|---|---|
| D1 accession receipt, licence or author written permission | No artifact exists | Status **PENDING**, Section B.1 and K.1 |
| System RAM | Not recorded | "Not recoverable from available project records" |
| MuRIL base checkpoint revision | Not recorded | Section E, K.4 |
| Training-time GPU driver and CUDA library versions beyond torch/CUDA | Not recorded | Section E, K.4 |
| `tokenizers` version | Not recorded | Section E, K.4 |
| cuDNN determinism settings, optimiser state | Not recorded | Section E, K.4 |
| Clean-virtualenv install log | Not performed | Section A, K.9 |
| Two-session concurrency, mobile viewport, accessibility audit | Not performed | Section I, K.8 |
| External Malayalam corpus | Does not exist in the project | Section L (Level 3 unavailable) |

No missing value was filled by inference, and no "Not recoverable" marker was replaced with a plausible guess.

---

## 7. Consistency with canonical sources

| Source | Consistency |
|---|---|
| `CANONICAL_FINAL_RESULTS.md` | All 5 D1 model rows, both D2 rows, all block rows, seed statistics and denominators match exactly |
| `FINAL_STATISTICAL_AUDIT.md` | Paired directions, tied-resample share, FPR bounds, bootstrap description and block membership match |
| `FINAL_TECHNICAL_VERIFICATION.md` | Alignment counts, exact intervals and source hashes match |
| `FINAL_TEST_REPORT.md` | 125 tests, framework, module coverage and stated limits match |
| `FINAL_REPRODUCIBILITY_GUIDE.md` | Install steps, do-not-rerun list and verification commands match; the guide's expected result is 15/15 |
| `FINAL_RELEASE_CHECKLIST.md` | Frozen-artifact and research-limitation statements match |
| `DATASET_PROVENANCE_AND_PERMISSIONS.md` | Authors, DOIs, dates, licence status and permission matrix match |
| `FINAL_CODE_RISK_REGISTER.md` | R-01, R-02, R-04 to R-08, R-13, R-15, R-16 are all reflected in Section K |
| `browser_ui_test_results.json` | 16 cases, PASS, caveat and unverified surfaces match |

No statement in the appendix contradicts these sources. Where older reports conflict (for example the historical manifest block table or the superseded `d1_block_robustness.json`), the appendix follows the canonical correction and labels the older artifact historical.

---

## 8. Residual validation limits

1. The appendix was validated against the project's own artifacts. Independent replication on second hardware was not performed and is not claimed.
2. The MuRIL fine-tuning run cannot be re-verified beyond its saved artifacts, by construction.
3. Dataset permission is a documentary question that no amount of code inspection can settle; it remains open.
4. The prototype was validated functionally, not visually; CSS, responsiveness and accessibility remain unverified.
5. The audit proves internal consistency and artifact stability; it cannot validate the scientific claim of generalisation, which the appendix declines to make.

---

## 9. Final validation status

| Criterion | Result |
|---|---|
| Every dataset figure traced to an artifact | Pass |
| Every split count traced to a manifest | Pass |
| Model configurations traced to code and result JSON | Pass |
| Statistical methods traced to implementation and independent recomputation | Pass |
| All reported performance values traced to canonical metric files | Pass |
| One-command audit executed and passing (15/15, exit 0) | Pass |
| All stated hashes retrieved, none invented | Pass |
| No permission status overstated (D1 PENDING throughout) | Pass |
| No statement conflicts with canonical results | Pass |
| Every limitation disclosed, including unresolved ones | Pass |
| Reproducibility levels stated without implying external validation | Pass |
| No frozen artifact modified while producing the appendix | Pass (39/39 byte-identical) |

**Verdict: the reproducibility appendix is accurate, internally consistent, and consistent with the frozen artifact set. It is ready for inclusion as an appendix or supplementary material, subject to the disclosed D1 permission status.**
