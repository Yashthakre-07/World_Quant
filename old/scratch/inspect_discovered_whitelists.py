import json

def main():
    with open("scratch/discovered_whitelists.json", "r") as f:
        data = json.load(f)
    
    print(f"Total keys in JSON: {len(data.keys())}")
    for k, v in data.items():
        # v is a list of fields or dict? Let's check type
        print(f"Key: {k}, type of val: {type(v)}, length: {len(v) if hasattr(v, '__len__') else 'N/A'}")
        if isinstance(v, dict):
            for subk, subv in list(v.items())[:3]:
                print(f"  sub-key: {subk}, type of val: {type(subv)}, length: {len(subv) if hasattr(subv, '__len__') else 'N/A'}")
        elif isinstance(v, list):
            print(f"  sample elements: {v[:5]}")

if __name__ == "__main__":
    main()
