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

ALPHAS_50 = [
    # === Regime A: Sentiment-Momentum Dynamics (20 Alphas) ===
    {
        "family": "Sales Revision Momentum Correlation",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_corr(returns, anl10_salsmun_1qf_1002, 10)), 0), subindustry)",
        "hypothesis": "Rolling correlation between equity returns and upward sales estimate revision frequency captures pricing confirmation.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Net Profit Count Momentum Correlation",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(ts_corr(returns, anl10_netsmun_1qf_1002, 10)), 0), subindustry)",
        "hypothesis": "Rolling correlation between equity returns and net profit estimate revision frequency indicates fundamental structural drift.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Basic EPS Revision Price Correlation",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.72, rank(ts_corr(returns, anl4_fs_basic_splt_v4_nd_eps_estimate, 10)), 0), subindustry)",
        "hypothesis": "High positive rolling correlation between EPS estimate growth and return signals fundamental momentum.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Sales Estimate Revision Price Correlation",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_corr(returns, anl4_fs_basic_splt_v4_nd_sales_estimate, 10)), 0), subindustry)",
        "hypothesis": "Rolling correlation of returns with raw consensus sales revisions captures sector demand growth.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Dividend Estimate Price Correlation",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.74, rank(ts_corr(returns, anl4_fs_basic_splt_v4_nd_div_estimate, 10)), 0), subindustry)",
        "hypothesis": "High positive rolling correlation between dividend consensus revisions and equity returns captures dividend safety momentum.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "FCF Revision Price Correlation",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_corr(returns, anl4_fs_detail_estimates_advanced_af_nd_fcf_high, 10)), 0), subindustry)",
        "hypothesis": "Positive correlation between price movement and upper-bound FCF estimate revision indicates strong cash-backed price discovery.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "EBITDA Revision Price Correlation",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(ts_corr(returns, anl4_fs_detail_estimates_advanced_af_nd_ebitda_high, 10)), 0), subindustry)",
        "hypothesis": "High correlation of EBITDA revisions with daily returns captures strong pricing momentum supported by operational cash flows.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Gross Income Revision Price Correlation",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.72, rank(ts_corr(returns, anl4_fs_detail_estimates_advanced_af_nd_grossincome_high, 10)), 0), subindustry)",
        "hypothesis": "Positive correlation of returns with high gross income consensus adjustment targets growth leaders.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pretax Income Price Correlation",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_corr(returns, anl4_fs_detail_estimates_advanced_af_nd_ptp_high, 10)), 0), subindustry)",
        "hypothesis": "Rolling correlation between returns and pretax profit estimates isolates firms with strong underlying pre-tax earnings potential.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Net Profit Revision Price Correlation",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.76, rank(ts_corr(returns, anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high, 10)), 0), subindustry)",
        "hypothesis": "Rolling correlation between high net profit estimates and returns isolates bottom-line profitability drift.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Sales Revision Short Reversion",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_corr(returns, anl10_salsmun_1qf_1002, 20)), 0), subindustry)",
        "hypothesis": "Longer term negative correlation indicates overextended sentiment-driven price runs set to revert.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Net Profit Revision Short Reversion",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank(ts_corr(returns, anl10_netsmun_1qf_1002, 20)), 0), subindustry)",
        "hypothesis": "Negative rolling correlation of returns with net profit revision count signals overbought mean-reversion triggers.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "EPS Revision Reversal Correlation",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.72, -rank(ts_corr(returns, anl4_fs_basic_splt_v4_nd_eps_estimate, 20)), 0), subindustry)",
        "hypothesis": "Medium term negative correlation of returns with consensus EPS revisions targets overbought pricing mean-reversion.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Sales Consensus Reversal Correlation",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_corr(returns, anl4_fs_basic_splt_v4_nd_sales_estimate, 20)), 0), subindustry)",
        "hypothesis": "Negative 20-day correlation of returns and consensus sales estimates triggers when price changes dislocate from fundamentals.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Dividend Yield Reversion Correlation",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.74, -rank(ts_corr(returns, anl4_fs_basic_splt_v4_nd_div_estimate, 20)), 0), subindustry)",
        "hypothesis": "Negative rolling correlation between returns and dividend consensus estimates identifies yield traps.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "FCF Consensus Reversal Correlation",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_corr(returns, anl4_fs_detail_estimates_advanced_af_nd_fcf_high, 20)), 0), subindustry)",
        "hypothesis": "Negative rolling correlation between FCF estimates and price changes signals intermediate trend corrections.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "EBITDA Consensus Reversal Correlation",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank(ts_corr(returns, anl4_fs_detail_estimates_advanced_af_nd_ebitda_high, 20)), 0), subindustry)",
        "hypothesis": "Negative correlation of returns with high EBITDA estimates exposes valuation expansions relative to operating profit.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Gross Income Consensus Reversion",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.72, -rank(ts_corr(returns, anl4_fs_detail_estimates_advanced_af_nd_grossincome_high, 20)), 0), subindustry)",
        "hypothesis": "Negative rolling correlation between returns and high gross income consensus identifies pricing fatigue.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pretax Income Reversal Correlation",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank(ts_corr(returns, anl4_fs_detail_estimates_advanced_af_nd_ptp_high, 20)), 0), subindustry)",
        "hypothesis": "Exposes valuation divergences from underlying pretax profits on highly active sessions.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Net Profit Reversal Correlation",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.76, -rank(ts_corr(returns, anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high, 20)), 0), subindustry)",
        "hypothesis": "Fading price action when returns show decoupling from net profit high estimates over 20-day windows.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },

    # === Regime B: Earnings Divergence & Yields (10 Alphas) ===
    {
        "family": "FCF EBITDA Coverage Spread",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_high / (anl4_fs_detail_estimates_advanced_af_nd_ebitda_high + 0.001)), 0), subindustry)",
        "hypothesis": "Ratio of upper-bound consensus FCF to EBITDA highlights cash-flow conversion quality, avoiding paper earnings traps.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Analyst Consensus Operating Margin",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "High consensus EBITDA-to-Sales margin signals exceptional sector-relative pricing power.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Net Profit Margin Proxy",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "Relative rank of net margin high expectations isolates bottom-line growth leaders within peers.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "ROE Fundamental Proxy",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high / (anl4_fs_detail_estimates_advanced_af_nd_sh_equity_high + 0.001)), 0), subindustry)",
        "hypothesis": "Forward return-on-equity proxy. High forward ROE expectations capture structural compounders.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "FCF Consensus Yield",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_high / (cap + 0.001)), 0), subindustry)",
        "hypothesis": "Forward FCF yield based on optimistic consensus estimates exploits cash value anomalies.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Earnings Yield Proxy",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_basic_splt_v4_nd_eps_estimate / (close + 0.001)), 0), subindustry)",
        "hypothesis": "High consensus EPS-to-price ratio captures mispriced value assets with strong fundamental support.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Dividend Yield Proxy",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.78, rank(anl4_fs_basic_splt_v4_nd_div_estimate / (close + 0.001)), 0), subindustry)",
        "hypothesis": "Consensus dividend yield captures yield-sensitive structural premium anomalies.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Gross Margin Profitability Proxy",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_grossincome_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "Ratio of consensus gross income to sales isolates firms with persistent unit economic dominance.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pretax Yield Proxy",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.72, rank(anl4_fs_detail_estimates_advanced_af_nd_ptp_high / (cap + 0.001)), 0), subindustry)",
        "hypothesis": "Forward pre-tax profit normalized by market capitalization isolates deep fundamental value.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Shareholder Equity Book Yield",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_sh_equity_high / (cap + 0.001)), 0), subindustry)",
        "hypothesis": "Optimistic shareholder equity to market capitalization represents a robust forward book-to-market factor.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },

    # === Regime C: Conservative Margin of Safety (10 Alphas) ===
    {
        "family": "FCF Pessimistic Yield Floor",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_low / (cap + 0.001)), 0), subindustry)",
        "hypothesis": "Downside FCF yield floor isolates value stocks that remain robust even under conservative worst-case scenario estimates.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pessimistic Operating Margin Floor",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_low / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "Worst-case EBITDA margin floor targets high-conviction margin-of-safety compounders.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Net Profit Pessimistic Margin Floor",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimate_1qf_v4_nd_netprofit_low / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "Under pessimistic consensus, firms preserving net profitability floors represent maximum capital protection.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pretax Income Downside Yield",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.72, rank(anl4_fs_detail_estimates_advanced_af_nd_ptp_low / (cap + 0.001)), 0), subindustry)",
        "hypothesis": "Pre-tax income yield under worst-case consensus measures robustness against negative operational surprises.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pessimistic Book Yield Floor",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.80, rank(anl4_fs_detail_estimates_advanced_af_nd_sh_equity_low / (cap + 0.001)), 0), subindustry)",
        "hypothesis": "Book value to market capitalization floor utilizing worst-case shareholder equity protects against capital erosion.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pessimistic Gross Margin Floor",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_grossincome_low / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "Worst-case gross margin ratio represents pure unit pricing power floor under distress.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "FCF Pessimistic Yield Fade",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_low / (cap + 0.001)), 0), subindustry)",
        "hypothesis": "Fading low worst-case FCF yield companies under extreme volume represents dynamic risk transference.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pessimistic Operating Margin Fade",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_low / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "Shorting companies with poor worst-case EBITDA margin floors captures operational decay premiums.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pessimistic Net Profit Floor Fade",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank(anl4_fs_detail_estimate_1qf_v4_nd_netprofit_low / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "Under pessimistic consensus, shorting firms that fail to defend their profitability floors matches decay expectations.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pessimistic Pretax Yield Fade",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.72, -rank(anl4_fs_detail_estimates_advanced_af_nd_ptp_low / (cap + 0.001)), 0), subindustry)",
        "hypothesis": "Shorting companies with high pre-tax downside risk isolates structural underperformers.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },

    # === Regime D: Advanced Transformations (10 Alphas) ===
    {
        "family": "EBITDA Dispersal Risk fading",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, -rank((anl4_fs_detail_estimates_advanced_af_nd_ebitda_high - anl4_fs_detail_estimates_advanced_af_nd_ebitda_low) / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "Severe analyst disagreement (high-low spread) indicates information asymmetry and fundamental instability. Shorting high dispersion avoids value traps.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "FCF Dispersal Risk fading",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.72, -rank((anl4_fs_detail_estimates_advanced_af_nd_fcf_high - anl4_fs_detail_estimates_advanced_af_nd_fcf_low) / (cap + 0.001)), 0), subindustry)",
        "hypothesis": "Scaling FCF estimate dispersion by market capitalization highlights excessive uncertainty. Fading high uncertainty generates premium.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Net Profit Dispersal fading",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank((anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high - anl4_fs_detail_estimate_1qf_v4_nd_netprofit_low) / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "High dispersion on bottom-line net profit estimates is scaled by sales. Shorting high uncertainty signals mean-reversion in expectations.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pre-tax Dispersion fading",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank((anl4_fs_detail_estimates_advanced_af_nd_ptp_high - anl4_fs_detail_estimates_advanced_af_nd_ptp_low) / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "Firms with tight pre-tax consensus have reliable pricing signals, while wide pre-tax consensus spreads are shorted.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Multi-Estimate Consensus Correlation Spread",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(ts_corr(returns, anl10_salsmun_1qf_1002, 10) + ts_corr(returns, anl10_netsmun_1qf_1002, 10)), 0), subindustry)",
        "hypothesis": "Double-confirmation of fundamental momentum using rolling return correlation with both Sales and Net Profit upward analyst revisions.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Margin Growth Divergence Spread",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimate_1qf_v4_nd_netprofit_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001) + anl4_fs_detail_estimates_advanced_af_nd_ebitda_high / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "Joint relative performance of net margin and operating cash margin isolates structural pricing leaders.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Yield Convergence Composite",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.72, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_high / (cap + 0.001) + anl4_fs_basic_splt_v4_nd_eps_estimate / (close + 0.001)), 0), subindustry)",
        "hypothesis": "Exposing the aggregate forward value premium through joint FCF yield and forward earnings yield parameters.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pessimistic Yield Floor Composite",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.70, rank(anl4_fs_detail_estimates_advanced_af_nd_fcf_low / (cap + 0.001) + anl4_fs_basic_splt_v4_nd_div_estimate / (close + 0.001)), 0), subindustry)",
        "hypothesis": "Joint forward downside protection yield combining worst-case FCF floor with consensus dividend yield metrics.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Pessimistic Margin Floor Composite",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, rank(anl4_fs_detail_estimates_advanced_af_nd_ebitda_low / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001) + anl4_fs_detail_estimate_1qf_v4_nd_netprofit_low / (anl4_fs_basic_splt_v4_nd_sales_estimate + 0.001)), 0), subindustry)",
        "hypothesis": "Combining absolute downside floor operating margin with net margin floor represents a fortress margin-of-safety portfolio.",
        "settings": {"decay": 5, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
    },
    {
        "family": "Consensus Trend Dispersal Spread",
        "formula": "group_neutralize(trade_when(volume > adv20 * 0.74, rank(ts_corr(returns, anl10_salsmun_1qf_1002, 10) - ts_corr(returns, anl10_netsmun_1qf_1002, 10)), 0), subindustry)",
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
        print(f"Pushing 50 premium alphas to {name.upper()}'s inbox queue...")
        
        # 1. Post to queue-alpha
        res, code = post_endpoint(conf["url"], "/api/queue-alpha", conf["token"], ALPHAS_50)
        print(f"Queue Status Code: {code} | Response: {res}")
        
        # 2. Inject immediately to simulation queue
        print(f"Injecting inbox to simulation queue on {name.upper()}...")
        inject_res, inject_code = post_endpoint(conf["url"], "/api/inject-inbox", conf["token"], {"all": True})
        print(f"Injection Status Code: {inject_code} | Response: {inject_res}")

if __name__ == "__main__":
    main()
