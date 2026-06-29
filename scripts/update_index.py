import os

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

edu_section = '''
<!-- Educational Section -->
<section id="level-up" class="section reveal-on-scroll" style="background:var(--bg-0); padding:100px 20px;">
  <div class="container text-center">
    <p class="section-eyebrow">Level Up Your Process</p>
    <h2 style="font-size:2.5rem; margin-bottom:60px;">Build an irresistible application.</h2>
    
    <div style="display:flex; gap:32px; flex-wrap:wrap; text-align:left;">
      <div class="card" style="flex:1; min-width:300px; padding:32px; border-radius:16px;">
        <div style="font-size:2rem; margin-bottom:16px;">📄</div>
        <h3 style="font-size:1.3rem; margin-bottom:12px;">Targeted Resumes</h3>
        <p style="color:var(--text-2); line-height:1.7; font-size:0.95rem;">
          Sending the same resume to 50 companies doesn't work anymore. Applify forces you to think dynamically. By tailoring your bullet points to explicitly mention the tech stack and keywords from the job description, you bridge the gap between 'candidate' and 'perfect fit'.
        </p>
      </div>
      <div class="card" style="flex:1; min-width:300px; padding:32px; border-radius:16px;">
        <div style="font-size:2rem; margin-bottom:16px;">🤝</div>
        <h3 style="font-size:1.3rem; margin-bottom:12px;">The Cover Letter Bridge</h3>
        <p style="color:var(--text-2); line-height:1.7; font-size:0.95rem;">
          Your portfolio shows what you've done. The cover letter explains why it matters to <em>them</em>. Our AI agent connects your past projects directly to the company's current pain points, making your application impossible to ignore.
        </p>
      </div>
      <div class="card" style="flex:1; min-width:300px; padding:32px; border-radius:16px;">
        <div style="font-size:2rem; margin-bottom:16px;">🧠</div>
        <h3 style="font-size:1.3rem; margin-bottom:12px;">Interview Mastery</h3>
        <p style="color:var(--text-2); line-height:1.7; font-size:0.95rem;">
          Passing the ATS is only step one. Reviewing our predicted behavioral and technical questions ensures you walk into the interview room with pre-prepared, STAR-method answers that align perfectly with the role.
        </p>
      </div>
    </div>
  </div>
</section>
'''

target = '<!-- How it works -->'
content = content.replace(target, edu_section + '\n' + target)

old_nav = '''<a href="#how-it-works" class="nav-link">How it works</a>
    <a href="#benefits" class="nav-link">Benefits</a>'''

new_nav = '''<a href="index.html#how-it-works" class="nav-link">How it works</a>
    <a href="about.html" class="nav-link">About Us</a>
    <a href="pricing.html" class="nav-link">Pricing</a>'''

content = content.replace(old_nav, new_nav)

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Update login.html navbar too
with open('frontend/login.html', 'r', encoding='utf-8') as f:
    login_content = f.read()

login_content = login_content.replace(old_nav, new_nav)
with open('frontend/login.html', 'w', encoding='utf-8') as f:
    f.write(login_content)

print('Updated index.html and login.html')
