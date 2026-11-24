# Model Training Readiness Checklist

**Status: classical baselines complete; formal sign-off still blocked by D1 access provenance.** See `Admin/FINAL_AUDIT.md`.  
Trained: TF-IDF + Logistic Regression / Linear SVM on D1 and D2. Transformers not started.

---

## 1. Approved task and data

| Item | Decision | Status |
|---|---|---|
| Project title | *Classical and Multilingual Transformer Models for SMS Spam and Smishing Detection in Malayalam-Script and English Text* | **Adopted** (Phase 2 direction) |
| Dataset 1 | `Datasets/Spam Message Collection.xlsx` — Dravidian SMS, Ham/Spam | Audited; **blocked on access provenance** |
| Dataset 2 | `Datasets/Dataset_5971.csv` — English SMS, ham/spam/smishing | Audited |
| Task T1 | D1 Malayalam subset, Ham vs Spam (1,992; 225 spam) | **Baselines done** |
| Task T2 | D2 three-class (5,971; 4,844/489/638) | **Baselines done** |
| Task T1b | D1 Malayalam-only script (1,489; 60 spam) | Descriptive only |
| Task T2b | D2 binary ham vs smishing (5,482) | Secondary |
| Task T4 | Cross-dataset probe | Exploratory |
| Combined training | **Prohibited** | Decided |
| Manglish | **Out of scope** | Decided |

## 2. Final label mapping

| Dataset | Raw | Model label | Handling |
|---|---|---|---|
| D1 | `Ham` | 0 | Keep |
| D1 | `Spam` | 1 | Keep |
| D1 | `Spa,` | — | **Exclude** (1 record; not relabelled) |
| D1 | empty message | — | **Exclude** (2 records) |
| D2 | `ham` | 0 | Keep |
| D2 | `spam` | 1 | Keep |
| D2 | `smishing` | 2 | Keep (never merged with spam) |
| D2 | `Smishing`/`Spam` capitalised | mapped to 2/1 | Analysis-only normalisation; file unchanged |

Usable totals: **D1 7,714 (6,320 Ham / 1,394 Spam)**; **D2 5,971 (4,844 / 489 / 638)**.

## 3. Final feature set

| Experiment | Features | Notes |
|---|---|---|
| Baseline 0 | Majority class | Reports the trivial floor |
| Baseline 1 | TF-IDF word (1–2 grams) + char_wb (3–5 grams), `min_df=2`, `sublinear_tf=True` | **Fit on training folds only** |
| Model A | Linear SVM (`LinearSVC`, class_weight balanced) | Classical baseline |
| Model B | Logistic Regression (class_weight balanced) | Second classical baseline |
| Model C | MuRIL fine-tuned | Primary transformer |
| Model D | XLM-R fine-tuned | Fallback if MuRIL unavailable/unsuitable |
| Ablation | + URL/EMAIL/PHONE flags (D2 only) | Secondary; reported as shortcut test |

No TF-IDF, vocabulary, scaler or feature selector may be fitted on validation or test data.

## 4. Preprocessing plan

1. Read original files read-only; write derived copies only.
2. Unicode NFKC normalisation; preserve Malayalam/Tamil/Telugu/Kannada characters.
3. Replace URLs, e-mail addresses, phone numbers and long digit runs with typed placeholders (`<url>`, `<email>`, `<phone>`, `<num>`).
4. Lowercase **Latin characters only**; do not alter Indic script case (none) or vowel signs.
5. Collapse whitespace; strip zero-width characters (1,230 in D1) and NBSP (57).
6. **Do not** remove stopwords (no verified Malayalam stopword list; removal would damage short SMS).
7. **Do not** stem/lemmatise Malayalam (no verified stemmer).
8. **Do not** transliterate or translate.
9. Record counts affected by every step in a preprocessing log.

## 5. Duplicate handling

- Exact and near-duplicate groups are computed before splitting and kept intact.
- Duplicates are **retained** in the data; no record is silently deleted.
- Conflicts (28 D1 / 37 D2 groups) are retained and reported.
- The split assertion (no group in two splits) must pass before training.

## 6. Language identification limitations

- Only Unicode **script** detection is used (Malayalam, Tamil, Telugu, Kannada, Latin, other).
- Script ≠ language; no language labels are claimed.
- Manglish screen is a 100-word heuristic yielding 34 records — **not** used as a label.
- No verified Malayalam/Manglish language-ID tool was found; this is a documented limitation.

## 7. Train / validation / test strategy

| Item | Value |
|---|---|
| Split | 70 / 15 / 15, grouped by exact + normalised + fuzzy duplicate clusters |
| Stratification | class only (D1 Malayalam and D2); class × script for the descriptive all-D1 view |
| Seed | 42 |
| Test handling | written once, hashed, evaluated once after validation-only selection |
| Cross-validation | Optional 5-fold grouped CV on train+val for model selection; test untouched |
| Class imbalance | class weights only; **no SMOTE/augmentation** |
| Minimum support | per-class results require ≥30 test examples |

Executed sizes: D1 Malayalam 1,394 / 299 / 299 (Spam 157/34/34); D2 4,127 / 885 / 883. Hashes: `Research Work/phase2/splits/split_manifest.json`.

## 8. Model candidates and compute

| Model | Params | Feasibility |
|---|---|---|
| Majority baseline | 0 | Certain |
| TF-IDF + LinearSVC | — | Certain (CPU) |
| TF-IDF + LogisticRegression | — | Certain (CPU) |
| MuRIL base | ~236M | Requires GPU for practical fine-tuning |
| XLM-R base | ~278M | Requires GPU |

**Compute status: verified.** NVIDIA GeForce RTX 4050 Laptop GPU with **6,141 MiB** VRAM (`nvidia-smi`, 5 Nov 2026). MuRIL/XLM-R base fine-tuning is feasible with batch size 8, max sequence length 128 and gradient accumulation; 6 GB is tight, so mixed precision and gradient checkpointing should be enabled and OOM must be handled explicitly. Full fine-tuning at batch 16 / max_len 256 is **not** safe on this GPU.

## 9. Evaluation metrics

- **Primary:** macro-F1.
- **Secondary:** per-class precision, recall, F1; confusion matrix; MCC; balanced accuracy.
- **Supplementary:** accuracy.
- **Uncertainty:** bootstrap 95% CI over duplicate groups (1,000 resamples).
- **Reporting:** support counts beside every metric; no metric without its support.
- **Error analysis:** 50 errors per class, stratified; script, length, URL presence.

## 10. Reproducibility requirements

| Requirement | Implementation |
|---|---|
| Fixed seeds | Python `random`, NumPy, framework seeds all set to 42 (plus 3-seed runs) |
| Deterministic splits | Split files generated once and hashed |
| Environment capture | `py -m pip freeze` written to `Research Work/env_freeze.txt` |
| Code versioning | Scripts committed with the split manifest |
| No manual edits | Derived data generated only by scripts |
| Logging | Every run writes config, seed, split hash, metrics, confusion matrix |
| Original data | Read-only; SHA-256 recorded in the audit report |

## 11. Go / no-go gates

| Gate | Requirement | Current |
|---|---|---|
| G1 | Scope and title approved (A or B) | ✅ Scope A adopted |
| G2 | D1 access authorisation documented (licence permits research use; receipt/permission missing) | ❌ Unresolved |
| G3 | D1 provenance confirmed by the team | ❌ Unresolved |
| G4 | Split script executed and manifest hashed | ✅ Executed |
| G5 | Preprocessing log produced | ✅ `phase2/p2_extract.py` + counts |
| G6 | Compute confirmed | ✅ RTX 4050 Laptop, 6,141 MiB |
| G7 | Baselines reproduce trivial floor | ✅ Both baselines exceed majority floor |
| G8 | Test set sealed | ✅ Created, hashed, evaluated once |

**6 of 8 gates pass. G2/G3 remain open; training proceeded at project direction with that caveat. Formal sign-off requires both.**

## 12. Known limitations to carry into the report

1. No Malayalam or Manglish phishing ground truth; no phishing claim is possible.
2. D1 is a five-language corpus, not Malayalam-English.
3. Malayalam-only-script spam support is 60 records (9 in test).
4. D1 source blocks make absolute scores optimistic.
5. D2 spam/smishing boundary is noisy (37 conflicting groups).
6. D2 ham/spam derives from UCI; near-ceiling results are expected.
7. Metadata flags are text-derivable shortcuts; text-only is primary.
8. No timestamps, sender IDs or URL content; temporal/sender/URL-behaviour leakage cannot be assessed.
9. Script is not language; no language-level claims.
10. Absolute performance will not transfer to real Malayalam SMS traffic without an external, independently collected test set — which this project is not permitted to create.
11. **D1 random-split scores are optimistic.** Leave-one-block-out macro-F1 is 0.6964 and 0.3677; Spam is concentrated in block 6001–7000. Report the block result beside every D1 headline.
12. **D1 access provenance is undocumented.** Research use is permitted by the platform terms, but no subscription receipt or author permission exists; no reuse permission is claimed.
