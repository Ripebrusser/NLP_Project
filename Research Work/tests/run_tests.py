#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run the code-audit unittest suite and write a machine-readable result file.

Run from the project root:
    .venv/Scripts/python.exe "Research Work/tests/run_tests.py"

Exit status is 0 only when every test passes. Nothing here writes to a dataset,
split, model or frozen prediction file.
"""
from __future__ import annotations

import io
import json
import platform
import sys
import time
import unittest
import warnings
from datetime import datetime, timezone
from pathlib import Path

TESTS = Path(__file__).resolve().parent
PHASE2 = TESTS.parent / "phase2"
OUT = PHASE2 / "metrics" / "code_audit_test_results.json"
for path in (str(TESTS), str(PHASE2), str(TESTS.parent)):
    if path not in sys.path:
        sys.path.insert(0, path)


def main() -> int:
    warnings.simplefilter("always")
    started = time.perf_counter()
    with warnings.catch_warnings(record=True) as caught:
        suite = unittest.defaultTestLoader.discover(
            str(TESTS), pattern="test_*.py", top_level_dir=str(TESTS))
        stream = io.StringIO()
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    duration = time.perf_counter() - started

    failed = [str(test) for test, _ in result.failures]
    errored = [str(test) for test, _ in result.errors]
    skipped = [str(test) for test, _ in result.skipped]
    payload = {
        "status": "PASS" if result.wasSuccessful() else "FAIL",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "command": ('python -m unittest discover -s "Research Work/tests" '
                    '-t "Research Work/tests" -v'),
        "python_version": sys.version,
        "platform": platform.platform(),
        "duration_seconds": round(duration, 2),
        "tests_run": result.testsRun,
        "passed": result.testsRun - len(result.failures) - len(result.errors)
        - len(result.skipped),
        "failed": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "expected_failures": len(result.expectedFailures),
        "unexpected_successes": len(result.unexpectedSuccesses),
        "warnings": len(caught),
        "failed_tests": failed,
        "errored_tests": errored,
        "skipped_tests": skipped,
        "warning_messages": sorted({str(w.message) for w in caught})[:25],
        "log_path": None,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                   encoding="utf-8")
    log_path = OUT.with_suffix(".log")
    log_path.write_text(stream.getvalue(), encoding="utf-8")
    payload["log_path"] = str(log_path)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                   encoding="utf-8")

    print(stream.getvalue())
    print(json.dumps({k: v for k, v in payload.items()
                      if k not in {"warning_messages"}}, indent=2,
                     ensure_ascii=False))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
