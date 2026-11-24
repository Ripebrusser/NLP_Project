# Final Code Fix Register

Every entry is a defect found by inspecting the implementation, not a restatement of a previous report. "Frozen" means a dataset, split, model, prediction or headline metric.

| ID | Severity | File(s) | Problem | Fix | Regression test | Status |
|---|---|---|---|---|---|---|
| F-01 | High | `phase2/p2_final_verification.py`, `phase2/p2_final_audit_stats.py` | Binary `exact_checks` accepted the 3-class D2 confusion matrix and emitted a meaningless single FPR (Smishing→Spam counted as false positives) | `exact_checks` raises `ValueError` unless exactly 2 labels; added `multiclass_exact_checks` with per-class CP/Wilson precision and recall; D2 metadata uses it | `test_multiclass_input_is_rejected`, `test_multiclass_per_class_checks` | Fixed |
| F-02 | High | `phase2/p2_common.py`, `phase2/p2_split.py`, `phase2/p2_robustness.py`, `phase2/p2_final_verification.py`, `phase2/p2_final_audit_stats.py` | Double subtraction `((source_row-1)-1)//1000+1` shifted every block boundary by one row; manifest block table is 631/991/370 instead of 630/991/371 | Added authoritative `block_number()`; all writers use it. Frozen manifest and historical robustness JSON left untouched | `test_first_and_last_row_of_each_block`, `test_only_the_block_boundary_rows_shift`, `test_corrected_block_totals`, `test_manifest_block_table_is_stale_and_still_unmodified` | Fixed in code; frozen artifacts preserved and documented |
| F-03 | High | `phase2/p2_common.py`, `phase2/p2_stats.py`, `phase2/p2_ci.py` | Prediction files were merged to splits with a plain inner join (or not aligned at all): missing/extra/duplicate IDs, label disagreements and group disagreements could silently change a metric | Added `align_predictions()` enforcing unique IDs, set equality, split order, label equality, allowed classes and group-ID equality; both scripts use it | 11 tests in `test_alignment.py`, including D1/D2 mix-up | Fixed |
| F-04 | Medium | `phase2/p2_stats.py`, `phase2/p2_final_verification.py`, `phase2/p2_final_audit_stats.py` | Empty prediction input produced `nan` (0/0) or a silent 0.0 instead of an error | All three metric functions raise `ValueError` on zero rows | `test_empty_input_fails_instead_of_returning_nan`, `test_empty_frame_does_not_return_a_metric` | Fixed |
| F-05 | Medium | `prototype/inference.py` | No length cap and no script enforcement in the library API: either model could be applied to the wrong language, and arbitrarily long input reached the vectorizer | `validate_input()` rejects `None`, blank, bytes, control-only, >5,000 chars, non-Malayalam for D1 and non-Latin for D2, with explicit messages. Frozen maximum is 910 chars | `TestInputValidation`, `TestGuardsThroughPublicApi` | Fixed |
| F-06 | Medium | `prototype/verify_prototype.py` | Verified only 2 of 4 model hashes; parity compared a prediction file against itself on its own text; alignment was positional | Hashes all 4 models and 6 splits; aligns by `record_id`; predicts from frozen split text; drives `classify_*` over all 299 + 883 rows; returns non-zero and `FAIL` on any error | `test_models.py`, `test_inference.py`, verifier itself | Fixed |
| F-07 | Low | `Admin/LITERATURE_VERIFICATION_REGISTER.md`, `Research Work/validate_literature_matrix.py` | Register summary said 9 METADATA records while listing 10; no machine check tied workbook to register | Summary corrected to 10; validator compares workbook ↔ register counts and the audited snapshot 7/6/10/1, cross-checks CSV and builder rows, and rejects uncaveated numeric claims on non-full-text records | `test_workbook_matches_register`, `test_register_parses_24_unique_records` | Fixed |
| F-08 | Low | `Research Work/audit_datasets.py` (`norm_key`) | The `<url>` placeholder is stripped to the ordinary token `url` by the following non-alphanumeric filter | Not fixed: any change moves normalised keys, group IDs and frozen splits. Behaviour documented and pinned | `test_url_placeholder_is_inserted` | Documented, intentionally unresolved |
| F-09 | Low | `phase2/metrics/d1_block_robustness.json` | Historical block diagnostic was produced with the old block formula | Preserved as historical evidence and labelled stale; the corrected block CV in `validation_summary.json` is authoritative. Rerunning would retrain and overwrite evidence | `test_manifest_block_table_is_stale_and_still_unmodified` pins the corrected composition | Documented, intentionally unresolved |
| F-10 | Low | `phase2/p2_ci.py`, `phase2/p2_stats.py`, `phase2/README.md` | Both scripts write `metrics/confidence_intervals.json`; the documented order is ambiguous and the legacy script overwrites the richer output | Kept both (historical evidence); README and reproducibility guide now name `p2_stats.py` as authoritative and mark `p2_ci.py` legacy | `test_statistics.py` exercises the authoritative implementation | Documented |

## Summary

| Severity | Found | Fixed | Unresolved (documented) |
|---|---:|---:|---:|
| High | 3 | 3 | 0 |
| Medium | 3 | 3 | 0 |
| Low | 4 | 1 | 3 |
| **Total** | **10** | **7** | **3** |

No frozen artifact was modified. The three unresolved items are deliberate: two would change frozen research data (group IDs, manifest, historical output) and one is a legacy script retained as evidence.
