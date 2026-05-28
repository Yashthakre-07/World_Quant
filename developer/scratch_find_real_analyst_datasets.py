import json

try:
    with open("documentation/dataset/raw_datasets.json", "r") as f:
        datasets = json.load(f)
    print(f"Total datasets in raw cache: {len(datasets)}")
    
    real_analyst_ds = []
    for d in datasets:
        cat_obj = d.get("category") or {}
        
        # Check if category is Analyst
        is_analyst = False
        if isinstance(cat_obj, dict):
            if cat_obj.get("name") == "Analyst" or cat_obj.get("id") == "analyst":
                is_analyst = True
        elif isinstance(cat_obj, str):
            if cat_obj.lower() == "analyst":
                is_analyst = True
                
        if is_analyst:
            real_analyst_ds.append(d)
            
    print(f"\nFound {len(real_analyst_ds)} datasets belonging to the 'Analyst' Category:")
    
    # Let's group by ID to see unique dataset IDs
    unique_ids = {}
    for d in real_analyst_ds:
        ds_id = d.get("id")
        if ds_id not in unique_ids:
            unique_ids[ds_id] = {
                "name": d.get("name"),
                "regions": set(),
                "universes": set()
            }
        unique_ids[ds_id]["regions"].add(d.get("region"))
        unique_ids[ds_id]["universes"].add(d.get("universe"))
        
    for idx, (ds_id, info) in enumerate(unique_ids.items()):
        print(f"  [{idx+1}] Dataset ID: {ds_id} | Name: {info['name']}")
        print(f"      Regions: {list(info['regions'])} | Universes: {list(info['universes'])}")
        
except Exception as e:
    print(f"Error: {e}")
