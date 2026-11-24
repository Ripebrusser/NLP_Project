#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Train and evaluate Logistic Regression + Linear SVM on the D1 Malayalam subset."""
from __future__ import annotations

from p2_modeling import error_examples, fit_and_evaluate, load_splits


def main() -> None:
    train, val, test = load_splits("d1_malayalam")
    results = fit_and_evaluate(train, val, test, task="binary",
                               labels=["Ham", "Spam"], tag="d1_malayalam")
    err = error_examples(results, "d1_malayalam", ["Ham", "Spam"])
    print("D1 selected family:", results["overall_model_family"])
    for fam, r in results["models"].items():
        t = r["test"]
        print(f"  {fam}: {r['selected_config']} C={r['C']} "
              f"acc={t['accuracy']:.4f} macroF1={t['macro_f1']:.4f} "
              f"spam_recall={t['spam_recall']:.4f} spam_prec={t['spam_precision']:.4f}")
    print("  errors:", err["n_errors"], "of", err["n_test"])
    if "malayalam_only_subgroup" in results:
        s = results["malayalam_only_subgroup"]
        print(f"  malayalam-only subgroup: n={s['rows']} spam_recall={s['metrics']['spam_recall']:.3f}")


if __name__ == "__main__":
    main()
