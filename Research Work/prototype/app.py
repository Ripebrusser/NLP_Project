#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Local Streamlit demonstration for the selected Phase 2 SMS classifiers.

Run from the project root:
    .venv/Scripts/python.exe -m streamlit run "Research Work/prototype/app.py"
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from inference import (
    classify_english,
    classify_malayalam,
    has_latin,
    has_malayalam,
    model_summary,
)
from research_data import (
    classic_block_table,
    d1_confusion,
    d1_model_table,
    d2_confusion,
    d2_model_table,
    final_comparison,
    muril_block_table,
    muril_random_table,
    muril_results,
    validation_summary,
)

st.set_page_config(
    page_title="SMS Classification Research Prototype",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
    :root {
        --ink: #172b3a;
        --muted: #5f6f78;
        --paper: #f5f2ea;
        --card: #fffdf8;
        --navy: #12344b;
        --teal: #176b73;
        --line: #d9d2c5;
        --ham: #24634a;
        --spam: #a33a32;
        --smishing: #95651a;
    }
    .stApp { background: var(--paper); color: var(--ink); }
    .block-container { max-width: 1180px; padding-top: 1.4rem; padding-bottom: 3rem; }
    h1, h2, h3 { color: var(--ink) !important; letter-spacing: -0.02em; }
    p, li, label { color: var(--ink); }
    [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * { color: var(--muted) !important; }
    [data-testid="stMetricValue"] { color: var(--ink) !important; }
    [data-testid="stAlert"] p { color: #3b352b !important; }

    [data-testid="stSidebar"] { background: var(--navy); }
    [data-testid="stSidebar"] * { color: #f7f3ea !important; }
    [data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] caption { color: #cad8dc !important; }
    [data-testid="stSidebar"] [data-testid="stAlert"] * { color: var(--navy) !important; }
    [data-testid="stSidebar"] hr { border-color: #315269; }
    [data-testid="stSidebar"] [data-baseweb="radio"] label { padding: 0.15rem 0; }

    .hero {
        background: linear-gradient(125deg, #12344b 0%, #176b73 100%);
        border-radius: 16px;
        padding: 2.1rem 2.4rem 2rem 2.4rem;
        margin-bottom: 1.4rem;
        box-shadow: 0 8px 24px rgba(18, 52, 75, 0.13);
    }
    .hero .eyebrow { color: #b9e1dc; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase; }
    .hero h1 { color: #fffdf8 !important; font-size: 2.25rem; line-height: 1.12; margin: 0.45rem 0 0.6rem 0; }
    .hero p { color: #e3eeeb !important; font-size: 1.02rem; max-width: 800px; margin: 0; line-height: 1.55; }

    .section-kicker { color: var(--teal); font-size: 0.72rem; font-weight: 800; letter-spacing: 0.17em; text-transform: uppercase; margin-bottom: 0.2rem; }
    .section-note { color: var(--muted); font-size: 0.92rem; margin-top: -0.5rem; margin-bottom: 1.1rem; }

    .result-card {
        border-radius: 13px;
        padding: 1.25rem 1.35rem 1.15rem 1.35rem;
        margin: 0.9rem 0 0.75rem 0;
        border: 1px solid var(--line);
        background: var(--card);
    }
    .result-card.ham { border-left: 7px solid var(--ham); }
    .result-card.spam { border-left: 7px solid var(--spam); }
    .result-card.smishing { border-left: 7px solid var(--smishing); }
    .result-kicker { color: var(--muted); font-size: 0.7rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; }
    .result-label { font-size: 2rem; font-weight: 800; letter-spacing: -0.03em; margin: 0.18rem 0 0.12rem 0; }
    .result-card.ham .result-label { color: var(--ham); }
    .result-card.spam .result-label { color: var(--spam); }
    .result-card.smishing .result-label { color: var(--smishing); }
    .result-detail { color: var(--muted); font-size: 0.88rem; line-height: 1.45; }

    .model-card {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 13px;
        padding: 1.1rem 1.2rem 0.9rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    .model-card h4 { margin: 0 0 0.25rem 0; color: var(--ink); }
    .model-card p { color: var(--muted); font-size: 0.87rem; margin: 0.25rem 0; }
    .mono { font-family: Consolas, "Courier New", monospace; font-size: 0.82rem; }

    .small-note {
        border-left: 3px solid #c7a85c;
        background: #fffaf0;
        color: #5f4b22;
        padding: 0.75rem 0.9rem;
        border-radius: 4px;
        font-size: 0.86rem;
        line-height: 1.45;
        margin: 0.75rem 0;
    }
    .privacy-note { color: var(--muted); font-size: 0.78rem; line-height: 1.45; }
    [data-testid="stMetric"] {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 11px;
        padding: 0.65rem 0.8rem;
    }
    [data-testid="stMetricLabel"] { color: var(--muted); }
    .stTextArea textarea {
        font-family: "Noto Sans Malayalam", "Nirmala UI", "Kartika", "Segoe UI", sans-serif;
        font-size: 1.08rem;
        line-height: 1.65;
        background: #fffdf8 !important;
        color: var(--ink) !important;
        -webkit-text-fill-color: var(--ink);
    }
    .stButton > button {
        border-radius: 8px;
        background: var(--teal) !important;
        color: #fffdf8 !important;
        border: 1px solid var(--teal) !important;
    }
    .stButton > button:hover { background: var(--navy) !important; border-color: var(--navy) !important; }
    .stDataFrame { border-radius: 10px; }
    footer { visibility: hidden; }
</style>
"""

SOURCE_WARNING = (
    "Dataset 1 has significant source-block bias. Random grouped-split performance "
    "does not establish generalisation to unseen Malayalam SMS sources. Random-split "
    "and block-held-out results are shown separately."
)

D1_LIMITATIONS = """
<div class="small-note">
<strong>Experimental limitations.</strong> The Malayalam model has 1,992 messages from
one corpus and only 225 Spam examples; 94.7% of Spam is in one source block. The random
test Macro-F1 is <strong>0.9650</strong>, but pooled leave-one-block-out Macro-F1 is
<strong>0.5378</strong>. This is a within-source demonstration, not evidence of field
performance. The classifier predicts the dataset's original Ham/Spam labels; it does
not verify URLs or detect phishing, malware or all cybersecurity threats.
</div>
"""

D2_LIMITATIONS = """
<div class="small-note">
<strong>Scope.</strong> Dataset 2 is an English/Latin-script, three-class corpus
(Ham, Spam, Smishing). It is not Malayalam detection and its classes are never merged.
The random test Macro-F1 is <strong>0.8877</strong>. No block-held-out estimate is
available for Dataset 2. Scores shown below are model outputs, not guaranteed
calibrated probabilities.
</div>
"""


def fmt(value, digits: int = 4) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "—"
    if isinstance(value, str):
        return value
    return f"{value:.{digits}f}"


def pretty(df: pd.DataFrame, digits: int = 4) -> pd.DataFrame:
    out = df.copy()
    for column in out.columns:
        if pd.api.types.is_float_dtype(out[column]):
            out[column] = out[column].map(lambda v: fmt(v, digits))
    return out


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">Phase 3 · Local research demonstration</div>
            <h1>SMS Classification Research Prototype</h1>
            <p>A transparent interface for the selected Phase 2 models: a Malayalam
            Ham/Spam classifier and a separate English/Latin-script SMS triage model.
            The models are frozen; nothing is retrained by this application.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> str:
    st.sidebar.markdown(
        '<div style="font-size:1.25rem;font-weight:800;line-height:1.1;">SMS research<br>'
        '<span style="font-size:0.7rem;font-weight:600;letter-spacing:0.14em;color:#b9e1dc;">'
        'PROTOTYPE</span></div>',
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")
    view = st.sidebar.radio(
        "Navigate",
        ["Malayalam SMS", "English SMS", "Research dashboard"],
        label_visibility="collapsed",
    )
    st.sidebar.markdown("---")
    st.sidebar.caption("SELECTED MODELS")
    st.sidebar.markdown(
        "**Dataset 1 · Malayalam**  \n"
        "Linear SVM · char 2–4 · C=0.5  \n"
        "Ham / Spam"
    )
    st.sidebar.markdown(
        "**Dataset 2 · English/Latin**  \n"
        "Logistic Regression · char 2–4 · C=1.0  \n"
        "Ham / Spam / Smishing"
    )
    st.sidebar.markdown("---")
    st.sidebar.info(
        "Local demonstration only. Messages are processed in this session, are not "
        "sent to an external API and are not written to disk."
    )
    st.sidebar.caption(
        "MuRIL is retained as an experimental comparator, not as the selected "
        "prototype model."
    )
    return view


def result_card(label: str, kicker: str, detail: str) -> None:
    tone = label.lower()
    if tone not in {"ham", "spam", "smishing"}:
        tone = "ham"
    st.markdown(
        f'<div class="result-card {tone}">'
        f'<div class="result-kicker">{kicker}</div>'
        f'<div class="result-label">{label}</div>'
        f'<div class="result-detail">{detail}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def model_card(task: str) -> None:
    try:
        info = model_summary(task)
    except Exception as exc:  # a missing or tampered artifact must not blank the page
        st.error(f"Model metadata could not be loaded: {exc}")
        return
    if task == "d1":
        title = "Linear SVM"
        subtitle = "Dataset 1 · binary Ham / Spam"
        extras = [
            f"TF-IDF: {info['config']} characters, {info['n_features']:,} features",
            f"C = {info['C']:.1f} · decision boundary = 0",
            "Fitted on 1,394 train + 299 validation messages",
            "Frozen test set: 299 messages",
        ]
    else:
        title = "Logistic Regression"
        subtitle = "Dataset 2 · Ham / Spam / Smishing"
        extras = [
            f"TF-IDF: {info['config']} characters, {info['n_features']:,} features",
            f"C = {info['C']:.1f} · multinomial classifier",
            "Fitted on 4,127 train + 885 validation messages",
            "Frozen test set: 883 messages",
        ]
    with st.container(border=True):
        st.markdown(f"#### {title}")
        st.caption(subtitle)
        for line in extras:
            st.markdown(f"- {line}")


def view_malayalam() -> None:
    st.markdown('<div class="section-kicker">Section A</div>', unsafe_allow_html=True)
    st.markdown("## Malayalam SMS Detector")
    st.markdown(
        '<div class="section-note">Explicit Dataset 1 mode. Enter Malayalam-containing '
        "text; the application applies the frozen cleaning function and saved SVM.</div>",
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.65, 1], gap="large")
    with left:
        with st.form("d1-form", clear_on_submit=False):
            sms = st.text_area(
                "Malayalam SMS text",
                height=180,
                max_chars=5000,
                placeholder="ഉദാഹരണം: ഇന്ന് വൈകുന്നേരം യോഗം ഉണ്ടോ?",
                help="Malayalam Unicode is preserved. URLs, digits and punctuation are not removed.",
            )
            submitted = st.form_submit_button(
                "Analyse Malayalam SMS",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            if not sms.strip():
                st.warning("Enter a message before analysing it.")
            elif not has_malayalam(sms):
                st.warning(
                    "No Malayalam Unicode characters (U+0D00–U+0D7F) were detected. "
                    "The Dataset 1 model was trained only on Malayalam-containing "
                    "messages, so no prediction is shown. Use the English/Latin-script "
                    "mode only when that task is appropriate."
                )
            else:
                try:
                    result = classify_malayalam(sms)
                except Exception as exc:  # do not hide a genuine artifact/loading failure
                    st.error(f"The selected model could not produce a prediction: {exc}")
                else:
                    detail = (
                        "Linear SVM class assignment. The model does not expose a "
                        "calibrated probability; no confidence value is shown."
                    )
                    result_card(result["display_label"], "Predicted class", detail)
                    st.caption(
                        "Input contains Malayalam Unicode; the text was cleaned with the "
                        "same NFKC/whitespace rules used during training. No text was saved."
                    )

        st.markdown(D1_LIMITATIONS, unsafe_allow_html=True)

    with right:
        model_card("d1")
        st.markdown("#### Reading the result")
        st.markdown(
            "The label is the model's class assignment for **Dataset 1's original "
            "Ham/Spam annotation**. A Spam output is not proof that a message is "
            "fraudulent, and a Ham output is not a safety guarantee."
        )
        st.caption(
            "Validation-selected thresholding was analysed separately in Phase 2.3; "
            "this prototype uses the selected model's default decision boundary."
        )


def view_english() -> None:
    st.markdown('<div class="section-kicker">Section B</div>', unsafe_allow_html=True)
    st.markdown("## English / Latin-script SMS Detector")
    st.markdown(
        '<div class="section-note">Explicit Dataset 2 mode. This is a separate '
        "three-class experiment; it is not Malayalam detection.</div>",
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.65, 1], gap="large")
    with left:
        with st.form("d2-form", clear_on_submit=False):
            sms = st.text_area(
                "English / Latin-script SMS text",
                height=160,
                max_chars=5000,
                placeholder="Example: Your parcel could not be delivered. Call this number to reschedule.",
                help="The three classes are Ham, Spam and Smishing and are never merged.",
            )
            submitted = st.form_submit_button(
                "Analyse English SMS",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            if not sms.strip():
                st.warning("Enter a message before analysing it.")
            elif not has_latin(sms):
                st.warning(
                    "No Latin-script characters (A–Z) were detected. This detector is "
                    "for English/Latin-script SMS, so no prediction is shown."
                )
            else:
                if has_malayalam(sms):
                    st.warning(
                        "Malayalam Unicode was detected. This is the English/Latin-script "
                        "model, not the Malayalam detector; interpret the result with care."
                    )
                try:
                    result = classify_english(sms)
                except Exception as exc:
                    st.error(f"The selected model could not produce a prediction: {exc}")
                else:
                    result_card(
                        result["display_label"],
                        "Predicted class",
                        "Logistic Regression class assignment for Dataset 2.",
                    )
                    scores = pd.DataFrame(
                        [{"Class": label, "Model output score": score}
                         for label, score in result["scores"].items()]
                    )
                    st.markdown("**Model output scores**")
                    st.dataframe(
                        scores,
                        hide_index=True,
                        use_container_width=True,
                        column_config={
                            "Model output score": st.column_config.NumberColumn(format="%.4f")
                        },
                    )
                    st.caption(
                        "These are the fitted model's output scores, not guaranteed "
                        "calibrated probabilities. Spam and Smishing are separate classes; "
                        "they are not combined."
                    )

        st.markdown(D2_LIMITATIONS, unsafe_allow_html=True)

    with right:
        model_card("d2")
        st.markdown("#### How to read the scores")
        st.markdown(
            "The largest score determines the displayed class. The scores are useful "
            "for inspecting model behaviour, but they should not be presented as "
            "real-world certainty. Dataset 2 has no Malayalam or Manglish labels."
        )
        st.caption(
            "The application does not route automatically between datasets; the user "
            "must choose the task."
        )


def show_confusion(matrix, labels, caption: str) -> None:
    frame = pd.DataFrame(
        matrix,
        index=[f"True {label}" for label in labels],
        columns=[f"Pred {label}" for label in labels],
    )
    st.dataframe(frame, use_container_width=True)
    st.caption(caption)


def dashboard_overview() -> None:
    st.markdown("### Consolidated comparison")
    st.caption(
        "Loaded directly from metrics/final_model_comparison.csv. Random-split metrics "
        "are point estimates; 95% group-bootstrap intervals are shown in the Phase 2.3 "
        "reports and in the D1/D2 tables below."
    )
    comparison = final_comparison()
    display = pd.DataFrame({
        "Model": comparison["model"],
        "Dataset": comparison["dataset"],
        "Random Macro-F1": comparison["random_macro_f1"].map(fmt),
        "95% CI": comparison.apply(
            lambda row: "—" if pd.isna(row["random_macro_f1_ci_low"])
            else f"[{row['random_macro_f1_ci_low']:.4f}, {row['random_macro_f1_ci_high']:.4f}]",
            axis=1,
        ),
        "Spam recall": comparison["random_spam_recall"].map(fmt),
        "Block Macro-F1": comparison["block_macro_f1"].map(fmt),
    })
    st.dataframe(display, hide_index=True, use_container_width=True)
    st.markdown(
        '<div class="small-note"><strong>Primary vs robustness.</strong> The random '
        "grouped split is the primary within-source benchmark. The block-held-out "
        "column is a separate robustness test, not a second headline. D2 has no "
        "source-block experiment.</div>",
        unsafe_allow_html=True,
    )

    columns = st.columns(3)
    with columns[0]:
        st.metric("D1 selected model", "Linear SVM", "char 2–4 · C=0.5")
    with columns[1]:
        st.metric("D1 random Macro-F1", "0.9650", "block-held-out 0.5378")
    with columns[2]:
        st.metric("D2 selected model", "Logistic Regression", "char 2–4 · C=1.0")


def dashboard_d1() -> None:
    st.markdown("### Dataset 1 — Logistic Regression vs Linear SVM")
    st.caption("Primary within-source benchmark; frozen grouped test set of 299 messages.")
    table = d1_model_table()
    st.dataframe(pretty(table), hide_index=True, use_container_width=True)
    chart = pd.DataFrame({
        "Model": ["Logistic Regression", "Linear SVM"],
        "Macro-F1": [
            d1_results_value("logreg", "macro_f1"),
            d1_results_value("linear_svm", "macro_f1"),
        ],
        "Spam recall": [
            d1_results_value("logreg", "spam_recall"),
            d1_results_value("linear_svm", "spam_recall"),
        ],
    })
    st.bar_chart(chart, x="Model", y=["Macro-F1", "Spam recall"], height=300)
    st.caption("Bars are random-split point estimates, not confidence intervals.")

    st.markdown("#### Confusion matrices")
    st.caption("Rows are true labels; columns are predicted labels.")
    left, right = st.columns(2)
    with left:
        st.markdown("**Logistic Regression**")
        show_confusion(
            d1_confusion("logreg"),
            ["Ham", "Spam"],
            "Test rows: 265 Ham / 34 Spam.",
        )
    with right:
        st.markdown("**Linear SVM**")
        show_confusion(
            d1_confusion("linear_svm"),
            ["Ham", "Spam"],
            "Selected D1 model; 265 Ham / 34 Spam test rows.",
        )
    st.warning(SOURCE_WARNING)


def d1_results_value(family: str, metric: str):
    from research_data import d1_results
    return d1_results()["models"][family]["test"][metric]



def dashboard_d2() -> None:
    st.markdown("### Dataset 2 — Logistic Regression vs Linear SVM")
    st.caption("Separate English/Latin-script three-class experiment; frozen test set of 883 messages.")
    st.dataframe(pretty(d2_model_table()), hide_index=True, use_container_width=True)
    st.caption("The classes are Ham, Spam and Smishing. No class is merged or relabelled.")

    st.markdown("#### Confusion matrices")
    st.caption("Rows are true labels; columns are predicted labels. Order: Ham, Spam, Smishing.")
    left, right = st.columns(2)
    with left:
        st.markdown("**Logistic Regression**")
        show_confusion(
            d2_confusion("logreg"),
            ["Ham", "Spam", "Smishing"],
            "Selected D2 model; test rows 726 Ham / 67 Spam / 90 Smishing.",
        )
    with right:
        st.markdown("**Linear SVM**")
        show_confusion(
            d2_confusion("linear_svm"),
            ["Ham", "Spam", "Smishing"],
            "Comparator on the same frozen test rows.",
        )
    st.info("Dataset 2 has no source-block structure, so no block-held-out result is reported.")


def dashboard_muril() -> None:
    st.markdown("### MuRIL — Dataset 1 comparator")
    st.warning(
        "MuRIL is retained as a research comparator and negative/limiting result. "
        "It is not the selected prototype model."
    )
    aggregate = muril_results()["random_split"]["aggregate"]
    columns = st.columns(3)
    with columns[0]:
        st.metric("Random Macro-F1", f"{aggregate['macro_f1']['mean']:.4f}",
                  f"seed SD {aggregate['macro_f1']['sd']:.4f}")
    with columns[1]:
        st.metric("Random Spam recall", f"{aggregate['spam_recall']['mean']:.4f}",
                  f"seed SD {aggregate['spam_recall']['sd']:.4f}")
    with columns[2]:
        st.metric("Random accuracy", f"{aggregate['accuracy']['mean']:.4f}",
                  f"seed SD {aggregate['accuracy']['sd']:.4f}")
    st.caption("Mean and standard deviation of three training seeds; these are not bootstrap intervals.")
    st.dataframe(pretty(muril_random_table()), hide_index=True, use_container_width=True)
    st.markdown(
        '<div class="small-note"><strong>The negative result.</strong> MuRIL ties the '
        "classical models within-source (seed-42/44 predictions are identical to the "
        "SVM), but under leave-one-block-out it falls to a pooled Macro-F1 of 0.5028 "
        "and 3.56% Spam recall. On block 6001–7000 every seed predicts Ham for all 213 "
        "Spam messages; its block probabilities are effectively constant. This is a "
        "representation/source-shift failure, not a decision-threshold issue.</div>",
        unsafe_allow_html=True,
    )


def dashboard_blocks() -> None:
    st.markdown("### Block-held-out evaluation — Dataset 1")
    st.warning(
        "There are only three source blocks and one contains no Spam. This is a "
        "stress test, not a population-level confidence interval. Each block is "
        "reported separately; no result here uses the held-out block for tuning."
    )
    st.markdown("**Classical models**")
    classic = classic_block_table()
    st.dataframe(pretty(classic), hide_index=True, use_container_width=True)
    st.caption(
        "* Block 5001–6000 has no Spam. Its Macro-F1 is not a balanced performance "
        "estimate and its Spam recall is undefined. False positives are the useful "
        "error signal for that block."
    )

    st.markdown("**MuRIL, by seed**")
    st.dataframe(pretty(muril_block_table()), hide_index=True, use_container_width=True)
    st.caption(
        "Block 6001–7000: MuRIL predicts Ham for every row in every seed. "
        "The model is not selected for the prototype."
    )
    st.markdown(
        '<div class="small-note"><strong>Source-block confound.</strong> 94.7% of D1 '
        "Spam is in block 6001–7000, and the random split places 95.5% of training Spam "
        "and 91.2% of test Spam in that same block. The random-split score measures "
        "within-batch structure, not generalisation to unseen Malayalam SMS sources."
        "</div>",
        unsafe_allow_html=True,
    )


def dashboard() -> None:
    st.markdown('<div class="section-kicker">Section C</div>', unsafe_allow_html=True)
    st.markdown("## Research Results Dashboard")
    st.caption(
        "All figures below are loaded read-only from the frozen Phase 2 metrics. "
        "No result is recalculated, sampled or invented by the prototype."
    )
    st.warning(SOURCE_WARNING)
    tabs = st.tabs(["Overview", "Dataset 1", "Dataset 2", "MuRIL", "Block holdout"])
    with tabs[0]:
        dashboard_overview()
    with tabs[1]:
        dashboard_d1()
    with tabs[2]:
        dashboard_d2()
    with tabs[3]:
        dashboard_muril()
    with tabs[4]:
        dashboard_blocks()


def main() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    render_hero()
    view = render_sidebar()
    if view == "Malayalam SMS":
        view_malayalam()
    elif view == "English SMS":
        view_english()
    else:
        dashboard()
    st.divider()
    st.markdown(
        '<div class="privacy-note">Research prototype · frozen Phase 2 models · '
        "local execution · no external API calls · submitted text is not permanently "
        "stored or logged.</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
