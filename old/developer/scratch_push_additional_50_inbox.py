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

ALPHAS_51_100 = [
    # === Regime A: Sentiment-Momentum Dynamics (20 Alphas) ===
    {
        "family": "Sales Revision Momentum Correlation (5d)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_corr(returns, anl10_salsmun_1qf_1002, 5)), 0), subindustry)",
        "hypothesis": "Short-term rolling correlation between equity returns and upward sales estimate revision frequency captures pricing confirmation.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Net Profit Count Momentum Correlation (5d)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(ts_corr(returns, anl10_netsmun_1qf_1002, 5)), 0), subindustry)",
        "hypothesis": "Short-term rolling correlation between equity returns and net profit estimate revision frequency indicates structural drift.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Basic EPS Revision Price Correlation (5d)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.72, rank(ts_corr(returns, anl4_fs_basic_splt_v4_nd_eps_estimate, 5)), 0), subindustry)",
        "hypothesis": "High positive short-term rolling correlation between EPS estimate growth and return signals fundamental momentum.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Sales Estimate Revision Price Correlation (5d)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_corr(returns, anl4_fs_basic_splt_v4_nd_sales_estimate, 5)), 0), subindustry)",
        "hypothesis": "Short-term rolling correlation of returns with raw consensus sales revisions captures demand growth.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Dividend Estimate Price Correlation (5d)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.74, rank(ts_corr(returns, anl4_fs_basic_splt_v4_nd_div_estimate, 5)), 0), subindustry)",
        "hypothesis": "Short-term positive rolling correlation between dividend consensus revisions and returns captures safety momentum.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "FCF Revision Price Correlation (5d)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_corr(returns, anl4_fs_detail_estimates_advanced_af_nd_fcf_high, 5)), 0), subindustry)",
        "hypothesis": "Short-term correlation between price movement and upper-bound FCF estimate revision indicates cash-backed price discovery.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "EBITDA Revision Price Correlation (5d)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(ts_corr(returns, anl4_fs_detail_estimates_advanced_af_nd_ebitda_high, 5)), 0), subindustry)",
        "hypothesis": "Short-term correlation of EBITDA revisions with returns captures momentum supported by operating cash flows.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Gross Income Revision Price Correlation (5d)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.72, rank(ts_corr(returns, anl4_fs_detail_estimates_advanced_af_nd_grossincome_high, 5)), 0), subindustry)",
        "hypothesis": "Short-term correlation of returns with high gross income consensus adjustment targets growth leaders.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pretax Income Price Correlation (5d)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_corr(returns, anl4_fs_detail_estimates_advanced_af_nd_ptp_high, 5)), 0), subindustry)",
        "hypothesis": "Short-term rolling correlation between returns and pretax profit estimates isolates firms with pre-tax potential.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Net Profit Revision Price Correlation (5d)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.76, rank(ts_corr(returns, anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high, 5)), 0), subindustry)",
        "hypothesis": "Short-term rolling correlation between high net profit estimates and returns isolates profitability drift.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Sales Revision Short Reversion (15d)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_corr(returns, anl10_salsmun_1qf_1002, 15)), 0), subindustry)",
        "hypothesis": "Intermediate term negative correlation indicates overextended sentiment-driven price runs set to revert.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Net Profit Revision Short Reversion (15d)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank(ts_corr(returns, anl10_netsmun_1qf_1002, 15)), 0), subindustry)",
        "hypothesis": "Intermediate negative rolling correlation of returns with net profit revision count signals reversion triggers.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "EPS Revision Reversal Correlation (15d)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.72, -rank(ts_corr(returns, anl4_fs_basic_splt_v4_nd_eps_estimate, 15)), 0), subindustry)",
        "hypothesis": "Intermediate negative correlation of returns with consensus EPS revisions targets overbought reversion.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Sales Consensus Reversal Correlation (15d)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_corr(returns, anl4_fs_basic_splt_v4_nd_sales_estimate, 15)), 0), subindustry)",
        "hypothesis": "Intermediate negative correlation of returns and consensus sales estimates triggers on fundamental dislocation.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Dividend Yield Reversion Correlation (15d)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.74, -rank(ts_corr(returns, anl4_fs_basic_splt_v4_nd_div_estimate, 15)), 0), subindustry)",
        "hypothesis": "Intermediate negative rolling correlation between returns and dividend consensus estimates identifies yield traps.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "FCF Consensus Reversal Correlation (15d)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_corr(returns, anl4_fs_detail_estimates_advanced_af_nd_fcf_high, 15)), 0), subindustry)",
        "hypothesis": "Intermediate negative rolling correlation between FCF estimates and price changes signals corrections.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "EBITDA Consensus Reversal Correlation (15d)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank(ts_corr(returns, anl4_fs_detail_estimates_advanced_af_nd_ebitda_high, 15)), 0), subindustry)",
        "hypothesis": "Intermediate negative correlation of returns with high EBITDA estimates exposes valuation expansions.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Gross Income Consensus Reversion (15d)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.72, -rank(ts_corr(returns, anl4_fs_detail_estimates_advanced_af_nd_grossincome_high, 15)), 0), subindustry)",
        "hypothesis": "Intermediate negative rolling correlation between returns and high gross income consensus identifies fatigue.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pretax Income Reversal Correlation (15d)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_corr(returns, anl4_fs_detail_estimates_advanced_af_nd_ptp_high, 15)), 0), subindustry)",
        "hypothesis": "Exposes valuation divergences from underlying pretax profits on active sessions (intermediate).",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Net Profit Reversal Correlation (15d)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.76, -rank(ts_corr(returns, anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high, 15)), 0), subindustry)",
        "hypothesis": "Fading price action when returns show decoupling from net profit high estimates over 15-day windows.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },

    # === Regime B: Earnings Divergence & Yields (10 Alphas) ===
    {
        "family": "FCF Net Profit Coverage Spread",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_high / (anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high + 0.001)), 0), subindustry)",
        "hypothesis": "Ratio of upper-bound consensus FCF to Net Profit highlights cash extraction efficiency, bypassing paper earnings.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Analyst Consensus Pretax Margin",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_ptp_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "High consensus Pre-tax Profit to Sales margin signals exceptional operational cost controls.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Gross Margin to Equity Ratio",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_grossincome_high / (anl4_fs_detail_estimates_advanced_af_nd_sh_equity_high + 0.001)), 0), subindustry)",
        "hypothesis": "Measures gross earnings generation per unit of book equity. Highlights operational asset compounders.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "EBITDA Return on Book Equity",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_high / (anl4_fs_detail_estimates_advanced_af_nd_sh_equity_high + 0.001)), 0), subindustry)",
        "hypothesis": "Consensus operating return on book equity captures core fundamental return potency.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Net Profit Yield Proxy",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high / (cap + 0.001)), 0), subindustry)",
        "hypothesis": "Bottom-line net profit consensus yield floor scaled by market capitalization captures pure value anomaly.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "EBITDA Yield Proxy",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_high / (cap + 0.001)), 0), subindustry)",
        "hypothesis": "Operating profit consensus yield captures core asset pricing premium relative to peer subindustry groups.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Gross Income Value Yield",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.78, rank(anl4_fs_detail_estimates_advanced_af_nd_grossincome_high / (cap + 0.001)), 0), subindustry)",
        "hypothesis": "Consensus gross income normalized by market capitalization isolates structural valuation discounts.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Net Profit Price Yield",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high / (close + 0.001)), 0), subindustry)",
        "hypothesis": "Forward earnings yield based on optimistic net profit estimates targets high-conviction value.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "FCF Price Yield",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.72, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_high / (close + 0.001)), 0), subindustry)",
        "hypothesis": "Forward FCF yield based on optimistic cash flow estimates normalized by share price captures structural anomalies.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pretax Income Price Yield",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_ptp_high / (close + 0.001)), 0), subindustry)",
        "hypothesis": "Forward pre-tax yield normalized by closing share price isolates robust capital efficiency leaders.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },

    # === Regime C: Conservative Margin of Safety (10 Alphas) ===
    {
        "family": "EBITDA Pessimistic Yield Floor",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_low / (cap + 0.001)), 0), subindustry)",
        "hypothesis": "Downside EBITDA yield floor isolates value stocks that remain resilient even under worst-case operating scenarios.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pessimistic Gross Yield Floor",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_grossincome_low / (cap + 0.001)), 0), subindustry)",
        "hypothesis": "Worst-case consensus gross profit yield targets premium margin-of-safety value positions.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pessimistic FCF Sales Margin",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_low / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "Firms preserving cash margins relative to sales even under worst-case consensus protect investors.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pessimistic Operating ROE Floor",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.72, rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_low / (anl4_fs_detail_estimates_advanced_af_nd_sh_equity_low + 0.001)), 0), subindustry)",
        "hypothesis": "Worst-case consensus operating return on book equity identifies stable, low-risk capital compounders.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pessimistic Net ROE Floor",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.80, rank(anl4_fs_detail_estimate_1qf_v4_nd_netprofit_low / (anl4_fs_detail_estimates_advanced_af_nd_sh_equity_low + 0.001)), 0), subindustry)",
        "hypothesis": "Firms defending net margin floor relative to downside equity preserve investment capital.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pessimistic Pre-tax Margin Floor",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_ptp_low / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "Pre-tax margin floor isolates firms with low operational risk profiles relative to subindustry peers.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "EBITDA Pessimistic Yield Fade",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_low / (cap + 0.001)), 0), subindustry)",
        "hypothesis": "Shorting companies with high downside EBITDA risk profiles targets structural operational declines.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pessimistic Gross Yield Fade",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank(anl4_fs_detail_estimates_advanced_af_nd_grossincome_low / (cap + 0.001)), 0), subindustry)",
        "hypothesis": "Shorting companies with poor worst-case gross yield margins targets weak unit compounders.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pessimistic FCF Margin Fade",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_low / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "Under pessimistic consensus, shorting firms that fail to defend cash flows relative to sales matches decay.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pessimistic Book Yield Floor Fade",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.72, -rank(anl4_fs_detail_estimates_advanced_af_nd_sh_equity_low / (cap + 0.001)), 0), subindustry)",
        "hypothesis": "Shorting companies with severe downside book erosion risk yields consistent premium.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },

    # === Regime D: Advanced Transformations (10 Alphas) ===
    {
        "family": "Gross Margin Dispersal Risk fading",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank((anl4_fs_detail_estimates_advanced_af_nd_grossincome_high - anl4_fs_detail_estimates_advanced_af_nd_grossincome_low) / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "Severe analyst disagreement on gross profit estimates represents pricing fatigue. Shorting high dispersion creates premium.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Book Equity Dispersal Risk fading",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.72, -rank((anl4_fs_detail_estimates_advanced_af_nd_sh_equity_high - anl4_fs_detail_estimates_advanced_af_nd_sh_equity_low) / (cap + 0.001)), 0), subindustry)",
        "hypothesis": "Consensus book value disagreement normalized by market capitalization highlights structural instability. Shorting high dispersion captures a premium.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Net Margin Growth Divergence",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001) - anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "Divergence spreads in net margin high expectations isolates structural compounders.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Consensus Operating Divergence Spread",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001) - anl4_fs_detail_estimates_advanced_af_nd_ptp_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "Divergence between EBITDA margin and Pretax margin consensus indicates tax/leverage inefficiencies.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Composite Revision Trend Spread (5d)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_corr(returns, anl10_salsmun_1qf_1002, 5) + ts_corr(returns, anl10_netsmun_1qf_1002, 5)), 0), subindustry)",
        "hypothesis": "Double-confirmation of fundamental momentum using short-term return correlation with both Sales and Net Profit upward revisions.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Composite Value Yield (Floor Cap)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_high / (cap + 0.001) + anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high / (cap + 0.001)), 0), subindustry)",
        "hypothesis": "Combined operating and net yield estimates captures aggregate value premium relative to subindustry.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Consensus Growth Convergence (5d)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.72, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_high / (close + 0.001) + anl4_fs_basic_splt_v4_nd_eps_estimate / (close + 0.001)), 0), subindustry)",
        "hypothesis": "Forward cash and EPS yields relative to share price isolates highly efficient capital allocators.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pessimistic Composite Yield Floor (5d)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_low / (close + 0.001) + anl4_fs_basic_splt_v4_nd_div_estimate / (close + 0.001)), 0), subindustry)",
        "hypothesis": "Forward downside protection yield floor combining worst-case FCF floor with consensus dividend yield metrics.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pessimistic Margin Floor Composite (5d)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_low / (cap + 0.001) + anl4_fs_detail_estimate_1qf_v4_nd_netprofit_low / (cap + 0.001)), 0), subindustry)",
        "hypothesis": "Combining absolute downside floor operating margin with net margin floor represents a fortress value portfolio.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Consensus Trend Dispersal Spread (5d)",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.74, rank(ts_corr(returns, anl10_salsmun_1qf_1002, 5) - ts_corr(returns, anl10_netsmun_1qf_1002, 5)), 0), subindustry)",
        "hypothesis": "Exposing divergence trends between top-line revenue revision intensity and bottom-line profit revision intensity.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
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
        print(f"Pushing additional 50 premium alphas (51-100) to {name.upper()}'s API Review Box...")
        
        # Only POST to queue-alpha to store in the inbox queue.
        # DO NOT call inject-inbox so they remain strictly in the API Review Box!
        res, code = post_endpoint(conf["url"], "/api/queue-alpha", conf["token"], ALPHAS_51_100)
        print(f"Queue Status Code: {code} | Response: {res}")

if __name__ == "__main__":
    main()
