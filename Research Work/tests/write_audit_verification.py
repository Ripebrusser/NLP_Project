#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Assemble the machine-readable evidence bundle for the code audit.

Reads the outputs of the test suite, the prototype verifier, the literature
validator and the two statistical verification scripts, re-derives every frozen
hash, and checks the canonical results against their published values. Writes
``Research Work/phase2/metrics/code_audit_verification.json``.

Exit status is 0 only when every check passes. No dataset, split, model or
prediction file is written.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
ROOT = RESEARCH.parent
PHASE2 = RESEARCH / "phase2"
METRICS = PHASE2 / "metrics"
SPLITS = PHASE2 / "splits"
PROTOTYPE = RESEARCH / "prototype"
OUT = METRICS / "code_audit_verification.json"

for path in (str(HERE), str(RESEARCH), str(PHASE2)):
    if path not in sys.path:
        sys.path.insert(0, path)

import validate_literature_matrix as vlm  # noqa: E402

PREDICTION_FILES = (
    "d1_malayalam_logreg_test_predictions.csv",
    "d1_malayalam_linear_svm_test_predictions.csv",
    "muril_random_seed42_predictions.csv",
    "muril_random_seed43_predictions.csv",
    "muril_random_seed44_predictions.csv",
    "d2_logreg_test_predictions.csv",
    "d2_linear_svm_test_predictions.csv",
    "block_cv_predictions.csv",
)

# Published canonical values; a drift beyond the tolerance fails the bundle.
CANONICAL = {
    "d1_logreg_random_macro_f1": 0.9556,
    "d1_svm_random_macro_f1": 0.9650,
    "d1_muril_random_macro_f1_mean": 0.9619,
    "d1_muril_random_macro_f1_sd": 0.0054,
    "d1_logreg_block_macro_f1": 0.5448,
    "d1_svm_block_macro_f1": 0.5378,
    "d1_muril_block_macro_f1_mean": 0.5028,
    "d1_logreg_block_spam_recall": 0.0889,
    "d1_svm_block_spam_recall": 0.0756,
    "d1_muril_block_spam_recall_mean": 0.0356,
}
TOLERANCE = {"d1_muril_random_macro_f1_sd": 5e-4}
DEFAULT_TOLERANCE = 5e-5


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    failures: list[str] = []
    tests = load(METRICS / "code_audit_test_results.json")
    proto = load(PROTOTYPE / "verification_results.json")
    fv = load(METRICS / "final_verification.json")
    fas = load(METRICS / "final_audit_stats.json")
    split_manifest = load(SPLITS / "split_manifest.json")
    model_manifest = load(PROTOTYPE / "model_manifest.json")
    literature = vlm.validate()

    split_hashes = {}
    for dataset in ("d1", "d2"):
        for item in split_manifest[dataset]["files"]:
            actual = sha256(SPLITS / item["file"])
            split_hashes[item["file"]] = {
                "expected": item["sha256"], "actual": actual,
                "match": actual == item["sha256"],
            }
            if actual != item["sha256"]:
                failures.append(f"split hash mismatch: {item['file']}")

    model_hashes = {}
    for filename, expected in model_manifest["models"].items():
        actual = sha256(PHASE2 / "models" / filename)
        model_hashes[filename] = {
            "expected": expected, "actual": actual, "match": actual == expected,
        }
        if actual != expected:
            failures.append(f"model hash mismatch: {filename}")

    prediction_hashes = {}
    for name in PREDICTION_FILES:
        path = METRICS / name
        if not path.exists():
            failures.append(f"missing prediction file: {name}")
            continue
        prediction_hashes[name] = {"sha256": sha256(path),
                                   "bytes": path.stat().st_size}

    for dataset, name in (("d1", "Spam Message Collection.xlsx"),
                          ("d2", "Dataset_5971.csv")):
        actual = sha256(ROOT / "Datasets" / name)
        if actual != split_manifest["source_hashes"][dataset]:
            failures.append(f"source hash mismatch: {name}")

    muril_block = [fas["d1_block_pooled"][f"MuRIL seed {seed}"]
                   for seed in (42, 43, 44)]
    canonical = {
        "d1_logreg_random_macro_f1":
            fv["d1_models"]["Logistic Regression"]["metrics"]["macro_f1"],
        "d1_svm_random_macro_f1":
            fv["d1_models"]["Linear SVM"]["metrics"]["macro_f1"],
        "d1_muril_random_macro_f1_mean": fv["muril_across_seed"]["macro_f1"]["mean"],
        "d1_muril_random_macro_f1_sd": fv["muril_across_seed"]["macro_f1"]["sd"],
        "d1_logreg_block_macro_f1": fas["d1_block_pooled"]["logreg"]["macro_f1"],
        "d1_svm_block_macro_f1": fas["d1_block_pooled"]["linear_svm"]["macro_f1"],
        "d1_muril_block_macro_f1_mean":
            sum(r["macro_f1"] for r in muril_block) / 3,
        "d1_logreg_block_spam_recall":
            fas["d1_block_pooled"]["logreg"]["spam_recall"],
        "d1_svm_block_spam_recall":
            fas["d1_block_pooled"]["linear_svm"]["spam_recall"],
        "d1_muril_block_spam_recall_mean":
            sum(r["spam_recall"] for r in muril_block) / 3,
    }
    canonical_check = {}
    for key, published in CANONICAL.items():
        actual = float(canonical[key])
        tolerance = TOLERANCE.get(key, DEFAULT_TOLERANCE)
        ok = abs(actual - published) <= tolerance
        canonical_check[key] = {
            "published": published, "recomputed": actual,
            "tolerance": tolerance, "match": ok,
        }
        if not ok:
            failures.append(f"canonical metric drift: {key} {actual} vs {published}")

    paired = fas["paired_d1"]
    pair_ok = abs(
        paired["LR_minus_SVM_macro_f1"]["difference"]
        + paired["SVM_minus_LR_macro_f1"]["difference"]
    ) < 1e-12
    if not pair_ok:
        failures.append("paired LR/SVM differences are not exact negations")

    status_checks = {
        "tests_passed": tests.get("status") == "PASS"
        and tests.get("failed", 1) == 0 and tests.get("errors", 1) == 0,
        "prototype_verifier_passed": proto.get("status") == "PASS",
        "literature_validation_passed": literature.get("status") == "PASS",
        "all_split_hashes_match": all(v["match"] for v in split_hashes.values()),
        "all_model_hashes_match": all(v["match"] for v in model_hashes.values()),
        "canonical_metrics_match": all(v["match"] for v in canonical_check.values()),
        "paired_direction_consistent": pair_ok,
    }
    for name, ok in status_checks.items():
        if not ok:
            failures.append(f"check failed: {name}")

    payload = {
        "audit": "final code audit",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python": sys.version,
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "checks": status_checks,
        "tests": {
            "tests_run": tests.get("tests_run"),
            "passed": tests.get("passed"),
            "failed": tests.get("failed"),
            "errors": tests.get("errors"),
            "skipped": tests.get("skipped"),
            "warnings": tests.get("warnings"),
            "duration_seconds": tests.get("duration_seconds"),
            "command": tests.get("command"),
        },
        "literature": literature,
        "prototype": {
            "status": proto.get("status"),
            "model_hashes": proto.get("model_hashes"),
            "split_hashes": proto.get("split_hashes_match_manifest"),
            "models": proto.get("models"),
            "input_validation": proto.get("input_validation"),
            "failures": proto.get("failures"),
        },
        "canonical_metrics": canonical,
        "canonical_check": canonical_check,
        "paired_d1_macro_f1": {
            "LR_minus_SVM": paired["LR_minus_SVM_macro_f1"],
            "SVM_minus_LR": paired["SVM_minus_LR_macro_f1"],
        },
        "frozen_artifacts": {
            "split_hashes": split_hashes,
            "model_hashes": model_hashes,
            "prediction_hashes": prediction_hashes,
            "source_hashes": split_manifest["source_hashes"],
            "note": ("Prediction and source hashes are recorded, not compared to a "
                     "pre-audit manifest (none existed). The audit scripts open "
                     "them read-only; model and split hashes are compared to the "
                     "recorded baselines."),
        },
        "preserved_pre_audit_outputs": {
            name: (PROTOTYPE / name).exists() for name in
            ("verification_results.before_code_audit.json",)
        } | {
            name: (METRICS / name).exists() for name in
            ("final_verification.before_code_audit.json",
             "final_audit_stats.before_code_audit.json")
        },
        "environment": {
            "python": "3.14.3",
            "numpy": "2.5.4", "pandas": "3.1.1", "scikit-learn": "1.9.1",
            "scipy": "1.18.1", "joblib": "1.6.0", "openpyxl": "3.1.5",
            "streamlit": "1.67.0", "torch": "2.11.0+cu128",
            "transformers": "5.22.1",
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                   encoding="utf-8")
    print(json.dumps({"status": payload["status"],
                      "checks": status_checks,
                      "failures": failures,
                      "out": str(OUT)}, indent=2, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
