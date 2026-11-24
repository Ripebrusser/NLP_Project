# Dataset 1 — Malayalam-Script SMS Spam (Primary)

> **HISTORICAL / SUPERSEDED.** Retained for experiment provenance. Do not cite for current numbers or claims. Current authority: `Admin/D1_RESULTS.corrected.md` and `Admin/CANONICAL_FINAL_RESULTS.md`.


> **CORRECTION NOTICE (6 Nov 2026):** Historical version preserved. Corrected block counts are **630 / 991 / 371** (not 631 / 991 / 370), corresponding Ham/Spam **618/12, 991/0, 158/213**; the block-6001 SVM fold is **0.368470** (not 0.3677), accuracy **0.4636**. Precision requires exact bounds (lower 0.8843/0.8806; zero-FP upper 1.382%). “Block-held-out” is a **leave-one-row-block-out stress test** on row-order proxies. See `Admin/D1_RESULTS.corrected.md`.

**Task:** Ham vs Spam. **No phishing claim.** D1 labels do not contain phishing.

## Data

| Item | Value |
|---|---|
| Malayalam-containing records | **1,992** |
| Labels | Ham 1,767 / Spam 225 (11.3% Spam) |
| Malayalam + Latin | 503 |
| Malayalam-only script | 1,489 (60 Spam) |
| Other Indic script co-occurring | **0** |
| Excluded | 0 (no empty messages, no invalid labels in this subset) |
| Duplicate groups | 1824 (168 duplicate excess removed from the split count, records retained) |
| Label conflicts | 0 |

The earlier “1,992 vs script totals” discrepancy is resolved: inclusive “contains” counts overlap (a message can contain Malayalam and Latin), while exclusive buckets sum to 7,717. The 1,992 Malayalam records split into 1,489 Malayalam-only and 503 Malayalam+Latin; none contain Tamil, Telugu or Kannada.

## Split

70/15/15 grouped and stratified, seed 42: train **1,394** (Spam 157), validation **299** (Spam 34), test **299** (Spam 34). Group/normalised-text overlap across splits is zero. Hashes: `phase2/splits/split_manifest.json`.

## Test results

Model selection used **validation macro-F1 only**; the test set was evaluated once after selection. Both final models were refit on train+validation.

| model | features | C | accuracy | macro-F1 | Spam P | Spam R | Spam F1 | ROC-AUC |
|---|---|---|---|---|---|---|---|---|
| linear_svm | char_2_4 | 0.5 | 0.9866 | 0.9650 | 1.0000 | 0.8824 | 0.9375 | 0.9765 |
| logreg | char_2_4 | 1.0 | 0.9833 | 0.9556 | 1.0000 | 0.8529 | 0.9206 | 0.9786 |

**Selected model:** linear_svm with `['Ham', 'Spam']`. Confusion matrix (rows = true, columns = predicted):

| true \ pred | Ham | Spam |
|---|---|---|
| Ham | 265 | 0 |
| Spam | 4 | 30 |

- Accuracy 98.66% (95% Wilson CI 96.61%–99.48%).
- Macro-F1 0.9650.
- Spam recall 88.24% (95% CI 73.38%–95.33%); observed precision 30/30 = 100%, exact 95% lower bound **88.43%**; zero FP among 265 Ham, exact 95% FPR upper bound **1.382%**.
- Errors: **4 of 299**, all false negatives. No Ham was flagged as Spam.

### Malayalam-only subgroup (descriptive)

Test rows with no Latin characters: **221** (Spam 11). Spam recall 81.82%, macro-F1 0.9476. This is a subgroup of the same model, not a separately trained model.

## Source-block robustness — the main caveat

The random split is **group-safe but not block-safe**. Malayalam rows occupy three populated 1,000-row workbook blocks, and the blocks have radically different label mixes. Leave-one-block-out results for the same selected pipeline:

| held-out block | test rows | Ham/Spam | train rows | train Spam | accuracy | macro-F1 | Spam recall | note |
|---|---|---|---|---|---|---|---|---|
| 4001-5000 | 630 | 618/12 | 1362 | 213 | 0.9857 | 0.6964 | 0.2500 |  |
| 5001-6000 | 991 | 991/0 | 1001 | 225 | 0.9889 | 0.4972 | — | test block contains no Spam |
| 6001-7000 | 371 | 158/213 | 1621 | 12 | 0.4636 | 0.3685 | 0.0657 | train blocks contain almost no Spam |

**Interpretation.** Random-split macro-F1 is 0.9650, but pooled leave-one-row-block-out macro-F1 falls to 0.6964 and 0.3685; the middle block cannot evaluate Spam at all. The high random-split score therefore measures **within-source/template performance**, not generalization to unseen message sources. This is a property of the dataset (spam is concentrated in one block), not a fixable tuning issue. Any headline must report the random-split score together with this result. A block-aware or external test set is required before claiming field performance.

## Error examples (all four)

| record | Excel row | margin | message (truncated) |
|---|---|---|---|
| D1-04452 | 4455 | 1.9228 | കേരളിയ തനിമ തൊട്ടുണര്‍ത്തുന്ന., മലയാളികളുടെ ഹൃദയത്തെ പൂക്കളം കൊണ്ട് തീര്‍ക്കുന്ന.,നാവില്‍ രുചിയേറിയ വിഭവങ്ങളുമായി ഈ പോന്നോണത്തെ വരവേല്കാം...എന്റെ ഹൃദയം നിറഞ്ഞ ഓ |
| D1-04453 | 4456 | 1.9184 | വീണ്ടുമൊരു പൊന്നോണം വരവായിപൂക്കളവും ഓണച്ചന്തയും വള്ളംകളിയുംകേരളക്കരയില്‍ അങ്ങോളമിങ്ങോളംമാവേലി നാടു വാണിടും കാലംമാനുഷരെല്ലാരും ഒന്നുപോലെആ കാലത്തിന്റെ ഓര്‍ത്തുകൊണ |
| D1-06180 | 6183 | 1.4927 | മദ്യപിച്ച് വാഹനമോടിക്കരുത്. മോർത്ത് |
| D1-06194 | 6197 | 1.1367 | * പ്രാർത്ഥന - മധുര !! |

The first two are Onam greeting/spam messages from block 4001–5000 (a low-spam block); the last two are short one-line messages from block 6001–7000.

## Reproduction

```
./.venv/Scripts/python.exe "Research Work/phase2/p2_extract.py"
./.venv/Scripts/python.exe "Research Work/phase2/p2_duplicates.py"
./.venv/Scripts/python.exe "Research Work/phase2/p2_split.py"
./.venv/Scripts/python.exe "Research Work/phase2/p2_train_d1.py"
./.venv/Scripts/python.exe "Research Work/phase2/p2_robustness.py"
```
