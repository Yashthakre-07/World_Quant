import json
import urllib.request
import ssl
import time

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

TOP_20_ALPHAS = [
    # === Regime A: Sentiment-Momentum Dynamics ===
    {
        "family": "Sales Revision Momentum Correlation",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_corr(returns, anl10_salsmun_1qf_1002, 10)), 0), subindustry)",
        "hypothesis": "Rolling correlation between equity returns and upward sales estimate revision frequency captures pricing confirmation.",
        "settings": {
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    },
    {
        "family": "Net Profit Count Momentum Correlation",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(ts_corr(returns, anl10_netsmun_1qf_1002, 10)), 0), subindustry)",
        "hypothesis": "Rolling correlation between equity returns and net profit estimate revision frequency indicates fundamental structural drift.",
        "settings": {
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    },
    {
        "family": "Basic EPS Revision Price Correlation",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.72, rank(ts_corr(returns, anl4_fs_basic_splt_v4_nd_eps_estimate, 10)), 0), subindustry)",
        "hypothesis": "High positive rolling correlation between EPS estimate growth and return signals fundamental momentum.",
        "settings": {
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    },
    {
        "family": "Sales Estimate Revision Price Correlation",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_corr(returns, anl4_fs_basic_splt_v4_nd_sales_estimate, 10)), 0), subindustry)",
        "hypothesis": "Rolling correlation of returns with raw consensus sales revisions captures sector demand growth.",
        "settings": {
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    },
    {
        "family": "FCF Revision Price Correlation",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_corr(returns, anl4_fs_detail_estimates_advanced_af_nd_fcf_high, 10)), 0), subindustry)",
        "hypothesis": "Positive correlation between price movement and upper-bound FCF estimate revision indicates strong cash-backed price discovery.",
        "settings": {
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    },

    # === Regime B: Earnings Divergence & Yields ===
    {
        "family": "FCF EBITDA Coverage Spread",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_high / (anl4_fs_detail_estimates_advanced_af_nd_ebitda_high + 0.001)), 0), subindustry)",
        "hypothesis": "Ratio of upper-bound consensus FCF to EBITDA highlights cash-flow conversion quality, avoiding paper earnings traps.",
        "settings": {
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    },
    {
        "family": "Analyst Consensus Operating Margin",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "High consensus EBITDA-to-Sales margin signals exceptional sector-relative pricing power.",
        "settings": {
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    },
    {
        "family": "Net Profit Margin Proxy",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "Relative rank of net margin high expectations isolates bottom-line growth leaders within peers.",
        "settings": {
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    },
    {
        "family": "ROE Fundamental Proxy",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high / (anl4_fs_detail_estimates_advanced_af_nd_sh_equity_high + 0.001)), 0), subindustry)",
        "hypothesis": "Forward return-on-equity proxy. High forward ROE expectations capture structural compounders.",
        "settings": {
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    },
    {
        "family": "FCF Consensus Yield",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_high / (cap + 0.001)), 0), subindustry)",
        "hypothesis": "Forward FCF yield based on optimistic consensus estimates exploits cash value anomalies.",
        "settings": {
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    },
    {
        "family": "Earnings Yield Proxy",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_basic_splt_v4_nd_eps_estimate / (close + 0.001)), 0), subindustry)",
        "hypothesis": "High consensus EPS-to-price ratio captures mispriced value assets with strong fundamental support.",
        "settings": {
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    },

    # === Regime C: Conservative Margin of Safety ===
    {
        "family": "FCF Pessimistic Yield Floor",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_low / (cap + 0.001)), 0), subindustry)",
        "hypothesis": "Downside FCF yield floor isolates value stocks that remain robust even under conservative worst-case scenario estimates.",
        "settings": {
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    },
    {
        "family": "Pessimistic Operating Margin Floor",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_low / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "Worst-case EBITDA margin floor targets high-conviction margin-of-safety compounders.",
        "settings": {
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    },
    {
        "family": "Net Profit Pessimistic Margin Floor",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimate_1qf_v4_nd_netprofit_low / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "Under pessimistic consensus, firms preserving net profitability floors represent maximum capital protection.",
        "settings": {
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    },
    {
        "family": "Pretax Income Downside Yield",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.72, rank(anl4_fs_detail_estimates_advanced_af_nd_ptp_low / (cap + 0.001)), 0), subindustry)",
        "hypothesis": "Pre-tax income yield under worst-case consensus measures robustness against negative operational surprises.",
        "settings": {
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    },

    # === Regime D: Advanced Transformations ===
    {
        "family": "EBITDA Dispersal Risk fading",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank((anl4_fs_detail_estimates_advanced_af_nd_ebitda_high - anl4_fs_detail_estimates_advanced_af_nd_ebitda_low) / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "Severe analyst disagreement (high-low spread) indicates information asymmetry and fundamental instability. Shorting high dispersion avoids value traps.",
        "settings": {
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    },
    {
        "family": "FCF Dispersal Risk fading",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.72, -rank((anl4_fs_detail_estimates_advanced_af_nd_fcf_high - anl4_fs_detail_estimates_advanced_af_nd_fcf_low) / (cap + 0.001)), 0), subindustry)",
        "hypothesis": "Scaling FCF estimate dispersion by market capitalization highlights excessive uncertainty. Fading high uncertainty generates premium.",
        "settings": {
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    },
    {
        "family": "Net Profit Dispersal fading",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank((anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high - anl4_fs_detail_estimate_1qf_v4_nd_netprofit_low) / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "High dispersion on bottom-line net profit estimates is scaled by sales. Shorting high uncertainty signals mean-reversion in expectations.",
        "settings": {
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    },
    {
        "family": "Pre-tax Dispersion fading",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank((anl4_fs_detail_estimates_advanced_af_nd_ptp_high - anl4_fs_detail_estimates_advanced_af_nd_ptp_low) / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "Firms with tight pre-tax consensus have reliable pricing signals, while wide pre-tax consensus spreads are shorted.",
        "settings": {
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
        }
    },
    {
        "family": "Multi-Estimate Consensus Correlation Spread",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_corr(returns, anl10_salsmun_1qf_1002, 10) + ts_corr(returns, anl10_netsmun_1qf_1002, 10)), 0), subindustry)",
        "hypothesis": "Double-confirmation of fundamental momentum using rolling return correlation with both Sales and Net Profit upward analyst revisions.",
        "settings": {
            "decay": 5,
            "neutralization": "SUBINDUSTRY",
            "universe": "TOP3000",
            "truncation": 0.08
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
    for name, conf in SERVERS.items():
        print(f"\n==========================================")
        print(f"Pushing institutional factors to {name.upper()}'s inbox queue...")
        
        # 1. Post to queue-alpha
        res, code = post_endpoint(conf["url"], "/api/queue-alpha", conf["token"], TOP_20_ALPHAS)
        print(f"Queue Status Code: {code} | Response: {res}")
        
        # 2. Inject immediately to simulation queue
        print(f"Injecting inbox to simulation queue on {name.upper()}...")
        inject_res, inject_code = post_endpoint(conf["url"], "/api/inject-inbox", conf["token"], {"all": True})
        print(f"Injection Status Code: {inject_code} | Response: {inject_res}")

if __name__ == "__main__":
    main()
