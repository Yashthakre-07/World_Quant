import urllib.request
import json
import ssl

def main():
    server_url = "https://world-quant.onrender.com/api/queue-alpha"
    inject_url = "https://world-quant.onrender.com/api/inject-inbox"
    token = "yashthakreop"
    
    alphas = []
    
    # Family 1: Range-Normalized Intraday Spread Reversion (12 alphas)
    # Formula: group_neutralize(trade_when(volume > adv20 * gate, -rank(ts_decay_linear((close - open) / (high - low + 0.001), decay)), 0), subindustry)
    gates_f1 = [0.55, 0.60, 0.65, 0.70, 0.75, 0.80]
    decays_f1 = [3, 4]
    for gate in gates_f1:
        for decay in decays_f1:
            alphas.append({
                "formula": f"group_neutralize(trade_when(volume > adv20 * {gate}, -rank(ts_decay_linear((close - open) / (high - low + 0.001), {decay})), 0), subindustry)",
                "family": f"Range-Normalized Intraday Spread Reversion (Gate {gate}, Decay {decay})",
                "hypothesis": f"Intraday session close-open spread normalized by the high-low session volatility range under peer-group hedge and liquidity gate {gate}.",
                "settings": {"decay": decay, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
            })
            
    # Family 2: Overnight Gap Reversion (12 alphas)
    # Formula: group_neutralize(trade_when(volume > adv20 * gate, -rank(ts_decay_linear((open - ts_delay(close, 1)) / (high - low + 0.001), decay)), 0), subindustry)
    gates_f2 = [0.55, 0.60, 0.65, 0.70, 0.75, 0.80]
    decays_f2 = [3, 4]
    for gate in gates_f2:
        for decay in decays_f2:
            alphas.append({
                "formula": f"group_neutralize(trade_when(volume > adv20 * {gate}, -rank(ts_decay_linear((open - ts_delay(close, 1)) / (high - low + 0.001), {decay})), 0), subindustry)",
                "family": f"Overnight Gap Reversion (Gate {gate}, Decay {decay})",
                "hypothesis": f"Overnight pricing gaps normalized by high-low session volatility range revert post-open under subindustry peer neutralization.",
                "settings": {"decay": decay, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
            })
            
    # Family 3: Volume-Weighted Intraday Spread Reversion (13 alphas)
    # Formula: group_neutralize(trade_when(volume > adv20 * gate, -rank(ts_decay_linear((close - open) * (volume / adv20), decay)), 0), subindustry)
    gates_f3 = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85]
    decays_f3 = [3, 4]
    for idx, gate in enumerate(gates_f3):
        # We need 13, so let's match decays to reach 13
        decays = [3, 4] if idx < 5 else [3]
        for decay in decays:
            alphas.append({
                "formula": f"group_neutralize(trade_when(volume > adv20 * {gate}, -rank(ts_decay_linear((close - open) * (volume / adv20), {decay})), 0), subindustry)",
                "family": f"Volume-Weighted Intraday Spread Reversion (Gate {gate}, Decay {decay})",
                "hypothesis": f"Session returns scaled by relative volume to capture liquidity-amplified order-flow mean reversion.",
                "settings": {"decay": decay, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
            })
            
    # Family 4: Intraday Shadow-Range Position Reversal (13 alphas)
    # Formula: group_neutralize(trade_when(volume > adv20 * gate, -rank(ts_decay_linear((close - ((open + close) / 2)) / (high - low + 0.001), decay)), 0), subindustry)
    gates_f4 = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85]
    for idx, gate in enumerate(gates_f4):
        # We need 13, so let's match decays to reach 13
        decays = [3, 4] if idx < 5 else [3]
        for decay in decays:
            alphas.append({
                "formula": f"group_neutralize(trade_when(volume > adv20 * {gate}, -rank(ts_decay_linear((close - ((open + close) / 2)) / (high - low + 0.001), {decay})), 0), subindustry)",
                "family": f"Intraday Shadow-Range Position Reversal (Gate {gate}, Decay {decay})",
                "hypothesis": f"Closing session displacement relative to session midpoint normalized by session volatility range.",
                "settings": {"decay": decay, "neutralization": "SUBINDUSTRY", "universe": "TOP3000", "truncation": 0.08}
            })
            
    print(f"Generated {len(alphas)} high-conviction academic-grade alphas.")
    
    # Disable SSL issues
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    # 1. POST to queue-alpha
    print(f"Injecting {len(alphas)} alphas into live inbox...")
    req_queue = urllib.request.Request(server_url, method="POST", data=json.dumps(alphas).encode("utf-8"))
    req_queue.add_header("Authorization", f"Bearer {token}")
    req_queue.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req_queue, context=ctx, timeout=45) as response:
            res_body = response.read().decode("utf-8")
            res_data = json.loads(res_body)
            print(f"Inbox Injection Successful! Added: {res_data.get('added')}, Skipped: {res_data.get('skipped')}")
    except Exception as e:
        print(f"FAILED inbox injection: {e}")
        return
        
    # 2. POST to inject-inbox
    print("Moving all inbox alphas to active scheduler...")
    req_inject = urllib.request.Request(inject_url, method="POST", data=json.dumps({"all": True}).encode("utf-8"))
    req_inject.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req_inject, context=ctx, timeout=30) as response:
            res_body = response.read().decode("utf-8")
            res_data = json.loads(res_body)
            print(f"Active Queue Injection Successful! Injected count: {res_data.get('injected_count')}")
    except Exception as e:
        print(f"FAILED active queue injection: {e}")

if __name__ == "__main__":
    main()
