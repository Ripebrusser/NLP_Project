#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Train and evaluate Logistic Regression + Linear SVM on the D2 3-class corpus."""
from __future__ import annotations

from p2_modeling import error_examples, fit_and_evaluate, load_splits


def main() -> None:
    train, val, test = load_splits("d2")
    results = fit_and_evaluate(train, val, test, task="multiclass",
                               labels=["ham", "spam", "smishing"], tag="d2")
    err = error_examples(results, "d2", ["ham", "spam", "smishing"])
    print("D2 selected family:", results["overall_model_family"])
    for fam, r in results["models"].items():
        t = r["test"]
        print(f"  {fam}: {r['selected_config']} C={r['C']} "
              f"acc={t['accuracy']:.4f} macroF1={t['macro_f1']:.4f} "
              f"smishing_recall={t['per_class']['smishing']['recall']:.4f}")
    print("  errors:", err["n_errors"], "of", err["n_test"])


if __name__ == "__main__":
    main()
