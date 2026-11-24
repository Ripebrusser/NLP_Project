#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase 2.2 Part B/C: MuRIL fine-tuning on Dataset 1 (Ham vs Spam).

- Uses the frozen Phase 2 splits; verifies their SHA-256 before training.
- Early stopping on validation macro-F1 only for the random-split runs.
- Test is evaluated once per seed after the best validation epoch.
- Block-held-out folds reuse the epoch count selected for that seed on the
  random validation split; the held-out block is never used for stopping,
  tuning or threshold selection.
- Saves one reference model (first seed) plus tokenizer; all per-seed metrics,
  predictions and histories are saved separately.

Run:
    ./.venv/Scripts/python.exe "Research Work/phase2/p2_muril.py" --seeds 42 43 44
"""
from __future__ import annotations

import argparse
import gc
import json
import logging
import random
import time

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_recall_fscore_support)
from torch.utils.data import DataLoader, Dataset
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          get_linear_schedule_with_warmup)

from p2_common import METRICS, MODELS, SPLITS, sha256_file

MODEL_NAME = "google/muril-base-cased"
LABELS = ["Ham", "Spam"]
L2I = {"Ham": 0, "Spam": 1}
LOG = logging.getLogger("muril")


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


class Encoded(Dataset):
    def __init__(self, enc):
        self.enc = enc

    def __len__(self):
        return self.enc["input_ids"].shape[0]

    def __getitem__(self, i):
        return {k: v[i] for k, v in self.enc.items()}


def encode(tokenizer, texts, max_len: int):
    return tokenizer(list(texts), truncation=True, max_length=max_len,
                     padding="max_length", return_tensors="pt")


def binary_metrics(y_true, y_pred) -> dict:
    p, r, f, s = precision_recall_fscore_support(
        y_true, y_pred, labels=[0, 1], zero_division=0)
    out = {
        "n": int(len(y_true)),
        "ham_support": int(s[0]), "spam_support": int(s[1]),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "ham_precision": float(p[0]), "ham_recall": float(r[0]), "ham_f1": float(f[0]),
        "spam_precision": float(p[1]) if s[1] else None,
        "spam_recall": float(r[1]) if s[1] else None,
        "spam_f1": float(f[1]) if s[1] else None,
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=[0, 1]).tolist(),
        "labels": LABELS,
        "evaluable_for_spam": bool(s[1] > 0),
    }
    return out


@torch.no_grad()
def predict(model, loader, device) -> tuple[np.ndarray, np.ndarray]:
    model.eval()
    probs, ys = [], []
    for batch in loader:
        y = batch.pop("labels")
        batch = {k: v.to(device, non_blocking=True) for k, v in batch.items()}
        with torch.amp.autocast("cuda", dtype=torch.float16):
            logits = model(**batch).logits
        probs.append(torch.softmax(logits.float(), dim=-1).cpu().numpy())
        ys.append(y.numpy())
    return np.concatenate(probs), np.concatenate(ys)


def make_loader(tokenizer, texts, labels, max_len, batch, shuffle, seed=0):
    enc = encode(tokenizer, texts, max_len)
    enc["labels"] = torch.tensor(np.asarray(labels), dtype=torch.long)
    gen = torch.Generator()
    gen.manual_seed(seed)
    return DataLoader(Encoded(enc), batch_size=batch, shuffle=shuffle,
                      num_workers=0, pin_memory=True, generator=gen)


def class_weights(y: np.ndarray, cap: float = 10.0) -> torch.Tensor:
    counts = np.bincount(y, minlength=2).astype(float)
    w = len(y) / (2.0 * np.maximum(counts, 1.0))
    w = np.minimum(w, cap)
    return torch.tensor(w, dtype=torch.float32)


def train_once(train_df, val_df, test_df, seed, args, tokenizer, tag,
               fixed_epochs=None, save_model=False) -> dict:
    set_seed(seed)
    device = torch.device("cuda")
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME, num_labels=2).to(device)
    train_loader = make_loader(tokenizer, train_df["text"], train_df["label"].map(L2I),
                               args.max_len, args.batch, True, seed)
    val_loader = (make_loader(tokenizer, val_df["text"], val_df["label"].map(L2I),
                              args.max_len, args.eval_batch, False)
                  if val_df is not None and len(val_df) else None)
    test_loader = (make_loader(tokenizer, test_df["text"], test_df["label"].map(L2I),
                               args.max_len, args.eval_batch, False)
                   if test_df is not None and len(test_df) else None)

    weights = class_weights(train_df["label"].map(L2I).to_numpy(), cap=args.weight_cap).to(device)
    criterion = nn.CrossEntropyLoss(weight=weights)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    epochs = int(fixed_epochs if fixed_epochs is not None else args.epochs)
    steps_per_epoch = (len(train_loader) + args.accum - 1) // args.accum
    total_steps = max(1, steps_per_epoch * epochs)
    scheduler = get_linear_schedule_with_warmup(
        optimizer, int(0.1 * total_steps), total_steps)
    scaler = torch.amp.GradScaler("cuda")
    best_f1, best_epoch, best_state = -1.0, -1, None
    history = []
    started = time.perf_counter()

    for epoch in range(1, epochs + 1):
        model.train()
        running = 0.0
        optimizer.zero_grad(set_to_none=True)
        for step, batch in enumerate(train_loader):
            y = batch.pop("labels").to(device, non_blocking=True)
            batch = {k: v.to(device, non_blocking=True) for k, v in batch.items()}
            with torch.amp.autocast("cuda", dtype=torch.float16):
                logits = model(**batch).logits
                loss = criterion(logits, y) / args.accum
            scaler.scale(loss).backward()
            running += float(loss.detach()) * y.size(0) * args.accum
            if (step + 1) % args.accum == 0 or (step + 1) == len(train_loader):
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad(set_to_none=True)
                scheduler.step()

        row = {"epoch": epoch, "train_loss": running / len(train_df)}
        if val_loader is not None:
            prob, yv = predict(model, val_loader, device)
            m = binary_metrics(yv, prob.argmax(1))
            row.update({"val_accuracy": m["accuracy"], "val_macro_f1": m["macro_f1"],
                        "val_spam_recall": m["spam_recall"],
                        "val_spam_precision": m["spam_precision"]})
            if m["macro_f1"] > best_f1:
                best_f1, best_epoch = m["macro_f1"], epoch
                best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            LOG.info("%s seed=%d epoch=%d loss=%.4f val_macro_f1=%.4f val_spam_recall=%.4f",
                     tag, seed, epoch, row["train_loss"], m["macro_f1"], m["spam_recall"])
            if epoch - best_epoch >= args.patience:
                history.append(row)
                LOG.info("%s seed=%d early stop at epoch %d (best %d)", tag, seed, epoch, best_epoch)
                break
        history.append(row)

    if best_state is not None:
        model.load_state_dict(best_state)

    result = {"tag": tag, "seed": seed, "epochs_run": len(history),
              "selected_epoch": int(best_epoch if fixed_epochs is None else epochs),
              "history": history,
              "train_seconds": round(time.perf_counter() - started, 2),
              "max_gpu_memory_mb": round(torch.cuda.max_memory_allocated() / 1e6, 1),
              "n_train": int(len(train_df)), "n_val": int(len(val_df) if val_df is not None else 0),
              "n_test": int(len(test_df) if test_df is not None else 0),
              "train_spam": int((train_df["label"] == "Spam").sum()),
              "class_weights": weights.detach().cpu().tolist()}

    if test_loader is not None:
        prob, yt = predict(model, test_loader, device)
        pred = prob.argmax(1)
        result["test"] = binary_metrics(yt, pred)
        result["predictions"] = [
            {"record_id": rid, "source_row": int(sr), "label": LABELS[y],
             "prediction": LABELS[p], "prob_spam": float(pr)}
            for rid, sr, y, p, pr in zip(test_df["record_id"], test_df["source_row"],
                                         yt, pred, prob[:, 1])]

    if save_model:
        out = MODELS / f"muril_d1_seed{seed}"
        out.mkdir(parents=True, exist_ok=True)
        model.save_pretrained(out)
        tokenizer.save_pretrained(out)
        result["saved_model"] = f"models/{out.name}"

    if torch.cuda.is_available():
        torch.cuda.synchronize()
    del model, optimizer, train_loader, val_loader, test_loader, best_state
    gc.collect()
    torch.cuda.empty_cache()
    return result


def verify_splits() -> dict:
    manifest = json.load(open(SPLITS / "split_manifest.json", encoding="utf-8"))
    checks = []
    for p in ("train", "val", "test"):
        f = SPLITS / f"d1_malayalam_{p}.csv"
        recorded = next(x["sha256"] for x in manifest["d1"]["files"] if x["file"] == f.name)
        digest = sha256_file(f)
        checks.append({"split": p, "file": f.name, "sha256": digest,
                       "hash_ok": digest == recorded,
                       "rows": int(len(pd.read_csv(f, encoding="utf-8-sig")))})
    if not all(c["hash_ok"] for c in checks):
        raise SystemExit("split hash mismatch; refusing to train")
    return {"manifest_hash_ok": True, "checks": checks}


def aggregate(runs: list[dict]) -> dict:
    keys = ["accuracy", "macro_f1", "spam_precision", "spam_recall", "spam_f1", "ham_f1"]
    out = {}
    for k in keys:
        vals = [r["test"][k] for r in runs if r.get("test", {}).get(k) is not None]
        if vals:
            out[k] = {"mean": float(np.mean(vals)),
                      "sd": float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0,
                      "values": vals}
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="+", type=int, default=[42, 43, 44])
    ap.add_argument("--epochs", type=int, default=6)
    ap.add_argument("--patience", type=int, default=2)
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--accum", type=int, default=2)
    ap.add_argument("--eval-batch", type=int, default=32)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--max-len", type=int, default=128)
    ap.add_argument("--weight-cap", type=float, default=10.0)
    ap.add_argument("--skip-block", action="store_true")
    args = ap.parse_args()

    logs = MODELS.parent / "logs"
    logs.mkdir(exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        handlers=[logging.FileHandler(logs / f"muril_{stamp}.log", encoding="utf-8"),
                  logging.StreamHandler()])
    LOG.info("args %s", vars(args))

    verification = verify_splits()
    LOG.info("split hashes verified: %s", verification)

    frames = {p: pd.read_csv(SPLITS / f"d1_malayalam_{p}.csv", encoding="utf-8-sig")
              for p in ("train", "val", "test")}
    for p, df in frames.items():
        LOG.info("%s rows=%d ids=%s..%s spam=%d groups=%d", p, len(df),
                 df["record_id"].iloc[0], df["record_id"].iloc[-1],
                 int((df["label"] == "Spam").sum()), df["group_id"].nunique())

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    all_texts = pd.concat(frames.values())["text"]
    lengths = np.array([len(tokenizer.encode(t, add_special_tokens=True)) for t in all_texts])
    length_stats = {
        "n": int(len(lengths)), "mean": round(float(lengths.mean()), 2),
        "median": float(np.median(lengths)), "p90": float(np.percentile(lengths, 90)),
        "p95": float(np.percentile(lengths, 95)), "p99": float(np.percentile(lengths, 99)),
        "max": int(lengths.max()), "max_len_used": args.max_len,
        "coverage_at_max_len": round(float((lengths <= args.max_len).mean()), 4),
        "coverage_64": round(float((lengths <= 64).mean()), 4),
        "coverage_96": round(float((lengths <= 96).mean()), 4),
    }
    LOG.info("token lengths %s", length_stats)

    full = pd.concat(frames.values(), ignore_index=True)
    full["block"] = ((full["source_row"].astype(int) - 1) // 1000) + 1
    block_frames = {int(b): g for b, g in full.groupby("block")}

    random_runs, block_runs = [], []
    for seed in args.seeds:
        LOG.info("=== random split seed %d ===", seed)
        r = train_once(frames["train"], frames["val"], frames["test"], seed, args,
                       tokenizer, "random", save_model=(seed == args.seeds[0]))
        random_runs.append(r)
        pd.DataFrame(r["predictions"]).to_csv(
            METRICS / f"muril_random_seed{seed}_predictions.csv", index=False,
            encoding="utf-8-sig")
        LOG.info("random seed=%d acc=%.4f macro_f1=%.4f spam_recall=%.4f time=%.1fs mem=%.0fMB",
                 seed, r["test"]["accuracy"], r["test"]["macro_f1"],
                 r["test"]["spam_recall"], r["train_seconds"], r["max_gpu_memory_mb"])

        if args.skip_block:
            continue
        epochs_for_fold = r["selected_epoch"]
        for b, held in block_frames.items():
            start, end = (b - 1) * 1000 + 1, b * 1000
            train = pd.concat([g for k, g in block_frames.items() if k != b])
            LOG.info("=== block %d-%d seed %d (fixed %d epochs) train n=%d spam=%d test n=%d spam=%d ===",
                     start, end, seed, epochs_for_fold,
                     len(train), int((train["label"] == "Spam").sum()),
                     len(held), int((held["label"] == "Spam").sum()))
            br = train_once(train, None, held, seed, args, tokenizer,
                            f"block_{start}_{end}", fixed_epochs=epochs_for_fold)
            br["held_out_block"] = f"{start}-{end}"
            block_runs.append(br)
            pd.DataFrame(br["predictions"]).to_csv(
                METRICS / f"muril_block{start}_seed{seed}_predictions.csv",
                index=False, encoding="utf-8-sig")
            LOG.info("block %s seed=%d acc=%.4f macro_f1=%.4f spam_recall=%s time=%.1fs",
                     br["held_out_block"], seed, br["test"]["accuracy"],
                     br["test"]["macro_f1"], br["test"]["spam_recall"],
                     br["train_seconds"])

    per_seed_block = []
    for seed in args.seeds:
        rows = [r for r in block_runs if r["seed"] == seed]
        if not rows:
            continue
        pred = pd.concat([pd.DataFrame(r["predictions"]) for r in rows])
        m = binary_metrics(pred["label"].map(L2I), pred["prediction"].map(L2I))
        per_seed_block.append({"seed": seed, "pooled": m,
                               "folds": [{**{k: r["test"][k] for k in
                                             ("accuracy", "macro_f1", "spam_precision",
                                              "spam_recall", "confusion_matrix",
                                              "spam_support", "ham_support")},
                                          "held_out_block": r["held_out_block"]}
                                         for r in rows]})
        LOG.info("block pooled seed=%d macro_f1=%.4f spam_recall=%.4f",
                 seed, m["macro_f1"], m["spam_recall"])

    pooled_metric = {}
    for k in ("accuracy", "macro_f1", "spam_precision", "spam_recall", "spam_f1"):
        vals = [r["pooled"][k] for r in per_seed_block if r["pooled"].get(k) is not None]
        if vals:
            pooled_metric[k] = {"mean": float(np.mean(vals)),
                                "sd": float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0,
                                "values": vals}

    results = {
        "model_name": MODEL_NAME,
        "tokenizer": MODEL_NAME,
        "max_len": args.max_len,
        "token_lengths": length_stats,
        "hyperparameters": {"lr": args.lr, "batch": args.batch, "accum": args.accum,
                            "effective_batch": args.batch * args.accum, "epochs_max": args.epochs,
                            "patience": args.patience, "weight_decay": 0.01,
                            "warmup_fraction": 0.1, "weight_cap": args.weight_cap,
                            "seeds": args.seeds, "fp16": True},
        "split_verification": verification,
        "random_split": {"runs": random_runs, "aggregate": aggregate(random_runs)},
        "block_held_out": {"runs": block_runs, "per_seed_pooled": per_seed_block,
                           "aggregate_pooled": pooled_metric},
        "versions": {"torch": torch.__version__,
                     "transformers": __import__("transformers").__version__,
                     "cuda": torch.version.cuda, "gpu": torch.cuda.get_device_name(0)},
        "notes": ("Per-seed early stopping uses validation macro-F1 only. Block folds use the "
                  "epoch count selected for that seed on the random validation split and never "
                  "use the held-out block for stopping or tuning. Test/held-out predictions are "
                  "evaluated once per seed."),
    }
    (METRICS / "muril_results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    LOG.info("wrote %s", METRICS / "muril_results.json")


if __name__ == "__main__":
    main()
