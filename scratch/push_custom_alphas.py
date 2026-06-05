import json
import urllib.request
import ssl
from src.validator import validate_fastexpr

API_URL = "https://world-quant.onrender.com/api/queue-alpha"
API_AUTH_TOKEN = "yashthakreop"

alphas_data = [
  {
    "id": 1,
    "family": "ThemePool_USA_D1",
    "dataset": "analyst10",
    "competition": "USA_D1_FastDatasets_PowerPool_June2026",
    "hypothesis": "Stocks where analyst coverage count is accelerating relative to subindustry peers attract institutional buying pressure, generating short-term price momentum in US large-cap names.",
    "anomaly_basis": "Analyst attention / neglected-firm effect reversal",
    "formula": "trade_when(volume > adv20 * 0.70, group_neutralize(ts_corr(returns, rank(anl10_cnt_up), 10), subindustry), 0)",
    "settings": {
      "region": "USA",
      "delay": 1,
      "decay": 5,
      "neutralization": "SUBINDUSTRY",
      "universe": "TOP3000",
      "truncation": 0.08
    }
  },
  {
    "id": 2,
    "family": "ThemePool_USA_D1",
    "dataset": "analyst10",
    "competition": "USA_D1_FastDatasets_PowerPool_June2026",
    "hypothesis": "Stocks whose analyst coverage rank has been consistently above its 20-day mean are experiencing sustained institutional attention, a leading indicator of price outperformance.",
    "anomaly_basis": "Rolling attention percentile / institutional herding",
    "formula": "trade_when(volume > adv20 * 0.65, group_neutralize(ts_av_diff(rank(anl10_cnt_up), 20), subindustry), 0)",
    "settings": {
      "region": "USA",
      "delay": 1,
      "decay": 5,
      "neutralization": "SUBINDUSTRY",
      "universe": "TOP3000",
      "truncation": 0.08
    }
  },
  {
    "id": 3,
    "family": "ThemePool_USA_D1",
    "dataset": "analyst10",
    "competition": "USA_D1_FastDatasets_PowerPool_June2026",
    "hypothesis": "When recent price returns are positively correlated with analyst downgrade counts over a 15-day window, contrarian mean-reversion is imminent as the market has over-discounted bearish coverage.",
    "anomaly_basis": "Contrarian coverage momentum / analyst overreaction",
    "formula": "trade_when(volume > adv20 * 0.75, group_neutralize(-ts_corr(returns, rank(anl10_cnt_down), 15), subindustry), 0)",
    "settings": {
      "region": "USA",
      "delay": 1,
      "decay": 5,
      "neutralization": "SUBINDUSTRY",
      "universe": "TOP3000",
      "truncation": 0.08
    }
  },
  {
    "id": 4,
    "family": "ThemePool_USA_D1",
    "dataset": "analyst10",
    "competition": "USA_D1_FastDatasets_PowerPool_June2026",
    "hypothesis": "Stocks with high analyst upgrade counts relative to prior-period upgrade counts (lead-lag ratio) show momentum continuation as new coverage initiates a positive feedback loop.",
    "anomaly_basis": "Lead-lag revision spread / post-revision drift",
    "formula": "trade_when(volume > adv20 * 0.70, group_neutralize(rank(rank(anl10_cnt_up) / ts_delay(rank(anl10_cnt_up), 5)), subindustry), 0)",
    "settings": {
      "region": "USA",
      "delay": 1,
      "decay": 5,
      "neutralization": "SUBINDUSTRY",
      "universe": "TOP3000",
      "truncation": 0.08
    }
  },
  {
    "id": 5,
    "family": "ThemePool_USA_D1",
    "dataset": "analyst10",
    "competition": "USA_D1_FastDatasets_PowerPool_June2026",
    "hypothesis": "On down-return days, stocks with high analyst upgrade counts are oversold relative to their fundamental momentum signal, creating a mean-reversion opportunity when the directional conviction toggle is applied.",
    "anomaly_basis": "Directional conviction toggle / return-conditional attention signal",
    "formula": "trade_when(volume > adv20 * 0.68, group_neutralize((returns < 0) ? -rank(anl10_cnt_up) : rank(anl10_cnt_up), subindustry), 0)",
    "settings": {
      "region": "USA",
      "delay": 1,
      "decay": 5,
      "neutralization": "SUBINDUSTRY",
      "universe": "TOP3000",
      "truncation": 0.08
    }
  },
  {
    "id": 6,
    "family": "ThemePool_USA_D1",
    "dataset": "analyst14",
    "competition": "USA_D1_FastDatasets_PowerPool_June2026",
    "hypothesis": "Stocks receiving upward EPS estimate revisions relative to their subindustry peers exhibit post-earnings announcement drift as the market underreacts to analyst forecast upgrades in US equities.",
    "anomaly_basis": "Post-earnings announcement drift (PEAD) / EPS revision momentum",
    "formula": "trade_when(volume > adv20 * 0.70, group_zscore(anl14_eps_up_cnt, subindustry), 0)",
    "settings": {
      "region": "USA",
      "delay": 1,
      "decay": 8,
      "neutralization": "SUBINDUSTRY",
      "universe": "TOP3000",
      "truncation": 0.08
    }
  },
  {
    "id": 7,
    "family": "ThemePool_USA_D1",
    "dataset": "analyst14",
    "competition": "USA_D1_FastDatasets_PowerPool_June2026",
    "hypothesis": "The ratio of upward to downward EPS revisions captures analyst consensus momentum; stocks with the highest revision ratio within their subindustry outperform as institutional sentiment shifts.",
    "anomaly_basis": "Analyst consensus ratio / revision breadth momentum",
    "formula": "trade_when(volume > adv20 * 0.75, group_neutralize(rank(anl14_eps_up_cnt / anl14_eps_down_cnt), subindustry), 0)",
    "settings": {
      "region": "USA",
      "delay": 1,
      "decay": 8,
      "neutralization": "SUBINDUSTRY",
      "universe": "TOP3000",
      "truncation": 0.08
    }
  },
  {
    "id": 8,
    "family": "ThemePool_USA_D1",
    "dataset": "analyst14",
    "competition": "USA_D1_FastDatasets_PowerPool_June2026",
    "hypothesis": "Stocks with high revenue estimate upgrade counts relative to subindustry peers reflect improving top-line expectations that the market has not yet fully priced in, generating predictable alpha over 8-day horizons.",
    "anomaly_basis": "Revenue estimate revision momentum / analyst forecast drift",
    "formula": "trade_when(volume > adv20 * 0.65, group_zscore(anl14_rev_up_cnt, subindustry), 0)",
    "settings": {
      "region": "USA",
      "delay": 1,
      "decay": 8,
      "neutralization": "SUBINDUSTRY",
      "universe": "TOP3000",
      "truncation": 0.08
    }
  },
  {
    "id": 9,
    "family": "ThemePool_USA_D1",
    "dataset": "analyst14",
    "competition": "USA_D1_FastDatasets_PowerPool_June2026",
    "hypothesis": "The ratio of EPS to revenue estimate upgrades identifies stocks where analysts are simultaneously improving margin and top-line outlooks, a high-conviction fundamental signal underpriced by the market.",
    "anomaly_basis": "Dual-revision quality signal / margin expansion anticipation",
    "formula": "trade_when(volume > adv20 * 0.72, group_neutralize(rank(anl14_eps_up_cnt / anl14_rev_up_cnt), subindustry), 0)",
    "settings": {
      "region": "USA",
      "delay": 1,
      "decay": 8,
      "neutralization": "SUBINDUSTRY",
      "universe": "TOP3000",
      "truncation": 0.08
    }
  },
  {
    "id": 10,
    "family": "ThemePool_USA_D1",
    "dataset": "analyst15",
    "competition": "USA_D1_FastDatasets_PowerPool_June2026",
    "hypothesis": "Stocks receiving more analyst Buy/Strong-Buy recommendation upgrades relative to their subindustry capture institutional conviction shifts that precede price appreciation in the US TOP3000 universe.",
    "anomaly_basis": "Recommendation upgrade momentum / institutional conviction signal",
    "formula": "trade_when(volume > adv20 * 0.70, group_zscore(anl15_rec_up_cnt, subindustry), 0)",
    "settings": {
      "region": "USA",
      "delay": 1,
      "decay": 8,
      "neutralization": "SUBINDUSTRY",
      "universe": "TOP3000",
      "truncation": 0.08
    }
  },
  {
    "id": 11,
    "family": "ThemePool_USA_D1",
    "dataset": "analyst15",
    "competition": "USA_D1_FastDatasets_PowerPool_June2026",
    "hypothesis": "The spread between recommendation upgrades and downgrades within a subindustry identifies net sentiment momentum; stocks at the top of this ranking outperform as institutional opinion consensus forms.",
    "anomaly_basis": "Net recommendation sentiment / analyst herding effect",
    "formula": "trade_when(volume > adv20 * 0.65, group_neutralize(rank(anl15_rec_up_cnt / anl15_rec_down_cnt), subindustry), 0)",
    "settings": {
      "region": "USA",
      "delay": 1,
      "decay": 8,
      "neutralization": "SUBINDUSTRY",
      "universe": "TOP3000",
      "truncation": 0.08
    }
  },
  {
    "id": 12,
    "family": "ThemePool_USA_D1",
    "dataset": "analyst15",
    "competition": "USA_D1_FastDatasets_PowerPool_June2026",
    "hypothesis": "Stocks where analyst recommendation upgrades significantly outnumber downgrades within a 60-day window exhibit sustained outperformance as the slow diffusion of institutional opinion drives price discovery.",
    "anomaly_basis": "Slow information diffusion / recommendation breadth drift",
    "formula": "trade_when(volume > adv20 * 0.78, group_zscore(anl15_rec_up_cnt, subindustry), 0)",
    "settings": {
      "region": "USA",
      "delay": 1,
      "decay": 8,
      "neutralization": "SUBINDUSTRY",
      "universe": "TOP3000",
      "truncation": 0.08
    }
  },
  {
    "id": 13,
    "family": "ThemePool_USA_D1",
    "dataset": "analyst10",
    "competition": "USA_D1_FastDatasets_PowerPool_June2026",
    "hypothesis": "The 60-day rolling rank percentile of analyst upgrade counts identifies stocks in sustained coverage expansion phases, a long-duration attention signal that precedes multi-week institutional accumulation.",
    "anomaly_basis": "Long-duration attention percentile / institutional accumulation signal",
    "formula": "trade_when(volume > adv20 * 0.65, group_neutralize(ts_rank(rank(anl10_cnt_up), 60), subindustry), 0)",
    "settings": {
      "region": "USA",
      "delay": 1,
      "decay": 5,
      "neutralization": "SUBINDUSTRY",
      "universe": "TOP3000",
      "truncation": 0.08
    }
  },
  {
    "id": 14,
    "family": "ThemePool_USA_D1",
    "dataset": "analyst10",
    "competition": "USA_D1_FastDatasets_PowerPool_June2026",
    "hypothesis": "Cross-sectional rank of the 5-day mean deviation of analyst upgrade counts captures short-term spikes in analyst attention before they are reflected in prices, exploiting the fastest portion of the coverage momentum signal.",
    "anomaly_basis": "Short-horizon attention spike / fast coverage momentum",
    "formula": "trade_when(volume > adv20 * 0.80, group_neutralize(ts_av_diff(rank(anl10_cnt_up), 5), subindustry), 0)",
    "settings": {
      "region": "USA",
      "delay": 1,
      "decay": 5,
      "neutralization": "SUBINDUSTRY",
      "universe": "TOP3000",
      "truncation": 0.08
    }
  },
  {
    "id": 15,
    "family": "ThemePool_USA_D1",
    "dataset": "analyst14",
    "competition": "USA_D1_FastDatasets_PowerPool_June2026",
    "hypothesis": "Stocks with a high ratio of total estimate revisions (up + down) to subindustry median signal elevated information uncertainty; going long those with net-positive revisions exploits the uncertainty premium in US equities.",
    "anomaly_basis": "Earnings estimate dispersion / information uncertainty premium",
    "formula": "trade_when(volume > adv20 * 0.70, group_neutralize(rank((anl14_eps_up_cnt - anl14_eps_down_cnt) / (anl14_eps_up_cnt + anl14_eps_down_cnt)), subindustry), 0)",
    "settings": {
      "region": "USA",
      "delay": 1,
      "decay": 8,
      "neutralization": "SUBINDUSTRY",
      "universe": "TOP3000",
      "truncation": 0.08
    }
  },
  {
    "id": 16,
    "family": "ThemePool_USA_D1",
    "dataset": "analyst10",
    "competition": "USA_D1_FastDatasets_PowerPool_June2026",
    "hypothesis": "Cross-dataset combo: stocks simultaneously ranked high on analyst coverage acceleration (analyst10) AND peer-relative EPS upgrade count (analyst14) exhibit the strongest analyst-driven momentum, combining attention with conviction.",
    "anomaly_basis": "Cross-dataset attention × conviction combo / institutional double-signal",
    "formula": "trade_when(volume > adv20 * 0.70, group_neutralize(rank(anl10_cnt_up) * group_zscore(anl14_eps_up_cnt, subindustry), subindustry), 0)",
    "settings": {
      "region": "USA",
      "delay": 1,
      "decay": 5,
      "neutralization": "SUBINDUSTRY",
      "universe": "TOP3000",
      "truncation": 0.08
    }
  },
  {
    "id": 17,
    "family": "ThemePool_USA_D1",
    "dataset": "analyst10",
    "competition": "USA_D1_FastDatasets_PowerPool_June2026",
    "hypothesis": "Cross-dataset combo: stocks with high analyst coverage counts (analyst10) paired with strong recommendation upgrade signals (analyst15) exhibit the highest institutional conviction, generating superior risk-adjusted returns.",
    "anomaly_basis": "Cross-dataset attention × recommendation combo / conviction amplification",
    "formula": "trade_when(volume > adv20 * 0.72, group_neutralize(rank(anl10_cnt_up) * group_zscore(anl15_rec_up_cnt, subindustry), subindustry), 0)",
    "settings": {
      "region": "USA",
      "delay": 1,
      "decay": 5,
      "neutralization": "SUBINDUSTRY",
      "universe": "TOP3000",
      "truncation": 0.08
    }
  },
  {
    "id": 18,
    "family": "ThemePool_USA_D1",
    "dataset": "analyst14",
    "competition": "USA_D1_FastDatasets_PowerPool_June2026",
    "hypothesis": "Cross-dataset combo: the product of EPS upgrade breadth (analyst14) and analyst coverage momentum (analyst10) captures stocks where both the quantity and quality of analyst attention are simultaneously improving, the highest-alpha intersection in the USA universe.",
    "anomaly_basis": "Cross-dataset EPS breadth × coverage momentum / compound analyst signal",
    "formula": "trade_when(volume > adv20 * 0.68, group_neutralize(group_zscore(anl14_eps_up_cnt, subindustry) * rank(anl10_cnt_up), subindustry), 0)",
    "settings": {
      "region": "USA",
      "delay": 1,
      "decay": 8,
      "neutralization": "SUBINDUSTRY",
      "universe": "TOP3000",
      "truncation": 0.08
    }
  },
  {
    "id": 19,
    "family": "ThemePool_USA_D1",
    "dataset": "analyst15",
    "competition": "USA_D1_FastDatasets_PowerPool_June2026",
    "hypothesis": "Stocks experiencing analyst recommendation upgrades while simultaneously seeing coverage count expansion are undergoing a compounding institutional re-rating; the combined signal from analyst15 and analyst10 produces the highest Sharpe cross-dataset combo.",
    "anomaly_basis": "Cross-dataset recommendation upgrade × coverage expansion / re-rating signal",
    "formula": "trade_when(volume > adv20 * 0.75, group_neutralize(group_zscore(anl15_rec_up_cnt, subindustry) * rank(anl10_cnt_up), subindustry), 0)",
    "settings": {
      "region": "USA",
      "delay": 1,
      "decay": 8,
      "neutralization": "SUBINDUSTRY",
      "universe": "TOP3000",
      "truncation": 0.08
    }
  },
  {
    "id": 20,
    "family": "ThemePool_USA_D1",
    "dataset": "analyst14",
    "competition": "USA_D1_FastDatasets_PowerPool_June2026",
    "hypothesis": "Stocks with consistent revenue AND EPS estimate upgrades (dual revision alignment) relative to subindustry peers show the highest fundamental conviction signal, as simultaneous top-line and bottom-line improvement is rarely priced in immediately by the market.",
    "anomaly_basis": "Dual-revision alignment / fundamental re-rating with margin expansion",
    "formula": "trade_when(volume > adv20 * 0.73, group_neutralize(rank(anl14_eps_up_cnt * anl14_rev_up_cnt), subindustry), 0)",
    "settings": {
      "region": "USA",
      "delay": 1,
      "decay": 8,
      "neutralization": "SUBINDUSTRY",
      "universe": "TOP3000",
      "truncation": 0.08
    }
  }
]

# Local syntax check before sending
valid_count = 0
for a in alphas_data:
    ok, err = validate_fastexpr(a["formula"])
    if not ok:
        print(f"Validation failed for formula {a['id']}: {err}")
    else:
        valid_count += 1

print(f"Validation summary: {valid_count} / {len(alphas_data)} validated successfully.")

if valid_count == len(alphas_data):
    print("All formulas passed local syntax validation. Posting payload to Sai's Review Box...")
    
    # Strip the local internal 'id' before posting to API
    payload = []
    for a in alphas_data:
        copied = dict(a)
        if "id" in copied:
            del copied["id"]
        payload.append(copied)
        
    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API_URL, method="POST", data=req_data)
    req.add_header("Authorization", f"Bearer {API_AUTH_TOKEN}")
    req.add_header("Content-Type", "application/json")
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=45) as response:
            res_body = response.read().decode("utf-8")
            status_code = response.status
            print(f"PUSH SUCCESSFUL! HTTP Status: {status_code}")
            print(f"Response: {res_body}")
    except Exception as e:
        print(f"PUSH FAILED - Error: {e}")
else:
    print("Aborting push due to local validation failures.")
