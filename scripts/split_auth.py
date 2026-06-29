import os

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

auth_start = content.find('<!-- ── Auth ──')
footer_start = content.find('<!-- ── Footer ──')

if auth_start != -1 and footer_start != -1:
    # 1. Create login.html
    head_nav = content[:content.find('<!-- ── Hero ──')]
    # Adjust nav links in head_nav
    head_nav = head_nav.replace('href="#auth-section"', 'href="login.html"')

    auth_section = content[auth_start:footer_start]
    footer_and_scripts = content[footer_start:]
    
    login_html = head_nav + auth_section + footer_and_scripts
    with open('frontend/login.html', 'w', encoding='utf-8') as f:
        f.write(login_html)
        
    # 2. Update index.html
    new_index = content[:auth_start] + footer_and_scripts
    new_index = new_index.replace('href="#auth-section"', 'href="login.html"')
    
    with open('frontend/index.html', 'w', encoding='utf-8') as f:
        f.write(new_index)
    
    print('Successfully split index.html and created login.html')
else:
    print('Could not find markers')
