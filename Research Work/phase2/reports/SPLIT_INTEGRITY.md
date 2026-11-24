# Split Integrity Report — Phase 2

**Generated from** `phase2/splits/split_manifest.json`. Seed 42; 70/15/15.

## Source integrity

| Dataset | File | SHA-256 |
|---|---|---|
| D1 | `Spam Message Collection.xlsx` | `24ca099ac1ffabc0b02fd491f57d577c56afb932bc81c5964a40e32eab9a023b` |
| D2 | `Dataset_5971.csv` | `649844f1c62a6b27e145eaf17a65f7010c56c390e11a794ea8329993a05ba71e` |

The originals were read only; all derived rows retain `record_id` and `source_row`.

## Split sizes

| dataset | split | rows | classes | groups | file SHA-256 |
|---|---|---|---|---|---|
| D1 Malayalam | train | 1394 | {'Ham': 1237, 'Spam': 157} | 1226 | bd4f5edb59ce2579… |
| D2 | train | 4127 | {'ham': 3391, 'smishing': 421, 'spam': 315} | 3895 | ad19a6e8042dd403… |
| D1 Malayalam | val | 299 | {'Ham': 265, 'Spam': 34} | 299 | 5bcc228f338b2685… |
| D2 | val | 885 | {'ham': 727, 'smishing': 90, 'spam': 68} | 885 | 2fc68c050731e90a… |
| D1 Malayalam | test | 299 | {'Ham': 265, 'Spam': 34} | 299 | 3922f037a2f52045… |
| D2 | test | 883 | {'ham': 726, 'smishing': 90, 'spam': 67} | 883 | 44409491ebb1c4e2… |

## Leakage assertions

| Check | D1 | D2 |
|---|---|---|
| group overlap train/val | 0 | 0 |
| group overlap train/test | 0 | 0 |
| group overlap val/test | 0 | 0 |
| normalised-text overlap train/test | 0 | 0 |

All overlaps are zero by construction.

## Duplicate handling

| Dataset | Records | Exact groups | Normalised groups | Fuzzy pairs added | Final groups | Conflict groups | Conflict records |
|---|---|---|---|---|---|---|---|
| D1 Malayalam | 1992 | 1905 | 1853 | 181 | 1824 | 0 | 0 |
| D2 | 5971 | 5949 | 5700 | 0 | 5700 | 37 | 76 |

D1 has no label conflicts. D2's 37 conflicting groups (76 records, almost all spam↔smishing) were excluded from supervised training and evaluation.

## Row-block composition (D1 primary)

| split | rows | 1000-row block → rows |
|---|---|---|
| train | 1394 | 4001-5000: 458, 5001-6000: 679, 6001-7000: 257 |
| val | 299 | 4001-5000: 84, 5001-6000: 153, 6001-7000: 62 |
| test | 299 | 4001-5000: 89, 5001-6000: 159, 6001-7000: 51 |

This is the confound quantified in `D1_RESULTS.md`: block 5001–6000 is almost entirely Ham, while block 6001–7000 contains most of the Spam. A random split shares these blocks between train and test.

## Malayalam-only descriptive subset

- Rows: **1489** — Ham 1429, Spam 60.
- Split rows: train 1052, val 216, test 221.
- Split Spam: train 37, val 12, test 11.
- **Descriptive only.** 11 Spam test rows cannot support a separate model claim.
