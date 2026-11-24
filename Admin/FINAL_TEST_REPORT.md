# Final Test Report

**Date:** 8 November 2026
**Framework:** Python `unittest` (`pytest` is not installed in the project environment and was not added, to avoid changing the environment for a test run)
**Location:** `Research Work/tests/`

## 1. Result

| Metric | Value |
|---|---:|
| Tests run | 125 |
| Passed | 125 |
| Failed | 0 |
| Errors | 0 |
| Skipped | 0 |
| Expected failures | 0 |
| Warnings | 0 |
| Duration | 13.3 s (the 11 widget tests start the Streamlit runtime) |
| Exit status | 0 |

Machine-readable results: `Research Work/phase2/metrics/code_audit_test_results.json` (with the full log in `code_audit_test_results.log`).

## 2. Exact commands

```bash
# full suite, writes the JSON result file
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe "Research Work/tests/run_tests.py"

# equivalent, without the JSON writer
.venv/Scripts/python.exe -m unittest discover -s "Research Work/tests" -t "Research Work/tests" -v
```

## 3. Environment

| Item | Value |
|---|---|
| OS | Windows 11 (10.0.26300) |
| Python | 3.14.3 (MSC v.1944, 64-bit) |
| numpy | 2.5.4 |
| pandas | 3.1.1 |
| scikit-learn | 1.9.1 |
| scipy | 1.18.1 |
| joblib | 1.6.0 |
| openpyxl | 3.1.5 |
| streamlit | 1.67.0 |
| torch | 2.11.0+cu128 |
| transformers | 5.22.1 |

## 4. Coverage by module

| Module | Tests | What it proves |
|---|---:|---|
| `test_statistics.py` | 20 | CP/Wilson reference values; exact and empty denominators; macro-F1 equals scikit-learn; Spam precision/recall denominators; no-predicted-positive behaviour; single-class artefact; bootstrap reproducibility and seed sensitivity; group as resampling unit; sign symmetry of paired differences; shared-label requirement; **frozen LR−SVM = −0.0093601 [−0.0321432, 0]** and exact reverse negation |
| `test_alignment.py` | 12 | Missing, extra, duplicate, null and mixed-dataset IDs all fail; label and group disagreement fail; unexpected class fails; correct shuffles align by ID; all frozen prediction files align cleanly |
| `test_blocks.py` | 8 | Block boundaries at 4001/5000/5001/6000/6001/7000; stale formula differs at every boundary row; corrected totals 630/991/371 and 618H/12S, 991H/0S, 158H/213S; test-split 86H/3S, 159H/0S, 20H/31S; manifest pinned as stale, not edited |
| `test_unicode.py` | 15 | Malayalam and combining marks preserved; ZWSP/ZWNJ/ZWJ/BOM/NBSP/controls handled; NFKC; U+FFFD retained; no transliteration; idempotence; cleaning parity on 7,887 rows; `text` column equals cleaned message in all splits; script detection; input guards |
| `test_duplicates.py` | 9 | `norm_key` URL/number/case/punctuation behaviour; union-find transitivity; deterministic groups; conflict flagging; grouped split keeps groups intact and leaks nothing; D1 pipeline reproduces 1,824 groups and every frozen `group_id`; D2 5,663 groups / 37 conflicts / 76 records |
| `test_splits.py` | 9 | 1,394/299/299 and 4,127/885/883; six hashes and two source hashes; disjoint IDs; class totals; zero group/norm overlap; singleton test groups |
| `test_models.py` | 7 | All four model hashes; pipeline steps; `char_wb` 2–4, `sublinear_tf`, `min_df`; C = 0.5/1.0; classes; summary; 299/883 batch parity; order independence |
| `test_inference.py` | 8 | Every frozen row reproduced through the public API (299 + 883); classify agrees with batch pipeline; payload shape; D2 scores ordered and sum to 1; Unicode accepted; guards reject empty, wrong script and 50,000 chars; 5,000-character input handled |
| `test_literature.py` | 7 | 24 unique register records; workbook/CSV/register agreement; 23 active, 7/6/10/1; P10 excluded and marked; no uncaveated decimals; missing reference, reclassification, numeric leak and CSV drift each detected |
| `test_streamlit_app.py` | 11 | Real app run through `streamlit.testing.v1.AppTest`: D1 and D2 page load; Malayalam and Latin predictions; Latin-only rejected in D1; Malayalam-only rejected in D2; mixed-script warning with prediction; empty input warning; widget caps input at 5,000; control characters do not crash; dashboard tabs/metrics/tables; missing artifact shows an inline error instead of a blank page |

## 5. Failures found while building the suite

The first execution ran 95 tests with 13 failures and 4 errors. Each was traced rather than adjusted away:

- **Real code defect (F-04):** empty metrics returned `nan`; now raises. The test was rewritten to expect the error.
- **Real documentation defect (F-07):** the register summary counted 9 METADATA records while listing 10; corrected.
- **Test-author errors, corrected against evidence:** expected macro-F1 for a no-positive-prediction fixture (1/3, not 0.5); sklearn's alphabetical D2 class order; `dict.update()` used with a list; `norm_key`'s placeholder becoming `token "url"`; `load_d1()` returning all 7,717 workbook rows rather than the 1,992 Malayalam subset; block boundaries shifting at every 1,000-row boundary; source row 4001 not being a Malayalam record.

No test was deleted, skipped or weakened to obtain a pass.

## 6. Independent verification runs

| Command | Exit | Result |
|---|---|---|
| `python "Research Work/prototype/verify_prototype.py"` | 0 | `PASS`; 4/4 model hashes, 6/6 split hashes, 299/299 and 883/883 batch and API parity, all guards true |
| `python "Research Work/validate_literature_matrix.py"` | 0 | `PASS`; 24 records, 23 active, counts 7/6/10/1 |
| `python phase2/p2_final_verification.py` | 0 | Regenerated; **22/22** metric values identical to the preserved pre-audit file |
| `python phase2/p2_final_audit_stats.py` | 0 | Regenerated; paired direction and block composition unchanged |

Pre-audit copies retained as `verification_results.before_code_audit.json`, `final_verification.before_code_audit.json` and `final_audit_stats.before_code_audit.json`.

## 7. What the suite does not prove

- It does not establish generalisation to new SMS sources: the data cannot support that.
- It does not re-verify MuRIL training hyperparameters; those remain partially unrecoverable.
- It does not judge visual quality, responsive layout or accessibility. The widget tree and every user-visible state are tested in `test_streamlit_app.py`, and a separate live Chromium pass is recorded in `phase2/metrics/browser_ui_test_results.json`, but CSS and viewport behaviour are unverified.
- It does not prove a clean-environment install end to end; the pinned versions are verified at run time and a fresh MuRIL/CUDA environment was not rebuilt.
- It does not test the fuzzy-duplicate threshold's sensitivity to corpus change, because that would require altering grouping.
