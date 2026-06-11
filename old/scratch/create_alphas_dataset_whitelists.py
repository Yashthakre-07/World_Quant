import os
import json

base_dir = "alphas_dataset"

# 1. analyst16 fields
os.makedirs(os.path.join(base_dir, "analyst16", "alphas"), exist_ok=True)
anl16_fields = [
    {"id": "anl16_actsurprise"},
    {"id": "anl16_actsuescore"},
    {"id": "anl16_actgrowth"},
    {"id": "anl16_actstability"},
    {"id": "anl16_actvalue"}
]
with open(os.path.join(base_dir, "analyst16", "alphas", "fields.json"), "w") as f:
    json.dump(anl16_fields, f, indent=2)

# 2. analyst44 fields
os.makedirs(os.path.join(base_dir, "analyst44", "alphas"), exist_ok=True)
anl44_fields = [
    {"id": "anl44_analyst"}
]
with open(os.path.join(base_dir, "analyst44", "alphas", "fields.json"), "w") as f:
    json.dump(anl44_fields, f, indent=2)

# 3. analyst45 fields
os.makedirs(os.path.join(base_dir, "analyst45", "alphas"), exist_ok=True)
anl45_fields = [
    {"id": "anl45_ad_rel_ret_per"},
    {"id": "anl45_jensensalpha"},
    {"id": "anl45_beta"},
    {"id": "anl45_ad_ret_per"}
]
with open(os.path.join(base_dir, "analyst45", "alphas", "fields.json"), "w") as f:
    json.dump(anl45_fields, f, indent=2)

print("Whitelists successfully created under alphas_dataset/")
