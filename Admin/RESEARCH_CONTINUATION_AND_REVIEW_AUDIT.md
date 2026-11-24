# Research Continuation and Review Audit

> **AUDIT WORKING DOCUMENT.** This is an intermediate audit working document, not a submission document. Authoritative sources: `CANONICAL_FINAL_RESULTS.md`, `FINAL_STATISTICAL_AUDIT.md` and `VERIFICATION_REPORT.md`.


**Project:** Malayalam-script SMS spam detection, with a separate English SMS spam/smishing experiment  
**Audit date:** 6 November 2026  
**Status:** audit and explanation only. No dataset, label, split, model, app, report or deployment artifact was changed. No deployment was performed.

**Evidence labels used throughout**

| Label | Meaning |
|---|---|
| **VERIFIED** | Directly supported by code, a saved artifact, a recomputation, or a full-text paper. |
| **NEEDS VERIFICATION** | The available evidence is incomplete, stale, or only abstract/metadata level. |
| **RECOMMENDATION** | A proposed improvement. It has not been implemented. |

The main evidence root is `Research Work/phase2/metrics/`, `Research Work/phase2/splits/`, `Research Work/phase2/models/`, `Research Work/phase2/reports/`, `Research Work/prototype/`, `Admin/`, and the original files under `Datasets/`. This workspace has **no `.git` directory**, so the claimed “9 changed files” and their line counts cannot be verified from version control. The files themselves are present and were inspected.

---

## 1. Current project status

### 1.1 What exists

| Component | Status | Evidence |
|---|---|---|
| D1 input | **VERIFIED present** | `Datasets/Spam Message Collection.xlsx`, 7,717 data rows before exclusions. |
| D2 input | **VERIFIED present** | `Datasets/Dataset_5971.csv`, 5,971 rows. |
| D1 Malayalam subset | **VERIFIED** | `Research Work/phase2/data/d1_malayalam.csv`: 1,992 rows, 1,767 Ham / 225 Spam. |
| D2 grouped data | **VERIFIED** | `Research Work/phase2/data/d2_grouped.csv`: 5,971 original rows; 37 conflict groups / 76 records excluded in the split step. |
| Frozen splits | **VERIFIED** | `Research Work/phase2/splits/*.csv` and `split_manifest.json`, all six hashes match `Research Work/prototype/model_manifest.json`. |
| Classical models | **VERIFIED** | Four `.joblib` files under `Research Work/phase2/models/`; D1 SVM 963,858 bytes, D2 LR 1,400,097 bytes. |
| MuRIL comparator | **VERIFIED present, excluded from deployment** | `Research Work/phase2/models/muril_d1_seed42/`, roughly 0.9 GB; the models directory totals about 917 MB. |
| Frozen predictions and metrics | **VERIFIED** | `Research Work/phase2/metrics/`, including all three MuRIL seed prediction files. |
| Reports | **VERIFIED present, partly stale** | `Research Work/phase2/reports/`; several older fold values remain, listed in §1.4. |
| Streamlit prototype | **VERIFIED functional** | `Research Work/prototype/app.py`, `inference.py`, `research_data.py`, `verify_prototype.py`; current health check returns `200`. |
| Prototype verification report referenced by README | **MISSING** | `Research Work/prototype/README.md` names `VERIFICATION_REPORT.md`; no such file exists. The actual machine result is `verification_results.json`. |
| Git history | **NOT AVAILABLE** | No `.git` directory. The “9 changed files” claim cannot be checked against a diff. |

### 1.2 The nine prototype files

The nine claimed files are present; their current sizes are shown because line counts cannot be recovered without Git.

| File | Bytes | Role |
|---|---:|---|
| `.streamlit/config.toml` | 155 | Light theme only. |
| `Research Work/prototype/app.py` | 26,181 | Streamlit UI. |
| `Research Work/prototype/inference.py` | 4,653 | Loads frozen pipelines and performs prediction. |
| `Research Work/prototype/MODEL_AND_DATASET_NOTES.md` | 4,363 | Scope and model notes. |
| `Research Work/prototype/model_manifest.json` | 1,095 | Model and split hashes. |
| `Research Work/prototype/README.md` | 3,365 | Run and file guide. |
| `Research Work/prototype/requirements.txt` | 181 | Pinned runtime dependencies. |
| `Research Work/prototype/research_data.py` | 5,448 | Read-only dashboard loaders. |
| `Research Work/prototype/verify_prototype.py` | 5,091 | Hash, parity, cleaning and class-coverage checks. |

The exact verification filename is **`Research Work/prototype/verify_prototype.py`**. Its latest run returned `status: PASS`; the saved result is `Research Work/prototype/verification_results.json`.

### 1.3 Current verification result

Re-running `verify_prototype.py` on this machine produced:

- D1 Linear SVM SHA-256 `9ba1dcd62655bf501f4b0297d543bd232ad1348ab476c2efca9b07e0b97225cd`, matching the manifest; 299/299 test predictions reproduced; cleaning parity 299/299.
- D2 Logistic Regression SHA-256 `6f8cd0e5498f672bd71ddeaf494284f3c7aad6315bc39dbfb449f0cf388dc856`, matching the manifest; 883/883 test predictions reproduced; cleaning parity 883/883.
- All six split hashes match the manifest.
- Malayalam detection, Latin detection, Malayalam preservation after cleaning and empty-input rejection all pass.
- Both classes/class sets are covered.

This establishes **model parity**, not new model performance. No model was fitted or modified.

### 1.4 Documentation inconsistencies that affect the record

These are **VERIFIED inconsistencies**, not changes made by this audit.

| Issue | Current evidence | Consequence |
|---|---|---|
| D1 block membership is still shown as 631/991/370 in older files | `Admin/EVIDENCE_REGISTER.md` E74; `Research Work/phase2/reports/D1_RESULTS.md` | The corrected membership is 630/991/371. The old off-by-one misclassified two Ham rows, `D1-04998` and `D1-05998`. |
| Old SVM block-6001 fold is 0.3677 in some files | `Admin/EVIDENCE_REGISTER.md` E74; `Admin/REVIEW_2_PROGRESS_REPORT.md` §1 and §7; `Research Work/phase2/reports/D1_RESULTS.md` | Corrected SVM fold is **0.368470**; the pooled result, 0.5378, is unchanged. |
| “Transformers — NOT STARTED” still appears | `Admin/REVIEW_2_PROGRESS_REPORT.md` §3; `Admin/REVIEW_2_PROGRESS_COMPARISON.md` | MuRIL is complete; this line is stale. |
| D2 is described as having “no source-block structure” | `Research Work/prototype/app.py` line 552; `Research Work/phase2/reports/FINAL_MODEL_SELECTION.md` | The defensible statement is “no source/collection metadata,” not “no structure.” |
| “Random Macro-F1” is used as a column/metric label | `Research Work/prototype/app.py` lines 458, 480, 564; `Admin/REVIEW_2_PROGRESS_REPORT.md` §11.4; `Research Work/phase2/reports/FINAL_MODEL_SELECTION.md` | The implemented protocol is a duplicate-group-aware, label-stratified random split. The label should say so. |
| README points to `VERIFICATION_REPORT.md` | `Research Work/prototype/README.md` | The file does not exist; `verification_results.json` is the actual artifact. |
| D2 headline denominator can be misread | `Admin/REVIEW_2_PROGRESS_REPORT.md` §2.1 vs §2.7 | 5,971 is the original count; the models use 5,895 after exclusion of 76 conflicting-label records. |

**RECOMMENDATION:** correct these labels and stale values in a later documentation pass, after the team accepts the audit. Do not silently overwrite prior artifacts; keep the old files as historical records and add a correction note or a corrected version.

---

## 2. Prototype and hosting diagnosis

### 2.1 Is the app functional and does it load the saved models?

**VERIFIED — yes.** The application is a read-only inference layer. `inference.py` loads only the two selected `.joblib` pipelines, validates required artifact keys, and applies the same conservative cleaner as training. `research_data.py` reads saved metrics only.

Evidence:

- `Research Work/prototype/inference.py`: `load_artifact()` and `model_summary()`; model files are `d1_malayalam_linear_svm.joblib` and `d2_logreg.joblib`.
- `Research Work/prototype/research_data.py`: read-only JSON/CSV loaders.
- `Research Work/prototype/verify_prototype.py`: hashes, exact prediction parity, cleaning parity, class coverage.
- Current run: `http://127.0.0.1:8501/_stcore/health` returned `ok`/HTTP 200; the browser rendered the Malayalam screen and the Research dashboard without console errors.
- The server process used about **245 MiB** working set (251,144 KB as reported by `tasklist`) while serving the dashboard. The two deployed models total about **2.36 MB**; MuRIL is not loaded.

The browser check was a local functional check, not a visual design review and not a deployment test.

### 2.2 Why did the local site become inaccessible?

**VERIFIED:**

- `Research Work/prototype/logs/streamlit.log` starts at 05:15:34 and its last entries are at 05:22:33.
- The log contains only Streamlit deprecation and Arrow serialization warnings; there is **no Python traceback and no application crash**.
- No process was listening on `127.0.0.1:8501` when the audit checked the next session.
- Windows system events recorded sleep at about 05:38:43, power-off initiation at 05:41:53, shutdown at 05:42:25, and the next boot at 16:22:49.
- The app had therefore already stopped about 16 minutes **before** sleep. The later machine shutdown would also have made it unreachable, but it was not the first cause.

**NEEDS VERIFICATION:** the exact reason the process ended. The available evidence supports **process/session termination** (the terminal or background runner that owned the child process ended), not a code exception. The log cannot distinguish a closed terminal from a manually stopped or cleaned-up background process.

A failed restart attempt during the earlier audit produced `Research Work/prototype/logs/audit_streamlit.log.err` with “provided file has no extension.” That was a shell-quoting error in the restart command, not evidence about the original app. The current restart was performed with a correctly quoted absolute-style path and succeeded.

**RECOMMENDATION:** for a persistent demonstration, run the app under a supervised process or a hosting platform; do not rely on a terminal session staying open. On Windows, a foreground terminal window must remain open. A platform service is the correct solution for remote access.

### 2.3 Is the app suitable for deployment?

**VERIFIED technically:** yes, as a **demonstration**. It loads frozen artifacts, makes no network calls, writes no user text to disk, needs no GPU, and its runtime footprint is small when MuRIL and raw datasets are excluded.

**NOT PRODUCTION-READY.** Reasons:

1. No authentication, authorization, rate limiting or abuse controls.
2. No external, source-diverse validation; D1’s random score is a within-source result (0.9650) and falls to 0.5378 under leave-one-row-block-out.
3. The D1 model is a linear SVM with a decision score, not a calibrated probability. The app correctly does not display a fake confidence value.
4. D2 is English/Latin-only and does not support Malayalam or Manglish claims.
5. D1 access provenance is unresolved; the dataset must not be published or redistributed.
6. The app classifies the datasets’ original labels; it does not verify URLs, detect phishing, or establish that a message is safe.

**RECOMMENDATION:** label it “academic research demonstration,” keep the source-block warning visible, and do not present it as a security product.

### 2.4 Streamlit Community Cloud vs Render

Official documentation checked on 6 November 2026:

- Streamlit Community Cloud resource limits and hibernation: <https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app>
- Streamlit deployment and Python-version selection: <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy>
- Render free-service limitations: <https://render.com/docs/free>

| Criterion | Streamlit Community Cloud | Render Free |
|---|---|---|
| Native fit | **Best** — runs Streamlit directly from a GitHub repo | Requires a Python web-service start command |
| Memory | Approximately 690 MB minimum to **2.7 GB maximum** | **512 MB** total for the free instance |
| CPU | 0.078–2 cores, shared | **0.1 CPU** |
| Idle behavior | Sleeps after **12 hours** without traffic | Spins down after **15 minutes** without inbound traffic |
| Wake-up | Visitor wakes the app | About **1 minute** cold start |
| Storage | Up to 50 GB, not needed here | Ephemeral; free instances cannot attach a persistent disk |
| Custom domain | `*.streamlit.app` subdomain; no custom domain | Custom domains supported |
| Cost | Free tier | Free tier; paid instance needed for no spin-down |
| Suitability for this app | **Recommended for the course demo** | Workable fallback, but less memory headroom and more setup |

**VERIFIED:** neither free plan provides permanent uptime. Streamlit hibernates after 12 hours; Render spins down after 15 minutes. A free URL is not an always-on service.

**RECOMMENDATION:** use **Streamlit Community Cloud** for this prototype. Use Render only if a custom domain, a private service, or a non-Streamlit process is required, or if the team pays for an always-on instance. A paid plan is the only honest route to continuous availability; verify current pricing before committing.

Measured local memory was about 245 MiB (251,144 KB working set). That is below Render’s 512 MB, but with little headroom for concurrent sessions and dependency overhead. Streamlit Cloud’s 2.7 GB maximum is the safer fit.

### 2.5 Deployment changes and repository structure

**VERIFIED:** the app does **not** need the raw datasets, the splits, the MuRIL model, or the research reports at runtime. It needs:

- `app.py`, `inference.py`, `research_data.py`;
- the two selected `.joblib` models;
- six aggregate metric files loaded by `research_data.py`:
  `d1_malayalam_results.json`, `d2_results.json`, `muril_results.json`, `validation_summary.json`, `final_model_comparison.csv`, `confidence_intervals.json`;
- `requirements.txt` and the theme config.

`inference.py` and `research_data.py` resolve paths as `parents[2] / "Research Work" / "phase2"`, so the simplest safe deployment is to preserve that relative tree rather than rewrite code during this audit:

```text
sms-research-demo/
  .streamlit/config.toml
  Research Work/prototype/app.py
  Research Work/prototype/inference.py
  Research Work/prototype/research_data.py
  Research Work/prototype/requirements.txt
  Research Work/prototype/model_manifest.json
  Research Work/phase2/models/d1_malayalam_linear_svm.joblib
  Research Work/phase2/models/d2_logreg.joblib
  Research Work/phase2/metrics/d1_malayalam_results.json
  Research Work/phase2/metrics/d2_results.json
  Research Work/phase2/metrics/muril_results.json
  Research Work/phase2/metrics/validation_summary.json
  Research Work/phase2/metrics/final_model_comparison.csv
  Research Work/phase2/metrics/confidence_intervals.json
```

Do **not** include:

- `Datasets/` (licence/provenance and privacy risk);
- `Research Work/phase2/models/muril_d1_seed42/` (roughly 0.9 GB; not used by the app);
- `Research Work/phase2/splits/` or frozen predictions containing message text;
- `.venv/`, `__pycache__/`, logs, local screenshots, or unrelated reports.

**Startup commands**

- Streamlit Community Cloud: select the repository, branch and entrypoint `Research Work/prototype/app.py`; choose a Python version compatible with the pinned environment; let the platform install `requirements.txt`. No custom start command is required.
- Render: build command `pip install -r "Research Work/prototype/requirements.txt"`; start command:

```bash
streamlit run "Research Work/prototype/app.py" --server.address 0.0.0.0 --server.port $PORT --server.headless true
```

Set a health-check path of `/_stcore/health`.

**Dependency/model compatibility:** `requirements.txt` is pinned to Streamlit 1.67.0, scikit-learn 1.9.1, joblib 1.6.0, pandas 3.1.1 and numpy 2.5.4, tested on Python 3.14.3. Joblib artifacts are version-sensitive. Run `verify_prototype.py` inside the deployment environment before calling the deployment successful. If the host does not offer 3.14.3, do not silently unpin; rebuild and re-verify in the selected supported version.

**RECOMMENDATION:** use a private repository or a clean public deployment repository containing only the files above. A public repository that includes `Datasets/`, frozen prediction CSVs or the MuRIL directory would expose restricted data or waste build resources. Deploy only after team approval.

### 2.6 Deployment checklist (not executed)

- [ ] Team approves a hosting choice and a public/private repository.
- [ ] D1 access/provenance question is resolved or D1 is removed from the public demo.
- [ ] Create a clean deployment tree with only the files in §2.5.
- [ ] Confirm `requirements.txt` installs in the host’s Python version.
- [ ] Run `verify_prototype.py` in a clean environment; require `PASS`.
- [ ] Start the app; check `/_stcore/health` and load both modes.
- [ ] Enter one Ham and one Spam example; confirm no server error.
- [ ] Check that no raw data or MuRIL files are in the build context.
- [ ] Add the source-block limitation to the landing screen (already present in the local app).
- [ ] Do not announce permanent uptime; document hibernation/spin-down.

---

## 3. MuRIL missing accuracy and full metrics audit

### 3.1 The metrics were computed; the presentation omitted accuracy

**VERIFIED:** `Research Work/phase2/metrics/muril_results.json` and `muril_seed_variation.json` contain per-seed accuracy, macro-F1, Ham/Spam precision, recall and F1, and confusion matrices. `muril_random_seed42_predictions.csv`, `...seed43...` and `...seed44...` contain the frozen per-row predictions. The omission was a **reporting omission**, not a missing computation.

The prior presentation emphasized Macro-F1 and Spam recall because the test set is 88.6% Ham (265/299); plain accuracy is dominated by the majority class. That is a defensible reason to make Macro-F1 primary, but it is not a reason to omit accuracy. Accuracy should be reported as a secondary metric.

### 3.2 Per-seed metrics on the frozen 299-row test set

All three runs use the same frozen grouped split, the same 299 test records, and the label order `["Ham", "Spam"]` (confusion matrix rows = true Ham/Spam; columns = predicted Ham/Spam).

| Seed | Accuracy | Macro-F1 | Ham P / R / F1 | Spam P / R / F1 | Confusion matrix |
|---:|---:|---:|---|---|---|
| 42 | 0.986622 | 0.965005 | 0.9851 / 1.0000 / 0.9925 | 1.0000 / 0.882353 / 0.9375 | `[[265, 0], [4, 30]]` |
| 43 | 0.983278 | 0.955645 | 0.9815 / 1.0000 / 0.9907 | 1.0000 / 0.852941 / 0.9206 | `[[265, 0], [5, 29]]` |
| 44 | 0.986622 | 0.965005 | 0.9851 / 1.0000 / 0.9925 | 1.0000 / 0.882353 / 0.9375 | `[[265, 0], [4, 30]]` |
| **Mean ± SD** | **0.985507 ± 0.001931** | **0.961885 ± 0.005404** | Ham F1 0.991891 ± 0.001071 | **1.000000 ± 0.000000 / 0.872549 ± 0.016981 / 0.931878 ± 0.009737** | — |

Sources: `Research Work/phase2/metrics/muril_results.json`, `muril_seed_variation.json`, and the three `muril_random_seed*_predictions.csv` files. The same values appear in `Research Work/phase2/reports/MURIL_BENCHMARK_REPORT.md`.

**Accuracy in percentage form:** 98.66%, 98.33%, 98.66%; mean **98.55% ± 0.19 percentage points**.  
**Macro-F1 in percentage form:** 96.50%, 95.56%, 96.50%; mean **96.19% ± 0.54 percentage points**.  
**Spam recall in percentage form:** 88.24%, 85.29%, 88.24%; mean **87.25% ± 1.70 percentage points**.

No ROC-AUC or PR-AUC is saved for MuRIL in these artifacts. Do not invent one. The saved artifacts do support accuracy, per-class precision/recall/F1 and confusion matrices.

### 3.3 Did MuRIL actually beat the Linear SVM?

**VERIFIED — no.** The comparison is:

| Model | Accuracy | Macro-F1 | Spam precision | Spam recall |
|---|---:|---:|---:|---:|
| D1 Linear SVM | **0.986622** | **0.965005** | 1.0000 | **0.882353** |
| D1 Logistic Regression | 0.983278 | 0.955645 | 1.0000 | 0.852941 |
| MuRIL, 3-seed mean | 0.985507 ± 0.001931 | 0.961885 ± 0.005404 | 1.0000 | 0.872549 ± 0.016981 |

MuRIL is slightly below the SVM on mean accuracy (by 0.001115, about 0.11 percentage points), below it on mean Macro-F1 (by 0.003120), and below it on mean Spam recall (by 0.009804). Seeds 42 and 44 produce predictions identical to the SVM; seed 43 differs by one Spam false negative. The paired comparison in `confidence_intervals.json` reports a zero difference for seed 42 vs SVM and a one-message difference for seed 43. There is no transformer advantage.

The defensible statement is: **MuRIL ties the classical SVM at best within the source and does not improve it.** It does not “perform better” on this experiment.

### 3.4 Why did MuRIL perform poorly under source-block holdout?

**VERIFIED data facts:**

- D1 has 225 Spam. Of these, **213 (94.7%) are in the 6001–7000 row block**.
- Holding out 6001–7000 leaves only **12 Spam** in the training data; the held-out block has 371 records, 213 Spam and 158 Ham.
- Training rows outside that block: 1,621, of which only 12 are Spam (0.74%); the held-out block is 57.4% Spam. This is a large prior/source shift.

**VERIFIED model behavior:** MuRIL predicts Ham for **all 213 Spam** messages in the 6001–7000 block in every seed. Its block-6001 confusion matrix is `[[158, 0], [213, 0]]`; accuracy is 0.425876, Spam recall is 0, and Macro-F1 is 0.298677. The pooled block-held-out result is **0.502777 ± 0.006232** Macro-F1 and **3.56%** Spam recall.

**Interpretation (VERIFIED/ RECOMMENDATION):** this is a source/template and class-prior failure, not a small calibration offset. The model has almost no Spam examples from the unseen block, and the held-out Spam campaign has no lexical/template overlap with the 12 training Spam. The saved block scores are nearly constant across the block, so the model is not ranking Spam above Ham there.

The transformer reproduces the dataset’s batch confound rather than removing it. The result does **not** prove that MuRIL is generally unsuitable for Malayalam; it shows that fine-tuning on 12 Spam from one batch does not transfer to a different batch.

### 3.5 Why all 213 Spam became Ham

The decisive mechanism is the combination of:

1. **Almost no positive examples in training:** 12 Spam, all from a different row block.
2. **A held-out block dominated by one campaign:** 213 of 225 total Spam, with a different surface form.
3. **A model that collapses toward Ham:** the saved MuRIL block probabilities are effectively constant (reported as about 0.1081, 0.2980 and 0.2920 by seed), so every row falls on the same side of the default boundary.
4. **No block-aware tuning:** the held-out block was not used to choose an epoch or threshold; that is methodologically correct, but it means the model cannot adapt to the unseen campaign.

### 3.6 Could threshold calibration solve it?

**VERIFIED — no for MuRIL; only partially for the classical model.**

- For MuRIL block 6001, the scores are effectively constant. Any threshold labels all rows one class; there is no operating point that separates Spam from Ham. This is a representation/source-shift failure.
- For the classical SVM, the ranking is informative (Spam PR-AUC about 0.9798), and a training-derived threshold can raise block-6001 recall from 6.57% to 60.09% at precision 1.0 in one split. But across 20 inner splits, recall is **44.34% ± 16.79%**, and the selected threshold ranges from **−0.6753 to −0.3152**. With only 12 training Spam, threshold selection is unstable.
- Therefore, thresholding is a useful sensitivity analysis, not a solution to the source-block problem. The durable fix is more source-diverse Spam data or a block-aware/external evaluation.

Sources: `Research Work/phase2/metrics/threshold_calibration.json`, `threshold_calibration.csv`, `threshold_calibration_splits.csv`, `Research Work/phase2/reports/THRESHOLD_CALIBRATION_REPORT.md`.

### 3.7 Recommended MuRIL reporting

**RECOMMENDATION:**

1. Add an accuracy column to the MuRIL table, clearly marked secondary.
2. Keep Macro-F1 and Spam recall as primary because Ham is 88.6% of the test set.
3. Report the three seeds and the mean ± SD, not only the mean.
4. State that seeds 42/44 are prediction-identical to the SVM and seed 43 differs by one Spam message.
5. Pair the random-split result with the block-held-out result in the same table or the same sentence.

---

## 4. Block-held-out evaluation explanation

### 4.1 What is a “source block”?

**VERIFIED:** in this project, a “source block” is a **consecutive 1,000-row window of the D1 workbook**, not a documented collection source. The block is computed from `source_row` (the Excel row number, with header = row 1):

```text
block = (source_row - 1) // 1000 + 1
```

`source_row` 4146, for example, falls in block 5, displayed as rows 4001–5000. The Malayalam subset occupies only three populated blocks:

| Block (source rows) | Records | Ham | Spam |
|---|---:|---:|---:|
| 4001–5000 | 630 | 618 | 12 |
| 5001–6000 | 991 | 991 | 0 |
| 6001–7000 | 371 | 158 | 213 |

**Important limitation:** these are row-order strata used as **source proxies**. The dataset does not provide a collection-batch ID. The block structure is strong evidence of batch composition (including a 991-row all-Ham block), but “source block” should not be written as if the original collectors documented these as sources. A more accurate name is “1,000-row workbook block” or “row-order block.”

### 4.2 How were the blocks identified?

**VERIFIED:** from the Excel row number preserved in `source_row` in `Research Work/phase2/data/d1_malayalam.csv` and the split files. The block assignment is deterministic; there is no clustering or manual labeling. The source-block audit is in `p2_validate.py` (`block_of`, `block_audit`, `block_cv`) and the resulting table is in `validation_summary.json`.

The earlier `p2_robustness.py` used an off-by-one formula, `((source_row-1)-1)//1000+1`, which shifted its labels one row low. That produced 631/991/370 membership and the stale SVM fold 0.3677. The corrected code is `(source_row-1)//1000+1`, giving 630/991/371 and SVM fold 0.368470. The correction moved exactly two Ham records, `D1-04998` and `D1-05998`; it did not change the headline pooled result 0.5378.

### 4.3 What does holding out a complete block mean?

For each block:

1. Remove every Malayalam record in that block from training.
2. Train a fresh pipeline on all records in the other two blocks.
3. Test only on the removed block.
4. Repeat for all three blocks.
5. Concatenate the three sets of test predictions into one 1,992-row prediction vector.
6. Compute **one** Macro-F1 on that pooled vector.

There is no validation-based tuning on the held-out block and no threshold selection on it. The pipeline configuration is the one selected on the ordinary training/validation split.

### 4.4 How is the pooled Macro-F1 calculated?

**VERIFIED:** “pooled” means the predictions are combined **before** scoring, not averaged across folds. The code in `p2_validate.py` (`block_cv`) appends every held-out prediction to `pooled_pred` and every true label to `pooled_true`, then calls the same binary metric function once. Macro-F1 is:

```text
Macro-F1 = (F1_Ham + F1_Spam) / 2
```

It is an unweighted mean of the two class F1 scores. The pooled calculation weights each fold by its number of records, so the 991-row block contributes most of the Ham predictions. The three fold scores are **not** averaged; a simple average would give a different number.

The pooled confusion matrices are:

| Model | True Ham / predicted Ham | True Ham / predicted Spam | True Spam / predicted Ham | True Spam / predicted Spam | Pooled Macro-F1 |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 1,746 | 21 | 205 | 20 | **0.544795** |
| Linear SVM | 1,756 | 11 | 208 | 17 | **0.537845** |
| MuRIL (seed 42) | 1,755 | 12 | 218 | 7 | **0.497940** |

The per-fold scores are descriptive, not a balanced estimate:

| Held-out block | Train Spam | Test rows | Test Spam | LR fold Macro-F1 | SVM fold Macro-F1 |
|---|---:|---:|---:|---:|---:|
| 4001–5000 | 213 | 630 | 12 | 0.696386 | 0.696386 |
| 5001–6000 | 225 | 991 | 0 | 0.494646 | 0.497210 |
| 6001–7000 | 12 | 371 | 213 | 0.382507 | **0.368470** |

The 5001–6000 fold has no Spam support, so its Spam F1 is set to zero by `zero_division=0`; its Macro-F1 is not a meaningful balanced score. That is why the report says the middle block cannot evaluate Spam.

### 4.5 Why is this different from a normal random split?

In the ordinary grouped random split, every block is represented in training and test. Because Spam is concentrated in one block, the training set contains many Spam messages from the same block/campaign as the test Spam. Duplicate groups are kept intact, but different messages from the same campaign or block can still share vocabulary and templates. The random split therefore measures **within-source/within-batch** performance.

In leave-one-block-out, an entire block is absent from training. The model must classify a campaign it has never seen. That is a much harder and more realistic test of source transfer, although with only three blocks it is a stress test, not a population estimate.

### 4.6 What does the drop tell us?

**VERIFIED:** the SVM drops from 0.9650 Macro-F1 on the grouped random split to 0.5378 pooled under block holdout; Spam recall drops from 88.24% to 7.56%. The LR drops from 0.9556 to 0.5448 and 85.29% to 8.89%. MuRIL drops to 0.5028 and 3.56%.

This tells us:

1. **The dataset has a strong batch/label confound.** Spam is not spread across sources; 94.7% sits in one row block.
2. **The random-split score is optimistic for unseen sources.** It is a valid within-source benchmark, not field performance.
3. **The failure is not just a threshold issue.** The classical model retains some ranking signal, but MuRIL’s scores are nearly constant in the critical block.
4. **No generalisation claim is supported.** A source-diverse external test set is required.

### 4.7 Is “block-held-out Macro-F1” clear enough?

**RECOMMENDATION:** the term is understandable only after the row-block definition is stated. For an academic presentation, use:

> **Leave-one-row-block-out (LORBO) pooled Macro-F1**

and define it in one sentence:

> “We split the workbook into consecutive 1,000-message blocks, hide one whole block, train on the other two, test on the hidden block, and then combine all held-out predictions before computing one Macro-F1.”

If the team prefers “source block,” write **“row-order source-block proxy”** at first use. Do not call the blocks verified collection sources.

---

## 5. D2 N/A explanation and possible evaluation

### 5.1 Why D2 has no block-held-out result

**VERIFIED:** D2 has no source or collection identifier. Its columns are `LABEL`, `TEXT`, `URL`, `EMAIL` and `PHONE`; `URL`, `EMAIL` and `PHONE` are binary flags, not provenance fields. `source_row` is only the CSV line number. There is no collection batch, date, provider or source label with which to define a source holdout.

Therefore the current N/A is **methodologically correct**. It is not a failed computation and not a missing model run. The correct wording is:

> **Not applicable — D2 has no source/collection metadata, so a source-block-held-out estimate cannot be defined. D2 is evaluated only under the duplicate-grouped random split.**

Do **not** write “D2 has no source-block structure.” That overclaims: absence of metadata is not proof that the underlying messages have no structure. The app line 552 and `FINAL_MODEL_SELECTION.md` should be corrected in the later documentation pass.

### 5.2 Are there meaningful groups that support an equivalent evaluation?

**VERIFIED:** D2 has duplicate groups, and those are already used to keep duplicates out of different splits. But duplicate groups are not source groups:

- Most D2 duplicate groups are size 1; a leave-one-group-out CV would approximate an ordinary random CV.
- A group holdout tests near-duplicate memorization, not transfer to a new collection source.
- A row-order block holdout on D2 would test arbitrary CSV order, not source shift; presenting it as “block-held-out” would be misleading.

**RECOMMENDATION:** do not invent source blocks. If a reviewer asks for a robustness check, the defensible optional analysis is a **grouped 5-fold cross-validation** to estimate split stability. It is not equivalent to a source holdout and should be labelled as such. It is not necessary for the current report.

### 5.3 Recommended table wording

Replace `N/A` in the D2 row with:

> **Not applicable — no source/collection metadata; grouped random split only.**

If space is limited, use `N/A (no source metadata)` and put the full sentence in the table note. Do not use a dash without explanation.

---

## 6. “Random Macro-F1” explanation

### 6.1 What the implemented protocol actually is

**VERIFIED:** the primary split is a **duplicate-group-aware, label-stratified 70/15/15 random split**, seed 42.

- D1: 1,992 records → 1,394 train / 299 validation / 299 test; test has 265 Ham / 34 Spam.
- D2: 5,895 records after conflicting-label exclusions → 4,127 train / 885 validation / 883 test; test has 726 Ham / 67 Spam / 90 Smishing.
- Groups are exact, normalised and (for D1) conservative fuzzy duplicate clusters. A group is never split.
- Within each label stratum, group IDs are shuffled with `numpy.default_rng(42)`, sorted by group size, and assigned to the split with the largest remaining record deficit (`p2_common.split_grouped`).
- The test set was evaluated once after model selection on validation Macro-F1; the final models were refit on train + validation.
- Macro-F1 is the unweighted mean of the per-class F1 scores. The metric implementation is `sklearn.metrics.f1_score(..., average="macro")`.
- Confidence intervals are a 2,000-replicate group bootstrap over the frozen test predictions, not a new split.

“Random” here means **random assignment of duplicate groups within label strata**, not random assignment of individual rows. “Macro-F1” means the unweighted class average, not accuracy and not weighted F1.

### 6.2 Is “Random Macro-F1” an accurate label?

**VERIFIED:** no, it is too vague. It hides both the grouping and the fact that this is a test-set metric. It also invites the incorrect reading that the reported mean ± SD for MuRIL comes from multiple random splits; it does not. MuRIL’s ± is the standard deviation across three fine-tuning seeds on **one** frozen split.

**RECOMMENDATION:** use one of these, consistently:

- **“Grouped random-split test Macro-F1”** — concise and accurate.
- **“Duplicate-grouped, stratified random-split test Macro-F1”** — fully explicit for a paper.
- For MuRIL: **“Mean ± SD over 3 fine-tuning seeds on one frozen grouped random split.”**

Do not use “Random Macro-F1” in the final presentation or paper without the definition.

---

## 7. Language-filter explanation

### 7.1 Why the filter was used

**VERIFIED:** D1 is a five-language Dravidian SMS corpus (English, Tamil, Telugu, Kannada, Malayalam). The project’s primary scope is **Malayalam-script** SMS, so the experiment selects messages containing at least one Malayalam Unicode character. Without this filter, the model would be dominated by Tamil, Telugu, Kannada and Latin-only messages and would not answer the Malayalam question.

### 7.2 How it is implemented

**VERIFIED:** `Research Work/phase2/p2_common.py` defines:

```python
MAL = re.compile(r"[\u0D00-\u0D7F]")
```

`add_script_flags()` sets `has_malayalam`; `p2_extract.py` selects `d1[d1["has_malayalam"]]` and keeps Ham/Spam labels. `inference.py` uses the same range for the D1 input guard. The filter is applied to the original message before model cleaning.

### 7.3 What it includes and excludes

**VERIFIED:**

- Total selected: **1,992** records, 1,767 Ham / 225 Spam.
- **1,489** are flagged Malayalam-only script (no Latin, no Tamil/Telugu/Kannada): 1,429 Ham / 60 Spam.
- **503** also contain Latin characters: 338 Ham / 165 Spam.
- The filter includes any message with at least one codepoint in U+0D00–U+0D7F, including Malayalam letters, vowel signs, virama and Malayalam punctuation.
- It excludes messages written entirely in Tamil, Telugu, Kannada or Latin script, and it excludes **Romanised Malayalam (Manglish)** unless the message also contains a Malayalam codepoint.
- It would include a message that is mostly Tamil/English but contains one Malayalam character. The audit found no Tamil/Telugu/Kannada co-occurrence in the Malayalam subset, but that is a dataset fact, not a guarantee of the filter.

An older audit table reports 1,486 Malayalam-only and 503 mixed, while the Phase 2 artifact reports 1,489 and 503. The 1,992 total and the labels are stable; the three-record difference is a script-category definition inconsistency that still needs reconciliation. It does not change the model results, but the final paper should use one definition and state it.

### 7.4 Why Unicode presence is not language identification

**VERIFIED:** Unicode block membership identifies **script**, not language. A message can contain Malayalam characters and English words, or a proper name, URL or emoji; it can be code-mixed; it can contain a single Malayalam glyph in an otherwise English message. Conversely, Malayalam typed in Latin letters has no Malayalam codepoint and is excluded. The project has no verified Malayalam/Manglish language-ID model (see `Admin/FINAL_AUDIT.md` B8 and `Literature Review/LITERATURE_REVIEW_VERIFICATION.md`).

Therefore write **“Malayalam-containing”** or **“Malayalam-script subset,”** not “Malayalam-language messages” and not “perfect language identification.”

### 7.5 Why distinguish Malayalam-only from Malayalam-plus-Latin

**VERIFIED:** the spam rate is dramatically different:

| Subset | Records | Ham | Spam | Spam rate |
|---|---:|---:|---:|---:|
| Malayalam-only script | 1,489 | 1,429 | 60 | **4.0%** |
| Malayalam + Latin | 503 | 338 | 165 | **32.8%** |

Script mixing is therefore correlated with the label. A model can exploit the presence of Latin characters, digits, URLs or message length rather than learning Malayalam spam content. The metadata/structure-only diagnostic in `validation_summary.json` reaches **0.8706 Macro-F1** on the random test set without any text, and block identity alone reaches 0.8423. That is a warning, not a competing classifier.

This is why the project should:

- report the primary 1,992-row any-Malayalam result;
- describe the 1,489-row Malayalam-only subset as **descriptive only** (only 60 Spam; 11 in the test set);
- never present the script-only result as the headline without saying it is underpowered;
- avoid claiming that the model learned “Malayalam semantics” when script composition alone is predictive.

### 7.6 Why the filter matters to the research scope

Without the filter, D1 is a five-language corpus and a “Malayalam” claim would be false. With the filter, the project can make a bounded claim about **Malayalam-script-containing SMS spam** and compare classical models with a multilingual transformer. The filter supports scope discipline; it does not solve language identification, code-mixing or Manglish.

---

## 8. Duplicate and leakage control

### 8.1 Exact duplicates

**VERIFIED:** an exact duplicate is a byte-for-byte identical message after the input has been read (before the model’s whitespace cleanup). In the full D1 workbook there are **1,154 exact groups / 1,224 excess records**. In the 1,992-row Malayalam subset there are **1,905 exact groups / 87 excess records** (`duplicates.json`). D2 has **22 exact groups / 22 excess records** across 5,971 rows.

### 8.2 Near-duplicates

**VERIFIED:** near-duplicates are messages that are not identical but share a normalised key or a high-similarity template. The audit’s `norm_key` normalises Unicode, lowercases, replaces URLs and digit runs, removes/normalises punctuation and collapses whitespace, so the same promotional message with different phone numbers maps to one key.

D1 receives an additional conservative fuzzy pass:

- character `char_wb` 3–5 TF-IDF cosine ≥ 0.90, plus token Jaccard ≥ 0.60; or cosine ≥ 0.97;
- implemented with `NearestNeighbors` and union-find in `p2_duplicates.py`;
- this produced 181 extra pairs in the Malayalam subset.

D2 uses **exact + normalised only**, deliberately no fuzzy pass. The reason documented in `p2_duplicates.py` is that fuzzy matching on 5,971 short English messages risks merging generic templates; D2 is secondary. This means D2’s near-duplicate control is weaker than D1’s, and the report should say so.

### 8.3 Conflicting-label groups

**VERIFIED:** a conflict group is a duplicate/near-duplicate group whose members do not all have the same label.

- Full D1: **28 conflict groups / 58 records**.
- D1 Malayalam subset: **0 conflict groups / 0 records**.
- D2: **37 conflict groups / 76 records**, overwhelmingly `spam` vs `smishing` (for example ringtone-subscription messages); these 76 records are excluded from supervised experiments, leaving **5,895** records.

Conflicts are reported, not relabelled. Relabelling would invent ground truth. The 5,971 → 5,895 reduction is the reason the D2 headline must state both denominators.

### 8.4 Why duplicates crossing train/test inflate results

**VERIFIED reasoning:** if the same message or a near-identical template appears in both training and test, the model can memorise its surface form, a phone number or a campaign phrase. The test score then measures recall of seen templates rather than classification of new messages. This is especially severe for SMS because messages are short and spam is template-heavy.

The project prevents this by grouping related records **before** splitting and assigning every group to exactly one split. `assert_no_leakage()` checks both group-ID overlap and normalised-key overlap across train/validation/test; all six checks are zero in `split_manifest.json` and `SPLIT_INTEGRITY.md`.

### 8.5 Exact split procedure

**VERIFIED:** `p2_common.split_grouped` is a deterministic greedy group-stratified assignment:

1. Group exact, normalised and (D1) fuzzy duplicates with union-find.
2. Flag groups with conflicting labels; exclude them (D2 only in practice).
3. For each label stratum, shuffle group IDs with `numpy.default_rng(42)`.
4. Sort groups by size, largest first.
5. Assign each group to the split (train/val/test) with the largest remaining record deficit.
6. Force validation and test to be non-empty when a stratum has at least three groups.

The result is 70/15/15 by records, not necessarily exactly by groups. D1: 1,394 / 299 / 299. D2: 4,127 / 885 / 883. The split manifest stores the source hashes, exclusion counts, class counts, block composition and file SHA-256 hashes.

### 8.6 What this control prevents

- Exact copies in train and test;
- normalised copies that differ only in URLs, numbers or punctuation;
- conservative fuzzy templates in D1;
- conflicting-label near-duplicates in D2 (by exclusion);
- duplicate-group leakage through the random split.

### 8.7 What it does not prevent

- **Source-block label bias.** Different messages from the same consecutive workbook region can share campaigns, style and label composition. Grouping duplicates does not remove this. The D1 random split remains within-source and the block holdout collapses.
- **Script/language confounding.** Malayalam-only vs Malayalam+Latin has a 4.0% vs 32.8% spam rate. Grouping does not remove this.
- **Semantic paraphrase beyond the threshold.** A paraphrased campaign that falls below the cosine/Jaccard threshold is not grouped.
- **Cross-dataset overlap.** D1 and D2 share 773 normalised keys; 1,555 D1 records have a D2 twin and 831 D2 records have a D1 twin. The datasets are kept separate, so this is not a training leak in the current experiments, but it invalidates any claim that they are independent sources.
- **Label noise.** Conflicting groups are excluded, but other annotation errors may remain.

### 8.8 Duplicate leakage versus source-block label bias

This distinction is essential for the review response:

| Issue | What repeats? | How it inflates a random split | Control |
|---|---|---|---|
| Duplicate leakage | The same/near-identical message or template | Memorised exact text or campaign phrase appears in test | Group-aware split; conflicts excluded |
| Source-block label bias | A whole row-order region has a characteristic label/source composition | Training and test share campaign/style even when messages are not duplicates | Leave-one-row-block-out; external source test |

The D1 block result is **not** a duplicate-control failure. The grouped split has zero group/key overlap. The block result is a separate dataset-level confound: 94.7% of Spam is in one row block, and holding that block out leaves only 12 training Spam from a different campaign.

---

## 9. Verified experimental results

### 9.1 Dataset 1 — primary Malayalam-containing experiment

**VERIFIED:** 1,992 messages, 1,767 Ham / 225 Spam. Grouped 70/15/15 split, seed 42: 1,394 train / 299 validation / 299 test; test 265 Ham / 34 Spam. The selected D1 model is Linear SVM, char_wb TF-IDF 2–4, `min_df=2`, `sublinear_tf=True`, `max_features=300,000`, `C=0.5`, `class_weight="balanced"`, default decision boundary 0.

| Model | Accuracy | Macro-F1 [95% CI] | Ham F1 | Spam P | Spam R | Spam F1 | Confusion matrix |
|---|---:|---|---:|---:|---:|---:|---|
| Logistic Regression | 0.983278 | 0.955645 [0.9121, 0.9903] | 0.990654 | 1.0000 | 0.852941 | 0.920635 | `[[265, 0], [5, 29]]` |
| Linear SVM | **0.986622** | **0.965005 [0.9250, 0.9922]** | 0.992509 | 1.0000 | **0.882353** | 0.937500 | `[[265, 0], [4, 30]]` |
| MuRIL, 3-seed mean | 0.985507 ± 0.001931 | 0.961885 ± 0.005404 | 0.991891 ± 0.001071 | 1.0000 | 0.872549 ± 0.016981 | 0.931878 ± 0.009737 | per-seed in §3.2 |

**VERIFIED:** the random-split SVM result is 0.9650 Macro-F1, 88.24% Spam recall, zero false positives, four false negatives. The LR result is 0.9556 Macro-F1, 85.29% Spam recall, five false negatives. The confidence intervals are group-bootstrap intervals over the frozen test predictions, not new splits.

### 9.2 Dataset 1 — block-held-out results

**VERIFIED:** the block counts are 630 / 991 / 371 with 12 / 0 / 213 Spam. Pooled leave-one-row-block-out results:

| Model | Pooled accuracy | Pooled Macro-F1 | Spam precision | Spam recall | Pooled CM |
|---|---:|---:|---:|---:|---|
| Logistic Regression | 0.886546 | 0.544795 | 0.487805 | 0.088889 | `[[1746, 21], [205, 20]]` |
| Linear SVM | 0.890060 | 0.537845 | 0.607143 | 0.075556 | `[[1756, 11], [208, 17]]` |
| MuRIL (3-seed mean) | 0.886546 | **0.502777 ± 0.006232** | 0.526994 ± 0.219705 | **0.035556 ± 0.007698** | seed-level, see §3.4 |

**VERIFIED:** the MuRIL pooled block values are 0.497940 / 0.500581 / 0.509809 for seeds 42/43/44; mean 0.502777, SD 0.006232. The block-6001 fold is the decisive failure: all 213 Spam are predicted Ham in every seed, CM `[[158, 0], [213, 0]]`, accuracy 0.425876, Macro-F1 0.298677, Spam recall 0.

### 9.3 Dataset 2 — secondary English experiment

**VERIFIED original counts:** 5,971 rows = 4,844 Ham + 489 Spam + 638 Smishing. **VERIFIED experiment counts after exclusion of 37 conflict groups / 76 records:** 5,895 = 4,844 Ham + 450 Spam + 601 Smishing. Split: 4,127 train / 885 validation / 883 test; test 726 Ham / 67 Spam / 90 Smishing. The headline metrics apply to **5,895**, not 5,971.

| Model | Accuracy | Macro-F1 [95% CI] | Ham F1 | Spam P / R / F1 | Smishing P / R / F1 | Confusion matrix |
|---|---:|---|---:|---|---|---|
| Logistic Regression | **0.963760** | **0.887742 [0.8482, 0.9239]** | 0.989719 | 0.785714 / 0.820896 / 0.802920 | 0.925000 / 0.822222 / 0.870588 | `[[722, 0, 4], [10, 55, 2], [1, 15, 74]]` |
| Linear SVM | **0.963760** | 0.882503 [0.8408, 0.9196] | 0.990437 | 0.776119 / 0.776119 / 0.776119 | 0.948718 / 0.822222 / 0.880952 | `[[725, 0, 1], [12, 52, 3], [1, 15, 74]]` |

**VERIFIED:** D2 has no source/collection metadata, so its block-held-out result is **not applicable**. Its grouped random-split result is a within-corpus result, not a claim about new SMS sources. The spam/smishing boundary is noisy: 37 conflict groups / 76 records were excluded, and the remaining classes still confuse each other (LR: 15 smishing → spam, 10 spam → ham, 4 ham → smishing).

### 9.4 Figure check against the review summary

| Claim in the review request | Audit result | Status |
|---|---|---|
| D1 1,992 messages, 1,767 Ham / 225 Spam | 1,992 / 1,767 / 225 | **VERIFIED** |
| D1 LR random Macro-F1 0.9556 | 0.955645 | **VERIFIED** |
| D1 SVM random Macro-F1 0.9650 | 0.965005 | **VERIFIED** |
| MuRIL three-seed mean 0.9619 ± 0.0054 | 0.961885 ± 0.005404 | **VERIFIED** |
| D1 LR pooled block Macro-F1 0.5448 | 0.544795 | **VERIFIED** |
| D1 SVM pooled block Macro-F1 0.5378 | 0.537845 | **VERIFIED** |
| MuRIL pooled block 0.5028 ± 0.0062 | 0.502777 ± 0.006232 | **VERIFIED** |
| D2 original 5,971: 4,844 / 489 / 638 | 5,971: 4,844 / 489 / 638 | **VERIFIED** |
| D2 LR random Macro-F1 0.8877 | 0.887742 | **VERIFIED** |
| D2 SVM random Macro-F1 0.8825 | 0.882503 | **VERIFIED** |
| D2 model metrics use 5,971 | No — use 5,895 after 76 exclusions; 883 test rows | **CORRECTION** |
| D1 SVM block-6001 fold 0.3677 | Corrected value is 0.368470 | **CORRECTION** |

### 9.5 Metric provenance

- D1 and D2 results: `d1_malayalam_results.json`, `d2_results.json`; predictions: `d1_malayalam_*_test_predictions.csv`, `d2_*_test_predictions.csv`.
- MuRIL: `muril_results.json`, `muril_seed_variation.json`, `muril_random_seed*_predictions.csv`.
- Block: `validation_summary.json`, `block_cv_predictions.csv`, `block_paired_comparison.csv`.
- Intervals/paired: `confidence_intervals.json`, `confidence_intervals.csv`, `paired_model_comparison.json`, `paired_model_comparison.csv`.
- Threshold: `threshold_calibration.json`, `threshold_calibration.csv`, `threshold_calibration_splits.csv`.
- Split integrity: `split_manifest.json`, `SPLIT_INTEGRITY.md`.

---

## 10. Baseline and similar-paper reading guide

### 10.1 Evidence status of the four papers

| Paper | What was actually read | What may be cited |
|---|---|---|
| Almeida, Gómez Hidalgo & Yamakami (2011) | 2011 ACM abstract and official dataset documentation; detailed protocol/results corroborated by the authors’ expanded 2013 IJISS article (open PDF). The 2011 four-page full text itself was not retrieved. | Dataset composition, task framing, and reported 2011 baseline values, with the status stated. |
| Mahmood & Hameed (2023) | **Full text and journal PDF**, including dataset, feature extraction, classifiers, 3-fold protocol and results tables. | Methods, dataset composition and numeric results. |
| Ramanujam, Abirami & Thirumalai (2025), FSSHAP | **Abstract and publisher metadata only**; full text paywalled. | Problem, model family and abstract-level claims. No numeric result, dataset size, split protocol or leakage claim. |
| Khanuja et al. (2021), MuRIL | **Full arXiv paper**, including model, pretraining data, XTREME results and Malayalam-specific tables. | Model design, benchmark numbers and limitations. |

Do not upgrade FSSHAP to “full text verified” and do not attribute numeric findings to it. Do not describe Almeida’s full text as directly read; use “reported in the 2011 paper and detailed in the 2013 expanded article.”

### 10.2 Almeida et al. (2011) — SMS spam filtering

**Problem.** SMS traffic grew rapidly, public real SMS spam corpora were scarce, and short messages with abbreviations and idioms were expected to degrade content-based filters.

**Dataset and languages.** English only. The released UCI SMS Spam Collection has **5,574 messages: 4,827 Ham / 747 Spam**. Sources: 425 Spam from Grumbletext, 3,375 Ham from the NUS SMS Corpus, 450 Ham from Caroline Tag’s PhD thesis, and 1,002 Ham + 322 Spam from the earlier SMS Spam Corpus v0.1 Big. The paper also studies near-duplicates with 5-, 6- and 10-gram matching and argues that merging the source collections did not add substantial new near-duplicates.

**Models and methodology.** The expanded study evaluates a large set of classical classifiers, including Naive Bayes variants, Logistic Regression, Multilayer Perceptron, Linear SVM, SMO, MDL, kNN, C4.5, boosted C4.5, PART and Random Forest, with tokenizer variants `tok1`/`tok2`. It uses a **30% training / 70% test holdout** (1,674 train / 3,900 test in the 2013 description), not cross-validation. Features are token-count style; this is not a TF-IDF validation study.

**Reported findings.** Best SVM (`SVM + tok1`): **97.64% accuracy, 83.10% Spam caught, 0.18% Ham blocked, MCC 0.893**. Logistic Regression: 97.59% accuracy, 95.48% Spam caught, 2.09% Ham blocked, MCC 0.899. The best five methods exceed 97% accuracy. The authors select linear SVM as the best baseline because it catches substantial spam with very few false positives, even though LR has a slightly higher MCC.

**Limitations.** English only; a single 30/70 split; Ham and Spam come largely from different sources; template duplicates and near-duplicates exist; no smishing labels; no Malayalam; no transformer; the evaluation predates modern reproducibility norms.

**Relevance.** Establishes the UCI benchmark, the class-imbalance problem, the cost of false positives, and linear SVM as a strong short-text baseline. D2’s Ham/Spam portion is linked to the UCI collection through the Mendeley record, so this paper is a legitimate ancestor of part of D2 — not an independent Malayalam baseline.

**Difference from this project.** D1 is Malayalam-script, grouped-split and source-block audited; D2 is a separate three-class English corpus. This project does not validate TF-IDF against Almeida’s token-count setup, and does not claim to reproduce his numbers.

### 10.3 Mahmood & Hameed (2023) — smishing with URL inspection

**Problem.** Detect SMS phishing (smishing) by combining message content with URL reputation, while controlling false positives.

**Dataset and languages.** English. The paper starts from the UCI SMS Spam Collection and adds 120 smishing messages extracted from Pinterest images, producing **4,825 Ham / 867 Smishing = 5,692** messages. The 867 smishing class is built from the 747 UCI spam messages plus the 120 Pinterest messages. This is a crucial label caveat: the paper treats all UCI promotional spam as smishing. Quote the final class counts from the paper’s table rather than recomputing an initial UCI total, because the additions and exclusions are not fully reconcilable from the prose alone.

**Models and methodology.** Content features use a class-split TF-IDF variant and chi-square selection of the top 1,000 features. Classifiers are SVM (RBF), Random Forest, AdaBoost and XGBoost. A separate URL-inspection stage queries Google and VirusTotal. Evaluation is **3-fold stratified cross-validation** with accuracy, precision, detection rate (recall) and F1.

**Reported findings.** Best SVM: **98.5% accuracy, 96.9% precision, 93.1% detection rate, 95.05% F1**. The combined Google + VirusTotal URL inspection detected 156 smishing messages, versus 140 and 145 for the individual baselines (as reported in the full text).

**Limitations.** English only; the 747 UCI spam messages are relabelled as smishing, so the label does not mean “verified phishing”; the 120 Pinterest items are image-derived and small; only 3 folds; the dataset is not released; the URL stage depends on live third-party APIs; no external source test; no Malayalam; no transformer.

**Relevance.** The selected baseline paper for smishing, and a useful example of combining content with orthogonal URL signals. It motivates keeping D2’s Spam and Smishing classes separate and reporting class-specific precision/recall, not just accuracy.

**Difference from this project.** D2 uses a real three-class Mendeley corpus and a text-only primary experiment; D1 has no phishing labels at all. This project cannot use B01 as a direct numerical baseline because the label construction and language differ.

### 10.4 Ramanujam, Abirami & Thirumalai (2025) — FSSHAP

**Status.** Abstract and publisher metadata only. IEEE MultiMedia 32(1):92–103, DOI 10.1109/MMUL.2024.3508765, published online 3 December 2024. The full text is paywalled.

**Problem (abstract-verified).** Spam SMS in Dravidian languages; high-dimensional handcrafted features; need a global, interpretable feature-selection method.

**Data and languages (abstract-verified).** Three SMS datasets, including Tamil, Kannada, Telugu and Malayalam. The abstract does not give per-dataset sizes, splits or exact Malayalam counts. The paper is by the same research group associated with the D1 corpus, and the D1 record is in its reference environment, but **whether the Malayalam subset is exactly our 1,992-row extraction is not verifiable from the abstract**. Do not state that it is.

**Method (abstract-verified).** SHAP-based global feature selection over handcrafted features, with a threshold on SHAP values; Random Forest classifier; comparison against traditional feature-selection methods across “various performance metrics.”

**Findings.** The abstract says the proposed FSSHAP approach is compared with traditional feature selection and reports performance metrics, but **no numeric result appears in the abstract**. A non-peer-reviewed author post claiming >90% accuracy is not usable evidence. This audit cannot state FSSHAP’s accuracy, F1, dataset sizes or split protocol.

**Limitations (some NEEDS VERIFICATION).** Paywalled; no verified numbers or protocol; likely random/CV evaluation but not confirmed; no source-block audit in the abstract; Random Forest + handcrafted features, not a transformer; no smishing; no Manglish. Only the first, second, fifth and sixth points are safe to assert from the accessible record; the rest require full text.

**Relevance.** The closest prior line of work on Dravidian SMS spam and a direct reason not to claim dataset or task novelty. It motivates a classical-vs-transformer comparison, but this project does not claim to improve FSSHAP’s feature selection.

**Difference from this project.** This project uses frozen grouped splits, a source-block stress test and a MuRIL comparator; it does not propose a new feature-selection method and does not claim to beat FSSHAP.

### 10.5 Khanuja et al. (2021) — MuRIL

**Problem.** Build multilingual representations for Indian languages that handle native scripts and transliteration, where monolingual data and lexical overlap are limited.

**Data and model.** 16 Indian languages plus English; about **236M parameters**, **~16B tokens**, **197,285 vocabulary**; BERT-style masked language modelling plus translation language modelling on translated/transliterated pairs. The model is evaluated on XTREME cross-lingual tasks.

**Reported findings (full text).** MuRIL’s XTREME average is **68.6 vs 59.1** for mBERT; on transliterated test sets, **48.9 vs 21.1**; Malayalam PANX **75.8 vs 54.8**; Malayalam Tatoeba **26.4 vs 20.2**. XNLI does not include Malayalam in the reported table. These are benchmark results, not SMS spam results.

**Limitations.** Encoder/pretrained representation, not a ready-made SMS classifier; XTREME tasks are not spam detection; zero-shot/cross-lingual evaluation; transliterated test sets are derived, not naturally typed Manglish; no source robustness; Malayalam Tatoeba is low; no evidence about small, imbalanced SMS corpora.

**Relevance.** A principled multilingual comparator for Malayalam and transliteration. This project fine-tunes it on D1 under the same frozen split as the classical models.

**Difference from this project.** This is supervised in-language SMS classification on 1,992 rows, not zero-shot benchmark evaluation. The negative block result is a property of this dataset/protocol, not a general indictment of MuRIL.

### 10.6 Full-text versus abstract-only summary

| Claim | Almeida | Mahmood | FSSHAP | MuRIL |
|---|---|---|---|---|
| Dataset size/composition | Verified via official dataset record/2013 expanded article | Full text | Not in abstract | Full text |
| Classifier list | 2013 expanded article | Full text | Abstract says RF | Full text (model) |
| Validation protocol | 30/70 holdout in 2013 description | 3-fold CV | Not verified | XTREME benchmarks |
| Numeric results | 97.64 SVM etc. reported | Full text | **Not available** | Full text |
| Malayalam-specific result | None | None | Abstract says Malayalam included; no numbers | PANX 75.8 / Tatoeba 26.4 |
| Source-block/leakage analysis | Near-duplicate N-gram analysis | None | Not verified | None |

---

## 11. Existing research versus our research

| Aspect | Existing research | Our research |
|---|---|---|
| Research task | English SMS spam (Almeida); English smishing with URL inspection (Mahmood); Dravidian SMS spam with handcrafted features/SHAP + RF (FSSHAP); multilingual representation learning (MuRIL) | Primary: Malayalam-script SMS Ham/Spam classification. Secondary: English three-class Ham/Spam/Smishing. Plus an empirical audit of source-block/script confounding and a classical-vs-transformer comparison. |
| Language | English in Almeida and Mahmood; multiple Dravidian languages in FSSHAP; 16 Indian languages + English in MuRIL | Malayalam-containing script subset of D1 (not full language ID); English/Latin D2 kept separate. No Manglish claim. |
| Dataset | UCI SMS Spam Collection; UCI + 120 Pinterest images; three Dravidian SMS datasets; multilingual pretraining corpora | D1: 1,992 Malayalam-containing rows from the 7,717-row Dravidian corpus. D2: 5,895 rows after conflicting-label exclusion from the 5,971-row Mendeley corpus. No new data, no synthetic SMS, no merging. |
| Models | SVM/RF/boosting/classical baselines; RF + SHAP; MuRIL as a pretrained encoder | Char TF-IDF Logistic Regression and Linear SVM; fine-tuned `google/muril-base-cased`; no new architecture. |
| Evaluation strategy | Mostly random/CV or a single holdout; Almeida uses 30/70; Mahmood uses 3-fold stratified CV; FSSHAP protocol unverified | Duplicate-grouped, label-stratified 70/15/15 with a frozen test set; 2,000-replicate group bootstrap; paired group bootstrap; leave-one-row-block-out stress test; threshold sensitivity analysis. |
| Robustness analysis | Rare or absent; Almeida studies near-duplicates; Mahmood has no source holdout; FSSHAP not verified; MuRIL benchmarks are not SMS-specific | Explicit source-block audit: 94.7% of Spam in one block; pooled block Macro-F1 0.5378 (SVM) vs 0.9650 random; MuRIL 0.5028 and 3.56% Spam recall; threshold instability quantified. |
| Main contribution | New corpus/baseline (Almeida); smishing method with URL inspection (Mahmood); interpretable feature selection (FSSHAP); multilingual representation (MuRIL) | A reproducible, leakage-controlled empirical comparison and a documented **negative/limiting result** about source-block and script confounding. Not a new detector, not a new dataset, not a first Malayalam study, not state of the art. |

### 11.1 Honest contribution statement

> This project provides a reproducible, duplicate-group-aware evaluation of classical character n-gram models and a multilingual transformer for Malayalam-script SMS spam, together with a separate English three-class spam/smishing experiment. Its main contribution is methodological and empirical: it quantifies how much the headline random-split score depends on a single source block and script composition, and it documents a negative transformer result under source holdout. It does not introduce a new classification algorithm, a new dataset, or a verified Malayalam phishing detector.

### 11.2 Claims that must not be made

- “First Malayalam phishing/smishing detector.” D1 has no phishing labels; D2 is English-only.
- “The filter performs perfect language identification.” It is Unicode script detection.
- “The model generalises to unseen SMS sources.” The block holdout contradicts this.
- “MuRIL improves on the classical model.” It does not.
- “D2 is independent of UCI.” It is partly derived from UCI, and D1/D2 overlap.
- “FSSHAP reports X% accuracy.” No numeric result is verified.
- “Almeida validates TF-IDF.” The 2011/2013 work uses token-count features; this project uses TF-IDF, which is a different choice.

---

## 12. One revised objective, problem statement and research questions

### 12.1 One overall objective

> **To determine, under a leakage-controlled evaluation, how well classical character n-gram models and a multilingual transformer classify Malayalam-script SMS spam, and how much of that measured performance depends on source-block and script composition in the available corpus.**

This is one objective with two connected parts: classification performance and validity of that performance. It does not multiply into five objectives.

### 12.2 Work packages that achieve the objective

These are work packages, not separate research objectives:

| WP | Work | Output |
|---|---|---|
| WP1 | Dataset audit and scope decision | Verified D1/D2 counts, labels, languages, provenance, restrictions |
| WP2 | Duplicate grouping and split construction | Frozen group-safe 70/15/15 splits with hashes |
| WP3 | Classical model development | Char TF-IDF LR/SVM, validation-only selection, frozen test evaluation |
| WP4 | Transformer comparison | MuRIL fine-tuning, three seeds, same frozen split |
| WP5 | Robustness and uncertainty | Block holdout, bootstrap intervals, paired tests, threshold diagnosis |
| WP6 | Prototype and dissemination | Read-only Streamlit demo, audit report, presentation/paper |

### 12.3 Problem statement

> Malayalam-script SMS spam detection is under-resourced, and the available Dravidian SMS corpus has a strong row-order/source-block label confound: 94.7% of its Spam lies in one 1,000-row block. A conventional random split can therefore report high within-source scores without establishing transfer to unseen SMS sources. At the same time, it is unclear whether a multilingual transformer such as MuRIL offers a real advantage over strong character n-gram baselines on this small, imbalanced corpus. The project addresses this by evaluating both model families under one frozen, duplicate-grouped protocol and by explicitly measuring the drop under leave-one-row-block-out evaluation. It also keeps a separate English three-class experiment to examine spam/smishing separability without merging the datasets or transferring claims across languages.

### 12.4 Three research questions

**RQ1.** On a duplicate-grouped, label-stratified random split of the 1,992 Malayalam-containing messages, how do character n-gram Logistic Regression and Linear SVM compare with a fine-tuned MuRIL model on Macro-F1, Spam recall and accuracy, and does MuRIL show a reproducible advantage across three seeds?

**RQ2.** How much does performance change when an entire 1,000-row workbook block is held out, and what does that change reveal about source-block label bias and the limits of the random-split result?

**RQ3.** In the separate English three-class corpus, how separable are Ham, Spam and Smishing under the same duplicate-grouped protocol, and what does the spam/smishing confusion imply for the scope and limitations of the project?

These three questions cover the primary Malayalam comparison, the validity/robustness question, and the secondary English task. They do not claim phishing detection in Malayalam or generalisation to unseen sources.

---

## 13. Remaining research tasks in priority order

### P0 — must be resolved before submission or public deployment

- [ ] **Resolve D1 access provenance.** Produce an IEEE DataPort subscription receipt, download log, author permission, or institutional confirmation. Store it in `Admin/`. If none exists, do not publish D1-derived content; consider the D2-only fallback. Evidence: `Admin/FINAL_AUDIT.md` B1; `Admin/DATASET_AUDIT_REPORT.md` §1E.
- [ ] **Freeze one canonical results table.** Use the corrected block values: 630/991/371, SVM fold 0.368470, pooled 0.5378. Add a correction note to stale files; do not silently overwrite them. Evidence: `validation_summary.json` vs `D1_RESULTS.md`, `EVIDENCE_REGISTER.md` E74, `REVIEW_2_PROGRESS_REPORT.md` §1/§7.
- [ ] **Add MuRIL accuracy** to the results table and label it secondary. Evidence: `muril_results.json`; §3.2 above.

### P1 — required for the revised presentation and paper

- [ ] Replace the five objectives with the one objective, one problem statement and three RQs in §12.
- [ ] Rename “Random Macro-F1” to “Grouped random-split test Macro-F1” everywhere; state that MuRIL’s ± is across three seeds on one split. Evidence: §6.
- [ ] Add a one-slide explanation of leave-one-row-block-out: the 1,000-row blocks, the 630/991/371 composition, train/test procedure, pooling, and why 0.9650 falls to 0.5378. Evidence: §4.
- [ ] Replace D2 “N/A” with “Not applicable — no source/collection metadata; grouped random split only,” and remove “no source-block structure” from the app/report wording. Evidence: §5.
- [ ] State the D2 denominator correctly: 5,971 original, 5,895 after 76 conflicting-label exclusions, 883 test rows. Evidence: §9.3.
- [ ] Add the script-mix confound: 1,489 Malayalam-only (4.0% Spam) vs 503 Malayalam+Latin (32.8% Spam); do not describe the filter as language identification. Evidence: §7.
- [ ] Add the duplicate-control explanation and distinguish it from the block confound. Evidence: §8.
- [ ] Use only verified paper claims; mark FSSHAP abstract-only and Almeida partial/expanded. Evidence: §10.

### P2 — deployment and reproducibility

- [ ] Build the clean deployment tree in §2.5; exclude `Datasets/`, MuRIL, splits, prediction CSVs and reports.
- [ ] Pin Python and dependencies; run `verify_prototype.py` in a clean environment; require parity before deployment.
- [ ] Choose Streamlit Community Cloud for the course demo; document 12-hour hibernation. Use Render only if a custom domain or paid always-on instance is required; document 15-minute spin-down and 512 MB.
- [ ] Add a public-demo disclaimer: academic prototype, not a security product, no URL verification, no generalisation claim.
- [ ] Do not announce permanent uptime.

### P2 — literature and evidence quality

- [ ] Obtain the FSSHAP full text through institutional access; if unavailable, keep every numeric claim marked “not verified.”
- [ ] Obtain the 2011 Almeida full text if the paper needs exact 2011 table values; otherwise cite the 2013 expanded article for the detailed protocol and state the status.
- [ ] Update the literature verification table with the full-text MuRIL reading and the abstract-only FSSHAP status.

### P3 — research extension (not required for the current audit)

- [ ] Design a source-diverse Malayalam external test set with documented provenance, consent, double annotation, adjudication and overlap screening. Do not synthesize SMS or scrape without approval. This is the only route to a generalisation claim.
- [ ] If a source-diverse set is unavailable, keep the claim at “within-source benchmark plus source-block stress test.”
- [ ] Optional: grouped 5-fold cross-validation on D2 for split stability; label it as a stability check, not a source holdout.

### Explicitly deferred

- Do not retrain models, change labels, change splits, add datasets, merge D1/D2, deploy, or create the final PPT/paper during this audit. The next step is team review of this report.

---

## Appendix A. Evidence index

| Claim area | Primary evidence |
|---|---|
| D1 counts and labels | `Research Work/phase2/data/d1_malayalam.csv`; `Admin/DATASET_AUDIT_REPORT.md` |
| D2 counts and exclusions | `Research Work/phase2/data/d2_grouped.csv`; `split_manifest.json`; `duplicates.json` |
| Splits and leakage | `split_manifest.json`; `Research Work/phase2/reports/SPLIT_INTEGRITY.md`; `p2_common.py` (`split_grouped`, `assert_no_leakage`) |
| D1/D2 metrics | `d1_malayalam_results.json`; `d2_results.json`; prediction CSVs |
| MuRIL metrics | `muril_results.json`; `muril_seed_variation.json`; three seed prediction CSVs; `muril_artifact_verification.json` |
| Block definition and folds | `p2_validate.py` (`block_of`, `block_cv`); `validation_summary.json`; `block_cv_predictions.csv` |
| Stale block artifact | `d1_block_robustness.json`; `p2_robustness.py`; `D1_RESULTS.md` |
| Threshold diagnosis | `threshold_calibration.json`; `threshold_calibration_splits.csv`; `THRESHOLD_CALIBRATION_REPORT.md` |
| Duplicate grouping | `p2_duplicates.py`; `duplicates.json`; `d2_grouped.csv` |
| Script filter | `p2_common.py` (`MAL`); `p2_extract.py`; `inference.py`; `d1_malayalam.csv` |
| Prototype parity | `verify_prototype.py`; `verification_results.json`; `model_manifest.json` |
| Prototype failure evidence | `Research Work/prototype/logs/streamlit.log`; Windows system events; no listener on 8501 |
| Hosting limits | Streamlit docs (manage-your-app); Render docs (`/docs/free`) |
| Papers | Almeida 2011/2013; Mahmood & Hameed 2023 full text; FSSHAP abstract/metadata; MuRIL arXiv 2103.10730 |

## Appendix B. Reproducibility commands used

```bash
# Verify frozen model/split parity
.venv/Scripts/python.exe "Research Work/prototype/verify_prototype.py"

# Start the local prototype (from project root)
.venv/Scripts/python.exe -m streamlit run "Research Work/prototype/app.py" \
  --server.address 127.0.0.1 --server.port 8501 --server.headless true

# Health check
curl http://127.0.0.1:8501/_stcore/health
```

The audit recomputed metrics from saved predictions; it did not retrain any model. Running the verifier regenerated `verification_results.json` with the same PASS content; no metric, model or split changed. The only other new files created during the audit are this report and temporary local logs used to verify startup; the logs are not research artifacts.

## Appendix C. Audit limitations

- No `.git` history, so the exact nine-file diff and added/deleted line counts cannot be confirmed.
- The original app-stop cause is inferred from logs/events, not from a process supervisor trace.
- FSSHAP numeric results and protocol are unavailable (paywall).
- The 2011 Almeida four-page full text was not retrieved; detailed protocol/results rely on the authors’ 2013 expanded article and official dataset record.
- No external, source-diverse Malayalam test set exists in the project; no generalisation claim is possible.
- D1 access provenance remains unresolved.

---

*End of audit. No model, dataset, split, app or deployment artifact was changed.*

