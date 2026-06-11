with open(r'c:\Users\Admin\Documents\VIBE_YT\wq\old\developer\prompt.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Encode to sys.stdout.encoding safely or print by encoding to bytes and writing to stdout buffer, or using print(..., errors='replace')
import sys
def safe_print(s):
    sys.stdout.buffer.write(s.encode('utf-8', errors='replace') + b'\n')

safe_print(f"File size of old/developer/prompt.txt: {len(text)}")
safe_print("=== Head of old/developer/prompt.txt ===")
safe_print(text[:4000])

import re
matches = [m.start() for m in re.finditer(r'(?i)generator', text)]
safe_print(f"Occurrences of 'generator': {len(matches)}")
for idx in matches:
    start = max(0, idx - 150)
    end = min(len(text), idx + 450)
    safe_print(f"--- Context at index {idx} ---")
    safe_print(text[start:end])
    safe_print("-"*40)
