# definitions of Alpha Families with custom allowed fields from fetched WQ Brain datasets

FAMILIES = {
    "Price Reversion": {
        "description": "Stocks that deviate from their rolling averages tend to revert to their mean.",
        "hypothesis": "Extreme short-term price moves are overreactions and will correct in the opposite direction.",
        "seeds": [
            "(high + low)/2 - close",
            "rank(close - ts_sum(close, 5)/5)",
            "-rank(ts_delta(close, 5))",
            "scale(ts_sum(close, 7)/7 - close) + 20 * scale(ts_corr(vwap, ts_delay(close, 5), 230))"
        ],
        "allowed_fields": ["open", "high", "low", "close", "vwap", "returns", "volume", "adv20", "cap"],
        "default_settings": {
            "universe": "TOP3000",
            "neutralization": "MARKET",
            "decay": 6,
            "truncation": 0.1
        }
    },
    "Volatility-Gated Reversion": {
        "description": "Exploit price reversion only when overall historical volatility is high.",
        "hypothesis": "Market participants overreact more severely during high-volatility environments, expanding arbitrage spreads.",
        "seeds": [
            "trade_when(ts_rank(ts_std_dev(returns, 22), 252) > 0.55, -ts_regression(returns, ts_delay(returns, 1), 252), -1)",
            "(-1 * rank(ts_std_dev(high, 10))) * ts_corr(high, volume, 10)"
        ],
        "allowed_fields": ["open", "high", "low", "close", "vwap", "returns", "volume", "adv20", "cap"],
        "default_settings": {
            "universe": "TOP3000",
            "neutralization": "SUBINDUSTRY",
            "decay": 10,
            "truncation": 0.1
        }
    },
    "Fundamental Value": {
        "description": "Stocks with low relative valuations (e.g. low EV/EBITDA, low trailing P/E) tend to outperform.",
        "hypothesis": "Fundamental metrics react slowly (quarterly) making value indicators low-turnover sources of alpha.",
        "seeds": [
            "-ts_zscore(close / open, 63)",  # Substitute formula to represent standard value indicator pattern
            "rank(1 / close) * volume / ts_sum(volume, 20)*20",
            "0 - (1 * (rank(ts_sum(returns, 10) / ts_sum(ts_sum(returns, 2), 3)) * rank(returns * cap)))"
        ],
        "allowed_fields": ["open", "high", "low", "close", "vwap", "returns", "volume", "adv20", "cap"],
        "default_settings": {
            "universe": "TOP1000",
            "neutralization": "INDUSTRY",
            "decay": 15,
            "truncation": 0.05
        }
    },
    "Volume Anomaly": {
        "description": "Unusual volume spikes or drops predict future price momentum or structural reversals.",
        "hypothesis": "A significant change in volume relative to historical averages indicates institutional positioning or news catalysts.",
        "seeds": [
            "group_neutralize(volume / (ts_sum(volume, 60)/60), sector)",
            "ts_rank(volume / (ts_sum(volume, 20)/20), 20) * ts_rank(-ts_delta(close, 7), 8)",
            "sign(ts_delta(volume, 1)) * (-1 * ts_delta(close, 1))",
            "log(pasteurize(vwap / close))"
        ],
        "allowed_fields": ["open", "high", "low", "close", "vwap", "returns", "volume", "adv20", "cap"],
        "default_settings": {
            "universe": "TOP3000",
            "neutralization": "SUBINDUSTRY",
            "decay": 6,
            "truncation": 0.1
        }
    },
    "Cross-Sectional Momentum": {
        "description": "Assets performing well in relative cross-sectional terms will continue their upward trajectory.",
        "hypothesis": "Trend-following behavior and post-earnings-announcement drift sustain relative performance trends.",
        "seeds": [
            "-ts_corr(rank(open), rank(volume), 10)",
            "rank(1 - rank(ts_std_dev(returns, 2) / ts_std_dev(returns, 5)) + (1 - rank(ts_delta(close, 1))))",
            "ts_rank(volume, 32) * (1 - ts_rank(close + high - low, 16)) * (1 - ts_rank(returns, 32))"
        ],
        "allowed_fields": ["open", "high", "low", "close", "vwap", "returns", "volume", "adv20", "cap"],
        "default_settings": {
            "universe": "TOP3000",
            "neutralization": "MARKET",
            "decay": 4,
            "truncation": 0.1
        }
    },
    "VWAP-Price Divergence": {
        "description": "Deviations of current close price from Volume-Weighted Average Price represent premium/discount anomalies.",
        "hypothesis": "Closing prices that drift away from volume centers are unstable and will snap back to trade weighted means.",
        "seeds": [
            "rank(vwap - close) / rank(vwap + close)",
            "(high * low)^0.5 - vwap",
            "-rank(close - ts_max(high, 5)) / (ts_max(high, 5) - ts_min(low, 5))",
            "(close - open) / (high - low + 0.001)"
        ],
        "allowed_fields": ["open", "high", "low", "close", "vwap", "returns", "volume", "adv20", "cap"],
        "default_settings": {
            "universe": "TOP3000",
            "neutralization": "SUBINDUSTRY",
            "decay": 6,
            "truncation": 0.1
        }
    },
    "Analyst Sentiment & Drift": {
        "description": "Consensus estimate drift and revisions from institutional analysts predict future price performance.",
        "hypothesis": "Analyst upward earnings revisions signal underlying business strength and trigger post-revision momentum.",
        "seeds": [
            "ts_delta(anl4_afv4_eps_mean, 5) / cap",
            "rank(ts_delta(anl4_ebitda_mean, 10))",
            "trade_when(ts_delta(anl4_afv4_eps_mean, 5) > 0, rank(returns), -rank(returns))"
        ],
        "allowed_fields": ["anl4_afv4_eps_mean", "anl4_ebitda_mean", "actual_eps_value_quarterly", "open", "high", "low", "close", "vwap", "returns", "volume", "adv20", "cap"],
        "default_settings": {
            "universe": "TOP3000",
            "neutralization": "SUBINDUSTRY",
            "decay": 8,
            "truncation": 0.1
        }
    },
    "Social Media Buzz & Sentiment": {
        "description": "Social media sentiment scores and volume buzz indicators capture retail investor expectations and sentiment shifts.",
        "hypothesis": "High social media buzz indicates retail interest; when combined with extreme negative returns it signals short-term oversold conditions.",
        "seeds": [
            "-snt_buzz * rank(returns)",
            "ts_decay_linear(scl12_sentvec, 5)",
            "trade_when(snt_buzz > 0.7, -returns, returns)"
        ],
        "allowed_fields": ["snt_buzz", "scl12_sentvec", "open", "high", "low", "close", "vwap", "returns", "volume", "adv20", "cap"],
        "default_settings": {
            "universe": "TOP3000",
            "neutralization": "MARKET",
            "decay": 4,
            "truncation": 0.1
        }
    },
    "Alternative Fundamental Ratios": {
        "description": "Ratios computed from financial footnote details like share-based compensation and common buyback payments.",
        "hypothesis": "Companies with low share-based compensation relative to market cap or high buybacks out-perform peers.",
        "seeds": [
            "-rank(allocated_sbp_expense_total / cap)",
            "rank(common_stock_buyback_payments / cap)",
            "rank(common_stock_buyback_payments / (allocated_sbp_expense_total + 1))"
        ],
        "allowed_fields": ["allocated_sbp_expense_total", "common_shares_outstanding_total", "common_stock_buyback_payments", "open", "high", "low", "close", "vwap", "returns", "volume", "adv20", "cap"],
        "default_settings": {
            "universe": "TOP1000",
            "neutralization": "INDUSTRY",
            "decay": 12,
            "truncation": 0.05
        }
    }
}

# Operator vocabulary for formatting LLM instructions
OPERATORS_HELP = """
- Cross-sectional normalization: rank(x), zscore(x), scale(x), sigmoid(x), pasteurize(x)
- Time-series indicators: ts_delta(x, d), ts_delay(x, d), ts_rank(x, d), ts_sum(x, d), ts_std_dev(x, d), ts_corr(x, y, d), ts_decay_linear(x, d), ts_max(x, d), ts_min(x, d), ts_arg_max(x, d), ts_arg_min(x, d), ts_covariance(x, y, d), ts_regression(x, y, d)
- Sector adjustments: group_neutralize(x, sector/industry/subindustry), group_zscore(x, sector/industry/subindustry), group_rank(x, sector/industry/subindustry)
- Conditionals: condition ? value_if_true : value_if_false
- Combining logic: trade_when(entry_condition, alpha_formula, exit_value)
"""
