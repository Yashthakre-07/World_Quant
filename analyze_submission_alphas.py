# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import pandas as pd

# Root directory setup
WQ_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WQ_ROOT)

import ace_lib
from helpful_functions import prettify_result

def load_simulated_alphas(results_file):
    """
    Loads simulated alpha IDs from the submission_results.json file.
    """
    if not os.path.exists(results_file):
        print(f"[-] Results file not found at: {results_file}")
        return []
    
    try:
        with open(results_file, "r") as f:
            data = json.load(f)
        
        alphas = []
        for item in data:
            if item.get("alpha_id") and item.get("status") == "success":
                alphas.append({
                    "alpha_id": item["alpha_id"],
                    "formula": item["formula"],
                    "settings": item.get("settings", {})
                })
        return alphas
    except Exception as e:
        print(f"[-] Error loading results file: {e}")
        return []

def main():
    print("=" * 70)
    print("      🚀 WORLDQUANT BRAIN - ACE SUBMISSION ANALYZER 🚀")
    print("=" * 70)
    
    # 1. Load results
    results_path = os.path.join(WQ_ROOT, "alphas", "analyst", "analyst10", "submission_results.json")
    simulated_alphas = load_simulated_alphas(results_path)
    
    if not simulated_alphas:
        print("\n[!] No active simulated alpha IDs found in 'submission_results.json'.")
        print("    Please provide a list of Alpha IDs to analyze manually:")
        manual_ids = input("    Enter Alpha IDs (comma-separated, e.g. a1b2c3d4, x9y8z7w6): ").strip()
        if not manual_ids:
            print("[-] No Alpha IDs provided. Exiting analysis.")
            sys.exit(0)
        
        simulated_alphas = [{"alpha_id": aid.strip(), "formula": "Manual Analysis", "settings": {}} for aid in manual_ids.split(",") if aid.strip()]
    
    print(f"\n[*] Identified {len(simulated_alphas)} Alpha IDs for advanced telemetry checking.")
    
    # 2. Establish WQ Session
    print("\n[*] Establishing WorldQuant Brain secure session...")
    try:
        session = ace_lib.start_session()
        print("[SUCCESS] Session established successfully.")
    except Exception as e:
        print(f"[-] Authentication failed: {e}")
        sys.exit(1)
        
    analysis_records = []
    
    # 3. Analyze each alpha
    print("\n" + "-" * 70)
    print(f"{'Alpha ID':<12} | {'Sharpe':<6} | {'Turnover':<8} | {'Fitness':<7} | {'Prod Corr':<9} | {'Self Corr':<9} | {'Result':<10}")
    print("-" * 70)
    
    for item in simulated_alphas:
        alpha_id = item["alpha_id"]
        formula = item["formula"]
        
        try:
            # A. Fetch general stats from WQ Brain
            stats_json = ace_lib.get_simulation_result_json(session, alpha_id)
            if not stats_json or "is" not in stats_json:
                print(f"{alpha_id:<12} | {'-':<6} | {'-':<8} | {'-':<7} | {'-':<9} | {'-':<9} | {'NOT_FOUND':<10}")
                continue
            
            is_data = stats_json["is"]
            sharpe = is_data.get("sharpe", 0.0)
            turnover = is_data.get("turnover", 0.0)
            fitness = is_data.get("fitness", 0.0)
            
            # Convert values
            sharpe_str = f"{sharpe:.2f}" if sharpe is not None else "N/A"
            turnover_str = f"{turnover * 100:.1f}%" if turnover is not None else "N/A"
            fitness_str = f"{fitness:.2f}" if fitness is not None else "N/A"
            
            # B. Check Production Correlation
            prod_df = ace_lib.check_prod_corr_test(session, alpha_id, threshold=0.70)
            prod_pass = "PASS"
            prod_val = 0.0
            if not prod_df.empty:
                prod_pass = prod_df.iloc[0]["result"]
                prod_val = prod_df.iloc[0]["value"]
            prod_val_str = f"{prod_val:.2f}" if prod_val is not None else "0.00"
            prod_status = f"{prod_val_str} ({prod_pass})"
            
            # C. Check Self Correlation
            self_df = ace_lib.check_self_corr_test(session, alpha_id, threshold=0.70)
            self_pass = "PASS"
            self_val = 0.0
            if not self_df.empty:
                self_pass = self_df.iloc[0]["result"]
                self_val = self_df.iloc[0]["value"]
            self_val_str = f"{self_val:.2f}" if self_val is not None else "0.00"
            self_status = f"{self_val_str} ({self_pass})"
            
            # D. Get strict submission criteria check
            checks_df = ace_lib.get_check_submission(session, alpha_id)
            all_checks_passed = True
            failed_reasons = []
            
            if not checks_df.empty:
                for _, row in checks_df.iterrows():
                    if row["result"] == "FAIL":
                        all_checks_passed = False
                        failed_reasons.append(row["name"])
            
            final_status = "ELIGIBLE" if (all_checks_passed and prod_pass == "PASS" and self_pass == "PASS") else "REJECTED"
            
            print(f"{alpha_id:<12} | {sharpe_str:<6} | {turnover_str:<8} | {fitness_str:<7} | {prod_val_str:<9} | {self_val_str:<9} | {final_status:<10}")
            if failed_reasons:
                print(f"   ⚠️  Failed Platform Checks: {', '.join(failed_reasons)}")
            if prod_pass == "FAIL":
                print(f"   ⚠️  Failed Production Correlation Check (Duplicate Alpha detected in WQ DB)")
            if self_pass == "FAIL":
                print(f"   ⚠️  Failed Self Correlation Check (Overlapping with your existing alphas)")
                
            analysis_records.append({
                "alpha_id": alpha_id,
                "formula": formula,
                "sharpe": sharpe,
                "turnover": turnover,
                "fitness": fitness,
                "prod_correlation": prod_val,
                "self_correlation": self_val,
                "platform_checks_passed": all_checks_passed,
                "failed_checks": failed_reasons,
                "final_status": final_status
            })
            
            time.sleep(1.0) # Graceful spacing
            
        except Exception as e:
            print(f"{alpha_id:<12} | Error fetching metrics: {e}")
            
    print("-" * 70)
    
    # 4. Save analysis report
    report_file = os.path.join(WQ_ROOT, "alphas", "analyst", "analyst10", "submission_analysis_report.json")
    try:
        with open(report_file, "w") as f:
            json.dump(analysis_records, f, indent=2)
        print(f"\n[SUCCESS] Completed advanced telemetry analysis.")
        print(f"[*] Detailed report saved to: {report_file}")
    except Exception as e:
        print(f"[-] Could not save report: {e}")
        
    # Summary stats
    eligible_count = sum(1 for r in analysis_records if r["final_status"] == "ELIGIBLE")
    print(f"\n📈 SUMMARY STATS:")
    print(f"   ✅ Total Eligible for Submission: {eligible_count} / {len(analysis_records)}")
    print(f"   ❌ Rejected (due to low metrics or duplicates): {len(analysis_records) - eligible_count}")
    print("=" * 70)

if __name__ == "__main__":
    main()
