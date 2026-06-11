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
        
        # Store unique dataset IDs under each subcategory
        tree[cat_name][subcat_name][ds_id] = ds_name

    # 3. Generate the markdown representing the hierarchy
    md_lines = []
    md_lines.append("\n## 1.1 Hierarchical Map of Categories, Subcategories, and Datasets\n\n")
    md_lines.append("Here is the outline of how the datasets are organized on the WorldQuant BRAIN platform:\n\n")
    
    for cat in sorted(tree.keys()):
        md_lines.append(f"- **📁 {cat}**\n")
        subcats = tree[cat]
        for subcat in sorted(subcats.keys()):
            md_lines.append(f"  - *📂 {subcat}*\n")
            datasets_in_sub = subcats[subcat]
            for ds_id in sorted(datasets_in_sub.keys()):
                ds_name = datasets_in_sub[ds_id]
                md_lines.append(f"    - `{ds_id}`: {ds_name}\n")
    md_lines.append("\n")
    
    hierarchy_md = "".join(md_lines)

    # 4. Read current dataset.md
    with open(dataset_md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # If the section already exists, let's remove it to avoid duplicates
    if "## 1.1 Hierarchical Map of Categories, Subcategories, and Datasets" in content:
        # Find start and end of it
        start_idx = content.find("## 1.1 Hierarchical Map of Categories, Subcategories, and Datasets")
        # Let's find the next section boundary "---" or "## " after start_idx
        end_idx = content.find("---", start_idx)
        if end_idx != -1:
            content = content[:start_idx] + content[end_idx:]
        else:
            # If "---" not found, just truncate/remove up to next major section
            next_sec = content.find("## ", start_idx + 10)
            if next_sec != -1:
                content = content[:start_idx] + content[next_sec:]
            else:
                content = content[:start_idx]

    # 5. Find the right place to insert.
    # We want to insert it right before the first "---" that appears after the Category table.
    # The category table starts with "## 1. Overview"
    overview_idx = content.find("## 1. Overview of All WorldQuant BRAIN Dataset Categories")
    if overview_idx != -1:
        # Find the "---" following this section
        insert_idx = content.find("---", overview_idx)
        if insert_idx != -1:
            # Insert right before the "---" separator
            updated_content = content[:insert_idx].rstrip() + "\n" + hierarchy_md + "\n" + content[insert_idx:]
        else:
            updated_content = content + "\n" + hierarchy_md
    else:
        # Fallback to appending at the end
        updated_content = content + "\n" + hierarchy_md

    # 6. Write back to dataset.md
    with open(dataset_md_path, "w", encoding="utf-8") as f:
        f.write(updated_content)
    print("Hierarchy successfully added to dataset.md!")

if __name__ == "__main__":
    main()
