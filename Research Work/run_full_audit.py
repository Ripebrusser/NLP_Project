#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-command engineering audit for the frozen Phase 2 project.

Runs every independent check, records its status, duration, command and failure
detail, and never stops at the first failure. Writes:

    Research Work/phase2/metrics/full_audit_results.json
    Research Work/phase2/metrics/audit_runs/<run_id>/...   (preserved evidence)

Usage (from the project root):

    .venv/Scripts/python.exe "Research Work/run_full_audit.py"
    .venv/Scripts/python.exe "Research Work/run_full_audit.py" --write-baseline

``--write-baseline`` records the current SHA-256 of every frozen artifact. It is
only used once, before a change window, so later runs can prove that nothing
frozen moved. Normal runs compare against that baseline and never write to a
dataset, split, model, prediction or metric file.

Exit status: 0 only when every required check passes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent          # Research Work/
ROOT = HERE.parent
PHASE2 = HERE / "phase2"
METRICS = PHASE2 / "metrics"
SPLITS = PHASE2 / "splits"
MODELS = PHASE2 / "models"
PROTOTYPE = HERE / "prototype"
ADMIN = ROOT / "Admin"
TESTS = HERE / "tests"

BASELINE = METRICS / "audit_hash_baseline.json"
RESULTS = METRICS / "full_audit_results.json"
RUNS = METRICS / "audit_runs"
MURIL_DIR = MODELS / "muril_d1_seed42"

VERIFICATION_OUTPUTS = (
    PROTOTYPE / "verification_results.json",
    METRICS / "final_verification.json",
    METRICS / "final_audit_stats.json",
)

REQUIRED_FILES = [
    "Admin/FINAL_CODEBASE_INVENTORY.md",
    "Admin/FINAL_CODE_AUDIT_REPORT.md",
    "Admin/FINAL_CODE_FIX_REGISTER.md",
    "Admin/FINAL_TEST_REPORT.md",
    "Admin/FINAL_REPRODUCIBILITY_GUIDE.md",
    "Admin/FINAL_SECURITY_AND_PRIVACY_AUDIT.md",
    "Admin/FINAL_CODE_RISK_REGISTER.md",
    "Admin/ONE_COMMAND_AUDIT_REPORT.md",
    "Admin/FINAL_RELEASE_CHECKLIST.md",
    "Admin/LITERATURE_VERIFICATION_REGISTER.md",
    "Admin/FINAL_LITERATURE_COMPARISON_MATRIX.xlsx",
    "Research Work/requirements-verification.txt",
    "Research Work/run_full_audit.py",
    "Research Work/tests/run_tests.py",
    "Research Work/tests/write_audit_verification.py",
    "Research Work/prototype/app.py",
    "Research Work/prototype/inference.py",
    "Research Work/prototype/verify_prototype.py",
    "Research Work/prototype/model_manifest.json",
    "Research Work/phase2/p2_common.py",
    "Research Work/phase2/p2_stats.py",
    "Research Work/phase2/p2_final_verification.py",
    "Research Work/phase2/p2_final_audit_stats.py",
    "Research Work/phase2/splits/split_manifest.json",
    "Research Work/phase2/metrics/final_model_comparison.csv",
    "Research Work/phase2/metrics/confidence_intervals.json",
]

PINNED_VERSIONS = {
    "numpy": "2.5.4",
    "pandas": "3.1.1",
    "sklearn": "1.9.1",
    "scipy": "1.18.1",
    "joblib": "1.6.0",
    "openpyxl": "3.1.5",
}


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def frozen_paths() -> dict[str, Path]:
    """Every artifact that this audit must never change."""
    paths: dict[str, Path] = {}
    for name in ("Spam Message Collection.xlsx", "Dataset_5971.csv"):
        paths[f"dataset:{name}"] = ROOT / "Datasets" / name
    for path in sorted(SPLITS.glob("*.csv")):
        paths[f"split:{path.name}"] = path
    for path in sorted(MODELS.glob("*.joblib")):
        paths[f"model:{path.name}"] = path
    if MURIL_DIR.exists():
        for path in sorted(p for p in MURIL_DIR.rglob("*") if p.is_file()):
            paths[f"muril:{path.relative_to(MURIL_DIR).as_posix()}"] = path
    for path in sorted(METRICS.glob("*predictions*.csv")):
        paths[f"predictions:{path.name}"] = path
    for name in ("split_manifest.json",):
        paths[f"manifest:{name}"] = SPLITS / name
    paths["manifest:model_manifest.json"] = PROTOTYPE / "model_manifest.json"
    for path in VERIFICATION_OUTPUTS:
        paths[f"verification:{path.name}"] = path
    return paths


def hash_map(paths: dict[str, Path]) -> dict[str, str]:
    out = {}
    for key, path in paths.items():
        out[key] = sha256_file(path) if path.exists() else "MISSING"
    return out


def metric_subset(payload: dict) -> dict:
    """Stable numeric evidence used to prove verification results did not move."""
    def get(obj, *keys, default=None):
        for key in keys:
            if not isinstance(obj, dict) or key not in obj:
                return default
            obj = obj[key]
        return obj

    return {
        "d1_logreg_macro_f1": get(payload, "d1_models", "Logistic Regression",
                                  "metrics", "macro_f1"),
        "d1_svm_macro_f1": get(payload, "d1_models", "Linear SVM",
                               "metrics", "macro_f1"),
        "muril_mean": get(payload, "muril_across_seed", "macro_f1", "mean"),
        "muril_sd": get(payload, "muril_across_seed", "macro_f1", "sd"),
        "block_logreg": get(payload, "d1_block_pooled", "logreg", "macro_f1"),
        "block_svm": get(payload, "d1_block_pooled", "linear_svm", "macro_f1"),
        "block_logreg_spam_recall": get(payload, "d1_block_pooled", "logreg",
                                        "spam_recall"),
        "block_svm_spam_recall": get(payload, "d1_block_pooled", "linear_svm",
                                     "spam_recall"),
    }


def run_script(cmd: list[str], cwd: Path, timeout: int = 900) -> dict:
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    started = time.perf_counter()
    try:
        proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                              encoding="utf-8", errors="replace",
                              timeout=timeout, env=env)
        duration = time.perf_counter() - started
        combined = (proc.stdout or "") + (proc.stderr or "")
        return {
            "returncode": proc.returncode,
            "duration_seconds": round(duration, 2),
            "stdout_tail": (proc.stdout or "")[-6000:],
            "stderr_tail": (proc.stderr or "")[-4000:],
            "output_tail": combined[-4000:],
            "timed_out": False,
        }
    except subprocess.TimeoutExpired:
        return {
            "returncode": None,
            "duration_seconds": round(time.perf_counter() - started, 2),
            "stdout_tail": "", "stderr_tail": f"timed out after {timeout}s",
            "output_tail": f"timed out after {timeout}s", "timed_out": True,
        }


PYTHON = sys.executable


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------
def check_environment() -> tuple[bool, str, dict]:
    import importlib
    failures = []
    versions = {}
    if sys.version_info[:2] != (3, 14):
        failures.append(f"Python {sys.version.split()[0]} (expected 3.14.x)")
    for module, expected in PINNED_VERSIONS.items():
        try:
            actual = importlib.import_module(module).__version__
        except Exception as exc:  # pragma: no cover - environment failure
            failures.append(f"{module}: import failed ({exc})")
            continue
        versions[module] = actual
        if actual != expected:
            failures.append(f"{module} {actual} != {expected}")
    try:
        import streamlit
        versions["streamlit"] = streamlit.__version__
    except Exception as exc:
        failures.append(f"streamlit: import failed ({exc})")
    return (not failures), "; ".join(failures) or "all pinned versions present", {
        "python": sys.version, "versions": versions}


def check_required_files() -> tuple[bool, str, dict]:
    missing = [name for name in REQUIRED_FILES if not (ROOT / name).is_file()]
    empty = [name for name in REQUIRED_FILES
             if (ROOT / name).is_file() and (ROOT / name).stat().st_size == 0]
    ok = not missing and not empty
    detail = ", ".join(missing + [f"{n} (empty)" for n in empty]) or \
        f"{len(REQUIRED_FILES)} required files present"
    return ok, detail, {"missing": missing, "empty": empty,
                        "checked": len(REQUIRED_FILES)}


def check_dataset_integrity() -> tuple[bool, str, dict]:
    import pandas as pd
    manifest = load_json(SPLITS / "split_manifest.json")
    sources = manifest["source_hashes"]
    d1 = ROOT / "Datasets" / "Spam Message Collection.xlsx"
    d2 = ROOT / "Datasets" / "Dataset_5971.csv"
    actual = {"d1": sha256_file(d1), "d2": sha256_file(d2)}
    failures = [f"{k}: hash {actual[k][:12]}… != {sources[k][:12]}…"
                for k in ("d1", "d2") if actual[k] != sources[k]]
    book, english = pd.read_excel(d1), pd.read_csv(d2, encoding="utf-8-sig")
    # The sheet has 7,718 physical rows: 7,717 labelled records plus one fully
    # blank trailer. Labels are Ham/Spam plus one typo ("Spa,").
    labelled = book[book["Type"].notna()]
    type_counts = {str(k): int(v) for k, v in
                   labelled["Type"].value_counts().items()}
    spam_total = sum(v for k, v in type_counts.items()
                     if k.lower().startswith("spa"))
    rows = {"d1_physical_rows": int(len(book)),
            "d1_labelled_records": int(len(labelled)),
            "d1_ham": type_counts.get("Ham"), "d1_spam_incl_typo": spam_total,
            "d2_rows": int(len(english))}
    for key, expected in (("d1_physical_rows", 7718),
                          ("d1_labelled_records", 7717),
                          ("d1_ham", 6322),
                          ("d1_spam_incl_typo", 1395),
                          ("d2_rows", 5971)):
        if rows[key] != expected:
            failures.append(f"{key}={rows[key]} (expected {expected})")
    return (not failures), "; ".join(failures) or "source hashes and row counts match", {
        "hashes": actual, "row_counts": rows}


def check_hashes(which: str) -> tuple[bool, str, dict]:
    if which == "splits":
        manifest = load_json(SPLITS / "split_manifest.json")
        expected = {}
        for dataset in ("d1", "d2"):
            for item in manifest[dataset]["files"]:
                expected[item["file"]] = item["sha256"]
        actual = {name: sha256_file(SPLITS / name) for name in expected}
        bad = [name for name in expected if actual[name] != expected[name]]
        return (not bad), (f"{len(expected)} split hashes match" if not bad
                           else f"mismatch: {bad}"), {"hashes": actual}
    if which == "models":
        manifest = load_json(PROTOTYPE / "model_manifest.json")
        bad, actual = [], {}
        for name, expected in manifest["models"].items():
            path = MODELS / name
            actual[name] = sha256_file(path) if path.exists() else "MISSING"
            if actual[name] != expected:
                bad.append(name)
        return (not bad), (f"{len(manifest['models'])} model hashes match"
                           if not bad else f"mismatch: {bad}"), {"hashes": actual}
    raise ValueError(which)


def check_baseline_hashes() -> tuple[bool, str, dict]:
    if not BASELINE.exists():
        return False, (f"baseline missing: {rel(BASELINE)}; run "
                       "--write-baseline once before the change window"), {}
    baseline = load_json(BASELINE)["hashes"]
    current = hash_map(frozen_paths())
    changed = sorted(k for k in baseline if baseline[k] != current.get(k))
    added = sorted(set(current) - set(baseline))
    ok = not changed and not added
    detail = ("all frozen artifacts byte-identical to baseline"
              if ok else f"changed: {changed}; new: {added}")
    return ok, detail, {"changed": changed, "added": added,
                        "artifact_count": len(baseline)}


def check_browser_evidence() -> tuple[bool, str, dict]:
    path = METRICS / "browser_ui_test_results.json"
    if not path.exists():
        return False, "no recorded browser pass (informational only)", {}
    payload = load_json(path)
    cases = payload.get("results", [])
    failed = [c["case"] for c in cases if c.get("status") != "PASS"]
    ok = payload.get("status") == "PASS" and not failed
    return ok, (f"{len(cases)} browser cases recorded, all PASS" if ok
                else f"browser cases not all passing: {failed}"), {
        "target": payload.get("target"),
        "timestamp_utc": payload.get("timestamp_utc"),
        "cases": len(cases),
        "not_covered": payload.get("not_covered_in_browser", []),
    }


def check_code_risks() -> tuple[bool, str, dict]:
    """Static invariants for the issues this audit closed or documented."""
    import pandas as pd
    sys.path.insert(0, str(PHASE2))
    import p2_common

    results = []

    def record(name, ok, detail):
        results.append({"check": name, "status": "PASS" if ok else "FAIL",
                        "detail": detail})

    manifest = load_json(SPLITS / "split_manifest.json")
    manifest_totals: dict[str, int] = {}
    for entry in manifest["d1"]["blocks"]:
        for block, n in entry["blocks"].items():
            manifest_totals[block] = manifest_totals.get(block, 0) + int(n)
    record("stale_manifest_block_table_preserved",
           manifest_totals == {"4001-5000": 631, "5001-6000": 991,
                               "6001-7000": 370},
           f"frozen manifest still records {manifest_totals} and was not edited")

    counts = {"train": {}, "val": {}, "test": {}}
    for part in counts:
        frame = pd.read_csv(SPLITS / f"d1_malayalam_{part}.csv",
                            encoding="utf-8-sig")
        counts[part] = (frame["source_row"].map(p2_common.block_number)
                        .value_counts().sort_index().to_dict())
    all_counts = {}
    for part, values in counts.items():
        for block, n in values.items():
            all_counts.setdefault(str(block), 0)
            all_counts[str(block)] += int(n)
    record("block_number_formula_correct",
           all_counts == {"5": 630, "6": 991, "7": 371},
           f"recomputed block totals {all_counts} (expected 630/991/371; "
           f"one train row moved out of 4001-5000)")

    split_src = (PHASE2 / "p2_split.py").read_text(encoding="utf-8")
    robust_src = (PHASE2 / "p2_robustness.py").read_text(encoding="utf-8")
    record("block_formula_used_by_writers",
           split_src.count("block_number") >= 2
           and robust_src.count("block_number") >= 2
           and "(source_row - 1) // 1000" not in split_src
           and "(source_row - 1) // 1000" not in robust_src,
           "split/robustness writers import and map p2_common.block_number")

    ci_src = (PHASE2 / "p2_ci.py").read_text(encoding="utf-8")
    record("legacy_ci_cannot_overwrite_canonical",
           "_legacy" in ci_src and "--overwrite-authoritative" in ci_src,
           "p2_ci.py writes *_legacy outputs unless explicitly overridden")

    inf_src = (PROTOTYPE / "inference.py").read_text(encoding="utf-8")
    record("joblib_load_is_hash_guarded",
           "verify_artifact_hash(" in inf_src
           and inf_src.index("verify_artifact_hash(MODEL_FILES[task]")
           < inf_src.index("joblib.load("),
           "artifact SHA-256 is checked before joblib.load")

    verifier_src = (PROTOTYPE / "verify_prototype.py").read_text(encoding="utf-8")
    record("verifier_never_fits",
           ".fit(" not in verifier_src and "train_d1" not in verifier_src,
           "prototype verifier only loads and predicts")

    stats_src = (PHASE2 / "p2_stats.py").read_text(encoding="utf-8")
    record("read_only_scripts_never_fit",
           all(".fit(" not in (PHASE2 / n).read_text(encoding="utf-8")
               for n in ("p2_final_verification.py", "p2_final_audit_stats.py")),
           "verification/statistics scripts do not fit models")

    readme = (PHASE2 / "README.md").read_text(encoding="utf-8")
    record("readme_documents_do_not_rerun",
           "Do not rerun" in readme and "p2_split.py" in readme,
           "Phase 2 README lists the scripts that must not be rerun")

    record("norm_key_url_placeholder_documented",
           "url" in p2_common.norm_key("see https://example.com/x")
           and "norm_key" in (ADMIN / "FINAL_CODE_RISK_REGISTER.md")
           .read_text(encoding="utf-8"),
           "URL placeholder behaviour is documented as a frozen-artifact limitation")

    record("stats_authoritative_documented",
           "authoritative" in stats_src or "authoritative" in readme,
           "p2_stats.py is documented as authoritative over p2_ci.py")

    failed = [r for r in results if r["status"] == "FAIL"]
    return (not failed), (f"{len(results)} code-risk invariants checked"
                          if not failed else
                          f"failed: {[r['check'] for r in failed]}"), {
        "invariants": results}


def check_verification_stability(before: dict) -> tuple[bool, str, dict]:
    after = {path.name: metric_subset(load_json(path))
             for path in (METRICS / "final_verification.json",
                          METRICS / "final_audit_stats.json")}
    diffs = []
    for name, values in after.items():
        old = before.get(name, {})
        for key, value in values.items():
            if old.get(key) != value:
                diffs.append(f"{name}.{key}: {old.get(key)} -> {value}")
    ok = not diffs
    return ok, ("frozen metrics identical before and after the audit"
                if ok else "; ".join(diffs)), {"before": before, "after": after}


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-baseline", action="store_true",
                        help="record current frozen-artifact hashes and exit")
    parser.add_argument("--skip-tests", action="store_true",
                        help="skip the regression suite (diagnostics only)")
    args = parser.parse_args()

    if args.write_baseline:
        payload = {
            "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "note": ("Baseline for the engineering-closure audit. Any change to a "
                     "frozen artifact after this point fails the audit."),
            "hashes": hash_map(frozen_paths()),
        }
        BASELINE.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                            encoding="utf-8")
        print(f"wrote {rel(BASELINE)} with {len(payload['hashes'])} artifacts")
        for key, value in payload["hashes"].items():
            print(f"  {value[:16]}…  {key}")
        return 0

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = RUNS / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    preserved = {}
    for path in VERIFICATION_OUTPUTS:
        if path.exists():
            preserved[path.name] = path.read_bytes()
            (run_dir / f"{path.stem}.before.json").write_bytes(preserved[path.name])
    before_metrics = {
        path.name: metric_subset(load_json(path))
        for path in (METRICS / "final_verification.json",
                     METRICS / "final_audit_stats.json")
        if path.exists()
    }

    checks: list[dict] = []

    def add(check_id: str, title: str, fn, required: bool = True,
            command: str | None = None):
        started = time.perf_counter()
        try:
            ok, detail, extra = fn()
        except Exception as exc:  # a broken check must not abort the audit
            ok, detail = False, f"{type(exc).__name__}: {exc}"
            extra = {"traceback": traceback.format_exc()[-3000:]}
        duration = round(time.perf_counter() - started, 2)
        checks.append({
            "id": check_id, "title": title, "required": required,
            "status": "PASS" if ok else "FAIL",
            "detail": detail, "duration_seconds": duration,
            "command": command, "evidence": extra,
        })
        print(f"[{'PASS' if ok else 'FAIL'}] {check_id}: {detail} "
              f"({duration:.1f}s)", flush=True)
        return ok

    add("environment", "Python and pinned dependency versions",
        check_environment)
    add("required_files", "Required deliverables and canonical files exist",
        check_required_files)
    add("dataset_integrity", "Dataset hashes and row counts",
        check_dataset_integrity)
    add("split_hashes", "Frozen split hashes match the manifest",
        lambda: check_hashes("splits"))
    add("model_hashes", "Classical model hashes match the manifest",
        lambda: check_hashes("models"))
    add("baseline_hashes", "All frozen artifacts match the pre-audit baseline",
        check_baseline_hashes)

    scripts = [
        ("regression_tests", "114+ regression tests",
         [PYTHON, str(TESTS / "run_tests.py")], ROOT,
         f'PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe '
         f'"Research Work/tests/run_tests.py"'),
        ("frozen_predictions", "Frozen-prediction verification",
         [PYTHON, "p2_final_verification.py"], PHASE2,
         "cd \"Research Work/phase2\" && PYTHONIOENCODING=utf-8 "
         "../../.venv/Scripts/python.exe p2_final_verification.py"),
        ("statistical_audit", "Independent statistical audit",
         [PYTHON, "p2_final_audit_stats.py"], PHASE2,
         "cd \"Research Work/phase2\" && PYTHONIOENCODING=utf-8 "
         "../../.venv/Scripts/python.exe p2_final_audit_stats.py"),
        ("prototype_verification", "Prototype parity and frozen hashes",
         [PYTHON, str(PROTOTYPE / "verify_prototype.py")], ROOT,
         "PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe "
         "\"Research Work/prototype/verify_prototype.py\""),
        ("literature_validation", "Literature matrix validation",
         [PYTHON, str(HERE / "validate_literature_matrix.py")], ROOT,
         "PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe "
         "\"Research Work/validate_literature_matrix.py\""),
    ]
    if args.skip_tests:
        scripts = [s for s in scripts if s[0] != "regression_tests"]

    for check_id, title, cmd, cwd, displayed in scripts:
        started = time.perf_counter()
        outcome = run_script(cmd, cwd)
        ok = outcome["returncode"] == 0
        detail = (f"exit {outcome['returncode']}" if ok
                  else (outcome["output_tail"][-600:]
                        or f"exit {outcome['returncode']}"))
        checks.append({
            "id": check_id, "title": title, "required": True,
            "status": "PASS" if ok else "FAIL", "detail": detail,
            "duration_seconds": round(time.perf_counter() - started, 2),
            "command": displayed, "evidence": outcome,
        })
        print(f"[{'PASS' if ok else 'FAIL'}] {check_id}: {detail[:160]} "
              f"({outcome['duration_seconds']:.1f}s)", flush=True)

    add("browser_ui_evidence", "Recorded browser pass (informational)",
        check_browser_evidence, required=False)
    add("code_risk_checks", "Documented code-risk invariants", check_code_risks)
    add("verification_stability", "Frozen metrics unchanged by the audit run",
        lambda: check_verification_stability(before_metrics))

    # restore the preserved verification outputs byte-for-byte: the audit may
    # read them, but it must not leave them modified.
    restored = []
    for path in VERIFICATION_OUTPUTS:
        if path.name in preserved:
            path.write_bytes(preserved[path.name])
            restored.append(rel(path))
    after_hashes = hash_map(frozen_paths())
    baseline = load_json(BASELINE)["hashes"] if BASELINE.exists() else {}
    changed_now = sorted(k for k in baseline
                         if baseline[k] != after_hashes.get(k))
    checks.append({
        "id": "post_run_hash_stability",
        "title": "No frozen artifact changed during the audit run",
        "required": True,
        "status": "PASS" if not changed_now else "FAIL",
        "detail": ("all frozen artifacts identical to the baseline after the run"
                   if not changed_now else f"changed during run: {changed_now}"),
        "duration_seconds": 0.0,
        "command": None,
        "evidence": {"restored_outputs": restored,
                     "changed": changed_now},
    })
    print(f"[{'PASS' if not changed_now else 'FAIL'}] post_run_hash_stability: "
          f"{checks[-1]['detail']}", flush=True)

    required = [c for c in checks if c["required"]]
    failed = [c for c in required if c["status"] != "PASS"]
    payload = {
        "audit": "engineering closure — one-command audit",
        "run_id": run_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "PASS" if not failed else "FAIL",
        "python": sys.version,
        "platform": platform.platform(),
        "command": (f'{rel(Path(PYTHON))} "Research Work/run_full_audit.py"'),
        "summary": {
            "checks_total": len(checks),
            "checks_passed": len(checks) - len([c for c in checks
                                                if c["status"] != "PASS"]),
            "checks_failed": len([c for c in checks if c["status"] != "PASS"]),
            "required_failed": [c["id"] for c in failed],
            "duration_seconds": round(sum(c["duration_seconds"] for c in checks), 1),
        },
        "checks": checks,
        "frozen_artifacts_unchanged": not changed_now,
        "baseline_path": rel(BASELINE),
        "preserved_outputs_dir": rel(run_dir),
        "run_directory": rel(run_dir),
    }
    RESULTS.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                       encoding="utf-8")
    (run_dir / "full_audit_results.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n=== SUMMARY ===")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    print(f"status={payload['status']}  results={rel(RESULTS)}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
