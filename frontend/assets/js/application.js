/**
 * application.js — Single application view page: upload, pipeline, results, diffs.
 */
import { applications, pipeline, downloadBlob, isLoggedIn, getUser } from './api.js';
import { showToast } from './toast.js';
import { renderDiff, renderFullResumeDiff } from './diff.js';

if (!isLoggedIn()) window.location.href = '/index.html';

// ── Globals ───────────────────────────────────────────────────────────────

const params  = new URLSearchParams(window.location.search);
const APP_ID  = parseInt(params.get('id'));
let currentApp   = null;
let currentDraft = null;

if (!APP_ID) window.location.href = '/dashboard.html';

// ── Init ──────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', async () => {
  setupNavbar();
  setupTabs();
  setupUploadZone();
  setupRunButton();
  setupRegenerateButtons();
  await loadApp();
});

// ── Load Application ──────────────────────────────────────────────────────

async function loadApp() {
  try {
    currentApp = await applications.get(APP_ID);
    renderAppHeader(currentApp);
    renderInputPanel(currentApp);

    try {
      currentDraft = await applications.getLatestDraft(APP_ID);
      renderAllResults(currentDraft);
    } catch {
      showPipelinePrompt();
    }
  } catch (err) {
    showToast('Failed to load application: ' + err.message, 'error');
  }
}

// ── Navbar ────────────────────────────────────────────────────────────────

function setupNavbar() {
  const user = getUser();
  if (user) {
    document.getElementById('nav-user-name').textContent = user.full_name;
    document.getElementById('nav-user-initial').textContent = user.full_name?.[0]?.toUpperCase() || '?';
  }
  document.getElementById('logout-btn')?.addEventListener('click', () => {
    localStorage.clear();
    window.location.href = '/index.html';
  });
}

// ── Render App Header ─────────────────────────────────────────────────────

function renderAppHeader(app) {
  document.title = `${app.job_title} at ${app.company} — Co-Pilot`;
  document.getElementById('app-title').textContent = `${app.job_title}`;
  document.getElementById('app-company').textContent = `🏢 ${app.company}`;

  const statusSel = document.getElementById('status-select');
  if (statusSel) {
    statusSel.value = app.status;
    statusSel.addEventListener('change', async () => {
      try {
        await applications.update(APP_ID, { status: statusSel.value });
        showToast('Status updated', 'success');
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  }
}

// ── Input Panel ───────────────────────────────────────────────────────────

function renderInputPanel(app) {
  const jdEl = document.getElementById('jd-display');
  if (jdEl) {
    jdEl.textContent = app.jd_text?.substring(0, 600) + (app.jd_text?.length > 600 ? '...' : '');
  }

  if (app.original_resume_filename) {
    const filenameEl = document.getElementById('resume-filename');
    if (filenameEl) {
      filenameEl.textContent = `📎 ${app.original_resume_filename}`;
      filenameEl.classList.remove('hidden');
    }
  }
}

// ── Pipeline Prompt ───────────────────────────────────────────────────────

function showPipelinePrompt() {
  document.getElementById('results-placeholder').classList.remove('hidden');
  document.getElementById('results-content').classList.add('hidden');
}

// ── Upload Zone ───────────────────────────────────────────────────────────

function setupUploadZone() {
  const zone  = document.getElementById('upload-zone');
  const input = document.getElementById('resume-input');
  const label = document.getElementById('upload-label');

  if (!zone || !input) return;

  zone.addEventListener('dragover', (e) => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', (e) => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    if (e.dataTransfer.files[0]) {
      input.files = e.dataTransfer.files;
      label.textContent = `📎 ${e.dataTransfer.files[0].name}`;
    }
  });

  input.addEventListener('change', () => {
    if (input.files[0]) label.textContent = `📎 ${input.files[0].name}`;
  });
}

// ── Run Pipeline ──────────────────────────────────────────────────────────

function setupRunButton() {
  const btn = document.getElementById('run-pipeline-btn');
  btn?.addEventListener('click', runPipeline);
}

async function runPipeline() {
  const input = document.getElementById('resume-input');
  if (!input?.files[0]) {
    showToast('Please upload your resume PDF first', 'warning');
    return;
  }

  const btn = document.getElementById('run-pipeline-btn');
  showPipelineProgress();

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Running Pipeline...';

  try {
    currentDraft = await pipeline.run(APP_ID, input.files[0]);
    showToast('✅ Pipeline complete! Your application kit is ready.', 'success');
    hidePipelineProgress();
    renderAllResults(currentDraft);
  } catch (err) {
    hidePipelineProgress();
    showToast('Pipeline failed: ' + err.message, 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '🚀 Run Pipeline';
  }
}

function showPipelineProgress() {
  const progress = document.getElementById('pipeline-progress');
  progress?.classList.remove('hidden');

  const steps = ['fit', 'resume', 'cover-letter', 'interview'];
  let stepIdx = 0;

  const interval = setInterval(() => {
    if (stepIdx >= steps.length) { clearInterval(interval); return; }
    const el = document.getElementById(`step-${steps[stepIdx]}`);
    if (el) { el.classList.remove('active'); el.classList.add('done'); }
    stepIdx++;
    if (stepIdx < steps.length) {
      const next = document.getElementById(`step-${steps[stepIdx]}`);
      next?.classList.add('active');
    }
  }, 8000);

  document.getElementById(`step-${steps[0]}`)?.classList.add('active');
  document.getElementById('pipeline-interval')?.setAttribute('data-interval', interval);
}

function hidePipelineProgress() {
  document.getElementById('pipeline-progress')?.classList.add('hidden');
  document.querySelectorAll('.pipeline-step').forEach(s => {
    s.classList.remove('active');
    s.classList.add('done');
  });
}

// ── Render All Results ────────────────────────────────────────────────────

function renderAllResults(draft) {
  document.getElementById('results-placeholder')?.classList.add('hidden');
  document.getElementById('results-content')?.classList.remove('hidden');

  renderFitAnalysis(draft.fit_analysis);
  renderResumeTab(draft);
  renderCoverLetter(draft);
  renderInterviewQA(draft.interview_qa);
  updateDownloadButtons(draft);
}

// ── Fit Analysis Tab ──────────────────────────────────────────────────────

function renderFitAnalysis(fit) {
  if (!fit) return;

  // Score ring
  const score = fit.overall_score || 0;
  const ring = document.getElementById('score-ring');
  if (ring) {
    ring.style.setProperty('--score', `${score}%`);
    ring.querySelector('.score-ring-value').textContent = `${score}%`;
  }

  document.getElementById('fit-summary').textContent = fit.match_summary || '';

  // Matched skills
  const matchedEl = document.getElementById('matched-skills');
  if (matchedEl && fit.matched_skills) {
    matchedEl.innerHTML = fit.matched_skills.map(s => `
      <span class="skill-pill matched" title="${escHtml(s.evidence || '')}">
        ✓ ${escHtml(s.skill)}
        <span class="badge badge-success" style="font-size:0.65rem">${s.importance}</span>
      </span>`).join('');
  }

  // Gaps
  const gapsEl = document.getElementById('skill-gaps');
  if (gapsEl && fit.skill_gaps) {
    gapsEl.innerHTML = fit.skill_gaps.map(s => `
      <span class="skill-pill gap" title="${escHtml(s.suggestion || '')}">
        ✗ ${escHtml(s.skill)}
        <span class="badge badge-danger" style="font-size:0.65rem">${s.importance}</span>
      </span>`).join('');
  }

  // Keywords
  const kwEl = document.getElementById('keywords-to-add');
  if (kwEl && fit.keywords_to_add) {
    kwEl.innerHTML = fit.keywords_to_add.map(k =>
      `<span class="skill-pill keyword">🔑 ${escHtml(k)}</span>`
    ).join('');
  }

  // Emphasis points
  const empEl = document.getElementById('emphasis-points');
  if (empEl && fit.emphasis_points) {
    empEl.innerHTML = `<ul class="emphasis-list">
      ${fit.emphasis_points.map(p => `<li>${escHtml(p)}</li>`).join('')}
    </ul>`;
  }

  // Red flags
  const rfEl = document.getElementById('red-flags');
  if (rfEl) {
    if (fit.red_flags?.length) {
      rfEl.innerHTML = fit.red_flags.map(r =>
        `<div class="flex gap-2 text-sm" style="color:var(--warning)">⚠️ ${escHtml(r)}</div>`
      ).join('');
    } else {
      rfEl.innerHTML = '<p class="text-muted text-sm">No significant red flags identified.</p>';
    }
  }
}

// ── Resume Tab ────────────────────────────────────────────────────────────

function renderResumeTab(draft) {
  const diffContainer = document.getElementById('resume-diff-container');
  if (!diffContainer) return;

  if (draft.resume_sections?.length > 0) {
    renderDiff(draft.resume_sections, diffContainer);
  } else if (draft.resume_rewrite) {
    renderFullResumeDiff(currentApp?.original_resume_text, draft.resume_rewrite, diffContainer);
  }

  // Full rewrite text view
  const rewriteEl = document.getElementById('resume-rewrite-text');
  if (rewriteEl && draft.resume_rewrite) {
    rewriteEl.textContent = draft.resume_rewrite;
  }
}

// ── Cover Letter Tab ──────────────────────────────────────────────────────

function renderCoverLetter(draft) {
  const el = document.getElementById('cover-letter-body');
  if (el && draft.cover_letter) {
    el.textContent = draft.cover_letter;
  }
}

// ── Interview Tab ─────────────────────────────────────────────────────────

function renderInterviewQA(qa) {
  const container = document.getElementById('interview-qa-list');
  if (!container || !qa?.length) {
    container && (container.innerHTML = '<p class="text-muted">No Q&A generated yet.</p>');
    return;
  }

  const TYPE_BADGE = {
    behavioural: 'badge-primary',
    technical:   'badge-info',
    situational: 'badge-warning',
    motivation:  'badge-success',
    growth:      'badge-neutral',
  };

  container.innerHTML = qa.map((item, i) => `
    <div class="qa-item" id="qa-item-${i}">
      <div class="qa-question" onclick="toggleQA(${i})">
        <div class="qa-number">${item.id || i+1}</div>
        <div style="flex:1">
          <div style="margin-bottom:6px">${escHtml(item.question)}</div>
          <div class="flex gap-2 flex-wrap">
            <span class="badge ${TYPE_BADGE[item.type] || 'badge-neutral'}">${item.type}</span>
            ${item.tests ? `<span class="badge badge-neutral text-xs">Tests: ${escHtml(item.tests)}</span>` : ''}
          </div>
        </div>
        <span class="qa-chevron">▾</span>
      </div>
      <div class="qa-answer">
        <p style="margin-bottom:12px; color: var(--text-primary)">${escHtml(item.sample_answer)}</p>
        ${item.tips ? `<div class="qa-tip">💡 ${escHtml(item.tips)}</div>` : ''}
      </div>
    </div>`).join('');
}

window.toggleQA = function(i) {
  const item = document.getElementById(`qa-item-${i}`);
  item?.classList.toggle('open');
};

// ── Tabs ──────────────────────────────────────────────────────────────────

function setupTabs() {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.tab;
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById(`tab-${target}`)?.classList.add('active');
    });
  });
}

// ── Regenerate Buttons ────────────────────────────────────────────────────

function setupRegenerateButtons() {
  document.querySelectorAll('[data-regen]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const section = btn.dataset.regen;
      if (!currentDraft) { showToast('Run the full pipeline first', 'warning'); return; }
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner"></span>';
      try {
        currentDraft = await pipeline.regenerate(APP_ID, section);
        renderAllResults(currentDraft);
        showToast(`${section} regenerated!`, 'success');
      } catch (err) {
        showToast(err.message, 'error');
      } finally {
        btn.disabled = false;
        btn.innerHTML = '🔄 Regenerate';
      }
    });
  });
}

// ── Downloads ─────────────────────────────────────────────────────────────

function updateDownloadButtons(draft) {
  document.getElementById('dl-cover-letter')?.addEventListener('click', async () => {
    try {
      const blob = await pipeline.downloadCoverLetter(APP_ID, draft.id);
      downloadBlob(blob, `cover_letter_${currentApp?.company}.docx`);
    } catch (err) { showToast(err.message, 'error'); }
  });

  document.getElementById('dl-resume')?.addEventListener('click', async () => {
    try {
      const blob = await pipeline.downloadResume(APP_ID, draft.id);
      downloadBlob(blob, `resume_${currentApp?.company}.docx`);
    } catch (err) { showToast(err.message, 'error'); }
  });
}

// ── Utils ─────────────────────────────────────────────────────────────────

function escHtml(str) {
  return String(str || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
