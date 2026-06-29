/**
 * diff.js — Resume diff renderer (before/after side-by-side view).
 */

/**
 * Render diff panels from an array of section objects.
 * @param {Array<{section_name, original_text, rewritten_text}>} sections
 * @param {HTMLElement} container - element to render into
 */
export function renderDiff(sections, container) {
  if (!sections || sections.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <span class="empty-icon">📄</span>
        <p class="empty-title">No diff data available</p>
        <p class="empty-desc">Run the pipeline to see before/after resume changes.</p>
      </div>`;
    return;
  }

  container.innerHTML = '';

  sections.forEach((section, idx) => {
    const wrap = document.createElement('div');
    wrap.className = 'mt-4';
    wrap.innerHTML = `
      <h4 class="text-sm font-semibold text-secondary mb-2" style="padding: 0 4px;">
        📝 ${escapeHtml(section.section_name)}
      </h4>
      <div class="diff-container">
        <div class="diff-panel before">
          <div class="diff-panel-header">
            <span>🔴</span> Before
          </div>
          <div class="diff-content" id="diff-before-${idx}"></div>
        </div>
        <div class="diff-panel after">
          <div class="diff-panel-header">
            <span>🟢</span> After
          </div>
          <div class="diff-content" id="diff-after-${idx}"></div>
        </div>
      </div>`;
    container.appendChild(wrap);

    renderLines(section.original_text, document.getElementById(`diff-before-${idx}`));
    renderLines(section.rewritten_text, document.getElementById(`diff-after-${idx}`));
  });
}

function renderLines(text, container) {
  if (!text) {
    container.innerHTML = '<div class="diff-line text-muted" style="padding: 16px;">—</div>';
    return;
  }
  const lines = text.split('\n');
  container.innerHTML = lines.map(line =>
    `<div class="diff-line">${escapeHtml(line) || '&nbsp;'}</div>`
  ).join('');
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Render a unified full-text diff for the whole resume.
 */
export function renderFullResumeDiff(originalText, rewrittenText, container) {
  if (!originalText || !rewrittenText) {
    container.innerHTML = '<p class="text-muted">No rewrite available yet.</p>';
    return;
  }

  container.innerHTML = `
    <div class="diff-container">
      <div class="diff-panel before">
        <div class="diff-panel-header"><span>🔴</span> Original Resume</div>
        <div class="diff-content" id="full-diff-before"></div>
      </div>
      <div class="diff-panel after">
        <div class="diff-panel-header"><span>🟢</span> Tailored Resume</div>
        <div class="diff-content" id="full-diff-after"></div>
      </div>
    </div>`;

  renderLines(originalText, document.getElementById('full-diff-before'));
  renderLines(rewrittenText, document.getElementById('full-diff-after'));
}
