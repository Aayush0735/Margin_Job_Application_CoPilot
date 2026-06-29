import glob
html_files = glob.glob('frontend/*.html')
for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace('?v=2"', '?v=5"')
    content = content.replace('?v=3"', '?v=5"')
    content = content.replace('?v=4"', '?v=5"')
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

print('Added ?v=5 cache busting to all HTML files')
