/**
 * auth.js — Login/Register flow for index.html
 */
import { auth, isLoggedIn } from './api.js';
import { showToast } from './toast.js';

// Redirect if already logged in
if (isLoggedIn()) {
  window.location.href = '/dashboard.html';
}

// ── Tab switching ────────────────────────────────────────────────────────

const loginTab  = document.getElementById('tab-login');
const registerTab = document.getElementById('tab-register');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');

loginTab?.addEventListener('click', () => {
  loginTab.classList.add('active');
  registerTab.classList.remove('active');
  loginForm.classList.remove('hidden');
  registerForm.classList.add('hidden');
});

registerTab?.addEventListener('click', () => {
  registerTab.classList.add('active');
  loginTab.classList.remove('active');
  registerForm.classList.remove('hidden');
  loginForm.classList.add('hidden');
});

// ── Login ────────────────────────────────────────────────────────────────

loginForm?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = loginForm.querySelector('[type=submit]');
  const email    = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;

  setLoading(btn, true);
  try {
    await auth.login(email, password);
    showToast('Welcome back!', 'success');
    setTimeout(() => window.location.href = '/dashboard.html', 500);
  } catch (err) {
    showToast(err.message || 'Login failed', 'error');
  } finally {
    setLoading(btn, false);
  }
});

// ── Register ─────────────────────────────────────────────────────────────

registerForm?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = registerForm.querySelector('[type=submit]');
  const email    = document.getElementById('reg-email').value.trim();
  const name     = document.getElementById('reg-name').value.trim();
  const password = document.getElementById('reg-password').value;
  const confirm  = document.getElementById('reg-confirm').value;

  if (password !== confirm) {
    showToast('Passwords do not match', 'error');
    return;
  }

  setLoading(btn, true);
  try {
    await auth.register(email, name, password);
    showToast('Account created! Welcome aboard 🚀', 'success');
    setTimeout(() => window.location.href = '/dashboard.html', 500);
  } catch (err) {
    showToast(err.message || 'Registration failed', 'error');
  } finally {
    setLoading(btn, false);
  }
});

// ── Hero CTA ─────────────────────────────────────────────────────────────

document.getElementById('hero-cta-btn')?.addEventListener('click', () => {
  registerTab?.click();
  document.getElementById('auth-section')?.scrollIntoView({ behavior: 'smooth' });
});

// ── Util ─────────────────────────────────────────────────────────────────

function setLoading(btn, loading) {
  if (!btn) return;
  btn.disabled = loading;
  btn.innerHTML = loading
    ? '<span class="spinner"></span> Please wait...'
    : btn.dataset.label || btn.innerHTML;
  if (!loading && btn.dataset.label) btn.textContent = btn.dataset.label;
}
