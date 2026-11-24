#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inference for the selected Phase 2 models.

This module only loads the frozen joblib artifacts. It never fits, refits or
tunes a model, and it never writes user text to disk.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "Research Work" / "phase2" / "models"
MANIFEST_PATH = Path(__file__).resolve().parent / "model_manifest.json"

MODEL_FILES = {
    "d1": "d1_malayalam_linear_svm.joblib",
    "d2": "d2_logreg.joblib",
}

DISPLAY_LABELS = {"ham": "Ham", "spam": "Spam", "smishing": "Smishing"}

MALAYALAM_RE = re.compile(r"[\u0D00-\u0D7F]")
LATIN_RE = re.compile(r"[A-Za-z]")
WS_RE = re.compile(r"\s+")
CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

# The longest message in either frozen corpus is 910 characters; the app caps
# input at 5,000. The cap is a denial-of-service guard, not a model change: no
# real SMS approaches it, and it is never applied silently.
MAX_INPUT_CHARS = 5000


def clean_text(value: str) -> str:
    """Apply the exact conservative cleaning used by the Phase 2 training code."""
    text = unicodedata.normalize("NFKC", str(value))
    for ch in ("\u200b", "\u200c", "\u200d", "\ufeff"):
        text = text.replace(ch, "")
    text = text.replace("\u00a0", " ")
    text = CTRL_RE.sub(" ", text)
    return WS_RE.sub(" ", text).strip()


def has_malayalam(value: str) -> bool:
    return bool(MALAYALAM_RE.search(str(value)))


def has_latin(value: str) -> bool:
    return bool(LATIN_RE.search(str(value)))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_artifact_hash(filename: str, path: Path) -> str:
    """Refuse to unpickle an artifact that does not match its recorded SHA-256.

    ``joblib.load`` executes pickle code, so the artifact is a trust boundary.
    The manifest is the only record of the expected bytes; a mismatch means the
    file was modified or replaced, and it must not be loaded.
    """
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(
            f"Model manifest not found: {MANIFEST_PATH}. Cannot verify the artifact."
        )
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    expected = manifest.get("models", {}).get(filename)
    if not expected:
        raise ValueError(f"No recorded SHA-256 for {filename} in the model manifest.")
    actual = sha256_file(path)
    if actual != expected:
        raise ValueError(
            f"Artifact integrity check failed for {filename}: recorded "
            f"{expected[:12]}…, found {actual[:12]}…. Refusing to load it."
        )
    return actual


@lru_cache(maxsize=4)
def load_artifact(task: str) -> dict:
    """Load and validate one saved inference artifact."""
    if task not in MODEL_FILES:
        raise ValueError(f"Unknown task: {task}")
    path = MODELS_DIR / MODEL_FILES[task]
    if not path.exists():
        raise FileNotFoundError(f"Saved model not found: {path}")
    verify_artifact_hash(MODEL_FILES[task], path)

    artifact = joblib.load(path)
    required = {"pipeline", "config", "C", "labels"}
    missing = required.difference(artifact)
    if missing:
        raise ValueError(f"Model artifact is missing keys: {sorted(missing)}")
    if "tfidf" not in artifact["pipeline"].named_steps:
        raise ValueError("Saved pipeline does not contain a tfidf step")
    return artifact


def model_summary(task: str) -> dict:
    """Return non-sensitive metadata for display and verification."""
    artifact = load_artifact(task)
    pipeline = artifact["pipeline"]
    vectorizer = pipeline.named_steps["tfidf"]
    return {
        "task": task,
        "model_file": MODEL_FILES[task],
        "config": artifact["config"],
        "C": float(artifact["C"]),
        "labels": list(artifact["labels"]),
        "classes": [str(c) for c in pipeline.classes_],
        "n_features": int(len(vectorizer.get_feature_names_out())),
        "classifier": type(pipeline.named_steps["clf"]).__name__,
    }


def validate_input(value, task: str) -> str:
    """Reject input that must not reach the frozen model.

    Raises ValueError with a user-facing message instead of returning a
    meaningless prediction. The script checks prevent the wrong dataset's model
    from being applied to the wrong language, which would look like a result.
    """
    if value is None:
        raise ValueError("The input is empty. Enter an SMS message first.")
    if isinstance(value, (bytes, bytearray)):
        raise ValueError("The input must be text, not bytes.")
    text = str(value)
    if not text.strip():
        raise ValueError("The input is empty. Enter an SMS message first.")
    if len(text) > MAX_INPUT_CHARS:
        raise ValueError(
            f"The input is {len(text):,} characters; the limit is "
            f"{MAX_INPUT_CHARS:,}. Shorten the message and try again."
        )
    if not clean_text(text):
        raise ValueError("The input contains no usable characters.")
    if task == "d1" and not has_malayalam(text):
        raise ValueError(
            "No Malayalam Unicode characters were detected. The Dataset 1 model "
            "was trained only on Malayalam-containing messages."
        )
    if task == "d2" and not has_latin(text):
        raise ValueError(
            "No Latin-script characters were detected. The Dataset 2 model was "
            "trained on English/Latin-script messages."
        )
    return text


def classify_malayalam(value: str) -> dict:
    """Classify a Malayalam-containing SMS with the frozen D1 Linear SVM.

    Returns a class assignment and the raw signed SVM decision value. The
    value is a margin, not a probability.
    """
    text = validate_input(value, "d1")
    cleaned = clean_text(text)
    artifact = load_artifact("d1")
    pipeline = artifact["pipeline"]
    prediction = str(pipeline.predict([cleaned])[0])
    decision = None
    try:
        decision = float(np.asarray(pipeline.decision_function([cleaned])).ravel()[0])
    except (AttributeError, ValueError):
        pass
    return {
        "task": "d1",
        "label": prediction,
        "display_label": DISPLAY_LABELS.get(prediction.lower(), prediction),
        "decision_value": decision,
        "clean_text": cleaned,
        "input_characters": len(text),
    }


def classify_english(value: str) -> dict:
    """Classify a Latin-script SMS with the frozen D2 Logistic Regression."""
    text = validate_input(value, "d2")
    cleaned = clean_text(text)
    artifact = load_artifact("d2")
    pipeline = artifact["pipeline"]
    prediction = str(pipeline.predict([cleaned])[0])
    probabilities = pipeline.predict_proba([cleaned])[0]
    classes = [str(c) for c in pipeline.classes_]
    score_map = {DISPLAY_LABELS.get(c.lower(), c): float(probabilities[i])
                 for i, c in enumerate(classes)}
    ordered = {label: score_map[label] for label in ("Ham", "Spam", "Smishing")
               if label in score_map}
    return {
        "task": "d2",
        "label": prediction,
        "display_label": DISPLAY_LABELS.get(prediction.lower(), prediction),
        "scores": ordered,
        "clean_text": cleaned,
        "input_characters": len(text),
    }
