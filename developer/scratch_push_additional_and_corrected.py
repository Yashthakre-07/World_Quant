import json
import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

SERVERS = {
    "sai": {
        "url": "https://world-quant.onrender.com",
        "token": "yashthakreop"
    },
    "yash": {
        "url": "https://world-quant-1.onrender.com",
        "token": "yashthakreop1"
    }
}

NEW_ALPHAS = [
    # 2 (Corrected). Participation Imbalance (using supported operators)
    {
        "family": "Participation Imbalance",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_mean(trade_when(returns > 0, returns * (volume / adv20), 0), 10) - ts_mean(trade_when(returns < 0, abs(returns) * (volume / adv20), 0), 10), 5)), 0), subindustry)",
        "hypothesis": "Asymmetry in volume-weighted positive vs negative return shocks indicates buy/sell participation imbalance.",
        "settings": {
            "decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08
        }
    },
    # 4 (Corrected). Entropy-like Instability (using range volatility ratio)
    {
        "family": "Entropy-like Instability",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank(ts_decay_linear(ts_std_dev((high - low) / (ts_mean(high - low, 20) + 0.0001), 10), 6)), 0), subindustry)",
        "hypothesis": "High instability in normalized daily spreads indicates entropy expansion preceding local corrections.",
        "settings": {
            "decay": 6, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08
        }
    },
    # 20 (Corrected). Kurtosis/Fat-tail proxy (using peak-to-std-dev ratio)
    {
        "family": "Kurtosis fat-tail indicator",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.60, -rank(ts_decay_linear(ts_max(abs(returns), 10) / (ts_std_dev(returns, 10) + 0.0001), 5)), 0), subindustry)",
        "hypothesis": "Assets experiencing tail return events relative to their rolling standard deviation mean-revert.",
        "settings": {
            "decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08
        }
    },
    # 21 (Premium Analyst). Analyst EPS Consensus Revision
    {
        "family": "Analyst Sentiment & Drift",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.50, rank(ts_decay_linear(ts_delta(anl4_afv4_eps_mean, 5) / (close + 0.001), 5)), 0), subindustry)",
        "hypothesis": "Upward revisions in consensus annual EPS expectations relative to current price signal post-revision momentum.",
        "settings": {
            "decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08
        }
    },
    # 22 (Premium Analyst). Analyst EBITDA revision momentum
    {
        "family": "Analyst Sentiment & Drift",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.55, rank(ts_decay_linear(ts_delta(anl4_ebitda_mean, 10) / (cap + 1.0), 5)), 0), subindustry)",
        "hypothesis": "Consensus EBITDA revisions normalized by market capitalization capture fundamental changes in profitability.",
        "settings": {
            "decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08
        }
    },
    # 23 (Premium Analyst). EPS Revision Volatility
    {
        "family": "Analyst Sentiment & Drift",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.60, -rank(ts_decay_linear(ts_std_dev(ts_delta(anl4_afv4_eps_mean, 3), 10) / (close + 0.001), 5)), 0), subindustry)",
        "hypothesis": "High instability in short-term consensus EPS estimates indicates earnings uncertainty, leading to price pressure.",
        "settings": {
            "decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08
        }
    },
    # 24 (Premium Analyst). Consensus EBITDA-to-EPS Divergence
    {
        "family": "Analyst Sentiment & Drift",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.50, rank(ts_decay_linear(ts_delta(anl4_ebitda_mean - anl4_afv4_eps_mean * 10, 5) / (close + 0.001), 5)), 0), subindustry)",
        "hypothesis": "Divergence between revisions in consensus operating cash expectations (EBITDA) and net earnings indicates quality of revisions.",
        "settings": {
            "decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08
        }
    },
    # 25 (Premium Analyst). Analyst Consensus Revisions Reversal
    {
        "family": "Analyst Sentiment & Drift",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_decay_linear(ts_delta(anl4_afv4_eps_mean, 3), 3)), 0), subindustry)",
        "hypothesis": "Overextended short-term consensus revisions on high volume trigger contrarian price adjustments.",
        "settings": {
            "decay": 3, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08
        }
    }
]

def post_endpoint(server_url, path, token, data):
    url = f"{server_url.rstrip('/')}{path}"
    req_data = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, method="POST", data=req_data)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
            res_body = response.read().decode("utf-8")
            return json.loads(res_body), response.status
    except Exception as e:
        return {"error": str(e)}, 500

def main():
    # 1. Queue to inbox
    for name, conf in SERVERS.items():
        print(f"\n==========================================")
        print(f"Pushing corrected/premium alphas to {name.upper()}'s inbox...")
        
        # Pushing to /api/queue-alpha queues it into the inbox_queue
        res, code = post_endpoint(conf["url"], "/api/queue-alpha", conf["token"], NEW_ALPHAS)
        print(f"Status Code: {code} | Response: {res}")
        
        # 2. Inject immediately
        print(f"Injecting inbox to simulation queue on {name.upper()}...")
        inject_res, inject_code = post_endpoint(conf["url"], "/api/inject-inbox", conf["token"], {"all": True})
        print(f"Injection Code: {inject_code} | Response: {inject_res}")

if __name__ == "__main__":
    main()
