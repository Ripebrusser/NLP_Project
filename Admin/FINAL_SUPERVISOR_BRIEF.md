# Final Supervisor Brief

**Date:** 8 November 2026  
**Purpose:** one-page decision brief. Full evidence is in `FINAL_MASTER_RESEARCH_AUDIT.md` and `CANONICAL_FINAL_RESULTS.md`.

## 1. One objective

> **To evaluate, under duplicate-group-controlled splitting and a row-order stress test, how well classical character n-gram models and a fine-tuned multilingual transformer classify Malayalam-containing SMS spam, and to conduct a separate three-class English SMS spam/smishing analysis, without claiming cross-dataset or source transfer.**

There is exactly one objective. The three research questions in `FINAL_OBJECTIVE_AND_SCOPE.md` are separate instruments, not additional objectives.

## 2. Research problem

D1 contains 1,992 Malayalam-containing SMS records (1,767 Ham / 225 Spam). Of the 225 Spam, 213 lie in one consecutive workbook block (6001–7000), and block 5001–6000 has none. A random split therefore shares the dominant Spam block between training and test. The high random-split score may reflect campaign/row-order structure rather than transferable spam cues. The project measures that dependence and compares classical models with MuRIL under the same frozen split.

## 3. Dataset scope

| Dataset | Role | Composition | Claim boundary |
|---|---|---|---|
| D1 | Primary | 1,992 Malayalam-containing: 1,767 Ham/225 Spam; 1,489 Malayalam-only; 503 Malayalam+Latin | Ham/Spam only; no phishing labels; within-corpus |
| D2 | Separate secondary | 5,971 original; 5,895 experimental after 37 conflicts/76 records; 883 test; 726/67/90 | English/Latin three-class; not external validation |

No pooling. No Manglish. No Malayalam smishing.

## 4. Models actually evaluated

- D1: Logistic Regression, Linear SVM, MuRIL seeds 42/43/44.
- D2: Logistic Regression, Linear SVM. **MuRIL was not evaluated on D2.**

## 5. Key findings

| Result | Value |
|---|---|
| D1 grouped random Macro-F1 | LR 0.9556; SVM 0.9650; MuRIL mean 0.9619 |
| D1 pooled row-block Macro-F1 | LR 0.5448; SVM 0.5378; MuRIL mean 0.5028 |
| D1 pooled Spam recall | LR 8.89%; SVM 7.56%; MuRIL 3.56% |
| SVM − LR Macro-F1 | +0.0094 [0.0000, 0.0321], one message, p = 1.0 |
| SVM − MuRIL mean Macro-F1 | +0.0031 [0.0000, 0.0101], not distinguishable |
| D1 perfect precision | SVM 30/30 [0.8843, 1.0]; LR 29/29 [0.8806, 1.0] |
| Zero FP among Ham | 0/265; exact upper FPR 1.382% |
| D2 Macro-F1 | LR 0.8877; SVM 0.8825; difference [−0.0121, 0.0244] |

**The headline is the pair:** 0.9650 random / 0.5378 row-block. Reporting only the first would misrepresent the result.

## 6. What is defensible

- A reproducible duplicate-controlled evaluation of D1.
- A quantified row-block stress test showing the random-split score is fragile.
- A negative transformer result: MuRIL does not reliably improve on SVM; two seeds are prediction-identical to SVM.
- A separate English three-class analysis with a weak Spam/Smishing boundary.
- Exact uncertainty at the perfect-precision boundary.

## 7. What is not defensible

- “First Malayalam/Dravidian spam detector.”
- “State of the art.”
- “Malayalam smishing detection.”
- “Manglish detection.”
- “Unified Malayalam–English model.”
- “Generalises to unseen sources.”
- “Validated production filter.”
- “D2 validates D1.”
- Any FSSHAP numeric result without full text.

## 8. Honest limitations

1. D1 permission is unresolved; no written access or publication permission is on file.
2. No source labels; blocks are row-order proxies.
3. Only three blocks; the critical fold has 12 training Spam.
4. No external Malayalam test set.
5. “Malayalam” means Malayalam script presence, not language identification.
6. Perfect precision is based on 29–30 positives concentrated in one block.
7. Only three MuRIL seeds; the mean interval is conditional.
8. FSSHAP is abstract-only; several secondary papers are not full text.
9. D2 is English/Latin and overlaps D1 on 773 normalised keys.
10. No production or adversarial validation.

## 9. Decisions required from the supervisor

1. **Title and framing:** approve the negative/limitation framing and a title that does not imply MuRIL was evaluated on smishing.
2. **D1 permission:** approve the author-contact letter and set a deadline. If permission is not obtained, should the thesis contain D1 as an internal case study, or should the paper pivot to D2 plus methods?
3. **FSSHAP:** is an abstract-only citation acceptable if disclosed, or must full text be obtained before submission?
4. **D2:** include as a bounded secondary section, or separate paper? It is not external validation.
5. **Raw examples:** request permission for up to three anonymised D1 excerpts, or use no D1 text at all?
6. **Venue:** is the contribution strong enough for an IEEE conference/journal, or should it target a student track/workshop where a negative evaluation study is a better fit?

## 10. Recommendation

Proceed to supervisor review. Do **not** submit until D1 permission is evidenced and the manuscript passes the claim-ledger check. The strongest honest paper is an evaluation/validity study, not a detector-success paper.
