# Final Claim–Evidence Ledger

**Date:** 8 November 2026  
**Rule:** if a claim is not supported at the stated strength, use the permitted wording or omit it.

| # | Proposed claim | Evidence | Limitation | Permitted wording | Prohibited wording |
|---|---|---|---|---|---|
| C01 | D1 contains 1,992 Malayalam-containing SMS: 1,767 Ham / 225 Spam. | `d1_malayalam.csv`; `subset_audit.json`; frozen manifest | “Malayalam-containing” is Unicode-script detection, not language ID | “1,992 messages containing Malayalam script (1,767 Ham/225 Spam)” | “1,992 Malayalam messages” without the script qualification |
| C02 | 1,489 records are Malayalam-only script and 503 also contain Latin. | `subset_audit.json`; script flags | Script mix is not language mix | “1,489 Malayalam-only-script; 503 Malayalam+Latin” | “503 Manglish messages” |
| C03 | D1 has no phishing or smishing labels. | D1 official record and label audit | None material | “D1 is binary Ham/Spam and contains no phishing labels” | “D1 smishing corpus” |
| C04 | D2 has 5,971 original records and 5,895 experimental records. | Mendeley record; `Dataset_5971.csv`; `d2_grouped.csv` | 37 groups/76 records excluded for label conflict | “5,971 original; 5,895 after excluding 37 conflicting groups (76 records)” | Using 5,971 as the modelling denominator |
| C05 | D2 test has 883 records: 726 Ham/67 Spam/90 Smishing. | `d2_test.csv`; verifier | One frozen split | “883-record test set” | “external test set” |
| C06 | The grouped random D1 test is 299 records (265/34). | Frozen split; five prediction files | Small Spam support | “299-record within-corpus test set” | “held-out source test” |
| C07 | LR D1 Macro-F1 is 0.9556; SVM 0.9650; MuRIL mean 0.9619. | Frozen predictions; independent verification | Random split shares row structure | “Within the grouped random test” | “Overall Malayalam spam performance” |
| C08 | SVM−LR Macro-F1 is +0.0094 [0, 0.0321]. | `final_audit_stats.json`; one discordant message; exact p=1.0 | One message; interval includes 0 | “SVM is 0.0094 higher, but the models are not statistically distinguishable” | “SVM outperforms LR” / “significant improvement” |
| C09 | SVM−MuRIL mean Macro-F1 is +0.0031 [0, 0.0101]. | Frozen paired bootstrap | Seeds 42/44 identical to SVM; only one distinct seed contrast | “No evidence of a MuRIL advantage” | “MuRIL is worse than SVM” as a population claim |
| C10 | SVM Spam precision is 30/30; LR 29/29. | Confusion matrices | Conditional on predicted positives; campaign concentration | “Observed precision 1.00 (30/30), exact 95% lower bound 0.8843” | “100% precision” without qualification |
| C11 | Zero false positives among 265 Ham. | Confusion matrices; exact binomial | 265 Ham; dependence; one campaign | “0/265; exact 95% upper FPR bound 1.382%” | “Zero false-positive rate” / “safe in deployment” |
| C12 | Pooled row-block Macro-F1 is 0.5378 SVM, 0.5448 LR, 0.5028 MuRIL mean. | Frozen block predictions; pooled calculation | Three row-order proxies; one block has no Spam; critical train fold has 12 Spam | “In a pooled leave-one-row-block-out stress test” | “On unseen sources” / “field performance” |
| C13 | Pooled Spam recall is 7.56% SVM, 8.89% LR, 3.56% MuRIL. | Frozen block predictions | Same three-block limitation | “Spam recall collapses under row-block holdout” | “The model cannot detect spam in general” |
| C14 | D2 LR Macro-F1 is 0.8877; SVM 0.8825. | Frozen D2 predictions | English/Latin only; not D1 validation | “In the separate English/Latin D2 experiment” | “D2 validates the Malayalam result” |
| C15 | D2 LR−SVM Macro-F1 is +0.0052 [−0.0121, 0.0244]. | Paired bootstrap | Interval includes zero | “A weak point-estimate preference, not a significant difference” | “LR is superior” |
| C16 | Structure-only features reach 0.8706 Macro-F1; block identity alone 0.8423. | Saved `validation_summary.json`; arithmetic checked from confusion matrices | Diagnostic fit on frozen train; not independent refit | “Diagnostics show measurable metadata/row-order association” | “Structure causes the performance” / “competing classifier” |
| C17 | D1 Spam is concentrated in block 6001–7000 (213/225; 94.7%). | `source_row` recomputation | Blocks are row-order proxies, not sources | “Spam is concentrated in one workbook block” | “All spam comes from one collection source” |
| C18 | Script composition is associated with label: Malayalam-only 60/1,489 Spam (4.0%) vs mixed 165/503 (32.8%). | `d1_malayalam.csv` | Association, not causation; Latin presence may proxy campaign | “Substantial association; a possible shortcut” | “Latin characters cause spam” |
| C19 | MuRIL was designed for Indian languages and transliteration. | Khanuja et al. (2021) full text | Not an SMS spam study | “MuRIL is a multilingual encoder evaluated on XTREME tasks” | “MuRIL is proven for SMS spam” |
| C20 | FSSHAP studies Dravidian SMS spam with SHAP feature selection. | IEEE/ACM abstract and metadata | Full text paywalled; exact D1 subset unconfirmed | “The abstract describes SHAP-based feature selection and a Random Forest” | “FSSHAP reports X%” / “FSSHAP used this exact subset” |
| C21 | Mahmood and Hameed report 98.5% accuracy, 96.9% precision, 93.1% detection, 95.05% F1. | Full-text PDF | English, UCI+Pinterest construction, URL inspection, not comparable to D1 | “Reported on its own English corpus” | “Outperforms our model” / “comparable baseline” |
| C22 | The contribution is an evaluation/validity study. | Frozen experiments and row-block result | No new dataset/algorithm | “A reproducible duplicate-controlled evaluation with a row-order stress test” | “First Malayalam spam detector” / “state of the art” |
| C23 | D1 access is subscription-gated and permission is unresolved. | Dataset page; no accession evidence | Written permission pending | “Access is subscription-gated; our permission is pending” | “Licence resolved” / “permission granted” |
| C24 | The prototype reproduces 299/299 and 883/883 predictions. | `verify_prototype.py` PASS | Demonstration only | “The prototype reproduces the frozen predictions” | “Validated production system” |

## Mandatory abstract sentences

The abstract must contain, in substance:

1. “Malayalam-containing” or “Malayalam-script-containing,” not an unqualified language claim.
2. The D1 random-split score **and** the row-block score.
3. The statement that MuRIL did not show a statistically reliable advantage.
4. The separate English-only status of D2.
5. No phishing, Manglish, deployment, or external-validation claim.
