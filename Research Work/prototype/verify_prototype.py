#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only verification for the prototype's frozen-model inference path.

Checks, in order:
  1. every model file listed in ``model_manifest.json`` hashes to its manifest value;
  2. all six frozen split files hash to the split manifest;
  3. each prototype model reproduces the frozen predictions row for row, aligned
     by ``record_id`` (never by position), with labels checked against the split;
  4. the public inference functions reproduce those same predictions after their
     own validation and cleaning;
  5. Unicode, empty-input and wrong-script guards behave as documented.

No model is fitted or written. Exit status is non-zero if any check fails.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PHASE2 = ROOT / "Research Work" / "phase2"
METRICS = PHASE2 / "metrics"
SPLITS = PHASE2 / "splits"
sys.path.insert(0, str(PHASE2))
sys.path.insert(0, str(ROOT / "Research Work"))

from inference import (  # noqa: E402
    MAX_INPUT_CHARS,
    classify_english,
    classify_malayalam,
    clean_text,
    has_latin,
    has_malayalam,
    load_artifact,
    validate_input,
)
from p2_common import align_predictions, clean_text as training_clean_text  # noqa: E402

MODEL_FILES = {
    "d1": "d1_malayalam_linear_svm.joblib",
    "d2": "d2_logreg.joblib",
}
TASKS = {
    "d1": ("d1_malayalam_linear_svm_test_predictions.csv", "d1_malayalam_test.csv",
           ["Ham", "Spam"]),
    "d2": ("d2_logreg_test_predictions.csv", "d2_test.csv",
           ["ham", "spam", "smishing"]),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_model_hashes(manifest: dict) -> tuple[dict, list[str]]:
    """Hash every model the manifest lists, not only the two prototype models."""
    results = {}
    failures = []
    for filename, expected in manifest["models"].items():
        path = PHASE2 / "models" / filename
        if not path.exists():
            results[filename] = {"exists": False, "sha256": None, "matches": False}
            failures.append(f"missing model file: {filename}")
            continue
        actual = sha256(path)
        matches = actual == expected
        results[filename] = {"exists": True, "sha256": actual, "matches": matches}
        if not matches:
            failures.append(
                f"hash mismatch for {filename}: {actual} != manifest {expected}"
            )
    return results, failures


def check_models(manifest: dict) -> tuple[dict, list[str]]:
    output = {}
    failures = []
    for task, (pred_name, split_name, labels) in TASKS.items():
        artifact = load_artifact(task)
        pipeline = artifact["pipeline"]
        split = pd.read_csv(SPLITS / split_name, encoding="utf-8-sig")
        pred = pd.read_csv(METRICS / pred_name, encoding="utf-8-sig")
        aligned = align_predictions(pred, split, f"prototype::{task}", labels)

        batch_pred = [str(v) for v in pipeline.predict(split["text"])]
        parity = int(sum(a == b for a, b in zip(batch_pred, aligned["prediction"])))
        classifier = classify_malayalam if task == "d1" else classify_english
        classify_pred = [classifier(message)["label"] for message in split["message"]]
        classify_parity = int(sum(a == b for a, b in zip(classify_pred,
                                                         aligned["prediction"])))
        cleaning = int(sum(clean_text(m) == training_clean_text(m)
                           for m in split["message"]))
        model_file = MODEL_FILES[task]
        actual_hash = sha256(PHASE2 / "models" / model_file)
        entry = {
            "model": model_file,
            "sha256": actual_hash,
            "hash_matches_manifest": actual_hash == manifest["models"][model_file],
            "test_rows": int(len(split)),
            "prediction_parity": parity,
            "classify_parity": classify_parity,
            "cleaning_parity": cleaning,
            "classes_observed": sorted(set(batch_pred)),
            "labels_checked": int(len(aligned)),
        }
        output[task] = entry
        if parity != len(split):
            failures.append(f"{task}: batch prediction parity {parity}/{len(split)}")
        if classify_parity != len(split):
            failures.append(
                f"{task}: inference parity {classify_parity}/{len(split)}"
            )
        if cleaning != len(split):
            failures.append(f"{task}: cleaning parity {cleaning}/{len(split)}")
    return output, failures


def check_splits(manifest: dict) -> tuple[dict, list[str]]:
    results = {}
    failures = []
    for dataset in ("d1", "d2"):
        for item in manifest[dataset]["files"]:
            path = SPLITS / item["file"]
            actual = sha256(path)
            ok = actual == item["sha256"]
            results[item["file"]] = ok
            if not ok:
                failures.append(f"split hash mismatch: {item['file']}")
    return results, failures


def check_guards() -> tuple[dict, list[str]]:
    failures = []
    checks = {}

    def expect_value_error(name: str, call) -> None:
        try:
            call()
        except ValueError:
            checks[name] = True
        else:
            checks[name] = False
            failures.append(f"{name}: expected ValueError, none raised")

    expect_value_error("empty_rejected", lambda: classify_malayalam("   "))
    expect_value_error("none_rejected", lambda: classify_english(None))
    expect_value_error("bytes_rejected", lambda: classify_english(b"hello"))
    expect_value_error("latin_only_rejected_by_d1", lambda: classify_malayalam("hello"))
    expect_value_error("malayalam_only_rejected_by_d2",
                       lambda: classify_english("മലയാളം മാത്രം"))
    expect_value_error("oversize_rejected",
                       lambda: classify_english("a" * (MAX_INPUT_CHARS + 1)))
    expect_value_error("controls_only_rejected", lambda: classify_english("\u0001\u0002"))

    checks["max_input_chars"] = MAX_INPUT_CHARS
    checks["length_at_limit_accepted"] = (
        len(validate_input("a" * MAX_INPUT_CHARS, "d2")) == MAX_INPUT_CHARS
    )
    if not checks["length_at_limit_accepted"]:
        failures.append("input exactly at the length limit was rejected")

    checks["malayalam_detected"] = has_malayalam("ഇന്ന് യോഗം ഉണ്ടോ?")
    checks["malayalam_absent"] = not has_malayalam("This is Latin only")
    checks["latin_detected"] = has_latin("Hello 123")
    checks["latin_absent"] = not has_latin("മലയാളം മാത്രം")
    checks["malayalam_preserved_after_clean"] = (
        clean_text("  ഇന്ന്\u200b   യോഗം  ") == "ഇന്ന് യോഗം"
    )
    for name, ok in checks.items():
        if isinstance(ok, bool) and not ok:
            failures.append(f"guard check failed: {name}")
    return checks, failures


def check_classes() -> tuple[dict, list[str]]:
    checks = {}
    failures = []
    for task, (pred_name, _, _) in TASKS.items():
        test = pd.read_csv(METRICS / pred_name, encoding="utf-8-sig")
        examples = {}
        for label in sorted(test["label"].unique()):
            match = test[(test["label"] == label) & (test["label"] == test["prediction"])]
            if match.empty:
                failures.append(f"{task}: no correctly predicted example for {label}")
                continue
            row = match.iloc[0]
            result = (classify_malayalam(row["message"]) if task == "d1"
                      else classify_english(row["message"]))
            examples[str(label)] = {
                "record_id": row["record_id"],
                "display_label": result["display_label"],
            }
            if task == "d2":
                if set(result["scores"]) != {"Ham", "Spam", "Smishing"}:
                    failures.append(f"d2: score keys {sorted(result['scores'])}")
                elif abs(sum(result["scores"].values()) - 1.0) > 1e-6:
                    failures.append("d2: scores do not sum to 1")
        checks[task] = examples
    expected = {"d1": {"Ham", "Spam"}, "d2": {"ham", "spam", "smishing"}}
    for task, labels in expected.items():
        if set(checks.get(task, {})) != labels:
            failures.append(f"{task}: class coverage {sorted(checks.get(task, {}))} "
                            f"!= {sorted(labels)}")
    return checks, failures


def main() -> int:
    manifest = json.loads((HERE / "model_manifest.json").read_text(encoding="utf-8"))
    split_manifest = json.loads((SPLITS / "split_manifest.json").read_text(encoding="utf-8"))

    model_hashes, hash_failures = check_model_hashes(manifest)
    split_hashes, split_failures = check_splits(split_manifest)
    models, model_failures = check_models(manifest)
    guards, guard_failures = check_guards()
    classes, class_failures = check_classes()

    failures = hash_failures + split_failures + model_failures + guard_failures + class_failures
    payload = {
        "status": "PASS" if not failures else "FAIL",
        "python": sys.version,
        "models": models,
        "model_hashes": model_hashes,
        "split_hashes_match_manifest": split_hashes,
        "unicode_checks": {
            "malayalam_detected": guards.get("malayalam_detected"),
            "latin_detected": guards.get("latin_detected"),
            "malayalam_preserved_after_clean": guards.get(
                "malayalam_preserved_after_clean"),
        },
        "input_validation": guards,
        "class_coverage": classes,
        "failures": failures,
        "note": ("No model was fitted or modified. Every frozen test prediction is "
                 "reproduced after record_id alignment, and every model and split "
                 "hash is re-derived from the file bytes."),
    }
    (HERE / "verification_results.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
