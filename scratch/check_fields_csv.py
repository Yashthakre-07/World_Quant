import csv
import os

fields_index_path = r"c:\Users\Admin\Documents\VIBE_YT\wq\documentation\dataset\fields_index.csv"
theme_json_path = r"c:\Users\Admin\Documents\VIBE_YT\wq\theme_Dataset.json"

import json
with open(theme_json_path, 'r', encoding='utf-8') as f:
    theme_datasets = json.load(f)
theme_ids = {d['id'] for d in theme_datasets}

if os.path.exists(fields_index_path):
    print("fields_index.csv exists.")
    dataset_fields_count = {}
    
    with open(fields_index_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            headers = next(reader)
            print("CSV Headers:", headers)
        except StopIteration:
            headers = []
            print("CSV is empty.")
            
        # Try to find which column holds the dataset ID or dataset name
        # We will scan rows and find dataset references.
        row_count = 0
        for row in reader:
            row_count += 1
            # Let's inspect some rows to see format
            if row_count <= 5:
                print(f"Row {row_count}: {row}")
            
            # Let's look for theme dataset IDs in row fields.
            for item in row:
                for tid in theme_ids:
                    if tid in item:
                        dataset_fields_count[tid] = dataset_fields_count.get(tid, 0) + 1
                        
    print(f"Total rows scanned in CSV: {row_count}")
    print("Found occurrences of theme dataset IDs in CSV:")
    for tid, count in sorted(dataset_fields_count.items()):
        print(f"  {tid}: {count} rows")
else:
    print("fields_index.csv does NOT exist.")
