# Final Security and Privacy Audit

**Date:** 8 November 2026
**Surface:** the Streamlit prototype (`app.py`, `inference.py`, `research_data.py`), the verification scripts, and the data they read. The project is a local academic demonstration; no service is deployed.

## 1. Threat model

| Asset | Exposure |
|---|---|
| D1/D2 message text | Local files; rendered only as aggregate metrics, never echoed by the app |
| Frozen models and splits | Local `.joblib` / `.csv`; loaded read-only |
| User-entered SMS | Session memory only; never written, logged or sent |
| Credentials | None exist in the project |

The realistic threats are: a malformed input crashing the app, a user applying the wrong model to a language it was not trained on, a tampered model artifact, and accidental disclosure of local paths or message text in output.

## 2. Findings

| ID | Severity | Finding | Evidence | Status |
|---|---|---|---|---|
| S-01 | Medium | The library API applied either model to any text; only the UI enforced script. A caller could run the English model on Malayalam text and present the label as a result. | `inference.classify_*` before the fix checked only for non-empty input | **Fixed** — `validate_input()` enforces D1 = Malayalam present, D2 = Latin present |
| S-02 | Medium | No input-length bound below the vectorizer; a very large string would be fully vectorised. | No cap in `inference.py`; UI-only `max_chars=5000` | **Fixed** — 5,000-character cap in the shared validator, with an explicit error |
| S-03 | Low | Error text from a failed artifact load is shown to the user (`st.error(f"… {exc}")`), which can include an absolute local path. | `app.py`, both detector branches | **Accepted** — local single-user demo; the message is needed to diagnose a missing artifact. No message text or credential is included |
| S-04 | Low | `unsafe_allow_html=True` is used for result cards. The interpolated values are the model's class label (`Ham`/`Spam`/`Smishing`) and fixed strings, not user text. | `result_card()` receives `result["display_label"]`, which comes from a fixed mapping | **Accepted** — no user-controlled HTML reaches the page. User text is never rendered as HTML |
| S-05 | Low | `joblib.load` executes pickle code. A tampered `.joblib` would run arbitrary code. | `inference.load_artifact` | **Fixed** — `verify_artifact_hash()` re-derives the SHA-256 and refuses to load on mismatch; a test simulates a corrupted hash. Trust boundary remains the local frozen artifact |
| S-06 | Info | Frozen prediction CSVs contain message text and live under `metrics/`. They are not read by the app's input path and are not served over a network. | `metrics/*_test_predictions.csv` | **Accepted** — required research evidence |
| S-07 | Info | No authentication, upload, database, subprocess, `eval`, `exec`, or user-controlled file path exists. | Full read of `app.py`, `inference.py`, `research_data.py` | No action needed |
| S-08 | Medium | Streamlit's default usage statistics contacted `data.streamlit.io` and a Fivetran webhook while the page loaded, so "no network calls" was false at the library level even though the application code made none. | Browser network log during the first pass | **Fixed** — `.streamlit/config.toml` sets `browser.gatherUsageStats = false`; the repeat pass recorded zero non-loopback requests |

## 3. Privacy review

- **No logging of submitted text.** The app holds text in the Streamlit session and passes it to `clean_text` / `pipeline.predict`. There is no `print`, `logging`, file write or cache of user input. `inference.py` has no I/O beyond `joblib.load`.
- **No application network calls.** No `requests`, HTTP client or external API anywhere in the prototype; MuRIL is not loaded. Streamlit's own usage-statistics telemetry is disabled in `.streamlit/config.toml` and the browser pass confirmed zero non-loopback requests.
- **No temporary files.** Nothing is written to disk at request time.
- **No secrets.** No API keys, tokens, environment-variable reads or credential files. `model_manifest.json` contains hashes only.
- **No raw D1/D2 messages in the UI.** The dashboard reads aggregate JSON/CSV values. Exception messages from artifact loading are the only path-derived strings shown.
- **Verification output.** `verify_prototype.py` writes record IDs and display labels for one correctly classified example per class; it does not write message text. `verification_results.json` therefore contains no SMS content.
- **Test output.** The suite never prints message text; failure messages use record IDs only.

## 4. Input-handling checks (executed)

| Input | Result |
|---|---|
| `None` | `ValueError` |
| `""`, spaces, tabs | `ValueError` |
| Control characters only | `ValueError` |
| Bytes | `ValueError` |
| 5,000 characters | accepted, prediction returned |
| 5,001 / 50,000 characters | `ValueError` before vectorisation |
| Latin-only in D1 mode | `ValueError` naming the Malayalam requirement |
| Malayalam-only in D2 mode | `ValueError` naming the Latin requirement |
| Emoji / URLs / phone numbers / HTML-like text | treated as text, cleaned conservatively, no rendering as HTML |
| Malayalam with ZWSP/ZWJ/NBSP | cleaned exactly as in training; script preserved |
| Lone replacement character U+FFFD | retained, not silently deleted |

## 5. Residual risk

1. **Tampered artifacts.** Hash pinning detects but does not prevent a malicious artifact; an attacker with write access to the project could alter both the model and the manifest. Acceptable for a local research demo; any deployment would require signed artifacts and a real trust boundary.
2. **Streamlit defaults.** The app is run with `--server.address 127.0.0.1`. Binding to `0.0.0.0` without authentication would expose it to the local network; the README does not do this.
3. **Model misuse.** The guards prevent the obvious cross-language mistake, but a user can still type Manglish (Latin script) into D2 and receive a confident label from a model that has no Manglish training data. The UI carries a written caveat; this is a scope limitation, not a vulnerability.
4. **Research artifacts are not encrypted.** Frozen prediction files contain SMS text. Anyone with filesystem access can read them; that is inherent to a local research repository.

## 6. Verdict

No critical or high-severity security defect. Two medium input-handling defects were fixed and are covered by tests. The remaining items are documented, low-severity, and consistent with a local, unauthenticated academic demonstration. The application must not be deployed publicly without adding authentication, transport security, artifact signing and a privacy review of the stored SMS text.
