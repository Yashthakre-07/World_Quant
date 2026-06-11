import json
import os

transcript_path = r'C:\Users\Admin\.gemini\antigravity\brain\749bd3d6-c1f0-40b3-bfdc-5cc49cd235de\.system_generated\logs\transcript.jsonl'
current_transcript_path = r'C:\Users\Admin\.gemini\antigravity\brain\5ce856c0-2e8c-4de5-a552-5b8bc5a05e6d\.system_generated\logs\transcript.jsonl'

def search_user_prompts(path):
    if not os.path.exists(path):
        print(f"Path does not exist: {path}")
        return
    with open(path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            try:
                data = json.loads(line)
                if data.get('source') == 'USER_EXPLICIT' and data.get('type') == 'USER_INPUT':
                    content = data.get('content', '')
                    content_lower = content.lower()
                    # Check for keywords indicating a generator prompt or formula details
                    keywords = ['generator', 'prompt', 'formula', 'alpha', 'rank', 'neutralize', 'decay', 'wq_generatorllm']
                    if any(k in content_lower for k in keywords) and len(content) > 100:
                        print(f"=== {os.path.basename(path)} Step {data.get('step_index')} ===")
                        print(content)
                        print('\n' + '='*80 + '\n')
            except Exception as e:
                pass

print("Searching previous transcript for user prompts:")
search_user_prompts(transcript_path)
print("Searching current transcript for user prompts:")
search_user_prompts(current_transcript_path)
