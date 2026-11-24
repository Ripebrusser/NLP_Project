# Dataset Provenance and Permissions

**Date:** 6 November 2026. This note corrects the earlier claim that the D1 licence question was “resolved.” It is an evidence record, not legal advice.

## 1. Dataset 1 — “Spam SMS in Dravidian Languages”

| Field | Verified status |
|---|---|
| Authors | Ramanujam Elangovan; Abirami A. M. |
| Publisher | IEEE DataPort |
| Date | 2 June 2023 |
| DOI | `10.21227/dcym-pd69` |
| File | `Spam Message Collection.xlsx` (1.26 MB listed; local SHA-256 `24ca099a…a023b`) |
| Languages | English, Tamil, Telugu, Kannada, Malayalam |
| Labels | Ham / Spam only; spam = business/annoying/unnecessary, **not phishing** |
| Access | Standard Dataset; **subscription required**, login-gated |
| Dataset-page licence | **Not displayed** |
| Local accession evidence | No subscription receipt, download log, invoice or author permission in the workspace. **8 Nov 2026:** the NLM lecturer has stated that he will approach the D1 author; no contact has been evidenced and no reply has been received. |
| Redistribution | **Not established. Do not redistribute raw messages, screenshots, examples or the workbook.** |
| Permission status | **PENDING.** Access authorisation, research use, aggregate publication, example reproduction and redistribution are separate questions; none is established by the lecturer's intention to contact the author. |

**What can be said:** the local file is strongly consistent with the official record (name, size, two-column layout, language mix, approximate count). The team has local access to a copy.

**8 November 2026 update:** the NLM lecturer's planned approach to the author is recorded as an intended action only. It does not establish access authorisation, research permission, aggregate-publication permission, example permission or redistribution permission. Until a written reply is preserved, the status is **PENDING** and the paper may report aggregate derived statistics only, subject to the unresolved publication-permission question.

**What cannot be said:** that the team’s access is authorised under a specific subscription or author permission; that a platform-wide CC BY default is a dataset-specific licence; that redistribution is permitted.

IEEE DataPort’s general Terms mention a CC BY 3.0 US default for uploaded content, but the dataset page itself displays no licence and access is subscription-based with personal, non-transferable credentials. A platform default is not a substitute for the dataset-specific terms or for this team’s accession record. This is why the prior “licence resolved” conclusion is withdrawn.

**Practical resolution (in order):**

1. Locate and retain the subscription receipt, institutional access confirmation, or written author permission. Record the date, account holder and scope.
2. Ask IEEE DataPort / the authors in writing whether **publication of aggregate derived statistics** (counts, metrics, confusion matrices) is permitted, separately from redistribution of messages.
3. Until answered: keep the D1 file local; publish **aggregate results only**; no raw message examples, screenshots, sample rows, or public demo that exposes D1 text.
4. If permission cannot be evidenced: do not submit a D1-based paper as-is. Either pivot to D2 plus a methods/validity contribution, or present D1 only as an internal case study with explicit “permission unresolved” disclosure and no redistributed content. Do not fabricate a licence.

## 2. Dataset 2 — Mendeley SMS Phishing Dataset

| Field | Verified status |
|---|---|
| Authors | Sandhya Mishra; Devpriya Soni |
| Publisher | Mendeley Data, V1 |
| Date | 20 June 2022 |
| DOI | `10.17632/f45bkkt8pr.1` |
| File | `Dataset_5971.csv` (local SHA-256 `649844f1…a71e`) |
| Licence | **CC BY 4.0** (displayed) |
| Composition | 5,971 = 4,844 Ham / 489 Spam / 638 Smishing |
| Source relation | Ham/Spam portion derives from the UCI SMS Spam Collection; linked on the record |
| Redistribution | Permitted under CC BY 4.0 **with attribution**, subject to privacy/ethics review of raw SMS content |

CC BY 4.0 is a broad reuse licence, but it does not automatically make publishing raw personal messages ethically appropriate. Do not publish raw SMS examples or screenshots without an ethics/privacy review; aggregate and paraphrased examples are safer. D2 is English/Latin-only and is **not** external validation for D1.

## 3. Cross-dataset status

The datasets share 773 normalised keys; 1,555 D1 records and 831 D2 records have a twin. They are **not independent**. No combined training, no pooled test, and no claim that D2 validates D1.

## 4. What the paper may state

**D1:** “We used the Malayalam-containing subset of the IEEE DataPort Dravidian SMS corpus (Elangovan & Abirami, 2023; DOI …). Access is subscription-gated and the dataset page displays no licence; our accession record is [receipt/permission or ‘unresolved’]. We report aggregate results only and do not redistribute messages.”

**D2:** “We used the Mendeley SMS Phishing Dataset (Mishra & Soni, 2022; DOI …; CC BY 4.0).” Include attribution and do not imply D2 is Malayalam or independent external validation.

## 5. Residual risk

If the submission contains D1 examples or a public demo and no permission is on file, the provenance risk becomes a rejection/ethics risk. Resolve this before writing the final paper; it cannot be fixed by statistical analysis.

## 6. Current action status (8 November 2026)

| Item | Status |
|---|---|
| Lecturer plans to contact author | **Stated intention only** |
| Contact made | **Not evidenced** |
| Author reply received | **No** |
| Access authorisation | **Pending** |
| Research-use permission | **Pending** |
| Aggregate-publication permission | **Pending** |
| Short-example permission | **Pending; do not publish examples** |
| Raw redistribution permission | **Not established; do not redistribute** |

The request wording and evidence checklist are in `D1_PERMISSION_REQUEST_AND_CHECKLIST.md`.
