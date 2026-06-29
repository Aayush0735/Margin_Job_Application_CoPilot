import os
import glob
import re

files_to_check = glob.glob('frontend/*.html') + ['backend/config.py', 'README.md']

for filepath in files_to_check:
    if not os.path.exists(filepath):
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace cases
    new_content = re.sub(r'Job Application Co-Pilot', 'Applify', content, flags=re.IGNORECASE)
    new_content = re.sub(r'Co-Pilot', 'Applify', new_content, flags=re.IGNORECASE)
    new_content = re.sub(r'Copilot', 'Applify', new_content, flags=re.IGNORECASE)
    
    if content != new_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Updated {filepath}')

print('Global rename complete.')
