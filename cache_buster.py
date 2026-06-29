import glob

html_files = glob.glob('frontend/*.html')
for file in html_files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple replace for .css and .js
    content = content.replace('.css"', '.css?v=2"')
    content = content.replace('.js"', '.js?v=2"')
    content = content.replace(".js'", ".js?v=2'")
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

print('Added cache busting to all HTML files')
