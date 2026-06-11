import urllib.request
import json
import ssl

def main():
    server_url = "https://world-quant.onrender.com/api/queue-alpha"
    token = "yashthakreop"
    
    alphas = [
        # Group 1: 37 Alphas that failed due to HTTP 401
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(returns, 5)), 0), subindustry)",
            "family": "Daily Return Reversal",
            "hypothesis": "Daily return overreactions in highly liquid names revert over a 5-day decay window.",
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.60, -rank(ts_decay_linear(ts_delta(close, 3), 6)), 0), subindustry)",
            "family": "Short Delta Reversal",
            "hypothesis": "3-day momentum overshoots in closing prices display mean reversion under peer-group neutralization.",
            "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_delta(close, 5), 6)), 0), subindustry)",
            "family": "Medium Delta Reversal",
            "hypothesis": "5-day rolling price changes reflect short-term trend exhaustion and subsequently revert.",
            "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(ts_delta(close, 10), 8)), 0), subindustry)",
            "family": "Long Delta Reversal",
            "hypothesis": "10-day price changes capture institutional block-execution extremes that fade under subindustry hedges.",
            "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.60, -rank(ts_decay_linear(ts_sum(returns, 3), 5)), 0), subindustry)",
            "family": "Short Return Sum Reversal",
            "hypothesis": "3-day accumulated returns identify short-term overbought/oversold clusters prone to mean reversion.",
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_sum(returns, 5), 6)), 0), subindustry)",
            "family": "Medium Return Sum Reversal",
            "hypothesis": "5-day cumulative returns capture short-term asset overbuying that reverts post order-flow clearing.",
            "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(ts_sum(returns, 10), 8)), 0), subindustry)",
            "family": "Long Return Sum Reversal",
            "hypothesis": "10-day cumulative returns reveal statistical overextension in stock-specific price channels.",
            "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.60, -rank(ts_decay_linear(returns - ts_mean(returns, 5), 5)), 0), subindustry)",
            "family": "Short Return Mean Deviation",
            "hypothesis": "Deviation of daily returns from their rolling 5-day mean captures short-term volatility shocks.",
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(returns - ts_mean(returns, 10), 6)), 0), subindustry)",
            "family": "Medium Return Mean Deviation",
            "hypothesis": "Daily return deviation from rolling 10-day mean filters out long-term trends to highlight short-term reversals.",
            "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(returns - ts_mean(returns, 20), 8)), 0), subindustry)",
            "family": "Long Return Mean Deviation",
            "hypothesis": "Daily return deviation from rolling 20-day mean identifies long-term asset pricing dislocations.",
            "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(returns * rank(volume / adv20), 5)), 0), subindustry)",
            "family": "Volume-Amplified Returns",
            "hypothesis": "Extreme price moves on high relative volume signal capital flow exhaustion and strong reversal.",
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(ts_delta(close, 3) * rank(volume / adv20), 6)), 0), subindustry)",
            "family": "Short Delta Volume Interactions",
            "hypothesis": "3-day price moves coupled with dynamic relative volume highlight peak buyer conviction zones.",
            "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank(ts_decay_linear(ts_delta(close, 5) * rank(volume / adv20), 6)), 0), subindustry)",
            "family": "Medium Delta Volume Interactions",
            "hypothesis": "5-day price changes amplified by volume rank isolate major institutional buy/sell exhaustions.",
            "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(returns * ts_rank(volume / adv20, 10), 5)), 0), subindustry)",
            "family": "Daily Return Time-Series Volume Rank",
            "hypothesis": "Daily returns scaled by the 10-day time-series rank of volume highlight volume-driven pricing shocks.",
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.60, -rank(ts_decay_linear(ts_delta(close, 5) * ts_rank(volume / adv20, 10), 6)), 0), subindustry)",
            "family": "Delta Time-Series Volume Rank",
            "hypothesis": "5-day delta scaled by rolling 10-day volume rank filters out low-liquidity price action.",
            "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(returns * (volume / adv20), 5)), 0), subindustry)",
            "family": "Return Relative Volume Product",
            "hypothesis": "Standard return scaled by relative volume captures raw liquidity-driven order flow imbalances.",
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(ts_delta(close, 3) * (volume / adv20), 6)), 0), subindustry)",
            "family": "Short Delta Relative Volume Product",
            "hypothesis": "3-day delta scaled by relative volume measures short-term institutional flow intensity.",
            "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank(ts_decay_linear(ts_sum(returns, 5) * (volume / adv20), 6)), 0), subindustry)",
            "family": "Medium Sum Volume Product",
            "hypothesis": "5-day accumulated returns scaled by relative volume isolate large-block order liquidations.",
            "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear((close - open) * rank(volume / adv20), 5)), 0), subindustry)",
            "family": "Candle Body Volume Product",
            "hypothesis": "Daily close-to-open change scaled by volume rank exposes high-volume intraday session traps.",
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear((open - ts_delay(close, 1)) * rank(volume / adv20), 6)), 0), subindustry)",
            "family": "Gap Volume Product",
            "hypothesis": "Overnight gap scaled by relative volume rank isolates high-volume retail gap-and-trap extremes.",
            "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear((close - low) / (high - low + 0.001), 5)), 0), subindustry)",
            "family": "Intraday Range Position Reversal",
            "hypothesis": "Daily closing position relative to high-low range marks intraday session overbought states.",
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.60, -rank(ts_decay_linear((close - ts_min(low, 5)) / (ts_max(high, 5) - ts_min(low, 5) + 0.001), 6)), 0), subindustry)",
            "family": "Short Channel Reversal",
            "hypothesis": "Closing price relative to rolling 5-day high-low channel identifies short-term channel exhaustion.",
            "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear((close - ts_min(low, 10)) / (ts_max(high, 10) - ts_min(low, 10) + 0.001), 6)), 0), subindustry)",
            "family": "Medium Channel Reversal",
            "hypothesis": "Closing price relative to rolling 10-day high-low channel represents standard mean-reversion extremes.",
            "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear((close - ts_min(low, 20)) / (ts_max(high, 20) - ts_min(low, 20) + 0.001), 8)), 0), subindustry)",
            "family": "Long Channel Reversal",
            "hypothesis": "Closing price relative to rolling 20-day high-low channel provides ultra-stable, low-turnover signals.",
            "settings": {"decay": 8, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear((high - low) / (ts_mean(high - low, 10) + 0.001), 5)), 0), subindustry)",
            "family": "Short Range Volatility Expansion",
            "hypothesis": "Daily range normalized by rolling 10-day average isolates temporary range expansion peaks.",
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear((high - low) / (ts_mean(high - low, 20) + 0.001), 6)), 0), subindustry)",
            "family": "Long Range Volatility Expansion",
            "hypothesis": "Daily range normalized by rolling 20-day average identifies long-term volatility regime contraction.",
            "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_std_dev(returns, 5) / (ts_std_dev(returns, 20) + 0.001), 5)), 0), subindustry)",
            "family": "Short Volatility Ratio",
            "hypothesis": "5-day rolling return volatility divided by 20-day volatility captures temporary volatility shocks.",
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(ts_std_dev(returns, 10) / (ts_std_dev(returns, 30) + 0.001), 6)), 0), subindustry)",
            "family": "Long Volatility Ratio",
            "hypothesis": "10-day rolling return volatility divided by 30-day volatility isolates structural volatility expansion.",
            "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear((close - ts_mean(close, 10)) / (ts_std_dev(close, 10) + 0.001), 5)), 0), subindustry)",
            "family": "Short Bollinger ZScore",
            "hypothesis": "Standardized close displacement from rolling 10-day mean highlights immediate Bollinger reversals.",
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear((close - ts_mean(close, 20)) / (ts_std_dev(close, 20) + 0.001), 6)), 0), subindustry)",
            "family": "Long Bollinger ZScore",
            "hypothesis": "Standardized close displacement from rolling 20-day mean provides a robust peer-group reversion signal.",
            "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_corr(close, volume, 10), 5)), 0), subindustry)",
            "family": "Short Price-Volume Correlation",
            "hypothesis": "10-day rolling correlation between price and volume identifies institutional order-book sweeps.",
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(ts_corr(close, volume, 20), 6)), 0), subindustry)",
            "family": "Long Price-Volume Correlation",
            "hypothesis": "20-day rolling correlation between price and volume isolates long-term capital accumulation phases.",
            "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank(ts_decay_linear(ts_corr(returns, volume, 10), 5)), 0), subindustry)",
            "family": "Short Return-Volume Correlation",
            "hypothesis": "10-day rolling correlation between returns and volume exposes intraday liquidity exhaustions.",
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_corr(returns, volume, 20), 6)), 0), subindustry)",
            "family": "Long Return-Volume Correlation",
            "hypothesis": "20-day rolling correlation between returns and volume filters out short-term price noise.",
            "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank(ts_decay_linear(ts_corr(returns, volume / adv20, 10), 5)), 0), subindustry)",
            "family": "Short Return-Relative Volume Correlation",
            "hypothesis": "10-day correlation between returns and relative volume exposes extreme, exhausted momentum runs.",
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_corr(returns, volume / adv20, 20), 6)), 0), subindustry)",
            "family": "Long Return-Relative Volume Correlation",
            "hypothesis": "20-day correlation between returns and relative volume tracks slow institutional accumulation.",
            "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_corr(close / (vwap + 0.001) - 1, volume / adv20, 10), 5)), 0), subindustry)",
            "family": "Short VWAP-Volume Correlation",
            "hypothesis": "10-day correlation between close-to-vwap ratio and relative volume identifies vwap execution imbalances.",
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },

        # Group 2: Corrected 3 Candle Shadow Alphas (Bypassing Bare max/min validation error)
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(high - ((open + close + abs(open - close)) / 2), 5)), 0), subindustry)",
            "family": "Upper Shadow Pressure",
            "hypothesis": "Large upper shadows signify failed bullish attempts. Bypassing illegal bare max keyword.",
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_decay_linear(((open + close - abs(open - close)) / 2) - low, 5)), 0), subindustry)",
            "family": "Lower Shadow Demand",
            "hypothesis": "Large lower shadows signal deep absorption of selling pressure. Bypassing illegal bare min keyword.",
            "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        },
        {
            "formula": "group_neutralize(trade_when(volume > adv20 * 0.65, -rank(ts_decay_linear(((high - ((open + close + abs(open - close)) / 2)) - (((open + close - abs(open - close)) / 2) - low)) / (high - low + 0.001), 6)), 0), subindustry)",
            "family": "Shadow Balance Reversal",
            "hypothesis": "Imbalance between upper shadow pressure and lower shadow demand. Bypassing illegal bare max/min keywords.",
            "settings": {"decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
        }
    ]
        
    req = urllib.request.Request(server_url, method="POST", data=json.dumps(alphas).encode("utf-8"))
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    print(f"Connecting to live API: {server_url}...")
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            res_body = response.read().decode("utf-8")
            print(f"SUCCESS! Status Code: {response.status}")
            print(f"Server Response:\n{json.dumps(json.loads(res_body), indent=2)}")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    main()
