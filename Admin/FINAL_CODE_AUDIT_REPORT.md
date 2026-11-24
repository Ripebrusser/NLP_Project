# Final Code Audit Report

**Audit date:** 8 November 2026
**Target:** the existing research codebase (40 Python files, 2 datasets, 6 frozen splits, 4 classical pipelines, 1 MuRIL reference model, frozen predictions, Streamlit prototype, literature workbook)
**Mode:** adversarial engineering audit — inspect, fix only genuine software defects, test, prove, preserve research artifacts.

## 1. Scope and method

Nothing was retrained, resampled, relabelled or regenerated. The audit read:

- every Phase 2 script from extraction through reporting, with line-level review of the statistical writers (`p2_final_verification.py`, `p2_final_audit_stats.py`, `p2_stats.py`, `p2_ci.py`);
- the data-preparation path (`p2_common.py`, `p2_extract.py`, `p2_duplicates.py`, `p2_split.py`);
- the modelling path (`p2_modeling.py`, `p2_train_d1.py`, `p2_train_d2.py`);
- the MuRIL path (`p2_muril.py`, `p2_muril_report.py`, `p2_threshold.py`) for configuration evidence only;
- the prototype (`app.py`, `inference.py`, `research_data.py`, `verify_prototype.py`, manifests, requirements);
- the literature automation (`build_final_lit_matrix.py`, legacy `build_lit_matrix.py`) and the verification register;
- all split/model manifests and the recorded hashes.

Method: independent recomputation from frozen predictions, differential testing against scikit-learn, boundary and corruption fixtures, and a second reviewer pass that tried to make each verifier pass while its inputs were wrong. Every fix was followed by a regression test and a re-run of the affected checks.

## 2. Evidence base

| Check | Result |
|---|---|
| Frozen split hashes vs `split_manifest.json` | 6/6 match |
| Frozen model hashes vs `model_manifest.json` | 4/4 match |
| Source hashes (D1 xlsx, D2 csv) | Match manifest |
| Prediction alignment (`record_id`) D1 | 299/299 for LR, SVM, seeds 42/43/44 |
| Prediction alignment D2 | 883/883 for LR and SVM |
| Prototype batch parity | 299/299 and 883/883 |
| Prototype public-API parity | 299/299 and 883/883 |
| `p2_final_verification.py` | exit 0; 22/22 metric values identical to the preserved pre-audit output |
| `p2_final_audit_stats.py` | exit 0 |
| Automated tests | 114 passed, 0 failed, 0 errors, 0 skipped |
| Literature matrix | PASS: 24 records, 23 active, register/workbook/CSV agree |

## 3. Defects found

### F-01 — Three-class D2 matrix fed to a binary exact-interval function (High)

`p2_final_verification.py` and `p2_final_audit_stats.py` computed false positives as "every non-diagonal entry in the Spam column" and true negatives as `n − tp − fp − fn`. That is arithmetically defined for a 3×3 matrix but statistically meaningless: Smishing→Spam errors were counted as false positives and the "FPR" denominator had no interpretation. The result was reported under keys that look like a valid binary FPR.

**Impact:** a misleading number in an audit artifact; no headline metric used it.
**Fix:** `exact_checks` now rejects any label list whose length is not 2; `multiclass_exact_checks` reports per-class precision/recall Clopper–Pearson and Wilson intervals and explicitly states that no multiclass FPR is defined.
**Regression:** `test_multiclass_input_is_rejected`, `test_multiclass_per_class_checks`.

### F-02 — Row-block off-by-one (High, reporting)

`p2_split.py` and `p2_robustness.py` used `((source_row - 1) - 1) // 1000 + 1`, which maps the first row of every block into the previous block. The formula is now centralised as `p2_common.block_number(source_row)` and both writers use it.

**Impact:** the descriptive `d1.blocks` table inside the frozen manifest is 631/991/370 instead of 630/991/371, and the historical `d1_block_robustness.json` was produced with the shifted membership. The corrected block CV (used for the headline 0.5378/0.5448/0.5028 and the 8.89/7.56/3.56% Spam recall) comes from `p2_validate.py`, which already defined blocks correctly and is unaffected.
**Fix:** code fixed; **manifest and historical robustness JSON deliberately not rewritten** (frozen artifacts). The mismatch is documented and pinned by a test.
**Regression:** `test_first_and_last_row_of_each_block`, `test_stale_formula_differs_at_the_boundary`, `test_only_the_block_boundary_rows_shift`, `test_manifest_block_table_is_stale_and_still_unmodified`.

### F-03 — Unvalidated prediction merges (High)

`p2_stats.py` merged predictions to the split with a plain inner join, and `p2_ci.py` used prediction files without the split at all. A missing row would silently shrink the test set, a duplicated `record_id` would silently duplicate it, and a label or group disagreement would pass unnoticed. Any of these changes a metric with no error.

**Fix:** `p2_common.align_predictions()` enforces unique IDs, exact set equality, split-order alignment, label equality, allowed classes, and group-ID equality when present. Both scripts now use it.
**Regression:** 11 alignment tests, including a D1/D2 mix-up fixture and all frozen files.

### F-04 — Empty input produced NaN metrics (Medium)

`metric_codes` / `metrics_from_codes` divided 0 by 0 when given no rows, yielding `nan` rather than an error. `p2_stats` masked it by using `max(n, 1)` and returned 0.0.

**Fix:** all three implementations raise `ValueError` on an empty input.
**Regression:** `test_empty_input_fails_instead_of_returning_nan`, `test_empty_frame_does_not_return_a_metric`.

### F-05 — Prototype accepted any text for either model (Medium)

`inference.py` only rejected empty strings. A caller could run the English model on Malayalam text or the D1 model on Latin-only text and receive a confident-looking label; the Streamlit UI guarded this, the library did not. There was also no length cap, so a multi-megabyte string reached the vectorizer.

**Fix:** `validate_input(value, task)` rejects `None`, empty/whitespace, bytes, control-only text, more than 5,000 characters, non-Malayalam input for D1 and non-Latin input for D2, with explicit messages. 5,000 is far above the longest frozen message (910 characters) and does not alter behaviour on real inputs.
**Regression:** input-validation and guard tests in `test_unicode.py` and `test_inference.py`.

### F-06 — Prototype verifier was weaker than its report (Medium)

It hashed only the two prototype models (not all four), and it predicted on the `text` column of the prediction CSV and compared with that same file's prediction column — a self-consistent loop that would not catch a swapped or truncated split. Prediction alignment was positional.

**Fix:** the verifier now hashes all four models and all six splits, aligns by `record_id` through `align_predictions`, predicts from the frozen split text, and additionally drives the public `classify_*` functions over every test row (299 + 883). It exits non-zero on any failure and reports `FAIL` explicitly.
**Regression:** the verifier itself, plus `test_models.py` and `test_inference.py`.

### F-07 — Literature register arithmetic inconsistency (Low, documentation)

The register's summary said "Metadata only … (9)" while listing ten records (P03, P11, P14, P15, T01, S01, E02–E05). The workbook and the register table both contain ten.

**Fix:** summary corrected to "(10)"; the new validator compares workbook counts to register-derived counts, then to the audited snapshot 7/6/10/1 = 24.
**Regression:** `test_workbook_matches_register`, `test_register_parses_24_unique_records`.

### F-08 — `norm_key` URL placeholder is stripped to the token `url` (Low, documented only)

`norm_key` substitutes `" <url> "` and then removes all non-alphanumerics, so the marker becomes the ordinary word `url`. Grouping is still deterministic and URL variants still collapse, but the key is less self-describing than the code implies.

**Not fixed:** changing the placeholder would change normalised keys, group IDs and therefore the frozen splits. Documented and pinned by `test_url_placeholder_is_inserted`.

### F-09 — Stale historical robustness output (Low, preserved)

`metrics/d1_block_robustness.json` was produced by the old formula and is labelled historical in the Phase 2 README. It is not regenerated because doing so would overwrite original evidence and retrain diagnostic models.

### F-10 — Duplicate CI writers (Low)

`p2_ci.py` and `p2_stats.py` write the same `confidence_intervals.json`. The documented run order is ambiguous; running both leaves the simpler output. The reproducibility guide now states that `p2_stats.py` is authoritative and `p2_ci.py` is legacy.

## 4. What was verified rather than changed

- **Paired direction.** LR − SVM Macro-F1 = `−0.009360118526741346`, 95% CI `[−0.03214315072560611, 0]`; the reverse comparison is the exact negation `[0, 0.032143150725606105]`. The two predictions disagree on exactly one test row (`a_wrong_b_right = 1`), so the exact discordance p-value is 1.0 and the interval includes zero: this is not evidence that SVM beats LR.
- **Shared resampling.** Both models see the same group draws; reversing the arguments negates the point estimate and mirrors the interval to 1e-12.
- **Intervals.** Clopper–Pearson and Wilson match published reference values (e.g. CP 5/10 = [0.18709, 0.81291]; Wilson 0/10 upper = 0.27753).
- **Class presence.** A missing class in a replicate contributes F1 = 0 and a macro-F1 of 0.5 for a perfect single-class resample; this is recorded, and the frozen tests never lose a class (299/299 and 883/883 singleton groups).
- **Grouping provenance.** Re-running the D1 duplicate pipeline (exact + normalised + fuzzy) on the 1,992 Malayalam rows reproduces the frozen 1,824 groups and the exact `group_id` of every row. D2 reproduces 5,663 groups after excluding 37 conflicting groups / 76 records.
- **Preprocessing.** `clean_text` in `p2_common` and `inference` agree on all 7,887 frozen rows, and every split's `text` column equals `clean_text(message)`.
- **Leakage.** Group and normalised-key overlap are zero for every split pair in both datasets; TF-IDF is a pipeline step fitted on training data only, then refit on train+validation after selection; no test text, label-derived feature or row ID enters training.
- **Model loading.** All four joblib pipelines load in a clean process, expose `tfidf` + `clf`, use `char_wb` 2–4 with `sublinear_tf`, and predict the frozen test files exactly.
- **Literature automation.** 24 records, 23 citable, 1 excluded; workbook equals the builder's declared rows and the CSV equals the workbook; no non-full-text record carries an uncaveated decimal result.

## 5. Residual weaknesses (not software defects)

1. **D1 provenance permission** is still unresolved. This is a research/governance blocker, not a code blocker.
2. **Source-block confound.** Three populated blocks, one with no Spam. No code change can turn this into external validation.
3. **MuRIL training settings** are only partially recoverable from saved artifacts; the exact optimizer state and epoch-level configuration cannot be re-derived without the original run logs.
4. **Fuzzy duplicate boundary.** The 0.90 cosine / 0.60 Jaccard rule is a documented heuristic; a different threshold would move a small number of groups.
5. **Single corpus per task.** All intervals are within-corpus message-level uncertainty.
6. **`pytest` is not installed**, so the suite uses `unittest`. This is a tooling limitation, not a skip: every test executes.

## 6. Verdict

**CONDITIONAL PASS.**

The implementation now fails loudly on misaligned, duplicated, missing, empty or mixed predictions; the paired comparison direction and interval arithmetic are verified numerically; the block-formula defect is fixed in code and pinned by tests; the prototype reproduces every frozen prediction through its public API; and the literature workbook is machine-checked against its register. No dataset, label, split, model, prediction or headline metric was modified (22/22 metrics identical after regeneration).

The condition is the research layer, not the code: D1 provenance permission, the row-block confound, the stale descriptive manifest table kept for artifact integrity, and the absence of any external validation set. Those must be stated as limitations in any publication; they cannot be fixed by engineering.
