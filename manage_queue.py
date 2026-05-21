import os
import sys
import json

QUEUE_PATH = os.path.join("db", "simulation_queue.json")

# Pool of 100% compliant price/volume alpha formulas
ALPHA_POOL = [
    {
        "family": "Price Reversion",
        "hypothesis": "Intraday close-to-open gaps represent temporary imbalances that revert; 3-day decay smoothing limits turnover.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.7, -rank(ts_decay_linear(close - open, 3)), 0), subindustry)",
        "settings": { "decay": 10, "neutralization": "SUBINDUSTRY", "universe": "TOP3000" }
    },
    {
        "family": "VWAP-Price Divergence",
        "hypothesis": "Deviations between the closing price and vwap volume centers represent unstable intraday drifts that revert.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear((close - vwap) / (ts_std_dev(close, 20) + 0.001), 3)), 0), subindustry)",
        "settings": { "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000" }
    },
    {
        "family": "Price Reversion",
        "hypothesis": "Short-term returns mean-revert on highly liquid sessions when institutional trade volumes are elevated.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.5, -rank(ts_decay_linear(returns, 3)), 0), subindustry)",
        "settings": { "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000" }
    },
    {
        "family": "Overnight Gap Reversion",
        "hypothesis": "Opening price gaps relative to the previous close represent liquidity mismatches that mean-revert intraday.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank(ts_decay_linear(open - ts_delay(close, 1), 3)), 0), subindustry)",
        "settings": { "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000" }
    },
    {
        "family": "Spread Reversion",
        "hypothesis": "Peaks in the intraday high-low spread indicate temporary volatility spikes that mean-revert on typical trading days.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(high - low, 3)), 0), subindustry)",
        "settings": { "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000" }
    },
    {
        "family": "VWAP Trend Reversion",
        "hypothesis": "Intraday drift between the volume center (vwap) and open price represents overextended liquidity that reverts.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(vwap - open, 3)), 0), subindustry)",
        "settings": { "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000" }
    },
    {
        "family": "Volume-Weighted Return Reversion",
        "hypothesis": "Returns weighted by volume deviations capture amplified trade imbalances that experience sharp reversion.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.55, -rank(ts_decay_linear(returns * rank(volume / adv20), 3)), 0), subindustry)",
        "settings": { "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000" }
    },
    {
        "family": "Overnight Trend Reversion",
        "hypothesis": "Extended 2-day gapped intraday movements represent overbought/oversold momentum exhaustion that mean-reverts.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.8, -rank(ts_decay_linear(open - ts_delay(close, 2), 3)), 0), subindustry)",
        "settings": { "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000" }
    },
    {
        "family": "Normalized Deviation Reversion",
        "hypothesis": "Normalized closing price deviation from the 10-day moving average mean-reverts on active trading sessions.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.7, -rank(ts_decay_linear((close - ts_mean(close, 10)) / (ts_std_dev(close, 10) + 0.001), 3)), 0), subindustry)",
        "settings": { "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000" }
    },
    {
        "family": "Intraday Volatility Reversion",
        "hypothesis": "Intraday high price deviation relative to the volume center represents temporary buying exhaustion that mean-reverts.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.6, -rank(ts_decay_linear(high - vwap, 3)), 0), subindustry)",
        "settings": { "decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000" }
    }
]

def load_queue():
    if not os.path.exists(QUEUE_PATH):
        return []
    try:
        with open(QUEUE_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_queue(queue):
    os.makedirs(os.path.dirname(QUEUE_PATH), exist_ok=True)
    with open(QUEUE_PATH, "w") as f:
        json.dump(queue, f, indent=2)

def main():
    if len(sys.argv) < 2:
        print("Usage: python manage_queue.py [append|replace]")
        sys.exit(1)

    mode = sys.argv[1].lower()
    current_queue = load_queue()
    existing_formulas = {item["formula"] for item in current_queue}

    if mode == "append":
        to_add = []
        for item in ALPHA_POOL:
            if item["formula"] not in existing_formulas:
                to_add.append(item)
                if len(to_add) >= 5:
                    break
        
        if not to_add:
            print("[QUEUE MANAGER] All pool alphas already exist in the active queue. No new alphas appended.")
            return

        extended_queue = current_queue + to_add
        save_queue(extended_queue)
        print(f"[QUEUE MANAGER] Appended {len(to_add)} fresh alphas to queue. Total queue length is now {len(extended_queue)}.")

    elif mode == "replace":
        # Load all 10 masterpieces directly
        fresh_queue = ALPHA_POOL[:10]
        save_queue(fresh_queue)
        print(f"[QUEUE MANAGER] Overwrote queue with {len(fresh_queue)} pristine price/volume factors.")
    
    else:
        print(f"Unknown mode: {mode}. Use 'append' or 'replace'.")
        sys.exit(1)

if __name__ == "__main__":
    main()
