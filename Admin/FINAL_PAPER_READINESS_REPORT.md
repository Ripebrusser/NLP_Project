# Final Paper Readiness Report

**Date:** 8 November 2026  
**Verdict:** **NOT READY FOR FINAL IEEE SUBMISSION.**  
**Ready for:** supervisor review of the design, results and scope, with two external blockers declared.

---

## 1. Readiness by component

| Component | Status | Reason |
|---|---|---|
| Frozen experiments | **PASS** | Predictions, splits, hashes and metrics reproduce |
| Statistical reporting | **PASS with caveats** | LR–SVM direction corrected; exact intervals and seed limitations documented |
| One objective | **PASS** | Authoritative objective established; historical seven-objective file superseded |
| Literature review | **PARTIAL** | Core papers full-text verified; FSSHAP and several secondary records abstract/metadata only |
| Research gap | **PASS, narrow** | Evaluation/validity gap is defensible; first-detector claims removed |
| D1 provenance | **FAIL / BLOCKER** | No access or publication permission evidence |
| D2 provenance | **PASS with ethics caveat** | CC BY 4.0, but raw SMS privacy review still needed |
| Claims discipline | **PASS** | Claim ledger written; unsupported phishing/Manglish/external claims prohibited |
| Reproducibility package | **PARTIAL** | Scripts and hashes exist; final public code/data-release decision not made |
| Paper draft | **NOT ASSESSED** | No final manuscript was supplied in this audit |

## 2. Submission blockers

### B1 — D1 permission (critical)

The paper cannot be submitted while D1 access and aggregate-publication permission are unevidenced. The dataset is subscription-gated and displays no dataset-specific licence. A plan for the lecturer to contact the author is not permission.

**Close by:** written confirmation covering access, research use and aggregate publication. If it does not arrive, do not submit a D1 results paper.

### B2 — FSSHAP full text (high)

FSSHAP is the closest paper. The current record is abstract/metadata only. The paper can still be written, but it must not assert FSSHAP’s exact dataset subset, numerical results, split protocol or absence of duplicate/row-order analysis.

**Close by:** library access or author manuscript. If unavailable, retain the limitation explicitly.

### B3 — No external Malayalam validation (critical limitation, not closable)

There is no source-diverse Malayalam test set. The row-block stress test is the only available robustness check. This cannot be fixed by more analysis of the same frozen data.

**Close by:** reframing the paper as a within-corpus evaluation. Do not promise source generalisation.

## 3. Reviewer rejection risks

| Risk | Likelihood | Why a reviewer will object | Mitigation |
|---|---|---|---|
| “This is just D1 again; FSSHAP already covers Dravidian SMS spam.” | High | FSSHAP and the Elangovan series exist | Cite them explicitly; frame the contribution as duplicate-controlled evaluation + row-block stress + MuRIL comparison, not a new detector |
| “Your split is random, so your high score is not generalisation.” | High | 94.7% of Spam in one block | Lead with the random/block pair; never report 0.9650 alone |
| “Your block test is not a source test.” | High | Blocks are workbook rows | Use “row-order proxy” and “stress test”; do not call it source-held-out |
| “Perfect precision is meaningless at n=30.” | High | 29–30 predicted positives; one campaign | Report exact lower bound and FPR upper bound; call it fragile |
| “MuRIL was not actually better, so why include it?” | Medium | No significant difference | The negative result is the point: no transformer advantage on this corpus |
| “D2 is not independent and is English-only.” | High | 773 overlapping keys; different labels | State this before the reviewer does; do not call it external validation |
| “You claim Malayalam but measured script.” | High | Unicode detection is not language ID; 503 mixed | Use “Malayalam-script-containing”; disclose mixed script |
| “Your literature review relies on abstracts.” | Medium | FSSHAP and several 2026 records | Mark verification levels; remove numbers from unread sources |
| “No code/data availability statement.” | Medium | IEEE expectations | Provide code and aggregate artifacts; do not redistribute D1 |
| “No ethics statement for SMS content.” | Medium | SMS can contain personal data | Add ethics/privacy statement; no raw examples without permission |

## 4. What is genuinely strong

1. **Prediction-level reproducibility.** Five D1 and two D2 files align exactly to frozen test manifests; 14/14 classical metrics reproduce.
2. **Duplicate control.** Exact/normalised/fuzzy grouping, group-aware splits, zero cross-split group/key overlap.
3. **Corrected uncertainty.** Exact intervals at the perfect-precision boundary; paired shared-resample bootstrap; explicit seed limitation.
4. **Honest negative result.** The row-block collapse is quantified and not hidden.
5. **Clear scope discipline.** No phishing, Manglish, pooling or deployment claims.

## 5. Required final tasks

### Before supervisor meeting

- [ ] Approve one objective and title.
- [ ] Decide whether to include D2 in the same paper or a separate section.
- [ ] Approve the negative/limitation framing.
- [ ] Confirm the D1 permission route and deadline.
- [ ] Decide whether an abstract-only FSSHAP citation is acceptable.

### Before submission

- [ ] Obtain D1 written permission (B1).
- [ ] Either obtain FSSHAP full text or retain abstract-only limitation (B2).
- [ ] Write the manuscript using `FINAL_CLAIM_EVIDENCE_LEDGER.md`.
- [ ] Run reference-to-citation audit.
- [ ] Add ethics/privacy and data-availability statements.
- [ ] Remove all raw D1 text/screenshots unless item 4 of the permission checklist is granted.
- [ ] Check every number against `CANONICAL_FINAL_RESULTS.md`.
- [ ] Have a second reader audit the abstract against the claim ledger.

## 6. Direct answer

**Is the work ready for the final IEEE paper?**

- **As a defensible study:** yes, the core evaluation is coherent and the negative result is real.
- **As a submission:** no, because D1 permission is unresolved and the closest paper is not full-text verified.
- **As a claim of a Malayalam smishing detector:** no, and it should never be presented as one.

The project should proceed to supervisor review, not to submission. The correct framing is a **bounded evaluation study with a negative robustness result**, not a detector-success paper.
