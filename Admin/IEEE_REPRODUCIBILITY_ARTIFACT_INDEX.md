# IEEE Reproducibility Artifact Index

**Companion to:** `Admin/IEEE_REPRODUCIBILITY_APPENDIX.md`
**Date:** 8 November 2026
**Baseline:** `Research Work/phase2/metrics/audit_hash_baseline.json` (39 tracked artifacts, created 2026-11-08T16:16:45Z)

## How to read this index

"Frozen" means the artifact participates in a reported result and must not be regenerated; its SHA-256 is compared against the baseline on every audit run. "Required for verification" means the single audit command in the appendix reads it; removing it fails a check. "Shareable" is a permissions statement, not a technical one — several artifacts are technically easy to copy and still must not be published.

Three sharing categories are used:

- **Public** — may be published as part of the paper or supplementary material.
- **Restricted (D1)** — derived from Dataset 1, whose permission is pending; contains or encodes D1 text; must not be redistributed.
- **Restricted (privacy)** — licensed for reuse but contains raw personal SMS content; publish aggregates only unless an ethics review permits more.

Full hashes are below for every frozen artifact. They are reproductions of values stored in `split_manifest.json`, `model_manifest.json`, `audit_hash_baseline.json` and the MuRIL artifact directory, not recomputed claims.

---

## 1. Source datasets (2)

| Artifact | Location | Purpose | Frozen | Required for verification | Shareable | Restriction |
|---|---|---|---|---|---|---|
| D1 workbook, `Spam Message Collection.xlsx` | `Datasets/` | Primary Malayalam corpus (IEEE DataPort, DOI 10.21227/dcym-pd69) | Yes | Yes (`dataset_integrity`) | **No** | Subscriber access, no displayed licence, author permission **pending**; no raw messages, screenshots or rows |
| D2 CSV, `Dataset_5971.csv` | `Datasets/` | Secondary English/Latin corpus (Mendeley, DOI 10.17632/f45bkkt8pr.1) | Yes | Yes (`dataset_integrity`) | **Link only** | CC BY 4.0 with attribution; raw SMS content withheld here for privacy |

Hashes: D1 `24ca099ac1ffabc0b02fd491f57d577c56afb932bc81c5964a40e32eab9a023b`; D2 `649844f1c62a6b27e145eaf17a65f7010c56c390e11a794ea8329993a05ba71e`.

---

## 2. Split files (7)

All split files contain the message text column, so D1-derived splits inherit the D1 restriction.

| Artifact | Rows | Purpose | Frozen | Required | Shareable | Restriction |
|---|---:|---|---|---|---|---|
| `d1_malayalam_train.csv` | 1,394 | D1 training split | Yes | Yes | **No** | Contains D1 text |
| `d1_malayalam_val.csv` | 299 | D1 validation split (selection only) | Yes | Yes | **No** | Contains D1 text |
| `d1_malayalam_test.csv` | 299 | D1 frozen test split | Yes | Yes | **No** | Contains D1 text |
| `d1_malayalam_only_descriptive.csv` | 1,489 | Descriptive Malayalam-only subset; never a training target | Yes | No | **No** | Contains D1 text |
| `d2_train.csv` | 4,127 | D2 training split | Yes | Yes | Link only | CC BY 4.0; privacy review needed for raw text |
| `d2_val.csv` | 885 | D2 validation split | Yes | Yes | Link only | Same |
| `d2_test.csv` | 883 | D2 frozen test split | Yes | Yes | Link only | Same |

Location: `Research Work/phase2/splits/`.

| Split | SHA-256 |
|---|---|
| `d1_malayalam_train.csv` | `bd4f5edb59ce2579f21a2ac9eca4a3b9968b499f15780cfa9a3bee306204ddc1` |
| `d1_malayalam_val.csv` | `5bcc228f338b2685e2d5887f48815ba80579b670a71b4a0df6c0989243487f1f` |
| `d1_malayalam_test.csv` | `3922f037a2f52045ffc1d682e799880a06311dec9017ff33abef3fdd3d40be0b` |
| `d1_malayalam_only_descriptive.csv` | `e0b5b47381418c9c7ba5b8ea94e3e1d5c7508b852db57db5d8c7d8dcfcaf3284` |
| `d2_train.csv` | `ad19a6e8042dd4036331cf6920cd77da9cafe16787cd946dd821b3f0b2598499` |
| `d2_val.csv` | `2fc68c050731e90a3e511a8817796a4f3c639d00f0e8dad9a9d0268aa230400f` |
| `d2_test.csv` | `44409491ebb1c4e22d3aa65b76ca6f4e18ad2eb6af1f58380ab7f19236b46c79` |

---

## 3. Classical model artifacts (4)

Deserialising these requires the hash check in `inference.verify_artifact_hash()` and scikit-learn 1.9.1.

| Artifact | Location | Purpose | Frozen | Required | Shareable | Restriction |
|---|---|---|---|---|---|---|
| `d1_malayalam_linear_svm.joblib` | `Research Work/phase2/models/` | Primary D1 model; prototype D1 | Yes | Yes | **No** | Fitted on D1 text |
| `d1_malayalam_logreg.joblib` | same | D1 comparison model | Yes | Yes | **No** | Fitted on D1 text |
| `d2_linear_svm.joblib` | same | D2 comparison model | Yes | Yes | Conditional | CC BY 4.0 derived; review before release |
| `d2_logreg.joblib` | same | Primary D2 model; prototype D2 | Yes | Yes | Conditional | Same |

| Model | SHA-256 |
|---|---|
| D1 Linear SVM | `9ba1dcd62655bf501f4b0297d543bd232ad1348ab476c2efca9b07e0b97225cd` |
| D1 Logistic Regression | `fd4a1542436fc81890b117cdeba6cd1e3753bb1f0e832875068908a117af6e69` |
| D2 Linear SVM | `5de720cfcc7fe7179e976b6e2bb3e0410d1ca04145003dfcb8cb3ce5c5ea042e` |
| D2 Logistic Regression | `6f8cd0e5498f672bd71ddeaf494284f3c7aad6315bc39dbfb449f0cf388dc856` |

---

## 4. MuRIL artifacts (4)

Location: `Research Work/phase2/models/muril_d1_seed42/`. Only the seed-42 reference model is saved; seeds 43 and 44 exist as predictions and metrics, not as weights.

| Artifact | Purpose | Frozen | Required | Shareable | Restriction |
|---|---|---|---|---|---|
| `config.json` | Architecture configuration | Yes | Yes (hash only) | Conditional | Fine-tuned derivative of D1; base-model terms also apply |
| `model.safetensors` (913 MB) | Fine-tuned weights | Yes | Yes (hash only) | Conditional | Same; large binary, not needed for verification |
| `tokenizer.json` | Tokenizer vocabulary | Yes | Yes (hash only) | Conditional | Base-model terms |
| `tokenizer_config.json` | Tokenizer settings | Yes | Yes (hash only) | Conditional | Base-model terms |

| Artifact | SHA-256 |
|---|---|
| `config.json` | `e4fa4dc7d8ddc0733add99d10c19403d1d5ebf5ff43d3d22bdf8ef1a9d1ae972` |
| `model.safetensors` | `88a459fedef334dbc203e7e8dcd344aa10f59711c8d313578156b1727ad14e8b` |
| `tokenizer.json` | `2c404b60e22d168964a9a133d043002311a1049cfa9f2663a7a23e9fcd8e1cf8` |
| `tokenizer_config.json` | `a9a744fdd6a0788619337f5ce2447e70eb92c9efb30f8570ecac929069709816` |

The MuRIL base checkpoint revision is not recorded; see Appendix Section E.

---

## 5. Frozen prediction files (17)

Location: `Research Work/phase2/metrics/`. Every file carries `record_id` and either `prediction` or per-class scores. All contain the message text column and therefore inherit the D1 or D2 sharing restriction of their source.

| Artifact | Records | Purpose | Frozen | Required | Shareable |
|---|---:|---|---|---|---|
| `d1_malayalam_linear_svm_test_predictions.csv` | 299 | D1 SVM test predictions | Yes | Yes | **No** (D1) |
| `d1_malayalam_logreg_test_predictions.csv` | 299 | D1 LR test predictions | Yes | Yes | **No** (D1) |
| `muril_random_seed42_predictions.csv` | 299 | MuRIL seed 42 test predictions | Yes | Yes | **No** (D1) |
| `muril_random_seed43_predictions.csv` | 299 | MuRIL seed 43 test predictions | Yes | Yes | **No** (D1) |
| `muril_random_seed44_predictions.csv` | 299 | MuRIL seed 44 test predictions | Yes | Yes | **No** (D1) |
| `d2_logreg_test_predictions.csv` | 883 | D2 LR test predictions | Yes | Yes | Conditional (CC BY, privacy) |
| `d2_linear_svm_test_predictions.csv` | 883 | D2 SVM test predictions | Yes | Yes | Conditional |
| `muril_block4001_seed42_predictions.csv` | 630 | Block-held-out seed 42 | Yes | Yes | **No** (D1) |
| `muril_block4001_seed43_predictions.csv` | 630 | Block-held-out seed 43 | Yes | Yes | **No** (D1) |
| `muril_block4001_seed44_predictions.csv` | 630 | Block-held-out seed 44 | Yes | Yes | **No** (D1) |
| `muril_block5001_seed42_predictions.csv` | 991 | Block-held-out seed 42 | Yes | Yes | **No** (D1) |
| `muril_block5001_seed43_predictions.csv` | 991 | Block-held-out seed 43 | Yes | Yes | **No** (D1) |
| `muril_block5001_seed44_predictions.csv` | 991 | Block-held-out seed 44 | Yes | Yes | **No** (D1) |
| `muril_block6001_seed42_predictions.csv` | 371 | Block-held-out seed 42 | Yes | Yes | **No** (D1) |
| `muril_block6001_seed43_predictions.csv` | 371 | Block-held-out seed 43 | Yes | Yes | **No** (D1) |
| `muril_block6001_seed44_predictions.csv` | 371 | Block-held-out seed 44 | Yes | Yes | **No** (D1) |
| `block_cv_predictions.csv` | 1,992 | Classical block cross-validation predictions | Yes | Yes | **No** (D1) |

| Prediction file | SHA-256 |
|---|---|
| `d1_malayalam_linear_svm_test_predictions.csv` | `bd88b3c4519bf1c6808bc90e7527cf9f185f8aa772e661d8bda6f9d6404e821b` |
| `d1_malayalam_logreg_test_predictions.csv` | `c977e1e0c65e2fb09afc900bfcc3ada6693f22bc48f056e3a451e51f1a28a7ff` |
| `d2_linear_svm_test_predictions.csv` | `72034359e8d726322ea00e973dfc989226447f337347a57206a7784f42557528` |
| `d2_logreg_test_predictions.csv` | `01d37c607cab4eacadd1e50ec2ef98f7fdef2382482edda8bbf1a6e39c6931b7` |
| `muril_random_seed42_predictions.csv` | `e0fbdf4267418dc78139ffddd9f0486fe935e4603b821484fd211db24c20acde` |
| `muril_random_seed43_predictions.csv` | `e8d8161016995493c950d8a258b2a5a07471cf3942181630a9464e47673b1c36` |
| `muril_random_seed44_predictions.csv` | `8e2f1dd539f98edeeef7bb040d977466b9cb9a1c1a0c57a696c2e993576aa12f` |
| `muril_block4001_seed42_predictions.csv` | `72368932fbf812c6e897d37bb536927459f27e93f2945ee5d8a28b8d3716d587` |
| `muril_block4001_seed43_predictions.csv` | `5958aedd7c5cca8a394259ddf11eab443be93f49599644c1c02cf0a140c7bc9e` |
| `muril_block4001_seed44_predictions.csv` | `ca9a23564b5317de97bf153fe2eb455c066630ac2602e0740608814a78b75452` |
| `muril_block5001_seed42_predictions.csv` | `48d0bf58475987071745365b345fd306a62101976e69a08e898843c960579b9d` |
| `muril_block5001_seed43_predictions.csv` | `331a11f6036111432b442ecde88f6c6cfc62801e3d0eaedfd8f26144465e2c1e` |
| `muril_block5001_seed44_predictions.csv` | `359b9ec2ccd79c6a0fd82935c5be43a231a715ce28def6721ddeeb26ab57baf5` |
| `muril_block6001_seed42_predictions.csv` | `10d98accae2ba34ec633f2c2b879a59d39899b1bd5db9084f78b2ab3229236c8` |
| `muril_block6001_seed43_predictions.csv` | `e65cd11abb185752b450515c097a807e40ecaeec088d95951f6b7cc4a2f5afe1` |
| `muril_block6001_seed44_predictions.csv` | `a69e106673e3bededd4b24af698c6f3903e54b6cda92e7e1dc92f6b6cffb4a59` |
| `block_cv_predictions.csv` | `7f500e348b03bfa013178338c6fbb703161b29ef2c280fee66a72da0ea98d7ad` |

---

## 6. Manifests (2)

| Artifact | Location | Purpose | Frozen | Required | Shareable |
|---|---|---|---|---|---|
| `split_manifest.json` | `Research Work/phase2/splits/` | Seed, ratios, algorithm, sizes, group counts, overlap checks, six split hashes | Yes | Yes | Yes (aggregate metadata only; its descriptive block table is stale — see Appendix K.7) |
| `model_manifest.json` | `Research Work/prototype/` | Baseline SHA-256 of 4 models and 6 splits; used by the prototype loader | Yes | Yes | Yes |

| Manifest | SHA-256 |
|---|---|
| `split_manifest.json` | `4c67a5cce2a3b1982e0aa64a49bfe80ad6cde9b7194fa3062d1eae384f9653a7` |
| `model_manifest.json` | `f36ec570855adec7b0975c5ba8b8ffe0d71f33c2b558572f4d91e2d9bbf8a4b3` |

---

## 7. Verification outputs (3, frozen)

| Artifact | Location | Purpose | Frozen | Required | Shareable |
|---|---|---|---|---|---|
| `verification_results.json` | `Research Work/prototype/` | Prototype verifier output: hashes, alignment, 299/883 parity, guards | Yes | Yes | Yes (aggregate) |
| `final_verification.json` | `Research Work/phase2/metrics/` | Independent recomputation of headline metrics, exact intervals, block audit | Yes | Yes | Yes (aggregate) |
| `final_audit_stats.json` | `Research Work/phase2/metrics/` | Second independent recomputation: paired directions, block and script composition | Yes | Yes | Yes (aggregate) |

| Output | SHA-256 |
|---|---|
| `verification_results.json` | `f897215e893606babd03768cc0f7e01f7a0a338a74c5db67931ed074e302a5ac` |
| `final_verification.json` | `e16a3ceb30826d79019344e79cc1f38445cfd5834d0799dd29263b56dabf9702` |
| `final_audit_stats.json` | `8cc64e945830c30116ffddfa4c03429bf2a0cac76aad91c4b2eecdc6a40b51b9` |

These three files are rewritten by their own scripts during an audit run and restored byte-for-byte afterwards; the post-run hash check proves the restoration.

---

## 8. Audit and evidence outputs (not part of the frozen 39)

| Artifact | Location | Purpose | Shareable |
|---|---|---|---|
| `audit_hash_baseline.json` | `phase2/metrics/` | 39-artifact hash baseline for change windows | Yes |
| `full_audit_results.json` | `phase2/metrics/` | Latest 15-check audit receipt, per-check status/duration/command | Yes |
| `audit_runs/<run_id>/` | `phase2/metrics/` | Preserved audit receipts and pre-run copies of the three verification outputs | Yes |
| `browser_ui_test_results.json` | `phase2/metrics/` | 16-case browser pass with driver caveat and unverified surfaces | Yes |
| `code_audit_test_results.json` / `.log` | `phase2/metrics/` | 125-test result summary and full log | Yes |
| `code_audit_verification.json` | `phase2/metrics/` | Aggregate of tests, verifier, literature and metric agreement | Yes |
| `streamlit_audit_server.log` | `phase2/metrics/` | Loopback server log from the browser pass | Yes |
| `d1_block_robustness.json` | `phase2/metrics/` | **Historical** diagnostic produced with the superseded block formula; not authoritative | Yes, labelled historical |
| `confidence_intervals.json`, `paired_model_comparison.json`, `muril_seed_variation.json`, `validation_summary.json` | `phase2/metrics/` | Statistical source files for the appendix tables | Yes (aggregate) |

---

## 9. Code required for verification

| Path | Role | Required |
|---|---|---|
| `Research Work/run_full_audit.py` | Single-command audit (15 checks) | Yes |
| `Research Work/tests/` (11 files) | 125-test suite and result writer | Yes |
| `Research Work/prototype/verify_prototype.py` | Hash, alignment and parity verification | Yes |
| `Research Work/prototype/inference.py`, `app.py`, `research_data.py` | Prototype and hash-guarded loading | Yes for prototype checks |
| `Research Work/validate_literature_matrix.py` | Literature workbook validator | Yes |
| `Research Work/phase2/p2_final_verification.py`, `p2_final_audit_stats.py` | Metric recomputation | Yes |
| `Research Work/phase2/p2_common.py`, `p2_extract.py`, `p2_duplicates.py`, `p2_split.py` | Data preparation and grouping (read-only in verification) | Yes |
| `Research Work/phase2/p2_modeling.py`, `p2_train_d1.py`, `p2_train_d2.py`, `p2_muril.py` | Training path | No (do not run; overwrites frozen artifacts) |
| `Research Work/phase2/p2_ci.py` | Legacy CI writer; writes `*_legacy` outputs by default | No |
| `Research Work/requirements-verification.txt`, `prototype/requirements.txt` | Pinned dependencies | Yes |
| `.streamlit/config.toml` | Disables usage statistics; no credentials | Yes for the zero-network claim |

---

## 10. Documentation

| Document | Role |
|---|---|
| `Admin/IEEE_REPRODUCIBILITY_APPENDIX.md` | Authoritative appendix (this index is its companion) |
| `Admin/REPRODUCIBILITY_APPENDIX.md` | Condensed manuscript version |
| `Admin/REPRODUCIBILITY_APPENDIX_VALIDATION.md` | Claim-by-claim validation of the appendix |
| `Admin/FINAL_REPRODUCIBILITY_GUIDE.md` | Operational install/run guide, do-not-rerun list, troubleshooting |
| `Admin/ONE_COMMAND_AUDIT_REPORT.md` | What the audit checks and what it refuses to touch |
| `Admin/FINAL_RELEASE_CHECKLIST.md` | Release gates |
| `Admin/CANONICAL_FINAL_RESULTS.md` | Authoritative metric table |
| `Admin/FINAL_STATISTICAL_AUDIT.md` | Statistical method and corrections |
| `Admin/DATASET_PROVENANCE_AND_PERMISSIONS.md` | Provenance and permission status |
| `Admin/FINAL_CODE_RISK_REGISTER.md` | Residual risks and statuses |
| `Admin/FINAL_TEST_REPORT.md` | Test coverage and limits |
| `Admin/FINAL_CODEBASE_INVENTORY.md` | File-by-file inventory |
| `Research Work/phase2/README.md`, `Research Work/prototype/README.md` | Operative run instructions |

---

## 11. Sharing summary

| Category | Public | Conditions |
|---|---|---|
| D1 workbook, D1 splits, D1 model artifacts, D1/MuRIL predictions | No | Permission pending; aggregate statistics only |
| D2 CSV and D2-derived artifacts | Link / conditional | CC BY 4.0 attribution; raw personal SMS content requires privacy review |
| Manifests, verification outputs, audit receipts, code, documentation | Yes | Aggregate content only; no raw message text |

No artifact in this index may be published in a form that reproduces D1 message content until written permission is on file. The paper may report the counts, hashes, metrics and intervals contained in the appendix.
