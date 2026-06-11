import os
import re
import json

formulas = set()

# Pattern for formulas in python files
formula_pattern = re.compile(r'"formula"\s*:\s*"([^"]+)"')
formula_pattern_single = re.compile(r"'formula'\s*:\s*'([^']+)'")

def extract_from_file(filepath):
    if filepath.endswith('.py'):
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                for match in formula_pattern.finditer(content):
                    formulas.add(match.group(1).replace('\\"', '"'))
                for match in formula_pattern_single.finditer(content):
                    formulas.add(match.group(1))
        except Exception as e:
            pass
    elif filepath.endswith('.json'):
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)
                def recurse(obj):
                    if isinstance(obj, dict):
                        formula = obj.get('formula') or obj.get('regular')
                        if formula and isinstance(formula, str):
                            formulas.add(formula)
                        for k, v in obj.items():
                            recurse(v)
                    elif isinstance(obj, list):
                        for item in obj:
                            recurse(item)
                recurse(data)
        except:
            pass

# Scan directories
dirs_to_scan = ['developer', 'alpha_maker', 'alphas', 'scratch']
for d in dirs_to_scan:
    if os.path.exists(d):
        for root, dirs, files in os.walk(d):
            for file in files:
                extract_from_file(os.path.join(root, file))

print(f"Total unique formulas extracted: {len(formulas)}")

# Write to scratch/all_extracted_formulas.json
with open("scratch/all_extracted_formulas.json", "w", encoding="utf-8") as f:
    json.dump(list(formulas), f, indent=2)
