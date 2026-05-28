import json
from pathlib import Path

# Paths
workspace_dir = Path("c:/Users/Admin/Documents/VIBE_YT/wq")
raw_datasets_path = workspace_dir / "documentation/dataset/all_raw_datasets_unfiltered.json"
dataset_md_path = workspace_dir / "dataset.md"

def main():
    # 1. Read all_raw_datasets_unfiltered.json
    with open(raw_datasets_path, "r", encoding="utf-8") as f:
        datasets = json.load(f)
    
    # 2. Build hierarchical tree: Category -> Subcategory -> unique Dataset ID -> Dataset Name
    tree = {}
    for ds in datasets:
        cat_name = ds.get("category", {}).get("name", "Uncategorized").strip()
        subcat_name = ds.get("subcategory", {}).get("name", "N/A").strip()
        ds_id = ds["id"].strip()
        ds_name = ds["name"].strip()
        
        if cat_name not in tree:
            tree[cat_name] = {}
        if subcat_name not in tree[cat_name]:
            tree[cat_name][subcat_name] = {}
        
        tree[cat_name][subcat_name][ds_id] = ds_name

    # 3. Generate simplified markdown content
    md = []
    md.append("# WorldQuant BRAIN Dataset Catalog\n\n")
    md.append("Below is the hierarchical list of all unique dataset categories, subcategories, IDs, and names available on WorldQuant BRAIN:\n\n")
    
    for cat in sorted(tree.keys()):
        cat_ds_count = sum(len(tree[cat][sc]) for sc in tree[cat])
        md.append(f"- **📁 {cat}** ({cat_ds_count} datasets)\n")
        subcats = tree[cat]
        for subcat in sorted(subcats.keys()):
            md.append(f"  - *📂 {subcat}*\n")
            datasets_in_sub = subcats[subcat]
            for ds_id in sorted(datasets_in_sub.keys()):
                ds_name = datasets_in_sub[ds_id]
                md.append(f"    - `{ds_id}`: {ds_name}\n")
        md.append("\n")

    # 4. Write to dataset.md
    with open(dataset_md_path, "w", encoding="utf-8") as f:
        f.write("".join(md))
        
    print("dataset.md successfully simplified to names and IDs only!")

if __name__ == "__main__":
    main()
