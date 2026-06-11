import json

def main():
    with open("scratch/discovered_whitelists.json", "r") as f:
        data = json.load(f)
    
    target_datasets = ['analyst4', 'analyst14', 'analyst16', 'analyst7', 'model26', 'model135', 'news12', 'news5', 'news21']
    
    for ds in target_datasets:
        if ds in data:
            info = data[ds]
            print(f"=== Dataset: {ds} ===")
            print(f"Vectors ({len(info['vectors'])}): {info['vectors'][:15]}")
            print(f"Matrices ({len(info['matrices'])}): {info['matrices'][:15]}")
            print()
        else:
            print(f"=== Dataset: {ds} (Not found in discovered_whitelists.json) ===\n")

if __name__ == "__main__":
    main()
