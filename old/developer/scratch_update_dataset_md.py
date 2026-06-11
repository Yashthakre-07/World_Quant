import json
from pathlib import Path

# Paths
workspace_dir = Path("c:/Users/Admin/Documents/VIBE_YT/wq")
raw_datasets_path = workspace_dir / "documentation/dataset/raw_datasets.json"
dataset_md_path = workspace_dir / "dataset.md"

def main():
    # 1. Read raw_datasets.json
    with open(raw_datasets_path, "r", encoding="utf-8") as f:
        datasets = json.load(f)
    
    # 2. Extract unique datasets by ID
    unique_datasets = {}
    for ds in datasets:
        ds_id = ds["id"]
        cat_name = ds.get("category", {}).get("name", "Uncategorized")
        subcat_name = ds.get("subcategory", {}).get("name", "N/A")
        region = ds.get("region", "N/A")
        delay = str(ds.get("delay", "N/A"))
        
        if ds_id not in unique_datasets:
            unique_datasets[ds_id] = {
                "id": ds_id,
                "name": ds["name"],
                "category": cat_name,
                "subcategory": subcat_name,
                "description": ds.get("description", "").strip(),
                "regions": {region},
                "delays": {delay}
            }
        else:
            unique_datasets[ds_id]["regions"].add(region)
            unique_datasets[ds_id]["delays"].add(delay)

    # Convert sets to sorted lists/strings
    for ds_id, ds in unique_datasets.items():
        ds["regions"] = ", ".join(sorted(list(ds["regions"])))
        ds["delays"] = ", ".join(sorted(list(ds["delays"])))

    # Sort datasets by category, then by name
    sorted_ds = sorted(unique_datasets.values(), key=lambda x: (x["category"], x["name"]))

    # 3. Read current dataset.md up to section 4
    with open(dataset_md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Find where Section 4 ends or locate where to append
    # Let's rebuild the file by keeping everything currently in dataset.md
    # and appending the new Section 5.
    existing_content = "".join(lines)
    
    # Check if Section 5 already exists to avoid duplicate appending
    if "## 5. Complete Catalog of All Available Datasets" in existing_content:
        # Truncate at Section 5
        idx = existing_content.find("## 5. Complete Catalog of All Available Datasets")
        existing_content = existing_content[:idx].strip() + "\n\n"
    else:
        existing_content = existing_content.strip() + "\n\n"

    # 4. Generate Section 5 Markdown
    md = []
    md.append("## 5. Complete Catalog of All Available Datasets\n\n")
    md.append("Below is the complete list of all unique datasets available on the WorldQuant BRAIN platform, compiled from the platform's metadata:\n\n")
    
    # We can group by category for better readability
    from collections import defaultdict
    by_cat = defaultdict(list)
    for ds in sorted_ds:
        by_cat[ds["category"]].append(ds)

    for cat, ds_list in sorted(by_cat.items()):
        md.append(f"### 📁 {cat} Datasets\n\n")
        md.append("| Dataset ID | Dataset Name | Subcategory | Delays | Regions | Description |\n")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for ds in ds_list:
            # Clean description for table format (remove newlines, escape pipes)
            desc = ds["description"].replace("\n", " ").replace("|", "\\|")
            if len(desc) > 200:
                desc = desc[:197] + "..."
            md.append(f"| `{ds['id']}` | {ds['name']} | {ds['subcategory']} | {ds['delays']} | {ds['regions']} | {desc} |\n")
        md.append("\n")

    full_md = existing_content + "".join(md)

    # 5. Write back to dataset.md
    with open(dataset_md_path, "w", encoding="utf-8") as f:
        f.write(full_md)
    print("dataset.md updated successfully with all datasets!")

if __name__ == "__main__":
    main()
