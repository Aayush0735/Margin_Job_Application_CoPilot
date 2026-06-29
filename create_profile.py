import re

with open('frontend/profile.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace <main class="main">...</main>
pattern = re.compile(r'(<main class="main">).*?(</main>)', re.DOTALL)
profile_main = r'''\1
    <div class="flex items-center justify-between gap-4 mb-4" style="margin-bottom:20px;">
      <div>
        <h1 style="font-size:1.4rem;font-weight:800;letter-spacing:-0.03em">Account Settings</h1>
        <p style="font-size:0.8rem;color:var(--text-3);margin-top:2px">Manage your profile details.</p>
      </div>
    </div>

    <div class="card" style="max-width: 600px; margin-bottom: 24px;">
      <div class="card-header">
        <h3 style="font-size:1rem">Profile Details</h3>
      </div>
      <div class="card-body">
        <form id="profile-form" style="display:flex;flex-direction:column;gap:16px">
          <div class="form-group">
            <label class="label">Full Name</label>
            <input type="text" class="input" id="profile-name" value="Loading..." disabled />
          </div>
          <div class="form-group">
            <label class="label">Email Address</label>
            <input type="email" class="input" id="profile-email" value="Loading..." disabled />
          </div>
        </form>
      </div>
    </div>
\2'''

content = pattern.sub(profile_main, content)

# Adjust active links in sidebar
content = content.replace('href="/dashboard.html" class="sidebar-link active"', 'href="/dashboard.html" class="sidebar-link"')
content = content.replace('<div class="sidebar-section-label">Account</div>', '<div class="sidebar-section-label">Account</div>\n    <a href="/profile.html" class="sidebar-link active"><span class="sidebar-link-icon">⚙️</span> Settings</a>')

with open('frontend/profile.html', 'w', encoding='utf-8') as f:
    f.write(content)
