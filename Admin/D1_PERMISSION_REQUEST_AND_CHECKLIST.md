# D1 Permission Request and Checklist

**Status:** **PENDING.** The NLM lecturer has said he will approach the D1 author. No written confirmation has been received. A plan to contact is not permission.

**Dataset:** R. Elangovan and A. M. Abirami, “Spam SMS in Dravidian Languages,” IEEE DataPort, 2 June 2023, DOI `10.21227/dcym-pd69`.

---

## 1. What must be established, separately

Do not infer one permission from another. Each row is a distinct question.

| # | Permission / fact | Why it matters | Current status | Evidence required |
|---|---|---|---|---|
| 1 | **Access authorisation**: the team obtained the file lawfully through an IEEE DataPort subscription or authorised institutional access. | The dataset is subscription-gated; credentials are personal and non-transferable. | **Unknown.** No receipt, invoice, login record or download log in the workspace. | Subscription receipt, institutional access confirmation, or written author confirmation that the team may use the copy. |
| 2 | **Research use**: the team may analyse the data for this project. | Access alone may not settle the scope of analysis. | **Pending.** Platform FAQ suggests research use, but dataset-specific terms are not displayed. | Written confirmation naming the project and institution. |
| 3 | **Publication of aggregate derived statistics**: counts, metrics, confusion matrices, calibration curves, model coefficients. | The paper cannot be published without this. | **Pending.** No dataset-specific statement. | Written confirmation that aggregate results may be published. |
| 4 | **Reproduction of short anonymised examples**: 1–3 SMS excerpts, with phone numbers/URLs removed. | Examples help the reader but are not necessary. Default is to omit them. | **Pending.** Do not publish examples until confirmed. | Written confirmation of the number/format permitted, or a clear refusal. |
| 5 | **Redistribution of raw data**: public release of the workbook or a derived row-level file. | Not needed for this paper and should not be requested unless the supervisor requires it. | **Not established.** Do not redistribute. | Separate written permission specifically covering redistribution. |
| 6 | **Version and composition confirmation**: the 1,992 Malayalam-containing rows (1,767 Ham/225 Spam; 1,489 Malayalam-only; 503 Malayalam+Latin) correspond to the authors’ current version. | Prevents a version-mismatch criticism. | **Unconfirmed by authors.** Local file audited. | Author confirmation of version/date and approximate subset composition. |
| 7 | **Label definition confirmation**: “Spam” means unsolicited/business/annoying messages, not phishing/smishing. | Prevents a category error. | **Confirmed from the official record**, not from a personal reply. | Cite the official record; ask authors to confirm if they reply. |
| 8 | **Citation requirement**: exact citation and any attribution wording. | Compliance and courtesy. | Dataset DOI known. | Use the official IEEE DataPort citation; confirm any additional wording. |

## 2. Critical distinction

| Concept | What it allows | What it does not allow |
|---|---|---|
| Dataset access authorisation | Local reading and analysis under the access terms | Publication, redistribution or public display |
| Permission to conduct research | Analysis for the described project | Publication of results |
| Permission to publish aggregate statistics | Tables/graphs of counts and metrics | Reproduction of messages or row-level data |
| Permission to reproduce examples | Quoting specified short excerpts | Publishing the workbook or a large sample |
| Permission to redistribute raw data | Sharing the dataset | Any use beyond the stated licence/consent |

The paper needs items **1–3** at minimum. Item **4** is optional. Item **5** is not needed and should not be assumed.

## 3. Draft message for the NLM lecturer to send

> **Subject:** Request for written confirmation of research use and aggregate publication — IEEE DataPort “Spam SMS in Dravidian Languages”
>
> Dear Professor Elangovan and Professor Abirami,
>
> I am writing on behalf of **[Student name]**, a postgraduate researcher at **[Institution]**, supervised by **[Lecturer name]**. We are using the Malayalam-containing subset of your IEEE DataPort dataset “Spam SMS in Dravidian Languages” (DOI: 10.21227/dcym-pd69) in a bounded study of classical character n-gram models and a multilingual transformer for Ham/Spam classification.
>
> We are not asking to redistribute the dataset. We would be grateful for written confirmation, by reply email, of the following points:
>
> 1. That our use of the local copy for this research is authorised under the dataset’s access terms;
> 2. That we may report **aggregate derived statistics** — record counts, evaluation metrics, confusion matrices and model comparisons — in a thesis and a journal/conference paper;
> 3. Whether we may reproduce **up to three short, fully anonymised SMS excerpts** (telephone numbers and URLs removed) for illustration, or whether we should use no message text at all;
> 4. Which version/date of the workbook we should cite, and whether the Malayalam-containing subset is approximately 1,992 records with 1,767 Ham and 225 Spam;
> 5. That the “Spam” label denotes unsolicited/business/annoying messages and does **not** denote phishing or smishing.
>
> If any of these points is not permitted, please tell us which, so that we can adjust the paper. A short reply covering the points above is sufficient; we do not need a formal legal document.
>
> Thank you for maintaining this resource and for considering our request.
>
> Yours sincerely,
> **[Lecturer name]**, on behalf of **[Student name]**
> **[Department, Institution, institutional email]**

**Do not send this without the student and lecturer checking names, institutional details and the exact scope. Do not attach the dataset or raw messages.**

## 4. Evidence preservation checklist

When a reply arrives, preserve:

- [ ] Full email headers (sender, recipient, date, subject).
- [ ] PDF export of the message and any attachment.
- [ ] The exact wording of each permission, not a paraphrase.
- [ ] The project name, institution and dataset version named in the reply.
- [ ] Any limits on examples, redistribution or duration.
- [ ] A file path in `Admin/evidence/` (create the folder only when evidence exists).
- [ ] An entry in the evidence register with date, sender, scope and file hash.

Do not store the evidence only in an email inbox.

## 5. Decision tree if no written permission arrives

| Situation | Permitted action | Prohibited action |
|---|---|---|
| No reply by submission deadline | Submit a D2-plus-methods paper, or withhold the D1 paper | Submit D1 results while implying permission |
| Author confirms research use but not aggregate publication | Do not publish D1 tables | Treat research use as publication permission |
| Author confirms aggregate publication but not examples | Publish tables/graphs only | Quote messages or screenshots |
| Author confirms examples | Use the permitted number, anonymised | Publish the workbook or a large sample |
| Author confirms redistribution | Follow any stated licence/conditions | Assume it also covers unrelated uses |

## 6. Provenance status wording for the paper

Until written confirmation:

> “The D1 corpus is subscription-gated and the IEEE DataPort record displays no dataset-specific licence. We analysed a local copy for this study. Permission to quote raw messages or redistribute the dataset is not claimed. Only aggregate derived statistics are reported. Written confirmation of access and aggregate-publication permission is pending.”

Do **not** write “permission was obtained,” “the licence is resolved,” or “the dataset is openly available.”

## 7. Current status

- Lecturer’s intended action: contact the D1 author. **Recorded as intended, not completed.**
- Author confirmation: **not received**.
- Permission scope: **unknown**.
- Raw examples: **prohibited until confirmed**.
- Aggregate publication: **pending**.
- Redistribution: **not permitted/assumed**.
