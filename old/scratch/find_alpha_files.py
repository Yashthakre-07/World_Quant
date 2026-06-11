import os

def find_file(filename):
    for root, dirs, files in os.walk('.'):
        if any(p in root for p in ['.git', '.venv', '.gemini', 'node_modules', '__pycache__']):
            continue
        if filename in files:
            print(f"Found {filename} at {os.path.join(root, filename)}")

find_file("alpha_VkO9lkz5.json")
find_file("alpha_lerLW6x7.json")
