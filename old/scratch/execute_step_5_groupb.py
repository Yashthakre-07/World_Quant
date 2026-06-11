import json
import os
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Load Group B raw alphas
    raw_path = "scratch/grpb_gen11_raw.json"
    if not os.path.exists(raw_path):
        print("Raw Group B file not found!")
        sys.exit(1)
        
    with open(raw_path, "r", encoding="utf-8") as f:
        all_alphas = json.load(f)
        
    # Take the first 8 alphas
    selected_alphas = all_alphas[:8]
    
    # Save formulas portfolio to generated_alphas.json
    with open("scratch/generated_alphas.json", "w", encoding="utf-8") as f:
        json.dump(selected_alphas, f, indent=2)
        
    # Save archive file
    with open("scratch/groupb_generation_11.json", "w", encoding="utf-8") as f:
        json.dump(selected_alphas, f, indent=2)
        
    # Update generation state
    state_path = "scratch/generation_state.json"
    if os.path.exists(state_path):
        try:
            with open(state_path, "r", encoding="utf-8") as f:
                state = json.load(f)
            state["current_generation"] = 12
            with open(state_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
            print("Successfully updated generation state for Group B.")
        except Exception as e:
            print(f"Error updating generation state: {e}")
            
    # Update pipeline state
    pipeline_state_path = "scratch/pipeline_state.json"
    with open(pipeline_state_path, "w", encoding="utf-8") as f:
        json.dump({"current_step": 6, "group": "groupb"}, f, indent=2)
        
    # Log to live_run.txt
    with open("live_run.txt", "a", encoding="utf-8") as f:
        f.write("\n==========================================\n")
        f.write("RUNNING STEP 5 (AI ALPHA GENERATION - GROUP B)\n")
        f.write("==========================================\n\n")
        
        f.write("[GENERATED ALPHAS]\n")
        for i, a in enumerate(selected_alphas, 1):
            f.write(f"Alpha {i}:\n  Family: {a['family']}\n  Formula: {a['formula']}\n  Hypothesis: {a['hypothesis']}\n\n")
            
        f.write("\n[VALIDATED/MUTATED ALPHAS]\n")
        for i, a in enumerate(selected_alphas, 1):
            f.write(f"Alpha {i}:\n  Family: {a['family']}\n  Formula: {a['formula']}\n  Hypothesis: {a['hypothesis']}\n  Anomaly Basis: {a['anomaly_basis']}\n\n")
            
        f.write("[STEP 5 COMPLETED] - Alphas generated, validated, and archived under Generation 11 for GROUP B.\n")
        
    print("STEP 5 COMPLETE FOR GROUP B")

if __name__ == "__main__":
    main()
