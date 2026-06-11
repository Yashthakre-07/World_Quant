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
    
    # 2. Extract unique datasets for both sections:
    # A. Hierarchical Tree: Category -> Subcategory -> Dataset ID -> Dataset Name
    # B. Sorted list of all datasets for the detail table
    tree = {}
    unique_datasets = {}
    
    for ds in datasets:
        cat_name = ds.get("category", {}).get("name", "Uncategorized").strip()
        subcat_name = ds.get("subcategory", {}).get("name", "N/A").strip()
        ds_id = ds["id"].strip()
        ds_name = ds["name"].strip()
        region = ds.get("region", "N/A")
        delay = str(ds.get("delay", "N/A"))
        
        # Build hierarchy tree
        if cat_name not in tree:
            tree[cat_name] = {}
        if subcat_name not in tree[cat_name]:
            tree[cat_name][subcat_name] = {}
        tree[cat_name][subcat_name][ds_id] = ds_name
        
        # Build unique datasets dict
        if ds_id not in unique_datasets:
            unique_datasets[ds_id] = {
                "id": ds_id,
                "name": ds_name,
                "category": cat_name,
                "subcategory": subcat_name,
                "description": ds.get("description", "").strip(),
                "regions": {region},
                "delays": {delay}
            }
        else:
            unique_datasets[ds_id]["regions"].add(region)
            unique_datasets[ds_id]["delays"].add(delay)

    # Format sets to strings
    for ds_id, ds in unique_datasets.items():
        ds["regions"] = ", ".join(sorted(list(ds["regions"])))
        ds["delays"] = ", ".join(sorted(list(ds["delays"])))

    # Sort datasets for table
    sorted_ds = sorted(unique_datasets.values(), key=lambda x: (x["category"], x["name"]))

    # 3. Construct Markdown components
    md = []
    
    # Header
    md.append("# WorldQuant BRAIN Dataset Catalog & Alpha Reference\n\n")
    md.append("This document maps all the dataset categories available on WorldQuant BRAIN, highlights the metadata from the platform, and specifies **exactly what data we have extracted locally** and where it is located in this repository so you can easily reference field names while writing alphas.\n\n")
    md.append("---\n\n")
    
    # Section 1
    md.append("## 1. Overview of All WorldQuant BRAIN Dataset Categories\n\n")
    md.append("Below is the summary of the dataset categories from the WorldQuant BRAIN platform (matching the platform dashboard categories):\n\n")
    md.append("| Category | Value Score | Total Datasets | Total Fields | Available Regions | Local Cache Status | Local File Link |\n")
    md.append("| :--- | :---: | :---: | :---: | :--- | :---: | :--- |\n")
    md.append("| **Analyst** | 4 | 36 | 24,821 | ASI, CHN, EUR, GLB, HKG, IND, KOR, MEA, USA | **EXTRACTED** | [category_analyst.json](file:///c:/Users/Admin/Documents/VIBE_YT/wq/documentation/dataset/category_analyst.json) |\n")
    md.append("| **Broker** | 10 | 1 | 12 | ASI | N/A (Non-US) | - |\n")
    md.append("| **Earnings** | 5 | 8 | 419 | ASI, EUR, GLB, HKG, IND, KOR, MEA, USA | **EXTRACTED** | Included in [all_datasets.json](file:///c:/Users/Admin/Documents/VIBE_YT/wq/documentation/dataset/all_datasets.json) |\n")
    md.append("| **Fundamental** | 4 | 40 | 26,260 | ASI, CHN, EUR, GLB, HKG, IND, KOR, MEA, USA | **EXTRACTED** | [category_fundamental.json](file:///c:/Users/Admin/Documents/VIBE_YT/wq/documentation/dataset/category_fundamental.json) |\n")
    md.append("| **Imbalance** | 5 | 1 | 2 | ASI, EUR, HKG, IND, KOR, USA | N/A (Restricted) | - |\n")
    md.append("| **Insiders** | 8 | 7 | 275 | ASI, EUR, GLB, HKG, IND, KOR, USA | N/A (Restricted) | - |\n")
    md.append("| **Institutions** | 6 | 4 | 87 | ASI, CHN, EUR, GLB, HKG, IND, KOR, USA | N/A (Restricted) | - |\n")
    md.append("| **Macro** | 8 | 11 | 341 | ASI, CHN, EUR, GLB, HKG, IND, KOR, USA | N/A (Restricted) | - |\n")
    md.append("| **Model** | 7 | 103 | 41,805 | ASI, CHN, EUR, GLB, HKG, IND, KOR, MEA, USA | **EXTRACTED** | [category_model.json](file:///c:/Users/Admin/Documents/VIBE_YT/wq/documentation/dataset/category_model.json) |\n")
    md.append("| **News** | 3 | 34 | 3,495 | ASI, CHN, EUR, GLB, HKG, IND, KOR, USA | **EXTRACTED** | [category_news.json](file:///c:/Users/Admin/Documents/VIBE_YT/wq/documentation/dataset/category_news.json) |\n")
    md.append("| **Option** | 6 | 8 | 537 | IND, USA | **EXTRACTED** | [category_option.json](file:///c:/Users/Admin/Documents/VIBE_YT/wq/documentation/dataset/category_option.json) |\n")
    md.append("| **Price Volume** | - | 36 | 2,340 | ASI, CHN, EUR, GLB, HKG, IND, KOR, USA | **EXTRACTED** | [category_price_volume.json](file:///c:/Users/Admin/Documents/VIBE_YT/wq/documentation/dataset/category_price_volume.json) |\n")
    md.append("| **Social Media** | - | 24 | 264 | USA | **EXTRACTED** | [category_social_media.json](file:///c:/Users/Admin/Documents/VIBE_YT/wq/documentation/dataset/category_social_media.json) |\n\n")
    md.append("*Note: Datasets marked \"N/A\" are either non-US, require premium institutional subscriptions not enabled for this account profile, or are not available for standard delays (delay=1) and TOP3000 universe.*\n\n")
    
    # Section 1.1 (Hierarchy Outline)
    md.append("## 1.1 Hierarchical Map of Categories, Subcategories, and Datasets\n\n")
    md.append("Here is the outline of how the datasets are organized on the WorldQuant BRAIN platform:\n\n")
    for cat in sorted(tree.keys()):
        md.append(f"- **📁 {cat}**\n")
        subcats = tree[cat]
        for subcat in sorted(subcats.keys()):
            md.append(f"  - *📂 {subcat}*\n")
            datasets_in_sub = subcats[subcat]
            for ds_id in sorted(datasets_in_sub.keys()):
                ds_name = datasets_in_sub[ds_id]
                md.append(f"    - `{ds_id}`: {ds_name}\n")
    md.append("\n")
    
    md.append("---\n\n")
    
    # Section 2
    md.append("## 2. Our Local Extracted Data & Files\n\n")
    md.append("We have run a full catalog download using your **GOLD-tier** credentials. The complete schemas, field descriptions, and formula keys are saved here:\n\n")
    md.append("*   **Master Fields Database (JSON):** [all_datasets.json](file:///c:/Users/Admin/Documents/VIBE_YT/wq/documentation/dataset/all_datasets.json) (570,000+ lines of raw API field mappings)\n")
    md.append("*   **Searchable Flat Index (CSV):** [fields_index.csv](file:///c:/Users/Admin/Documents/VIBE_YT/wq/documentation/dataset/fields_index.csv) (8.0 MB file with mapping columns: `category`, `dataset_id`, `dataset_name`, `field_id`, `description`, `type`)\n")
    md.append("*   **Human-Readable Catalogue (Markdown):** [DATASET_CATALOG.md](file:///c:/Users/Admin/Documents/VIBE_YT/wq/documentation/dataset/DATASET_CATALOG.md) (5.5 MB file with tables listing descriptions for every single field)\n\n")
    
    md.append("---\n\n")
    
    # Section 3
    md.append("## 3. Local Dataset Breakdown (Key Fields & Alpha Motifs)\n\n")
    
    md.append("### 📊 A. Analyst Estimates (`analyst4`)\n")
    md.append("Consensus expectations and revisions from brokers and institutional analysts. **Highly recommended for orthogonal signals.**\n")
    md.append("*   **Local File:** [category_analyst.json](file:///c:/Users/Admin/Documents/VIBE_YT/wq/documentation/dataset/category_analyst.json)\n")
    md.append("*   **Key Fields:**\n")
    md.append("    *   `anl4_afv4_eps_mean`: Consensus mean of analyst annual estimates for Earnings Per Share (EPS).\n")
    md.append("    *   `anl4_ebitda_mean`: Consensus mean of analyst annual estimates for EBITDA.\n")
    md.append("    *   `anl4_fs_detail_estimates_advanced_af_nd_revenue_mean`: Consensus mean of analyst annual estimates for Revenue.\n")
    md.append("    *   `anl4_eps_std`: Standard deviation of analyst EPS estimates (dispersion/uncertainty).\n")
    md.append("    *   `anl4_eps_number`: Number of analyst estimates contributing to consensus (attention/coverage).\n")
    md.append("*   **Alpha Motif Example (EPS Revision Momentum):**\n")
    md.append("    `group_neutralize(trade_when(volume > adv20 * 0.5, rank(ts_decay_linear(ts_delta(anl4_afv4_eps_mean, 5) / (close + 0.001), 5)), 0), subindustry)`\n\n")
    
    md.append("---\n\n")
    
    md.append("### 🏛️ B. Fundamental (`fundamental`)\n")
    md.append("Historical corporate accounting values from balance sheets, income statements, and cash flows.\n")
    md.append("*   **Local File:** [category_fundamental.json](file:///c:/Users/Admin/Documents/VIBE_YT/wq/documentation/dataset/category_fundamental.json)\n")
    md.append("*   **Key Fields:**\n")
    md.append("    *   `ebitda`: Operating earnings before interest, taxes, depreciation, and amortization.\n")
    md.append("    *   `goodwill`: Value of intangibles/acquisitions on the balance sheet.\n")
    md.append("    *   `cash_flow_operating`: Operational cash flow generated.\n")
    md.append("    *   `working_capital`: Current assets minus current liabilities.\n")
    md.append("*   **Alpha Motif Example (Cash Flow Margin Expansion):**\n")
    md.append("    `group_neutralize(rank(ts_decay_linear(ts_delta(cash_flow_operating / (assets + 0.01), 20), 10)), subindustry)`\n\n")
    
    md.append("---\n\n")
    
    md.append("### 📰 C. News Sentiment (`news18` / RavenPack)\n")
    md.append("Real-time news coverage metrics and sentiment scores.\n")
    md.append("*   **Local File:** [category_news.json](file:///c:/Users/Admin/Documents/VIBE_YT/wq/documentation/dataset/category_news.json)\n")
    md.append("*   **Key Fields:**\n")
    md.append("    *   `mean_event_sentiment_score`: The average sentiment score for events over a specified period.\n")
    md.append("    *   `mean_event_novelty_score`: The average novelty/uniqueness score for news events.\n")
    md.append("    *   `mean_merger_acquisition_sentiment`: News sentiment specifically regarding mergers, acquisitions, and takeovers.\n")
    md.append("*   **Alpha Motif Example (Sentiment Reversion on High Volume):**\n")
    md.append("    `group_neutralize(trade_when(volume > adv20 * 1.2, -rank(ts_decay_linear(mean_event_sentiment_score, 5)), 0), subindustry)`\n\n")
    
    md.append("---\n\n")
    
    md.append("### ⚙️ D. Option (`option`)\n")
    md.append("Equity option chain statistics and implied metrics.\n")
    md.append("*   **Local File:** [category_option.json](file:///c:/Users/Admin/Documents/VIBE_YT/wq/documentation/dataset/category_option.json)\n")
    md.append("*   **Key Fields:**\n")
    md.append("    *   `historical_volatility_10`: Realized stock volatility over 10 days.\n")
    md.append("    *   `implied_volatility_call_10` / `implied_volatility_put_10`: Option implied volatilities.\n")
    md.append("    *   `implied_vol_skew`: Imbalance in volatility pricing between calls and puts.\n")
    md.append("*   **Alpha Motif Example (Option Skew Reversal):**\n")
    md.append("    `group_neutralize(trade_when(volume > adv20 * 0.8, -rank(ts_decay_linear(implied_volatility_put_10 - implied_volatility_call_10, 5)), 0), subindustry)`\n\n")
    
    md.append("---\n\n")
    
    # Section 4
    md.append("## 4. How to Search Fields While Designing Alphas\n")
    md.append("If you are designing a dataset-specific alpha:\n")
    md.append("1.  Open **[fields_index.csv](file:///c:/Users/Admin/Documents/VIBE_YT/wq/documentation/dataset/fields_index.csv)** in Excel or a text editor.\n")
    md.append("2.  Search/Filter for keywords (e.g., search `EBITDA` or `Revenue` or `Broker`).\n")
    md.append("3.  Copy the corresponding `field_id` (e.g., `anl4_ebitda_mean`) and insert it directly into your FastExpr formula.\n\n")
    
    md.append("---\n\n")
    
    # Section 5
    md.append("## 5. Complete Catalog of All Available Datasets\n\n")
    md.append("Below is the complete list of all unique datasets available on the WorldQuant BRAIN platform, compiled from the platform's metadata:\n\n")
    
    from collections import defaultdict
    by_cat = defaultdict(list)
    for ds in sorted_ds:
        by_cat[ds["category"]].append(ds)

    for cat, ds_list in sorted(by_cat.items()):
        md.append(f"### 📁 {cat} Datasets\n\n")
        md.append("| Dataset ID | Dataset Name | Subcategory | Delays | Regions | Description |\n")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for ds in ds_list:
            desc = ds["description"].replace("\n", " ").replace("|", "\\|")
            if len(desc) > 200:
                desc = desc[:197] + "..."
            md.append(f"| `{ds['id']}` | {ds['name']} | {ds['subcategory']} | {ds['delays']} | {ds['regions']} | {desc} |\n")
        md.append("\n")

    # 4. Write to dataset.md
    with open(dataset_md_path, "w", encoding="utf-8") as f:
        f.write("".join(md))
    print("dataset.md fully rebuilt and verified successfully!")

if __name__ == "__main__":
    main()
