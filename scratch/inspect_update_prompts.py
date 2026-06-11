import sys
def safe_print(s):
    sys.stdout.buffer.write(s.encode('utf-8', errors='replace') + b'\n')

with open(r'c:\Users\Admin\Documents\VIBE_YT\wq\old\scratch\update_agent_prompts.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Parse python file or find all variables defined in it
# Let's execute the file in a restricted dict to see its variables
loc = {}
try:
    exec(text, globals(), loc)
    for k, v in loc.items():
        if isinstance(v, str) and ('prompt' in k.lower() or 'generator' in k.lower() or 'validator' in k.lower()):
            safe_print(f"=== Variable: {k} (len: {len(v)}) ===")
            safe_print(v)
            safe_print("="*80)
except Exception as e:
    safe_print(f"Error executing file: {str(e)}")
    # fallback to regex/substring
    safe_print("Fallback dump of file:")
    safe_print(text)
