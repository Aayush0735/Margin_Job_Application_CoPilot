import glob
import os

html_files = glob.glob('frontend/*.html')

for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    
    # 1. Remove pricing from navbar
    content = content.replace('<a href="pricing.html" class="nav-link">Pricing</a>\n', '')
    content = content.replace('<a href="pricing.html" class="nav-link">Pricing</a>', '')

    # 2. Update footer links
    old_privacy = '<a href="#" style="color:var(--text-3); text-decoration:none;">Privacy Policy</a>'
    new_privacy = '<a href="privacy.html" style="color:var(--text-3); text-decoration:none;">Privacy Policy</a>'
    
    old_terms = '<a href="#" style="color:var(--text-3); text-decoration:none;">Terms of Service</a>'
    new_terms = '<a href="terms.html" style="color:var(--text-3); text-decoration:none;">Terms of Service</a>'

    content = content.replace(old_privacy, new_privacy)
    content = content.replace(old_terms, new_terms)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")

print("Update complete.")
