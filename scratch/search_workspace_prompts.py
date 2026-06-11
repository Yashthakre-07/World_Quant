import os

workspace = r'c:\Users\Admin\Documents\VIBE_YT\wq'
exclude = ['.git', 'node_modules', '__pycache__', '.pytest_cache']

matches = []
for root, dirs, files in os.walk(workspace):
    dirs[:] = [d for d in dirs if d not in exclude]
    for file in files:
        if file.endswith(('.md', '.py', '.txt', '.json', '.html', '.css', '.js')):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    content_lower = content.lower()
                    if 'prompt' in content_lower and 'generator' in content_lower:
                        matches.append((path, len(content)))
            except Exception as e:
                pass

print("Files matching 'prompt' and 'generator':")
for m in matches:
    print(f"- {m[0]} (size: {m[1]} bytes)")
