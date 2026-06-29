/**
 * api.js — Centralized fetch() wrapper with JWT token management.
 */

const API_BASE = 'https://margin-job-application-copilot.onrender.com/api';

// ── Token Management ─────────────────────────────────────────────────────

export function getToken() {
  return localStorage.getItem('jwt_token');
}

export function setToken(token) {
  localStorage.setItem('jwt_token', token);
}

export function removeToken() {
  localStorage.removeItem('jwt_token');
  localStorage.removeItem('user');
}

export function getUser() {
  try {
    return JSON.parse(localStorage.getItem('user') || 'null');
  } catch {
    return null;
  }
}

export function setUser(user) {
  localStorage.setItem('user', JSON.stringify(user));
}

export function isLoggedIn() {
  return !!getToken();
}

// ── Core fetch wrapper ───────────────────────────────────────────────────

async function request(path, options = {}) {
  const token = getToken();
  const headers = {
    ...(options.headers || {}),
  };

  // Don't set Content-Type for FormData (browser sets it with boundary)
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  // Auth error → redirect to login
  if (res.status === 401) {
    removeToken();
    window.location.href = '/index.html';
    return;
  }

  if (!res.ok) {
    let errMsg = `HTTP ${res.status}`;
    try {
      const err = await res.json();
      if (Array.isArray(err.detail)) {
        errMsg = err.detail.map(d => d.msg).join(', ');
      } else {
        errMsg = err.detail || JSON.stringify(err);
      }
    } catch {}
    throw new Error(typeof errMsg === 'string' ? errMsg : JSON.stringify(errMsg));
  }

  // 204 No Content
  if (res.status === 204) return null;

  // Check if response is binary (for downloads)
  const contentType = res.headers.get('content-type') || '';
  if (contentType.includes('application/vnd') || contentType.includes('application/octet-stream')) {
    return res.blob();
  }

  return res.json();
}

// ── Auth endpoints ───────────────────────────────────────────────────────

export const auth = {
  async register(email, fullName, password) {
    const data = await request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, full_name: fullName, password }),
    });
    setToken(data.access_token);
    setUser(data.user);
    return data;
  },

  async login(email, password) {
    const data = await request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    setToken(data.access_token);
    setUser(data.user);
    return data;
  },

  logout() {
    removeToken();
    window.location.href = '/index.html';
  },

  async me() {
    return request('/auth/me');
  },
};

// ── Applications endpoints ───────────────────────────────────────────────

export const applications = {
  async list() {
    return request('/applications');
  },

  async get(id) {
    return request(`/applications/${id}`);
  },

  async create(data) {
    return request('/applications', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async update(id, data) {
    return request(`/applications/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async delete(id) {
    return request(`/applications/${id}`, { method: 'DELETE' });
  },

  async getDrafts(id) {
    return request(`/applications/${id}/drafts`);
  },

  async getLatestDraft(id) {
    return request(`/applications/${id}/drafts/latest`);
  },
};

// ── Pipeline endpoints ───────────────────────────────────────────────────

export const pipeline = {
  async run(appId, resumeFile) {
    const form = new FormData();
    form.append('resume_file', resumeFile);
    return request(`/applications/${appId}/run-pipeline`, {
      method: 'POST',
      body: form,
    });
  },

  async regenerate(appId, section) {
    return request(`/applications/${appId}/regenerate/${section}`, {
      method: 'POST',
    });
  },

  async downloadCoverLetter(appId, draftId) {
    return request(`/applications/${appId}/drafts/${draftId}/download/cover-letter`);
  },

  async downloadResume(appId, draftId) {
    return request(`/applications/${appId}/drafts/${draftId}/download/resume`);
  },
};

// ── JD Scraper ───────────────────────────────────────────────────────────

export async function scrapeJD(url) {
  return request('/scrape-jd', {
    method: 'POST',
    body: JSON.stringify({ url }),
  });
}

// ── Utility: Trigger a file download from a Blob ─────────────────────────

export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
