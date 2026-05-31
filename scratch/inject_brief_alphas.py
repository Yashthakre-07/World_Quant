import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.validator import validate_fastexpr

# Define exactly 50 elite institutional quantitative alphas matching all constraints perfectly
alphas = [
    # Regime 1: Sentiment-Momentum Dynamics (Using Analyst 10 counts)
    {
        "family": "Sentiment_Momentum",
        "hypothesis": "Positive correlation between price returns and analyst sales count over 10 days indicates strong fundamental consensus momentum.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_corr(returns, anl10_salsmun_1qf_1002, 10)), 0), subindustry)"
    },
    {
        "family": "Sentiment_Momentum",
        "hypothesis": "Net profit analyst count momentum correlated with price returns captures high-conviction earnings revision trends.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(ts_corr(returns, anl10_netsmun_1qf_1002, 10)), 0), subindustry)"
    },
    {
        "family": "Sentiment_Momentum",
        "hypothesis": "Negative 20-day correlation between price returns and analyst sales counts indicates extreme momentum exhaustion or consensus divergence.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_corr(returns, anl10_salsmun_1qf_1002, 20)), 0), subindustry)"
    },
    {
        "family": "Sentiment_Momentum",
        "hypothesis": "Fading net profit count revision momentum over a 20-day lookback exploits consensus analyst crowd reversals.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank(ts_corr(returns, anl10_netsmun_1qf_1002, 20)), 0), subindustry)"
    },
    {
        "family": "Sentiment_Momentum",
        "hypothesis": "High short-term correlation (5 days) between returns and sales count revisions isolates immediate momentum trends.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.80, rank(ts_corr(returns, anl10_salsmun_1qf_1002, 5)), 0), subindustry)"
    },
    {
        "family": "Sentiment_Momentum",
        "hypothesis": "High short-term correlation (5 days) between returns and net profit revision counts identifies active systematic consensus drift.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(ts_corr(returns, anl10_netsmun_1qf_1002, 5)), 0), subindustry)"
    },
    {
        "family": "Sentiment_Momentum",
        "hypothesis": "Divergence between sales-momentum and profit-momentum correlations exposes early-stage sector margin shifts.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_corr(returns, anl10_salsmun_1qf_1002, 10)) - rank(ts_corr(returns, anl10_netsmun_1qf_1002, 10)), 0), subindustry)"
    },
    {
        "family": "Sentiment_Momentum",
        "hypothesis": "Medium-term divergence (20 days) between sales and net profit consensus momentum isolates deep valuation shifts.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(ts_corr(returns, anl10_salsmun_1qf_1002, 20)) - rank(ts_corr(returns, anl10_netsmun_1qf_1002, 20)), 0), subindustry)"
    },
    {
        "family": "Sentiment_Momentum",
        "hypothesis": "Short-term divergence (5 days) between sales and profit consensus revision count momentum signals early margin breakouts.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.80, rank(ts_corr(returns, anl10_salsmun_1qf_1002, 5)) - rank(ts_corr(returns, anl10_netsmun_1qf_1002, 5)), 0), subindustry)"
    },
    {
        "family": "Sentiment_Momentum",
        "hypothesis": "Return momentum multiplied by 12-day sales count correlation captures institutional block purchasing flows.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_corr(returns, anl10_salsmun_1qf_1002, 12)) * rank(returns), 0), subindustry)"
    },
    {
        "family": "Sentiment_Momentum",
        "hypothesis": "Return momentum multiplied by 12-day net profit count correlation isolates high-conviction earnings breakouts.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(ts_corr(returns, anl10_netsmun_1qf_1002, 12)) * rank(returns), 0), subindustry)"
    },
    {
        "family": "Sentiment_Momentum",
        "hypothesis": "Consensus momentum decay captures the 10-day delay drift in sales count correlations.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.80, rank(ts_corr(returns, anl10_salsmun_1qf_1002, 8)) - rank(ts_delay(ts_corr(returns, anl10_salsmun_1qf_1002, 8), 10)), 0), subindustry)"
    },
    {
        "family": "Sentiment_Momentum",
        "hypothesis": "Consensus momentum decay captures the 10-day delay drift in net profit count correlations.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(ts_corr(returns, anl10_netsmun_1qf_1002, 8)) - rank(ts_delay(ts_corr(returns, anl10_netsmun_1qf_1002, 8), 10)), 0), subindustry)"
    },

    # Regime 2: Earnings Divergence & Yields (Analyst 14 & 15 estimates ratios)
    {
        "family": "Earnings_Yields",
        "hypothesis": "High EBITDA-to-Sales estimate ratio represents strong forecast operating margin efficiency.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_high / anl4_fs_basic_splt_v4_nd_sales_estimate), 0), subindustry)"
    },
    {
        "family": "Earnings_Yields",
        "hypothesis": "Cash conversion efficiency (FCF divided by Net Profit estimate) signals high-quality earnings backed by tangible cash flows.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_high / anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high), 0), subindustry)"
    },
    {
        "family": "Earnings_Yields",
        "hypothesis": "Gross margin estimate ratio identifies firms with pricing power and premium product positioning.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_grossincome_high / anl4_fs_basic_splt_v4_nd_sales_estimate), 0), subindustry)"
    },
    {
        "family": "Earnings_Yields",
        "hypothesis": "Free cash flow yield scaled by gross sales estimates identifies superior capital allocation prospects.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_high / anl4_fs_basic_splt_v4_nd_sales_estimate), 0), subindustry)"
    },
    {
        "family": "Earnings_Yields",
        "hypothesis": "High EBITDA-to-Net Profit ratio reveals non-operating adjustments or financial leverage mismatches.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_high / anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high), 0), subindustry)"
    },
    {
        "family": "Earnings_Yields",
        "hypothesis": "Forecast earnings yield (EPS Estimate divided by closing price) represents intrinsic equity value spreads.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_basic_splt_v4_nd_eps_estimate / close), 0), subindustry)"
    },
    {
        "family": "Earnings_Yields",
        "hypothesis": "Forecast dividend yield (Dividend Estimate divided by closing price) isolates defensive yield plays.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_basic_splt_v4_nd_div_estimate / close), 0), subindustry)"
    },
    {
        "family": "Earnings_Yields",
        "hypothesis": "Pre-tax margin estimate ratio highlights raw forecast operating profitability.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.80, rank(anl4_fs_detail_estimates_advanced_af_nd_ptp_high / anl4_fs_basic_splt_v4_nd_sales_estimate), 0), subindustry)"
    },
    {
        "family": "Earnings_Yields",
        "hypothesis": "High book value yield (Shareholder Equity divided by market cap) functions as a safe Fama-French HML proxy.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_sh_equity_high / cap), 0), subindustry)"
    },
    {
        "family": "Earnings_Yields",
        "hypothesis": "Net margin forecast yield (Net Profit Estimate divided by Sales) isolates bottom-line earners.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high / anl4_fs_basic_splt_v4_nd_sales_estimate), 0), subindustry)"
    },
    {
        "family": "Earnings_Yields",
        "hypothesis": "EBITDA yield relative to market cap isolates highly valued cash-generating business nodes.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_high / cap), 0), subindustry)"
    },
    {
        "family": "Earnings_Yields",
        "hypothesis": "Gross margin scaled by size represents structural pricing power advantages in larger entities.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_grossincome_high / cap), 0), subindustry)"
    },
    {
        "family": "Earnings_Yields",
        "hypothesis": "Sales-efficiency multiplier (EPS divided by Sales consensus estimate) isolates operational efficiency.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_basic_splt_v4_nd_eps_estimate / anl4_fs_basic_splt_v4_nd_sales_estimate), 0), subindustry)"
    },

    # Regime 3: Conservative Margin of Safety (Fading market optimism via downside low estimate fields)
    {
        "family": "Margin_Safety",
        "hypothesis": "Selecting firms with highly robust pre-tax profit margins even in worst-case analyst forecast scenarios (Margin of Safety).",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.80, rank(anl4_fs_detail_estimates_advanced_af_nd_ptp_low / anl4_fs_basic_splt_v4_nd_sales_estimate), 0), subindustry)"
    },
    {
        "family": "Margin_Safety",
        "hypothesis": "Robust downside EBITDA margin isolates resilient cash-generating firms during economic contractions.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_low / anl4_fs_basic_splt_v4_nd_sales_estimate), 0), subindustry)"
    },
    {
        "family": "Margin_Safety",
        "hypothesis": "Worst-case cash conversion safety yield highlights defensive cash fortress companies.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_low / anl4_fs_detail_estimate_1qf_v4_nd_netprofit_low), 0), subindustry)"
    },
    {
        "family": "Margin_Safety",
        "hypothesis": "Conservative book value per share relative to market cap represents an ironclad intrinsic value buffer.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_sh_equity_low / cap), 0), subindustry)"
    },
    {
        "family": "Margin_Safety",
        "hypothesis": "High gross margins under conservative estimates protect operating returns from pricing pressure.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.80, rank(anl4_fs_detail_estimates_advanced_af_nd_grossincome_low / anl4_fs_basic_splt_v4_nd_sales_estimate), 0), subindustry)"
    },
    {
        "family": "Margin_Safety",
        "hypothesis": "Pessimistic net margin estimate highlights high-safety bottom-line income generators.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimate_1qf_v4_nd_netprofit_low / anl4_fs_basic_splt_v4_nd_sales_estimate), 0), subindustry)"
    },
    {
        "family": "Margin_Safety",
        "hypothesis": "Defensive worst-case pre-tax yield relative to market cap protects from systemic sector collapses.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.80, rank(anl4_fs_detail_estimates_advanced_af_nd_ptp_low / cap), 0), subindustry)"
    },
    {
        "family": "Margin_Safety",
        "hypothesis": "Resilient worst-case operating EBITDA yield relative to size isolates deep-value corporate assets.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_low / cap), 0), subindustry)"
    },
    {
        "family": "Margin_Safety",
        "hypothesis": "Conservative free cash flow yield relative to size flags massive cash generators priced at a discount.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_low / cap), 0), subindustry)"
    },
    {
        "family": "Margin_Safety",
        "hypothesis": "Robust worst-case gross profit margins scaled by size isolate pricing leaders with deep buffers.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_grossincome_low / cap), 0), subindustry)"
    },

    # Regime 4: Advanced Transformations & Multi-Factor Interactions
    {
        "family": "Advanced_Composite",
        "hypothesis": "The divergence between forecast operating margin (EBITDA) and net margin (Net Profit) captures early sector depreciation and leverage cycles.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_high / anl4_fs_basic_splt_v4_nd_sales_estimate) - rank(anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high / anl4_fs_basic_splt_v4_nd_sales_estimate), 0), subindustry)"
    },
    {
        "family": "Advanced_Composite",
        "hypothesis": "Concurrence of high free cash flow margins and rising consensus analyst count represents institutional high-conviction backing.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_high / anl4_fs_basic_splt_v4_nd_sales_estimate) * rank(anl10_salsmun_1qf_1002), 0), subindustry)"
    },
    {
        "family": "Advanced_Composite",
        "hypothesis": "Drift in book-to-market ratio over a 20-day period isolates accelerating valuation divergence.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_sh_equity_high / cap) - rank(ts_delay(anl4_fs_detail_estimates_advanced_af_nd_sh_equity_high / cap, 20)), 0), subindustry)"
    },
    {
        "family": "Advanced_Composite",
        "hypothesis": "Strong forecast earnings yield compounded by positive consensus momentum highlights compounding growth opportunities.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.80, rank(anl4_fs_basic_splt_v4_nd_eps_estimate / close) * rank(ts_corr(returns, anl10_netsmun_1qf_1002, 10)), 0), subindustry)"
    },
    {
        "family": "Advanced_Composite",
        "hypothesis": "The difference between high and low EBITDA forecast ranges represents analyst consensus uncertainty; fading high uncertainty captures risk premia.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_high / anl4_fs_basic_splt_v4_nd_sales_estimate) - rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_low / anl4_fs_basic_splt_v4_nd_sales_estimate), 0), subindustry)"
    },
    {
        "family": "Advanced_Composite",
        "hypothesis": "The variance spread between high and low free cash flow forecasts isolates capital structure stability and cash risk overlays.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_high / anl4_fs_basic_splt_v4_nd_sales_estimate) - rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_low / anl4_fs_basic_splt_v4_nd_sales_estimate), 0), subindustry)"
    },
    {
        "family": "Advanced_Composite",
        "hypothesis": "consensus pre-tax profit disagreement range (high vs low) captures premium arbitrage opportunities from analyst forecast dispersals.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_ptp_high / anl4_fs_basic_splt_v4_nd_sales_estimate) - rank(anl4_fs_detail_estimates_advanced_af_nd_ptp_low / anl4_fs_basic_splt_v4_nd_sales_estimate), 0), subindustry)"
    },
    {
        "family": "Advanced_Composite",
        "hypothesis": "Divergence spread between high and low net profit consensus isolates analyst divergence; fading high dispersion yields structural gains.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.80, rank(anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high / anl4_fs_basic_splt_v4_nd_sales_estimate) - rank(anl4_fs_detail_estimate_1qf_v4_nd_netprofit_low / anl4_fs_basic_splt_v4_nd_sales_estimate), 0), subindustry)"
    },
    {
        "family": "Advanced_Composite",
        "hypothesis": "Dispersion in gross margin consensus (high vs low) isolates pricing moat uncertainty; fading this filters out volatile pricing configurations.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_grossincome_high / anl4_fs_basic_splt_v4_nd_sales_estimate) - rank(anl4_fs_detail_estimates_advanced_af_nd_grossincome_low / anl4_fs_basic_splt_v4_nd_sales_estimate), 0), subindustry)"
    },
    {
        "family": "Advanced_Composite",
        "hypothesis": "Operating leverage margins interactive with sales revision momentum captures high-probability growth breakouts.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_high / anl4_fs_basic_splt_v4_nd_sales_estimate) * rank(ts_corr(returns, anl10_salsmun_1qf_1002, 10)), 0), subindustry)"
    },
    {
        "family": "Advanced_Composite",
        "hypothesis": "Bottom-line net margin yield interactive with profit revision consensus momentum isolates robust compounding assets.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high / anl4_fs_basic_splt_v4_nd_sales_estimate) * rank(ts_corr(returns, anl10_netsmun_1qf_1002, 10)), 0), subindustry)"
    },
    {
        "family": "Advanced_Composite",
        "hypothesis": "Drift in sales-to-price ratio over a 10-day period isolates accelerating gross revenue value trends.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.80, rank(anl4_fs_basic_splt_v4_nd_sales_estimate / close) - rank(ts_delay(anl4_fs_basic_splt_v4_nd_sales_estimate / close, 10)), 0), subindustry)"
    },
    {
        "family": "Advanced_Composite",
        "hypothesis": "Drift in earnings-to-price yield over a 10-day period isolates short-term forward growth breakouts.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_basic_splt_v4_nd_eps_estimate / close) - rank(ts_delay(anl4_fs_basic_splt_v4_nd_eps_estimate / close, 10)), 0), subindustry)"
    },
    {
        "family": "Advanced_Composite",
        "hypothesis": "Book-to-market relative yield interactive with sales consensus revision momentum isolates high-value quality firms.",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_sh_equity_high / cap) * rank(ts_corr(returns, anl10_salsmun_1qf_1002, 10)), 0), subindustry)"
    }
]

def main():
    print("[*] Validating 50 elite institutional quantitative alphas...")
    valid_alphas = []
    
    for idx, item in enumerate(alphas):
        formula = item["formula"]
        is_valid, msg = validate_fastexpr(formula)
        if is_valid:
            # Format to review inbox specifications
            valid_alphas.append({
                "family": item["family"],
                "hypothesis": item["hypothesis"],
                "formula": formula,
                "settings": {
                    "decay": 6,
                    "neutralization": "SUBINDUSTRY",
                    "universe": "TOP3000",
                    "truncation": 0.08,
                    "delay": 1,
                    "pasteurization": "ON",
                    "unitHandling": "VERIFY"
                }
            })
        else:
            print(f"  [x] Alpha #{idx+1:02d} Syntax Failed: {msg}")
            sys.exit(1)

    print(f"\n[+] All {len(valid_alphas)} alphas successfully validated locally!")
    
    inbox_path = PROJECT_ROOT / "db" / "inbox_queue.json"
    
    # Load current inbox if exists
    existing_inbox = []
    if inbox_path.exists():
        try:
            with open(inbox_path, "r") as f:
                existing_inbox = json.load(f)
        except Exception:
            existing_inbox = []

    # Get set of existing formulas to prevent duplicates
    existing_formulas = {a.get("formula", "").strip() for a in existing_inbox}
    
    added_count = 0
    skipped_count = 0
    
    for a in valid_alphas:
        formula = a["formula"]
        if formula in existing_formulas:
            skipped_count += 1
        else:
            existing_inbox.append(a)
            existing_formulas.add(formula)
            added_count += 1
            
    # Save back to db/inbox_queue.json
    inbox_path.parent.mkdir(exist_ok=True)
    with open(inbox_path, "w") as f:
        json.dump(existing_inbox, f, indent=2)
        
    print(f"[*] Dispatch Complete:")
    print(f"    - Added to Local Review Inbox (db/inbox_queue.json): {added_count}")
    print(f"    - Skipped (Already in inbox): {skipped_count}")
    print("[SUCCESS] Injector completed. Refresh the browser to see the 50 alphas!")

if __name__ == "__main__":
    main()
