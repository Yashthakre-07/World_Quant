"""
Push 10 high-fitness research-backed alphas to Yash's Render server (world-quant-1).
Target: Fitness > 1.0 | Turnover < 30% | Sharpe > 1.4

Research findings:
- BEST turnover reducer: HIGH volume gate (1.2x-2.0x adv20) -> proven by VkO9lkz5 (turnover 21%, fitness 1.01)
- Winning signal families: close-open body, (close-open)/(high-low), range location
- decay=3 or 5 both work when gate is high enough
- New families needed to pass self-correlation checks
"""
import urllib.request
import urllib.error
import json

SERVER = "https://world-quant.onrender.com"
TOKEN  = "yashthakreop"

ALPHAS = [
    {
        "family": "High-Gate Body Reversion",
        "hypothesis": "On extreme volume days (>1.5x avg), close-open gap represents exhausted directional conviction. Tight high-gate minimizes noise and dramatically reduces turnover to target fitness > 1.1.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.5, -rank(ts_decay_linear(close - open, 3)), 0), subindustry)",
        "settings": {"decay": 3, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Ultra-Gate Normalized Body",
        "hypothesis": "Close-open gap normalized by intraday range, filtered to only 2x average volume days. Extreme volume gate slashes turnover to ~15%, boosting fitness significantly above 1.0.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 2.0, -rank(ts_decay_linear((close - open) / (high - low + 0.001), 3)), 0), subindustry)",
        "settings": {"decay": 3, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "High-Gate Range Location Reversion",
        "hypothesis": "Where close sits in the intraday range on high-volume days (>1.3x) captures extreme intraday dislocation. Same proven signal that achieved fitness 1.04, with higher gate for less turnover.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.3, -rank(ts_decay_linear(((close - low) - (open - low)) / (high - low + 0.001), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Volume-Surge Body Ratio Reversion",
        "hypothesis": "Candle body-to-range ratio on 1.5x volume days exposes the strongest intraday conviction exhaustion events. Body-ratio signal (VkO9lkz5 fitness 1.01) with even tighter volume gate.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.5, -rank(ts_decay_linear((close - open) / (high - low + 0.001), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Cumulative Body High-Gate",
        "hypothesis": "Sum of 2-day close-open gaps captures multi-session directional persistence. High volume gate (1.2x) reduces noise. Cumulative signal over 2 days smooths single-day outliers without extending decay window.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.2, -rank(ts_decay_linear(ts_sum(close - open, 2), 4)), 0), subindustry)",
        "settings": {"decay": 4, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Stochastic Overbought High-Gate",
        "hypothesis": "10-day stochastic %K position (where close sits in 10-day channel) with 1.2x volume gate. Near 1.0 = 10-day overbought, near 0.0 = 10-day oversold. Medium-term reversal with proven low-turnover decay-5 structure.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.2, -rank(ts_decay_linear((close - ts_min(low, 10)) / (ts_max(high, 10) - ts_min(low, 10) + 0.001), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "High-Gate Shadow Imbalance",
        "hypothesis": "Net shadow imbalance (upper shadow minus lower shadow) normalized by range, on 1.3x volume days. Shadow-based signal is completely orthogonal to all body and gap signals.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.3, -rank(ts_decay_linear(((high - max(open, close)) - (min(open, close) - low)) / (high - low + 0.001), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Midpoint-VWAP High-Gate Reversion",
        "hypothesis": "Midpoint (high+low)/2 minus VWAP on 1.4x volume days captures peak intraday range-to-volume-center divergence. Midpoint above VWAP means buyers dominated range but not volume — clean fade signal with low turnover.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.4, -rank(ts_decay_linear((high + low) / 2 - vwap, 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Volatility-Gated Overnight Reversion",
        "hypothesis": "Overnight gap normalized by 10-day return-vol on extreme volume days (1.3x). Proven Gen-3 gap signal with high volume gate to crush turnover. Distinct from all submitted alphas.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.3, -rank(ts_decay_linear((open - ts_delay(close, 1)) / (ts_std_dev(returns, 10) + 0.0001), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Volume-Corr Body Overlay High-Gate",
        "hypothesis": "10-day price-volume correlation multiplied by close-open body on 1.2x volume days. Combines structural regime signal (ts_corr) with the winning body signal. Proven operators, novel combination.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 1.2, -rank(ts_decay_linear(ts_corr(close, volume, 10) * (close - open), 5)), 0), subindustry)",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
]

def push_alphas():
    print()
    print("=" * 55)
    print("  ALPHAFORGE — Pushing 10 Alphas to Yash Server")
    print(f"  Server : {SERVER}")
    print("  Account: beyondsynapse@gmail.com (Yash)")
    print("=" * 55)
    print()

    for i, alpha in enumerate(ALPHAS, 1):
        print(f"  [{i:02d}/10] {alpha['family']}")

    print()
    payload = json.dumps(ALPHAS).encode("utf-8")
    req = urllib.request.Request(
        f"{SERVER}/api/queue-alpha",
        data=payload,
        method="POST"
    )
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            print(f"SUCCESS (HTTP {resp.status})")
            print(json.dumps(body, indent=2))
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8")
        print(f"HTTP Error {e.code}: {err}")
    except Exception as e:
        print(f"Connection Error: {e}")


if __name__ == "__main__":
    push_alphas()
