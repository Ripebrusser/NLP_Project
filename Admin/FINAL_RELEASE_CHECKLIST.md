# Final Release Checklist

**Project:** Malayalam / English SMS spam–smishing classification, Phase 2 + prototype
**Release:** frozen codebase for paper preparation
**Date:** 8 November 2026
**Evidence root:** `Research Work/phase2/metrics/full_audit_results.json`

## A. Reproducibility gate

- [x] One-command audit exists and runs: `Research Work/run_full_audit.py`
- [x] All 15 checks pass on the final run (14 required + recorded browser evidence)
- [x] Verification-only dependency pins recorded (`Research Work/requirements-verification.txt`)
- [x] Reproducibility guide documents install, order, do-not-rerun list, hashes and troubleshooting
- [x] Audit result written to a machine-readable file with per-check status, duration, command and failure detail

## B. Research integrity gate

- [x] Dataset hashes unchanged (`24ca099a…a023b`, `649844f1…a71e`)
- [x] Six split hashes unchanged and matched to `split_manifest.json`
- [x] Four classical model hashes unchanged (`9ba1dcd6…`, `fd4a1542…`, `5de720cf…`, `6f8cd0e5…`)
- [x] MuRIL saved artifacts unchanged (config, tokenizer, tokenizer_config, 913 MB safetensors)
- [x] All 17 frozen prediction files unchanged
- [x] Frozen headline metrics identical before and after the audit (22/22 values in the earlier audit; 8/8 comparison values here)
- [x] No retraining, split regeneration, relabelling, augmentation or new data
- [x] Stale descriptive manifest block table preserved and documented rather than rewritten

## C. Correctness gate

- [x] 125/125 automated tests pass, 0 failures, 0 errors, 0 skipped
- [x] Statistical implementation corrected earlier (binary exact checks, block formula, alignment, empty input)
- [x] Paired LR/SVM direction and negation verified
- [x] Prototype reproduces 299/299 D1 and 883/883 D2 frozen predictions, batch and API
- [x] Cleaning parity 299/299 and 883/883
- [x] Literature matrix: 24 records, 23 active, 7 FULL / 6 ABSTRACT / 10 METADATA / 1 EXCLUDED, workbook = CSV = register = builder
- [x] Block totals recomputed as 630/991/371; manifest's 631/991/370 is documented as historical

## D. Application gate

- [x] Streamlit app loads locally on 127.0.0.1
- [x] D1 page, Malayalam input, Spam and Ham results observed in a browser
- [x] D2 page, Latin input, result card and score table observed in a browser
- [x] Latin input rejected in D1 mode with an explanatory message
- [x] Malayalam-only input rejected in D2 mode; mixed-script input warns but still predicts
- [x] Empty input warns without a prediction
- [x] Oversized input capped at 5,000 characters by the widget; 5,001 rejected by the library
- [x] Control-character input does not crash
- [x] Model-loading failure shows an inline error and leaves the page usable
- [x] Research dashboard renders 5 tabs, 6 metrics, 10 tables, 11 charts, block-holdout tab content
- [x] No console errors during the browser pass
- [x] No outbound network requests after disabling Streamlit usage statistics
- [x] Not deployed and not exposed beyond loopback

## E. Security and privacy gate

- [x] Artifact SHA-256 verified before `joblib.load`
- [x] Input validation: None, empty, bytes, control-only, oversize, wrong script
- [x] No user text logged, written or transmitted
- [x] No credentials in the repository
- [x] `unsafe_allow_html` only receives fixed or model-derived labels
- [x] Residual risks recorded with severity and acceptance rationale

## F. Documentation gate

- [x] `Admin/FINAL_CODEBASE_INVENTORY.md`
- [x] `Admin/FINAL_CODE_AUDIT_REPORT.md`
- [x] `Admin/FINAL_CODE_FIX_REGISTER.md`
- [x] `Admin/FINAL_TEST_REPORT.md`
- [x] `Admin/FINAL_REPRODUCIBILITY_GUIDE.md` (includes the single execution command)
- [x] `Admin/FINAL_SECURITY_AND_PRIVACY_AUDIT.md`
- [x] `Admin/FINAL_CODE_RISK_REGISTER.md` (final status per issue)
- [x] `Admin/ONE_COMMAND_AUDIT_REPORT.md`
- [x] `Admin/FINAL_RELEASE_CHECKLIST.md` (this file)
- [x] `Research Work/phase2/README.md` audit section and do-not-rerun list
- [x] `Research Work/prototype/README.md` verification section and input limits

## G. Explicitly out of scope / unresolved

These do **not** block the engineering freeze, but they must stay visible in the paper:

- [ ] D1 author permission (governance; unresolved)
- [ ] Source-block confound and the drop from 0.9650 to 0.5378 under block holdout (research limitation)
- [ ] No external, source-diverse Malayalam test set (research limitation)
- [ ] Exact MuRIL training configuration only partially recoverable (documented)
- [ ] `norm_key` collapses URLs to a `url` token (frozen group IDs; not changed)
- [ ] Historical `d1_block_robustness.json` retains old block membership (preserved, labelled)
- [ ] Fuzzy-duplicate threshold is a heuristic (reproducible, sensitivity untested)
- [ ] Manglish is unsupported by either model
- [ ] No visual/CSS, mobile-viewport, concurrency or accessibility-tooling pass on the UI

## H. Sign-off

| Item | Result |
|---|---|
| One-command audit | PASS (15/15) |
| Frozen artifacts | UNCHANGED (39/39 baseline hashes) |
| Regression suite | 125/125 PASS |
| Prototype parity | 299/299 + 883/883 |
| Literature validation | PASS |
| Browser pass | PASS, with documented driver caveat |
| Engineering status | **FROZEN — ready for paper preparation** |
| Research caveats | Open and documented; not code defects |
