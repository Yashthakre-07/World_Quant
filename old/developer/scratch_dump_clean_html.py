import re

def main():
    file_path = "C:/Users/Admin/.gemini/antigravity-ide/brain/69b811e2-ff07-4a79-a843-8a4998a0e418/.system_generated/steps/423/content.md"
    
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Clean scripts and styles
    html_clean = re.sub(r'<script.*?>.*?</script>', '', html, flags=re.DOTALL)
    html_clean = re.sub(r'<style.*?>.*?</style>', '', html_clean, flags=re.DOTALL)

    print(f"Cleaned HTML size: {len(html_clean)} characters")

    # Let's search if the word 'EBIT' or 'EBITDA' or 'actual' exists in the cleaned HTML (case-insensitive)
    for term in ["ebit", "ebitda", "eps", "dividend", "estimate", "actual"]:
        matches = [m.start() for m in re.finditer(term, html_clean, re.IGNORECASE)]
        print(f"Term '{term}': found {len(matches)} times. Positions: {matches[:10]}")
        
        # Print a snippet around the first match
        if matches:
            pos = matches[0]
            start = max(0, pos - 50)
            end = min(len(html_clean), pos + 150)
            print(f"  Snippet around first match: {html_clean[start:end]}\n")

if __name__ == "__main__":
    main()
