# Classical versus Transformer — D1 Malayalam Ham vs Spam

> **HISTORICAL / SUPERSEDED.** Retained for experiment provenance. Do not cite for current numbers or claims. Current authority: `Admin/MODEL_COMPARISON.corrected.md` and `Admin/CANONICAL_FINAL_RESULTS.md`.


> **CORRECTION NOTICE (6 Nov 2026):** Historical version preserved. Read “Random Macro-F1” as **grouped random-split test Macro-F1** and “block-held-out” as **pooled leave-one-row-block-out stress-test Macro-F1**. Blocks are row-order proxies, not verified collection sources. MuRIL is not shown to improve: SVM−mean(MuRIL) Macro-F1 = +0.0031 [0.0000, 0.0101]. See `Admin/MODEL_COMPARISON.corrected.md`.

**Phase 2.2, Part D.** All values are actual saved results from the frozen split and the same leave-one-block-out protocol. No model was retrained for this table and no value is estimated.

## 1. Headline comparison

| Model | Random-split Macro-F1 | Spam Recall | Block-held-out Macro-F1 |
|---|---|---|---|
| Logistic Regression | 0.9556 | 0.8529 | 0.5448 |
| Linear SVM | **0.9650** | **0.8824** | **0.5378** |
| MuRIL | 0.9619 ± 0.0054 | 0.8725 ± 0.0170 | 0.5028 ± 0.0062 |

- Classical values: single selected configuration, refit on train+validation, evaluated once on test.
- MuRIL values: mean ± standard deviation over seeds 42, 43 and 44, each early-stopped on validation macro-F1 and evaluated once on test.
- Block-held-out Macro-F1 is the **pooled** leave-one-block-out result (all 1,992 rows), not an average of fold scores. The 5001–6000 fold contains no Spam and is included only through its Ham predictions.

Supporting metrics:

| Model | Random Accuracy | Random Spam P | Random Spam F1 | Block Accuracy | Block Spam P | Block Spam R |
|---|---|---|---|---|---|---|
| Logistic Regression | 0.9833 | 1.0000 | 0.9206 | 0.8865 | 0.488 | 0.0889 |
| Linear SVM | 0.9866 | 1.0000 | 0.9375 | 0.8901 | 0.607 | 0.0756 |
| MuRIL (mean) | 0.9855 | 1.0000 | 0.9319 | 0.8865 | 0.527 | 0.0356 |

## 2. Is the difference meaningful?

**No. MuRIL does not provide a meaningful improvement over the classical baselines, and under source holdout it is worse.**

**Random grouped split.** MuRIL's mean macro-F1 is 0.0031 **below** the SVM and 0.0063 above logistic regression. Its three seed values are 0.9650, 0.9556 and 0.9650 — the entire seed range straddles the two classical results. Two seeds reproduce the SVM's exact confusion matrix `[[265, 0], [4, 30]]`; the third reproduces logistic regression's five errors. All three have zero false positives. There is no consistent, let alone meaningful, advantage.

**Block-held-out.** MuRIL's pooled macro-F1 is 0.0350 below the SVM (0.5028 vs 0.5378) and 0.0420 below logistic regression (0.5028 vs 0.5448). Its pooled Spam recall is **3.56%**, less than half the SVM's 7.56% and well below logistic regression's 8.89%. With 225 Spam across the pooled folds, that is roughly 8 detected messages instead of 17–20.

**Fold decomposition explains the pooled gap:**

| Fold | Logistic Regression | Linear SVM | MuRIL (mean of 3 seeds) |
|---|---|---|---|
| 4001–5000 (12 Spam) | 0.6964 | 0.6964 | **0.8306** |
| 5001–6000 (0 Spam) | 0.4946* | 0.4972* | 0.4987* |
| 6001–7000 (213 Spam) | **0.3825** | 0.3685 | 0.2987 |

\* Artefact of an absent class; not a balanced score.

MuRIL is clearly **better on the small 4001 fold** (0.831 vs 0.696; Spam recall 58–83% vs 25%). It is indistinguishable on the degenerate 5001 fold. It is **worse on the decisive 6001 fold**, where 213 of the 225 Spam live: it predicts Ham for every single Spam message in all three seeds. That single fold dominates the pooled score and reverses the apparent advantage.

This is the same structural failure the classical models show, expressed more sharply. With only 12 Spam examples in training for that fold, a 237M-parameter transformer collapses to the majority class more completely than a class-weighted linear model. The fold is underpowered for any model; it is not evidence that transformers are intrinsically worse at Malayalam spam, and it is not something more capacity can fix.

## 3. What the comparison does and does not establish

**Established:**

- On messages drawn from the same collection batches, MuRIL and char-TF-IDF linear models perform equivalently at roughly 0.96 macro-F1.
- Under the only source-aware protocol this corpus permits, MuRIL does **not** improve cross-source Spam detection and in fact detects fewer Spam messages.
- The random-split score is not a generalisation estimate for either model family. The transformer reproduces the batch confound rather than removing it.

**Not established:**

- That MuRIL is worse than classical models in general. One corpus, three blocks and 12 training Spam in the critical fold cannot support that claim.
- That MuRIL is better within-source. The 0.0031 gap is smaller than seed variation and rests on four versus five errors out of 299.
- Any real-world Malayalam SMS performance. No external, source-diverse test set was used.

**Do not** select MuRIL on the random split, and do not report its 0.9619 without the 0.5028. The honest headline is the pair.

## 4. Recommendation

1. Keep the **linear SVM as the within-source baseline of record** (0.9650 / 0.8824) until a source-diverse corpus exists.
2. Report MuRIL as a **negative replication of the transformer advantage** on this corpus, with the 4001-fold win and 6001-fold collapse shown side by side.
3. Do not tune on block 6001, merge Spam with Ham, or drop the fold to improve the pooled number.
4. Treat the 4001 result as a hypothesis worth testing externally: MuRIL may help when some Spam from the target source is available, but this corpus cannot confirm it.
5. Resolve D1 access provenance before any publication claim.

## 5. Future work — external validation (Part E)

No external dataset was downloaded, collected or used in this phase. The following describes what a valid external test set would require; it is a design specification, not a completed experiment.

### 5.1 Independence and provenance

- Messages must be **independently collected** for evaluation, not drawn from the same workbook, export, operator dump or collection campaign as D1. A different sending period, region, operator and collection method are the point of the exercise.
- Record **provenance per message**: collection date, source type (personal inbox, operator corpus, public report), region, operator, and the consent or licence under which it was obtained.
- Obtain ethics/IRB approval where human participants or private messages are involved; document consent, anonymisation and retention. Do not ingest personal data without a lawful basis.
- Keep the external set **frozen and access-controlled**; publish only aggregate metrics and vetted, redacted examples.

### 5.2 Label quality

- Use a written **label codebook** that separates ordinary Ham, promotional Spam, transactional/OTP messages, and fraudulent Smishing/phishing. D1 has no phishing labels, so a binary Ham/Spam mapping must be defined explicitly and applied consistently.
- **Double-annotate** every item with Malayalam-literate annotators, measure agreement (e.g. Cohen's κ) and adjudicate disagreements. Report per-class and per-source agreement, not just a single overall figure.
- Audit near-duplicate campaigns and bulk-sent templates. The block-4001 case in this corpus shows the same campaign can carry both labels; external data must resolve that before it is used as ground truth.
- Preserve the original label and the adjudicated label so disagreements remain auditable.

### 5.3 Malayalam-language verification

- Confirm each message is actually Malayalam (or Malayalam–English code-mixed) and record the script mix. Do not accept a language identifier's output without human verification.
- Decide explicitly whether romanised Malayalam (Manglish) is in scope; if it is, report it as a separate stratum because its surface form is very different.
- Verify that normalisation preserves Malayalam Unicode and does not apply English-only lowercasing, stop-word removal or stemming.
- Include a human fluency check on a sample; machine translation is not a substitute for a Malayalam speaker's judgement.

### 5.4 No overlap with existing data

- Before evaluation, screen candidate messages against D1 and D2 using exact hashes, normalised text, duplicate-group keys, character n-gram near-duplicate search and shared URL/sender indicators.
- Exclude any message that is a duplicate, near-duplicate, template variant or forwarded copy of a training/evaluation item. Report how many candidates were removed and why.
- Check campaign-level overlap, not only message-level overlap: a new Onam greeting with a changed phone number is still the same campaign.

### 5.5 Evaluation design

- **Pre-register** the model, threshold and metrics before opening the external set; evaluate once.
- Report results **stratified by source**, with source-clustered confidence intervals, not a single pooled number that hides between-source variance.
- Report Ham/Spam prevalence in the external set. A corpus with 1% Spam cannot be compared naively with one at 11%.
- Include the block-held-out and random-split results alongside the external result so readers can see how much of the original score was batch-driven.
- Target enough independent sources and Spam messages for a stable estimate. Three blocks and 225 Spam, as here, cannot support a generalisation claim regardless of the model.

Until such a set exists, the defensible claim is about **method behaviour on this corpus**, not about Malayalam SMS spam detection in the field.

---

*Sources: `metrics/validation_summary.json`, `metrics/confidence_intervals.json`, `metrics/muril_results.json`, `reports/muril_tables.md`. No model was retrained for this comparison.*
