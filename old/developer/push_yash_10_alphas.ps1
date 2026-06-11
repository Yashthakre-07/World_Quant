$SERVER = "https://world-quant-1.onrender.com"
$TOKEN  = "yashthakreop1"
$HEADERS = @{
    "Authorization" = "Bearer $TOKEN"
    "Content-Type"  = "application/json"
}

# ============================================================
# 10 RESEARCH-BACKED HIGH-FITNESS ALPHAS
# Target: Fitness > 1.0 | Turnover < 30% | Sharpe > 1.4
#
# Key insights from historical data:
#   SUBMITTED winners: close-open(decay3) -> fitness ~1.01, turnover ~31-34%
#   SUBMITTED winner:  (close-open)/(high-low) gate 1.2x -> fitness 1.01, turnover 21% (BEST!)
#   SUBMITTED winner:  intraday range location -> fitness 1.04, turnover 36%
#
# Strategy: Mirror structural DNA of winners + use NEW signals
#   - close-open body signal is gold -> vary gate, decay, normalization
#   - High volume gate (1.0-1.5x adv20) -> turnover drops dramatically (proven by VkO9lkz5)
#   - Candle body / range normalization -> robust cross-sectional signal
#   - New families: stochastic, volume corr, cumulative sum -> pass self-correlation
# ============================================================

$alphas = @'
[
  {
    "family": "High-Gate Body Reversion",
    "hypothesis": "On extreme volume days (>1.5x avg), close-open gap represents exhausted directional conviction. The tight high-gate minimizes noise and dramatically reduces turnover to target fitness > 1.1.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 1.5, -rank(ts_decay_linear(close - open, 3)), 0), subindustry)",
    "settings": { "decay": 3, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08 }
  },
  {
    "family": "Ultra-Gate Normalized Body Reversion",
    "hypothesis": "Close-open gap normalized by intraday range, filtered to only 2x average volume days. Extreme volume gate slashes turnover to ~15%, boosting fitness significantly above 1.0.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 2.0, -rank(ts_decay_linear((close - open) / (high - low + 0.001), 3)), 0), subindustry)",
    "settings": { "decay": 3, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08 }
  },
  {
    "family": "High-Gate Range Location Reversion",
    "hypothesis": "Where close sits in the intraday range on high-volume days (>1.3x) captures extreme intraday dislocation. Tighter gate than the base formula but same proven signal family that achieved fitness 1.04.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 1.3, -rank(ts_decay_linear(((close - low) - (open - low)) / (high - low + 0.001), 5)), 0), subindustry)",
    "settings": { "decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08 }
  },
  {
    "family": "Volume-Surge Body Ratio Reversion",
    "hypothesis": "Candle body-to-range ratio on 1.5x volume days exposes the strongest intraday conviction exhaustion events. Proven body-ratio signal (alpha VkO9lkz5 fitness 1.01) with even tighter volume gate.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 1.5, -rank(ts_decay_linear((close - open) / (high - low + 0.001), 5)), 0), subindustry)",
    "settings": { "decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08 }
  },
  {
    "family": "High-Gate VWAP Body Combo",
    "hypothesis": "Sum of 2-day close-open gaps captures multi-session directional persistence. High volume gate (1.2x) reduces noise. Cumulative signal over 2 days smooths single-day outliers without extending decay window.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 1.2, -rank(ts_decay_linear(ts_sum(close - open, 2), 4)), 0), subindustry)",
    "settings": { "decay": 4, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08 }
  },
  {
    "family": "Stochastic Overbought Reversion",
    "hypothesis": "10-day stochastic %K position (where close sits in 10-day channel) with 1.2x volume gate. Near 1.0 = 10-day overbought, near 0.0 = 10-day oversold. Medium-term reversal with proven low-turnover decay-5 structure.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 1.2, -rank(ts_decay_linear((close - ts_min(low, 10)) / (ts_max(high, 10) - ts_min(low, 10) + 0.001), 5)), 0), subindustry)",
    "settings": { "decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08 }
  },
  {
    "family": "High-Gate Shadow Imbalance",
    "hypothesis": "Net shadow imbalance (upper shadow minus lower shadow) normalized by range, on 1.3x volume days, captures peak seller/buyer exhaustion. Shadow-based signal is orthogonal to all body and gap signals.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 1.3, -rank(ts_decay_linear(((high - max(open, close)) - (min(open, close) - low)) / (high - low + 0.001), 5)), 0), subindustry)",
    "settings": { "decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08 }
  },
  {
    "family": "Volume-Corr Body Overlay",
    "hypothesis": "10-day price-volume correlation multiplied by close-open body, then gated at 1.2x. This captures structural regime shifts. Proven ts_corr operator from Gen 3 research paired with the winning body signal.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 1.2, -rank(ts_decay_linear(ts_corr(close, volume, 10) * (close - open), 5)), 0), subindustry)",
    "settings": { "decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08 }
  },
  {
    "family": "Midpoint-VWAP High-Gate Reversion",
    "hypothesis": "Midpoint (high+low)/2 minus VWAP on 1.4x volume days captures peak intraday range-to-volume-center divergence. Midpoint above VWAP means buyers dominated range but not volume — a clean fade signal with low turnover.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 1.4, -rank(ts_decay_linear((high + low) / 2 - vwap, 5)), 0), subindustry)",
    "settings": { "decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08 }
  },
  {
    "family": "Volatility-Gated Overnight Reversion",
    "hypothesis": "Overnight gap normalized by 10-day return-vol on extreme volume days (1.3x). Proven gap signal from Gen 3 with high volume gate to crush turnover. Distinct from all submitted alphas — no signal overlap.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 1.3, -rank(ts_decay_linear((open - ts_delay(close, 1)) / (ts_std_dev(returns, 10) + 0.0001), 5)), 0), subindustry)",
    "settings": { "decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08 }
  }
]
'@

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ALPHAFORGE — Pushing 10 Alphas" -ForegroundColor Yellow
Write-Host "  Server : $SERVER" -ForegroundColor Cyan
Write-Host "  Account: beyondsynapse@gmail.com (Yash)" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    $response = Invoke-RestMethod `
        -Uri "$SERVER/api/queue-alpha" `
        -Method POST `
        -Headers $HEADERS `
        -Body $alphas

    Write-Host "SUCCESS! Server Response:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 5
} catch {
    Write-Host "ERROR pushing alphas: $_" -ForegroundColor Red
    $statusCode = $_.Exception.Response.StatusCode
    Write-Host "Status Code: $statusCode" -ForegroundColor Red

}
