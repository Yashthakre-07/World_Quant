import json
import os
from pathlib import Path

class AlphaRegistry:
    def __init__(self, registry_path=None):
        base_dir = Path(__file__).resolve().parent.parent
        if registry_path is None:
            self.registry_path = base_dir / "alphas_dataset" / "registry.json"
        else:
            self.registry_path = Path(registry_path)
            
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.alphas = []
        self.load()

    def load(self):
        """Loads all registered alphas from the registry JSON file."""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    self.alphas = json.load(f)
                print(f"[Registry] Loaded {len(self.alphas)} existing alphas from {self.registry_path.name}")
            except Exception as e:
                print(f"[Registry] Error loading registry: {e}. Starting fresh.")
                self.alphas = []
        else:
            self.alphas = []
            print(f"[Registry] Registry file {self.registry_path.name} not found. Created a new registry.")

    def save(self):
        """Saves the active alphas portfolio back to the registry JSON file."""
        try:
            with open(self.registry_path, "w", encoding="utf-8") as f:
                json.dump(self.alphas, f, indent=2)
            print(f"[Registry] Successfully saved registry -> {self.registry_path}")
        except Exception as e:
            print(f"[Registry] Error saving registry: {e}")

    def get_formulas(self):
        """Returns a set of all unique math formulas currently in the registry."""
        formulas = set()
        for a in self.alphas:
            formula = a.get("regular", a.get("formula", ""))
            if formula:
                formulas.add(formula.strip().replace(" ", ""))
        return formulas

    def append_batch(self, new_alphas_list):
        """
        Safely appends a list of new alphas to the registry.
        Automatically checks for mathematical duplicate expressions and skips them.
        """
        existing_formulas = self.get_formulas()
        added_count = 0
        skipped_count = 0
        
        for a in new_alphas_list:
            formula = a.get("regular", a.get("formula", "")).strip().replace(" ", "")
            if not formula:
                continue
                
            if formula in existing_formulas:
                skipped_count += 1
            else:
                self.alphas.append(a)
                existing_formulas.add(formula)
                added_count += 1
                
        print(f"[Registry] Append Complete:")
        print(f"  * Successfully Added (New): {added_count}")
        print(f"  * Skipped (Duplicate Math): {skipped_count}")
        print(f"  * Total Active Registry Portfolio: {len(self.alphas)}")
        
        if added_count > 0:
            self.save()
            
        return added_count, skipped_count
