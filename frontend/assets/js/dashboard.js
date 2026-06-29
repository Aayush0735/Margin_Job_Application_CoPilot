/**
 * dashboard.js — Role pipeline dashboard page logic.
 */
import { applications, auth, getUser, isLoggedIn } from './api.js';
import { showToast } from './toast.js';

if (!isLoggedIn()) window.location.href = '/index.html';

// ── Globals ───────────────────────────────────────────────────────────────

const user = getUser();
let allApps = [];

// ── Init ──────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', async () => {
  // Set user info in navbar
  if (user) {
    document.getElementById('nav-user-name').textContent = user.full_name;
    document.getElementById('nav-user-initial').textContent = user.full_name?.[0]?.toUpperCase() || '?';
  }

  document.getElementById('logout-btn')?.addEventListener('click', () => auth.logout());
  document.getElementById('new-app-btn')?.addEventListener('click', openNewAppModal);
  document.getElementById('new-app-btn-empty')?.addEventListener('click', openNewAppModal);

  setupNewAppModal();
  await loadApplications();
});

// ── Load & Render ─────────────────────────────────────────────────────────

async function loadApplications() {
  const listEl = document.getElementById('apps-list');
  listEl.innerHTML = '<div class="flex items-center gap-3 text-secondary p-4"><span class="spinner"></span> Loading your applications...</div>';

  try {
    allApps = await applications.list();
    renderApplications(allApps);
    updateStats(allApps);
  } catch (err) {
    listEl.innerHTML = `<div class="empty-state"><span class="empty-icon">⚠️</span><p class="empty-title">Failed to load applications</p><p class="empty-desc">${err.message}</p></div>`;
  }
}

function renderApplications(apps) {
  const listEl = document.getElementById('apps-list');
  const emptyEl = document.getElementById('empty-state');
  const countEl = document.getElementById('apps-count');

  countEl.textContent = apps.length;

  if (apps.length === 0) {
    listEl.innerHTML = '';
    emptyEl.classList.remove('hidden');
    return;
  }

  emptyEl.classList.add('hidden');
  listEl.innerHTML = apps.map(app => roleCardHTML(app)).join('');

  // Attach event listeners
  listEl.querySelectorAll('[data-app-id]').forEach(card => {
    const id = card.dataset.appId;
    card.addEventListener('click', (e) => {
      if (e.target.closest('.btn')) return; // don't nav if clicking action btns
      window.location.href = `/application.html?id=${id}`;
    });
  });

  listEl.querySelectorAll('[data-delete-id]').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.stopPropagation();
      const id = btn.dataset.deleteId;
      if (!confirm('Delete this application?')) return;
      try {
        await applications.delete(id);
        showToast('Application deleted', 'info');
        await loadApplications();
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  });

  listEl.querySelectorAll('[data-status-id]').forEach(sel => {
    sel.addEventListener('change', async (e) => {
      e.stopPropagation();
      const id = sel.dataset.statusId;
      try {
        await applications.update(id, { status: sel.value });
        showToast('Status updated', 'success');
        await loadApplications();
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  });

  // Filter
  const search = document.getElementById('search-input');
  const filter = document.getElementById('filter-status');

  function applyFilter() {
    const q = (search.value || '').toLowerCase();
    const s = filter.value;
    const filtered = allApps.filter(app => {
      const matchesQuery = !q || app.job_title.toLowerCase().includes(q) || app.company.toLowerCase().includes(q);
      const matchesStatus = !s || app.status === s;
      return matchesQuery && matchesStatus;
    });
    renderApplications(filtered);
  }

  search?.addEventListener('input', applyFilter);
  filter?.addEventListener('change', applyFilter);
}

function roleCardHTML(app) {
  const pipelineIcon = {
    pending:  '⏳',
    running:  '⚙️',
    done:     '✅',
    failed:   '❌',
  }[app.pipeline_status] || '⏳';

  const initial = (app.company?.[0] || '?').toUpperCase();
  const date = new Date(app.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

  return `
    <div class="role-card" data-app-id="${app.id}" style="cursor:pointer; margin-bottom: 12px;">
      <div class="role-card-logo" style="background: ${companyColor(app.company)}">
        ${initial}
      </div>
      <div class="role-card-info">
        <div class="role-card-title">${escHtml(app.job_title)}</div>
        <div class="role-card-company">🏢 ${escHtml(app.company)}</div>
        <div class="role-card-meta">
          <span>${pipelineIcon} ${app.pipeline_status.replace('_', ' ')}</span>
          <span>📅 ${date}</span>
        </div>
      </div>
      <div class="role-card-actions">
        <select class="form-select btn-sm" data-status-id="${app.id}" style="width:140px; padding: 6px 32px 6px 10px; font-size: 0.8rem;"
          onclick="event.stopPropagation()">
          ${['not_yet','applied','interviewing','offered','rejected'].map(s =>
            `<option value="${s}" ${app.status === s ? 'selected' : ''}>${statusLabel(s)}</option>`
          ).join('')}
        </select>
        <button class="btn btn-ghost btn-icon btn-sm" data-delete-id="${app.id}" title="Delete" onclick="event.stopPropagation()">🗑️</button>
      </div>
    </div>`;
}

function updateStats(apps) {
  const stats = { total: apps.length, applied: 0, interviewing: 0, offered: 0 };
  apps.forEach(a => {
    if (a.status === 'applied') stats.applied++;
    if (a.status === 'interviewing') stats.interviewing++;
    if (a.status === 'offered') stats.offered++;
  });
  document.getElementById('stat-total')?.setAttribute('data-value', stats.total);
  document.getElementById('stat-applied')?.setAttribute('data-value', stats.applied);
  document.getElementById('stat-interviewing')?.setAttribute('data-value', stats.interviewing);
  document.getElementById('stat-offered')?.setAttribute('data-value', stats.offered);

  // Animate counters
  document.querySelectorAll('[data-value]').forEach(el => {
    const target = parseInt(el.dataset.value || 0);
    animateCounter(el, target);
  });
}

function animateCounter(el, target) {
  let current = 0;
  const step = Math.max(1, Math.ceil(target / 20));
  const interval = setInterval(() => {
    current = Math.min(current + step, target);
    el.textContent = current;
    if (current >= target) clearInterval(interval);
  }, 40);
}

// ── New Application Modal ─────────────────────────────────────────────────

function setupNewAppModal() {
  const overlay = document.getElementById('new-app-modal');
  const form = document.getElementById('new-app-form');
  const scrapeBtn = document.getElementById('scrape-jd-btn');
  const jdUrlInput = document.getElementById('new-jd-url');
  const jdTextInput = document.getElementById('new-jd-text');
  const closeBtn = document.getElementById('modal-close-btn');
  const cancelBtn = document.getElementById('modal-cancel-btn');

  [closeBtn, cancelBtn].forEach(btn => {
    btn?.addEventListener('click', closeModal);
  });

  overlay?.addEventListener('click', (e) => {
    if (e.target === overlay) closeModal();
  });

  scrapeBtn?.addEventListener('click', async () => {
    const url = jdUrlInput?.value.trim();
    if (!url) { showToast('Enter a URL first', 'warning'); return; }
    scrapeBtn.disabled = true;
    scrapeBtn.innerHTML = '<span class="spinner"></span>';
    try {
      const { jd_text, title, company } = await import('./api.js').then(m => m.scrapeJD(url));
      jdTextInput.value = jd_text;
      if (title) document.getElementById('new-job-title').value = title;
      if (company) document.getElementById('new-company').value = company;
      showToast('Job description scraped!', 'success');
    } catch (err) {
      showToast('Scrape failed: ' + err.message, 'error');
    } finally {
      scrapeBtn.disabled = false;
      scrapeBtn.innerHTML = '🔗 Scrape';
    }
  });

  form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = form.querySelector('[type=submit]');
    const data = {
      job_title: document.getElementById('new-job-title').value.trim(),
      company: document.getElementById('new-company').value.trim(),
      jd_text: jdTextInput.value.trim(),
      jd_url: jdUrlInput.value.trim() || null,
    };

    if (!data.jd_text) { showToast('Please enter the job description', 'warning'); return; }

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Creating...';
    try {
      const app = await applications.create(data);
      closeModal();
      showToast('Application created! 🎉', 'success');
      setTimeout(() => window.location.href = `/application.html?id=${app.id}`, 600);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      btn.disabled = false;
      btn.innerHTML = 'Create Application';
    }
  });
}

function openNewAppModal() {
  document.getElementById('new-app-modal')?.classList.add('open');
}

function closeModal() {
  document.getElementById('new-app-modal')?.classList.remove('open');
}

// ── Utils ─────────────────────────────────────────────────────────────────

function statusLabel(s) {
  return { not_yet: '📋 Not Applied', applied: '📤 Applied', interviewing: '💬 Interviewing', offered: '🎉 Offered', rejected: '❌ Rejected' }[s] || s;
}

function companyColor(name) {
  const colors = [
    'linear-gradient(135deg,#6366f1,#8b5cf6)',
    'linear-gradient(135deg,#06b6d4,#0284c7)',
    'linear-gradient(135deg,#10b981,#059669)',
    'linear-gradient(135deg,#f59e0b,#d97706)',
    'linear-gradient(135deg,#ec4899,#db2777)',
    'linear-gradient(135deg,#ef4444,#dc2626)',
  ];
  let hash = 0;
  for (const c of (name || '')) hash = (hash * 31 + c.charCodeAt(0)) & 0xffffffff;
  return colors[Math.abs(hash) % colors.length];
}

function escHtml(str) {
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
