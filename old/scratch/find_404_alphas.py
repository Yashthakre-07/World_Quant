import os
import json
from pathlib import Path

target_ids = ["VkO9lkz5", "28960689", "d5ad670d", "d5dXLQYJ", "63bc7ea1", "06f64e69", "03cbc7dc", "66dd7b5e"]

def search_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Simple substring check first
            for tid in target_ids:
                if tid in content:
                    print(f"[FOUND] ID '{tid}' in text of file: {file_path}")
            
            # Now try parsing as JSON to find key-value matching
            try:
                data = json.loads(content)
                find_in_object(data, file_path)
            except Exception:
                pass
    except Exception as e:
        pass

def find_in_object(obj, file_path):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if v in target_ids or k in target_ids:
                print(f"[JSON MATCH] {file_path} -> key/value: {k}: {v}")
            if isinstance(v, (dict, list)):
                find_in_object(v, file_path)
    elif isinstance(obj, list):
        for item in obj:
            if item in target_ids:
                print(f"[JSON LIST MATCH] {file_path} -> list item: {item}")
            if isinstance(item, (dict, list)):
                find_in_object(item, file_path)

def main():
    root_dir = Path(".")
    print("Searching for target 404 alpha IDs in all json files...")
    for path in root_dir.glob("**/*.json"):
        search_json_file(path)
    print("Search complete.")

if __name__ == "__main__":
    main()
