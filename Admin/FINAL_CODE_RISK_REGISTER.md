# Final Code Risk Register

Risks are ranked by residual severity after this audit. "Code" risks can be fixed by engineering; "research" risks cannot and must be disclosed as limitations.

| Rank | ID | Risk | Severity | Likelihood | Impact | Mitigation / status |
|---:|---|---|---|---|---|---|
| 1 | R-01 | D1 provenance and author permission remain unresolved | High | Certain | Publication or redistribution could be blocked; the corpus cannot be defended as authorised | Research/governance action, not code. Tracked in `Admin/D1_PERMISSION_REQUEST_AND_CHECKLIST.md`; do not redistribute D1 |
| 2 | R-02 | Source-block confound: 94.7% of D1 Spam sits in one 1,000-row block; block 5001–6000 has no Spam | High | Certain | Random-split 0.9650 overstates field performance; pooled block Macro-F1 is 0.5378 | Reported separately; the block stress test is the honest headline. No code change can remove the confound |
| 3 | R-03 | No external, source-diverse Malayalam test set | High | Certain | Generalisation to unseen senders/collectors is unknown | Stated as a limitation; external validation is future work, not a code fix |
| 4 | R-04 | Frozen `split_manifest.json` block table is stale (631/991/370 vs 630/991/371) | Medium | Certain (artifact) | A reader trusting the manifest gets a one-record-wrong descriptive table; headline metrics unaffected | Code fixed (`block_number`); manifest preserved for artifact integrity; mismatch documented and pinned by tests. **Do not hand-edit the manifest** |
| 5 | R-05 | Historical `d1_block_robustness.json` was produced with the old block formula | Medium | Certain (artifact) | Anyone quoting that file gets shifted block membership | Labelled historical in the Phase 2 README; use `validation_summary.json`; not regenerated |
| 6 | R-06 | MuRIL training configuration only partially recoverable | Medium | High | Exact reproducibility of the MuRIL run cannot be claimed | Frozen predictions and metrics are verified; settings are marked unrecoverable rather than guessed |
| 7 | R-07 | Fuzzy duplicate threshold (cosine ≥ 0.90 + Jaccard ≥ 0.60) is a heuristic | Medium | Medium | A different threshold would move a few groups and could shift borderline metrics | Grouping reproduced exactly from code; frozen group IDs are stable; sensitivity not tested because it would require regrouping |
| 8 | R-08 | `norm_key` URL placeholder collapses to the token `url` | Low | Certain | Keys are less self-describing and a literal "url" token could collide with a placeholder | Documented; not changed because it would alter frozen group IDs |
| 9 | R-09 | `p2_ci.py` and `p2_stats.py` write the same confidence-interval file | Low | Medium | Running the legacy script last silently replaces the richer output | **Fixed in code:** `p2_ci.py` now writes `confidence_intervals_legacy.json/.csv` and a legacy report, and only touches the authoritative files with `--overwrite-authoritative`. Enforced by a static audit check |
| 10 | R-10 | Model artifacts are unpickled with `joblib.load` | Low | Low | A tampered artifact executes code | **Fixed in code:** `inference.verify_artifact_hash()` checks the recorded SHA-256 before `joblib.load` and refuses a mismatch. Enforced by tests and a static audit check |
| 11 | R-11 | Prototype can classify Manglish as if it were English | Low | Medium | Confident but unsupported label for Romanised Malayalam | UI caveat; script guard prevents the reverse (Malayalam into D2). No Manglish training data exists |
| 12 | R-12 | Streamlit error text can reveal a local path | Low | Low | Minor information disclosure on a local machine | Accepted for a local demo; no message text or credential is exposed |
| 13 | R-13 | `pytest` and `datasets` are absent from `.venv` | Low | Certain | The suite runs on `unittest`; HF `datasets` cannot be used for a fresh MuRIL environment without installation | **Closed:** `requirements-verification.txt` pins the real stack and the audit checks every version at run time. A clean-env install is documented but not exercised here (torch/CUDA is out of scope) |
| 14 | R-14 | No root README; two operative READMEs | Low | Certain | New readers may miss the run order or the do-not-rerun list | Both READMEs updated; reproducibility guide added |
| 15 | R-15 | Streamlit page itself was not browser-driven | Low | Medium | A rendering regression could go unnoticed | **Closed:** 11 `AppTest` widget tests plus a live Chromium pass over both detectors, warnings, errors and the dashboard. Visual/CSS quality, mobile viewport, concurrency and accessibility tooling remain unverified |
| 16 | R-16 | Streamlit sent default usage statistics to `data.streamlit.io` and a webhook | Low | Certain | A privacy claim of "no network calls" would be false at the library level | **Fixed:** `.streamlit/config.toml` sets `browser.gatherUsageStats = false`; the browser pass then recorded zero non-loopback requests |

## Closure status of the seven remaining engineering issues

| Issue | Classification | Final status |
|---|---|---|
| 1. URL normalisation collapses distinct URLs to `url` | Frozen artifact / research limitation | **Unchanged by design.** Changing `norm_key` would move frozen group IDs and splits. Documented here and asserted by the audit |
| 2. Stale row-block table in the manifest | Historical artifact that must remain untouched | **Preserved.** The audit asserts the manifest still says 631/991/370 *and* that live recomputation gives 630/991/371 |
| 3. Historical robustness JSON with obsolete values | Historical artifact | **Preserved and labelled** in the Phase 2 README; not regenerated |
| 4. Duplicate `p2_ci.py` / `p2_stats.py` output | Safe code correction | **Fixed.** Legacy suffix by default; explicit flag to overwrite; static check added |
| 5. `joblib` loading trust boundary | Safe code correction | **Fixed.** SHA-256 verified before unpickling; negative test added |
| 6. No browser-driven Streamlit test | Safe test addition | **Closed.** `AppTest` suite + live Chromium pass; evidence in `browser_ui_test_results.json` |
| 7. Dependency reproducibility / clean environment | Documentation + audit correction | **Closed.** Pins recorded, versions checked every run, single command documented. A full clean-venv reinstall was not executed (torch stack excluded) |

## Residual-risk statement

The code layer is now defensively validated: misaligned, duplicated, missing, empty or cross-dataset predictions fail loudly; interval arithmetic and paired direction are verified; the prototype reproduces every frozen prediction through its public API; artifacts are hash-checked before they are unpickled; and the literature workbook is machine-checked. A single command re-runs all of it and proves that nothing frozen moved.

The dominant residual risks are research risks — permission, source bias, corpus scope — and frozen-artifact documentation risks (R-04, R-05) that were deliberately **not** repaired by rewriting evidence. Any paper or report must carry those limitations explicitly.
