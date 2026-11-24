"""Shared fixtures and paths for the code-audit test suite.

Tests read frozen artifacts only. No test writes to a dataset, split, model or
prediction file; the two literature tests that need a corrupted copy write to a
temporary directory.
"""
from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path

import pandas as pd

TESTS = Path(__file__).resolve().parent
RESEARCH = TESTS.parent
ROOT = RESEARCH.parent
PHASE2 = RESEARCH / "phase2"
SPLITS = PHASE2 / "splits"
METRICS = PHASE2 / "metrics"
MODELS = PHASE2 / "models"
PROTOTYPE = RESEARCH / "prototype"

for _p in (str(PHASE2), str(RESEARCH), str(PROTOTYPE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

D1_LABELS = ["Ham", "Spam"]
D2_LABELS = ["ham", "spam", "smishing"]


@lru_cache(maxsize=None)
def _split_cached(name: str) -> pd.DataFrame:
    return pd.read_csv(SPLITS / name, encoding="utf-8-sig")


def split(name: str) -> pd.DataFrame:
    """A copy of a frozen split file."""
    return _split_cached(name).copy()


@lru_cache(maxsize=None)
def _prediction_cached(name: str) -> pd.DataFrame:
    return pd.read_csv(METRICS / name, encoding="utf-8-sig")


def prediction(name: str) -> pd.DataFrame:
    """A copy of a frozen prediction file."""
    return _prediction_cached(name).copy()


@lru_cache(maxsize=None)
def split_manifest() -> dict:
    return json.loads((SPLITS / "split_manifest.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def model_manifest() -> dict:
    return json.loads((PROTOTYPE / "model_manifest.json").read_text(encoding="utf-8"))
