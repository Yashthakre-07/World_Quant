# -*- coding: utf-8 -*-
"""
desktop_control.py
--------------------
Elite Desktop Quant Dev Panel for AlphaForge.
Establishes a secure remote control bridge to the Render cloud servers 
using the Bearer Token API keys.
"""

import os
import sys
import json
import requests
import time
from datetime import datetime

# Remote server configurations
DEFAULT_URL = "https://world-quant.onrender.com"
API_TOKEN = "yashthakreop"

class QuantControlPanel:
    def __init__(self):
        self.server_url = DEFAULT_URL
        self.headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        
    def query_server(self, endpoint, method="GET", json_data=None):
        url = f"{self.server_url}{endpoint}"
        try:
            if method == "GET":
                r = requests.get(url, headers=self.headers, timeout=20)
            elif method == "POST":
                r = requests.post(url, headers=self.headers, json=json_data, timeout=20)
            else:
                return {"error": "Unsupported HTTP method"}
                
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 401:
                return {"error": "HTTP 401: Unauthorized. Please check your Bearer Token."}
            else:
                return {"error": f"HTTP {r.status_code}: {r.text}"}
        except Exception as e:
            return {"error": f"Connection error: {e}"}

    def show_status(self):
        """Displays real-time telemetry from the cloud backend."""
        print("\n=== Fetching Cloud Telemetry ===")
        status = self.query_server("/api/queue-status")
        stats = self.query_server("/api/stats")
        
        if "error" in status or "error" in stats:
            print(f"[ERROR] Failed to query server. Details:")
            print(f"  Queue: {status.get('error', 'OK')}")
            print(f"  Stats: {stats.get('error', 'OK')}")
            return

        print("\n" + "=" * 50)
        print(f"🔋 PIPELINE STATUS: {status.get('pipeline_status', 'UNKNOWN')}")
        print(f"📁 Queue On Disk: {status.get('queue_on_disk', 0)} alphas")
        print(f"⚙️ Queue In Memory: {status.get('in_memory', 0)} active simulations")
        print("=" * 50)
        
        print(f"📊 Total Simulations Run: {stats.get('total_runs', 0)}")
        print(f"✅ Total Accepted Alphas: {stats.get('total_submissions', 0)}")
        print(f"🏆 Best Sharpe Simulated: {stats.get('best_sharpe', 0.0):.4f}")
        print(f"🔥 Best Fitness Score:    {stats.get('best_fitness', 0.0):.4f}")
        print("=" * 50)
        
        # Display preview of queue
        formulas = status.get("formulas", [])
        if formulas:
            print("\n🔍 Next Queue Items Preview:")
            for idx, f in enumerate(formulas[:5], 1):
                print(f"  [{idx:02d}] {f[:75]}...")
        else:
            print("\nℹ️ Queue is currently empty.")

    def trigger_generation(self):
        """Remotely triggers AI generation sequence on the server."""
        print("\n=== Trigger AI Quant Generation ===")
        dataset = input("Enter target dataset (e.g. analyst4, analyst14, analyst45) [analyst4]: ").strip() or "analyst4"
        count = input("Enter number of alphas to generate [20]: ").strip() or "20"
        
        try:
            count = int(count)
        except ValueError:
            print("[ERROR] Count must be an integer.")
            return

        payload = {"dataset": dataset, "count": count}
        print(f"[*] Dispatching generation request to cloud server for {dataset}...")
        res = self.query_server("/api/trigger-flow", "POST", payload)
        
        if "error" in res:
            print(f"[ERROR] {res['error']}")
        else:
            print(f"\n[SUCCESS] Server response: {res.get('message')}")
            print("[*] Polling generation progress...")
            
            # Poll status
            for _ in range(15):
                time.sleep(2)
                prog = self.query_server("/api/trigger-status")
                if "error" in prog:
                    break
                print(f"  -> State: {prog.get('current_step')} | Generated: {prog.get('generated_count')}/{count} ({prog.get('progress_percent')}%)")
                if prog.get("status") in ("SUCCESS", "ERROR"):
                    break

    def trigger_reauth(self):
        """Remotely requests WorldQuant session re-authentication."""
        print("\n=== Request WorldQuant Session Re-authentication ===")
        res = self.query_server("/api/reauthenticate", "POST")
        
        if "error" in res:
            print(f"[ERROR] {res['error']}")
            return

        status = res.get("status", "IDLE")
        if status == "SUCCESS":
            print("\n[SUCCESS] Cloud server authenticated instantly using saved session cookies!")
        elif status == "POLLING":
            print("\n🔐 BIOMETRIC CHALLENGE ISSUED")
            print(f"WorldQuant requires biometric ID check. Open this URL in your web browser:")
            print(f"\n  >>> {res.get('url')} <<<\n")
            print("[*] Server is currently polling for confirmation. Please complete on your phone or PC.")
        else:
            print(f"Unhandled re-auth response: {res}")

    def clean_rejects(self):
        """Remotely wipes failed and rejected formulas from the queue."""
        print("\n=== Remote Queue Clean & Purge Rejects ===")
        res = self.query_server("/api/clean-queue", "POST", {})
        if "error" in res:
            print(f"[ERROR] {res['error']}")
        else:
            print(f"\n[SUCCESS] Removed {res.get('removed_count', 0)} failed/rejected alphas from the dynamic queue.")
            print(f"Remaining queue items: {res.get('remaining_queue_count', 0)}")

    def overwrite_portfolio(self):
        """Loads a local JSON portfolio and overwrites the remote queue."""
        print("\n=== Overwrite Cloud Queue with Local Portfolio ===")
        filepath = input("Enter path to local json portfolio [alphas_portfolio_20.json]: ").strip() or "alphas_portfolio_20.json"
        
        if not os.path.exists(filepath):
            print(f"[ERROR] File not found: {filepath}")
            return
            
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            print(f"[*] Loaded {len(data)} alphas from {filepath}. Uploading...")
            res = self.query_server("/api/overwrite-queue", "POST", data)
            if "error" in res:
                print(f"[ERROR] {res['error']}")
            else:
                print(f"\n[SUCCESS] Cloud queue successfully overwritten with exactly {res.get('overwritten_count', 0)} alphas.")
        except Exception as e:
            print(f"[ERROR] Failed to read or upload file: {e}")

    def control_pipeline(self, action):
        """Remotely pauses or resumes the backend simulation engine."""
        print(f"\n=== Turning pipeline state to {action.upper()} ===")
        endpoint = "/api/start-pipeline" if action == "start" else "/api/stop-pipeline"
        res = self.query_server(endpoint, "POST")
        if "error" in res:
            print(f"[ERROR] {res['error']}")
        else:
            print(f"\n[SUCCESS] Server response: {res.get('message')}")

    def run_menu(self):
        while True:
            print("\n" + "=" * 50)
            print("       💎 ALPHAFORGE DESKTOP QUANT dev panel 💎")
            print("=" * 50)
            print("  [1] Check Cloud Status & Telemetry")
            print("  [2] Trigger AI Alpha Generation Sequence")
            print("  [3] Dynamic Biometric Session Re-Auth")
            print("  [4] Clean Cloud Queue (Purge Failed/Rejects)")
            print("  [5] Overwrite Cloud Queue (Upload Local JSON)")
            print("  [6] Pause Pipeline Execution")
            print("  [7] Resume Pipeline Execution")
            print("  [0] Exit")
            print("=" * 50)
            
            choice = input("Enter choice: ").strip()
            if choice == "1":
                self.show_status()
            elif choice == "2":
                self.trigger_generation()
            elif choice == "3":
                self.trigger_reauth()
            elif choice == "4":
                self.clean_rejects()
            elif choice == "5":
                self.overwrite_portfolio()
            elif choice == "6":
                self.control_pipeline("stop")
            elif choice == "7":
                self.control_pipeline("start")
            elif choice == "0":
                print("\nExiting Quant Dev Panel. Good hunting.")
                break
            else:
                print("\n[ERROR] Invalid choice. Try again.")
            
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    panel = QuantControlPanel()
    panel.run_menu()
