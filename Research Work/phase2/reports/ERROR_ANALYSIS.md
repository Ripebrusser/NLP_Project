# Error Analysis — Phase 2

## D1 (Malayalam subset)

| group | n | URL % | digit % | Latin % | mean tokens |
|---|---|---|---|---|---|
| correct | 295 | 2.7 | 13.2 | 25.8 | 11.9 |
| errors | 4 | 0.0 | 50.0 | 50.0 | 10.2 |

All four errors are false negatives (Spam→Ham), so spam precision is 1.000 on this test set. Two are long Onam greeting messages; two are very short one-liners. The model has learned that promotional vocabulary and length are spam signals, and misses short or culturally specific spam.

## D2 (three-class)

| group | n | URL % | digit % | Latin % | mean tokens |
|---|---|---|---|---|---|
| correct | 851 | 2.7 | 27.1 | 100.0 | 15.4 |
| errors | 32 | 12.5 | 75.0 | 100.0 | 20.5 |

The dominant error is **smishing predicted as spam** (15 of 32), followed by **spam predicted as ham** (10). Both classes share promotional SMS cues (shortcodes, “TXT”, prizes, STOP instructions); the distinction is intent, which character n-grams cannot represent. This motivates a transformer with context, and a clearer annotation guide for the spam/smishing boundary.

## Implications

1. Do not report accuracy alone for D1: 88.6% is the majority-class floor.
2. D1’s high random-split score must be paired with the block-held-out result.
3. For D2, report per-class F1; smishing recall and spam F1 are the meaningful metrics.
