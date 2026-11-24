# SMS Classification Research Prototype

Local, read-only demonstration of the two models selected in Phase 2.3:

| Mode | Dataset | Model | Classes |
|---|---|---|---|
| Malayalam SMS | Dataset 1 | Linear SVM, char TF-IDF 2–4, C = 0.5 | Ham / Spam |
| English/Latin SMS | Dataset 2 | Logistic Regression, char TF-IDF 2–4, C = 1.0 | Ham / Spam / Smishing |

MuRIL is retained as a research comparator in the dashboard, not as a prototype
model. The application loads the saved `.joblib` pipelines and **never retrains or
fits a vectorizer**.

## Run locally

From the project root:

```bash
.venv/Scripts/python.exe -m pip install -r "Research Work/prototype/requirements.txt"
.venv/Scripts/python.exe -m streamlit run "Research Work/prototype/app.py" --server.address 127.0.0.1 --server.port 8501
```

Then open `http://127.0.0.1:8501`.

The dependencies are already installed in the existing project environment; the
first command is included for a clean reproduction. The app has no network calls.

## Verification

```bash
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe "Research Work/prototype/verify_prototype.py"
```

Exit status 0 means: all four model hashes and all six split hashes match their
manifests; the saved pipelines reproduce the frozen test predictions row for row
after `record_id` alignment (D1 299/299, D2 883/883); the public `classify_*`
functions reproduce the same predictions after their own cleaning and guards; and
the empty/wrong-script/length guards behave as documented. The verifier writes
`verification_results.json`; the previous copy is kept as
`verification_results.before_code_audit.json`.

Input limits enforced in `inference.py` (not only in the UI): 1–5,000 characters,
non-empty after cleaning, Malayalam present for D1, Latin present for D2. The
longest frozen message is 910 characters, so normal inputs are unaffected.

Before unpickling, `inference.load_artifact()` re-derives the artifact's SHA-256
and compares it with `model_manifest.json`; a mismatch is an error, not a
prediction. The app shows such a failure inline instead of blanking the page.

The app makes no outbound network calls. `.streamlit/config.toml` disables
Streamlit's default usage statistics (`browser.gatherUsageStats = false`); the
browser audit recorded zero non-loopback requests after that change.

## What the app contains

- **Malayalam SMS Detector (Section A):** explicit D1 mode. It blocks empty input
  and text without Malayalam Unicode, applies the exact training cleaner, and uses
  the saved SVM. The SVM returns a class, not a calibrated probability, so no
  confidence value is displayed.
- **English / Latin-script SMS Detector (Section B):** explicit D2 mode. It blocks
  empty input and text without Latin characters, predicts Ham, Spam or Smishing
  separately, and shows the logistic-regression output scores with a calibration
  caveat.
- **Research Results Dashboard (Section C):** actual saved random-split and
  block-held-out metrics, per-class F1, Spam recall, confusion matrices and the
  MuRIL comparison. Random and block results are displayed separately.

The source-block warning is shown in the dashboard and in the D1 detector:

> Dataset 1 has a strong row-block label confound. Grouped random-split
> performance does not establish generalisation to unseen Malayalam SMS sources.
> This is a demonstration, not a validated production system.

## Files

| Path | Purpose |
|---|---|
| `app.py` | Streamlit interface |
| `inference.py` | Frozen model loading, exact cleaning, D1/D2 prediction |
| `research_data.py` | Read-only loaders for the saved Phase 2 metrics |
| `requirements.txt` | Runtime dependencies and tested versions |
| `MODEL_AND_DATASET_NOTES.md` | Dataset, split, model and limitation notes |
| `model_manifest.json` | Baseline model/split hashes for verification |
| `verify_prototype.py` | Artifact, parity, class-coverage and hash checks |
| `VERIFICATION_REPORT.md` | Prototype-local verification results; project-wide verification is `Admin/VERIFICATION_REPORT.md` |
| `screenshots/` | Captured working-application screenshots |

Phase 2 artifacts remain under `Research Work/phase2/`; this prototype does not
modify them.

## Privacy and scope

- All processing is local; no SMS text is sent to an external API.
- Submitted text is held only in the Streamlit session and is not written to disk
  or logged by the application.
- The application is an academic demonstration, not a production security tool.
- It classifies the datasets' original labels. It does not verify URLs or claim to
  detect phishing, malware or all cybersecurity threats.
- Dataset 2 is English/Latin-only. Do not describe its results as Malayalam
  detection or merge Spam and Smishing.
- Dataset 1 access provenance remains unresolved; see the Phase 2.3 reports.
