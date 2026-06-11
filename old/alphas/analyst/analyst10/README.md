# analyst10 — Performance-Weighted Analyst Estimates

This folder contains **200 unique alpha formulas** for the `analyst10` dataset.

## How to Use

### Step 1 — Fetch real field names (requires internet)
```bash
python fetch_analyst10_fields.py
```
This uses **ace_lib's `get_datafields()`** to pull all real analyst10 field IDs
and **`get_operators()`** to pull all available operators. Saves:
- `analyst10_fields.json` — real field IDs from API
- `operators.json` — all operators from API

### Step 2 — Generate 200 alphas (works offline after Step 1)
```bash
python generate_analyst10_alphas.py
```
Produces `analyst10_alphas.json` with 200 unique alpha configs.

### Step 3 — Submit to pipeline queue
The output JSON is compatible with `run_pipeline.py`. Each alpha has the
exact `generate_alpha()` format from ace_lib:
```python
{
  "type": "REGULAR",
  "settings": { ... },
  "regular": "<formula>"
}
```

## Field Groups Covered
| Group | Fields Used | # Alphas |
|---|---|---|
| EPS Smart Estimate | `analyst10_eps_smart` | 20 |
| Analyst Recommendation | `analyst10_rec_mean`, `analyst10_rec_change` | 20 |
| Price Target | `analyst10_price_tgt` | 20 |
| EPS Surprise | `analyst10_eps_surprise` | 20 |
| Revenue Smart | `analyst10_rev_smart` | 20 |
| Coverage & Revisions | `analyst10_eps_numest`, `_revup`, `_revdn` | 20 |
| Forward EPS | `analyst10_eps_fwd1`, `analyst10_eps_fwd2` | 20 |
| EBITDA Smart | `analyst10_ebitda_smart` | 20 |
| DPS + LT Growth | `analyst10_dps_smart`, `analyst10_eps_ltgrowth` | 20 |
| Cross-Field Combos | All of the above combined | 20 |

## Operators Used (from ace_lib get_operators)
- **Time-series**: `ts_delta`, `ts_rank`, `ts_corr`, `ts_mean`, `ts_std_dev`, `ts_decay_linear`, `ts_decay_exponential`, `ts_regression`, `ts_delay`, `ts_entropy`
- **Cross-sectional**: `rank`, `group_zscore`, `group_neutralize`, `group_rank`, `zscore`
- **Math**: `sign`, `abs`, `max`, `min`, `log`, `sqrt`
- **Conditional**: `trade_when`

## Anti-Self-Correlation Strategy
1. Different fields per group → different underlying signals
2. Different lookbacks: 5, 10, 20, 63, 126, 252 days
3. Different neutralization: INDUSTRY vs SUBINDUSTRY
4. Different decay: 0, 3, 5, 10, 21 days
5. Different truncation: 0.05 vs 0.08
6. Cross-field combos create structurally different signal vectors
