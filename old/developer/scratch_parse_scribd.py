import re

def main():
    file_path = "C:/Users/Admin/.gemini/antigravity-ide/brain/69b811e2-ff07-4a79-a843-8a4998a0e418/.system_generated/steps/423/content.md"
    
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    print(f"Total HTML size: {len(html)} characters")
    
    # Let's remove script and style blocks
    html_clean = re.sub(r'<script.*?>.*?</script>', '', html, flags=re.DOTALL)
    print(f"Size after removing scripts: {len(html_clean)} characters")
    
    html_clean_2 = re.sub(r'<style.*?>.*?</style>', '', html_clean, flags=re.DOTALL)
    print(f"Size after removing styles: {len(html_clean_2)} characters")
    
    print("\nFirst 2000 chars of cleaned HTML:")
    print(html_clean_2[:2000])

if __name__ == "__main__":
    main()
