import glob
import re

html_files = glob.glob('frontend/*.html')

for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    
    # 1. Remove pricing from navbar or footer
    content = re.sub(r'<a[^>]*href="pricing\.html"[^>]*>Pricing</a>', '', content)
    
    # 2. Update Privacy Policy links
    content = re.sub(r'<a[^>]*href="#"[^>]*>Privacy Policy</a>', '<a href="privacy.html" style="color:var(--text-3); text-decoration:none;">Privacy Policy</a>', content)
    
    # 3. Update Terms of Service links
    content = re.sub(r'<a[^>]*href="#"[^>]*>Terms of Service</a>', '<a href="terms.html" style="color:var(--text-3); text-decoration:none;">Terms of Service</a>', content)

    # 4. Clean up empty lines that might have been left by removing the pricing link
    content = re.sub(r'\n\s*\n', '\n\n', content)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")

print("Update complete.")
