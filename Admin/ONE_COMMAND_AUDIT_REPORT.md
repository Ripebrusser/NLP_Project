# One-Command Audit Report

**Script:** `Research Work/run_full_audit.py`
**Evidence:** `Research Work/phase2/metrics/full_audit_results.json` (latest run) and `Research Work/phase2/metrics/audit_runs/<run_id>/`
**Date:** 8 November 2026

## 1. How to run

```bash
.venv/Scripts/python.exe "Research Work/run_full_audit.py"
```

`PYTHONIOENCODING=utf-8` is not required for this entry point (it sets the variable for every child process itself), but it is safe to add on Windows.

Useful flags:

| Flag | Effect |
|---|---|
| `--write-baseline` | Records the SHA-256 of every frozen artifact and exits. Used once, before a change window. |
| `--skip-tests` | Skips the regression suite for fast diagnosis. Never used for a release result. |

Exit status is `0` only when every required check passes.

## 2. What it runs

| # | Check | What it proves |
|---:|---|---|
| 1 | `environment` | Python 3.14 and the pinned numpy/pandas/scikit-learn/scipy/joblib/openpyxl versions are importable |
| 2 | `required_files` | Every deliverable, script, manifest and canonical metric file exists and is non-empty |
| 3 | `dataset_integrity` | Both source hashes match the manifest; 7,718 physical rows, 7,717 labelled records, 6,322 Ham, 1,395 Spam-including-typo; D2 = 5,971 rows |
| 4 | `split_hashes` | All six frozen splits match `split_manifest.json` |
| 5 | `model_hashes` | All four classical `.joblib` artifacts match `model_manifest.json` |
| 6 | `baseline_hashes` | All 39 frozen artifacts (2 datasets, 6 splits, 4 models, 4 MuRIL files, 17 prediction files, 2 manifests, 3 verification outputs) are byte-identical to the pre-audit baseline |
| 7 | `regression_tests` | The full `unittest` suite |
| 8 | `frozen_predictions` | `p2_final_verification.py` recomputes every headline metric from frozen predictions |
| 9 | `statistical_audit` | `p2_final_audit_stats.py` recomputes intervals, paired comparisons and block results |
| 10 | `prototype_verification` | `verify_prototype.py` re-hashes models/splits and reproduces every frozen test prediction through the saved pipeline and the public API |
| 11 | `literature_validation` | Workbook, CSV, register and builder agree on 24 records / 23 active |
| 12 | `browser_ui_evidence` | The recorded Chromium pass exists and every case in `browser_ui_test_results.json` is `PASS` (informational; it does not launch a browser) |
| 13 | `code_risk_checks` | 10 static invariants: frozen manifest block table untouched, corrected block formula in use, legacy CI writer cannot overwrite authoritative evidence, hash check precedes `joblib.load`, no fitting in read-only scripts, README do-not-rerun list present, `norm_key` limitation documented |
| 14 | `verification_stability` | The numbers inside the two statistical JSONs are identical before and after the run |
| 15 | `post_run_hash_stability` | Nothing frozen changed during the run |

Checks 7–11 run as real subprocesses with captured exit codes, so a failure in the script is a failure here; they are not re-implemented assertions. Child processes receive `PYTHONIOENCODING=utf-8` and `PYTHONUTF8=1`.

## 3. Latest result

```
PASS environment                       2.3s    all pinned versions present
PASS required_files                    0.0s    26 required files present
PASS dataset_integrity                 1.0s    source hashes and row counts match
PASS split_hashes                      0.0s    6 split hashes match
PASS model_hashes                      0.0s    4 model hashes match
PASS baseline_hashes                   1.0s    39 frozen artifacts byte-identical
PASS regression_tests                 13.8s    exit 0 (125 tests)
PASS frozen_predictions                4.6s    exit 0
PASS statistical_audit                 6.3s    exit 0
PASS prototype_verification            3.6s    exit 0
PASS literature_validation             1.1s    exit 0
PASS browser_ui_evidence               0.0s    16 browser cases recorded, all PASS
PASS code_risk_checks                  0.0s    10 invariants checked
PASS verification_stability            0.0s    frozen metrics identical
PASS post_run_hash_stability           0.0s    all artifacts identical to baseline
```

Fifteen checks (14 required, plus the informational browser-evidence check), all passing, 33.5 s, exit status 0. `Admin/FINAL_RELEASE_CHECKLIST.md` maps each check to the release gate it satisfies.

## 4. Failure behaviour

- Each check is wrapped independently: an exception is recorded as `FAIL` with a traceback tail, and the remaining checks still run.
- Subprocess timeouts (900 s) are recorded as `timed_out: true`, not as a pass.
- A failed check does not stop later checks, so one run shows every problem.
- The run always writes its JSON (even when failing), so a failure is inspectable.
- Only required checks decide the exit status.

## 5. What the run writes — and what it refuses to touch

Writes:
- `phase2/metrics/full_audit_results.json`
- `phase2/metrics/audit_runs/<run_id>/full_audit_results.json`
- `phase2/metrics/audit_runs/<run_id>/*.before.json` — byte copies of the three verification outputs taken before the child scripts run

The three verification scripts (`final_verification.json`, `final_audit_stats.json`, `verification_results.json`) are rewritten by their own scripts during the run and then **restored byte-for-byte** from the copies. The post-run hash check proves the restore worked.

Never written: datasets, splits, models, prediction CSVs, manifests, threshold outputs, reports.

## 6. Coverage limits

- The Streamlit page is not driven by this script (no browser is launched). Widget-level behaviour is covered by `test_streamlit_app.py` inside the regression suite; a separate browser pass is recorded in `phase2/metrics/browser_ui_test_results.json`.
- MuRIL is never loaded or retrained; only its saved artifact hashes are checked.
- The audit proves internal consistency and artifact stability. It cannot prove dataset permission, source independence, or field performance.
