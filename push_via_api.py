import requests
import json
import sys

# Define our ultra-optimized alpha formula
alpha = {
    "family": "Volatility-Normalized Overnight Gap Reversion (Ultra)",
    "hypothesis": "Overnight price gaps normalized by dynamic 10-day return volatility represent pure dislocation signals. By applying a 75% liquidity gate and a smooth 6-day decay, we minimize turnover and maximize risk-adjusted payout.",
    "formula": "group_neutralize(trade_when(volume > adv20 * 0.75, -rank(ts_decay_linear((open - ts_delay(close, 1)) / (ts_std_dev(returns, 10) + 0.0001), 6)), 0), subindustry)",
    "settings": { 
        "decay": 6, 
        "neutralization": "SUBINDUSTRY", 
        "universe": "TOP3000", 
        "truncation": 0.08 
    }
}

# Bearer token configured as API_SECRET_TOKEN in environment variables
TOKEN = "yashthakreop"

# Default API endpoints (local and Render)
urls = [
    "http://127.0.0.1:8000/api/queue-alpha",
    "https://worldquant-pipeline.onrender.com/api/queue-alpha"
]

# If a custom URL is passed as a command-line argument, use that instead
if len(sys.argv) > 1:
    urls = [sys.argv[1]]

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

print("🚀 Attempting to push new elite alpha directly to the live queue...")
for url in urls:
    try:
        print(f"Connecting to: {url} ...")
        response = requests.post(url, json=[alpha], headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"✅ SUCCESS! Alpha successfully queued on server.")
            print(f"Server Response: {response.json()}\n")
        else:
            print(f"❌ FAILED! Server returned status code {response.status_code}")
            print(f"Server Response: {response.text}\n")
    except Exception as e:
        print(f"⚠️ Could not connect to {url}: {e}\n")
