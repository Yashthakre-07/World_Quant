import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    try:
        with open("scratch/generated_alphas.json", "r", encoding="utf-8") as f:
            alphas = json.load(f)
    except Exception as e:
        print(f"Error loading generated_alphas.json: {e}")
        return

    print("==========================================")
    print("NEWLY GENERATED ALPHAS FOR SLOTS 1-8")
    print("==========================================\n")

    # We generated 40 alphas. Let's group them by slot.
    # Group A: slots 1-4 (first 20, 5 per slot)
    # Group B: slots 5-8 (remaining 20, 5 per slot)
    
    print("--- GROUP A (Slots 1-4) ---")
    for slot_idx in range(4):
        slot_num = slot_idx + 1
        print(f"\n[SLOT {slot_num}]")
        slot_alphas = alphas[slot_idx * 5 : (slot_idx + 1) * 5]
        for i, a in enumerate(slot_alphas, 1):
            print(f"  {i}. Family: {a['family']}")
            print(f"     Formula: {a['formula']}")

    print("\n\n--- GROUP B (Slots 5-8) ---")
    for slot_idx in range(4):
        slot_num = slot_idx + 5
        print(f"\n[SLOT {slot_num}]")
        slot_alphas = alphas[20 + slot_idx * 5 : 20 + (slot_idx + 1) * 5]
        for i, a in enumerate(slot_alphas, 1):
            print(f"  {i}. Family: {a['family']}")
            print(f"     Formula: {a['formula']}")

if __name__ == "__main__":
    main()
