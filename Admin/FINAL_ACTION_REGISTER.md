# Final Action Register

**Date:** 8 November 2026  
**Purpose:** every remaining problem that affects submission, with an owner and the evidence needed to close it.  
**Rule:** an action is closed only by evidence, not by a document asserting that it is closed.

| ID | Priority | Problem | Exact action | Owner | Required evidence | Status |
|---|---|---|---|---|---|---|
| A01 | **P0** | D1 access and publication permission are unevidenced. | Send the author request in `D1_PERMISSION_REQUEST_AND_CHECKLIST.md`; preserve the reply and its scope. | NLM lecturer → D1 authors; student records | Written confirmation naming the dataset, the research use, aggregate publication, any excerpt permission and any redistribution limit | **Open — external** |
| A02 | **P0** | D1 raw text, examples or screenshots could breach access terms. | Until A01: publish aggregate statistics only; remove D1 message text/screenshots from paper, slides, repository and demo. | Student | Final paper and repository checked for raw D1 strings | **Open** |
| A03 | **P0** | FSSHAP full text is unavailable, so its exact dataset use and results are unknown. | Obtain through library/IEEE Computer Society access or contact the authors. If unavailable, retain abstract-only status. | Student / library | PDF or author manuscript; otherwise a dated access log | **Open — access** |
| A04 | **P0** | The paper must contain exactly one objective. | Use `FINAL_OBJECTIVE_AND_SCOPE.md`; do not import objectives from historical files. | Student | Final manuscript has one “Objective” paragraph; research questions labelled separately | Ready to implement |
| A05 | **P1** | SVM–LR and SVM–MuRIL differences could be overclaimed. | Report differences with intervals and state “not statistically distinguishable”; never rank by 0.009 or 0.003 alone. | Student | Results and abstract match `FINAL_STATISTICAL_AUDIT.md` | Ready to implement |
| A06 | **P1** | Perfect precision could be read as deployment safety. | Report 30/30 or 29/29 with exact lower bound and 0/265 FPR upper bound 1.382%; add campaign-concentration caveat. | Student | Results section contains all three elements | Ready to implement |
| A07 | **P1** | Row blocks could be described as sources. | Use “pooled leave-one-row-block-out stress test”; never “source-held-out” or “unseen-source validation.” | Student | Terminology search of final manuscript | Ready to implement |
| A08 | **P1** | Literature statuses are incomplete for several secondary records. | Update every citation to the status in `LITERATURE_VERIFICATION_REGISTER.md`; remove numeric claims from abstract-only records. | Student | Bibliography annotations and citation audit | Partly ready |
| A09 | **P1** | FSSHAP overlap could make the novelty claim look ignorant or inflated. | Cite FSSHAP and the Elangovan series explicitly; state the evaluation-gap contribution narrowly. | Student | Related-work and contribution paragraphs | Ready to implement |
| A10 | **P1** | The title may imply MuRIL was evaluated on smishing. | Use the recommended title in `FINAL_OBJECTIVE_AND_SCOPE.md` or an equally explicit alternative. | Student + supervisor | Approved title | **Needs supervisor decision** |
| A11 | **P1** | No source-diverse Malayalam test set exists. | Do not create one. Report the limitation and position the work as within-corpus. | Student | Limitations paragraph | Cannot be closed with current data |
| A12 | **P2** | Some secondary literature is abstract/metadata only (P02, P03, P06, P09, P11, T01, T02, S01). | Obtain full texts where the argument depends on them; otherwise cite only bibliographic/abstract-level facts. | Student | PDFs or dated failed-access log | Open |
| A13 | **P2** | D2 Spam/Smishing confusion is a substantive result, not a nuisance. | Report per-class F1 and confusion matrix; do not merge classes; state that Smishing F1 0.8706 (LR) is not high-stakes detection evidence. | Student | Results and discussion | Ready to implement |
| A14 | **P2** | The paper may accidentally claim D2 validates D1. | State explicitly that D2 is separate, English/Latin, and shares 773 normalised keys with D1. | Student | Scope paragraph and limitations | Ready to implement |
| A15 | **P2** | Prototype could be described as a production filter. | Keep “academic demonstration”; no URL verification or malware claim; no D1 text exposure. | Student | README/demo labels | Ready to implement |
| A16 | **P2** | Structural/script confounds are associational. | Report structure-only 0.8706 and block-only 0.8423 as diagnostics; avoid causal language. | Student | Discussion paragraph | Ready to implement |
| A17 | **P3** | The old block artifact contains 631/370 and 0.3677. | Keep as historical but do not cite; active documents use 630/991/371 and 0.3685. | Student | Artifact banner / register | Fixed in active record |
| A18 | **P3** | Old scope and audit reports contain seven objectives and “models not trained.” | Marked historical and superseded. Do not include in submission packet. | Student | Submission file list | Fixed |
| A19 | **P3** | The paper needs a complete reference-to-citation check. | Build final bibliography from the register; ensure every entry is cited and every citation resolves. | Student | Reference audit | Not started |
| A20 | **P3** | The abstract may overstate “Malayalam” when the unit is Malayalam script. | Use “Malayalam-script-containing SMS” and disclose 503 mixed-script records. | Student | Abstract and scope | Ready to implement |

## Closing rule

A01 and A03 are the two genuine external blockers. A04–A07, A09–A11, A13–A16 and A20 are writing controls and can be closed before submission. A11 cannot be closed with the existing data and must remain an explicit limitation.
