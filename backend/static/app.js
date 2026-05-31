/**
 * StockNet — Shared API Client & UI Engine
 * All API calls go to /api/* on the same origin.
 * Cookie-based auth (HttpOnly) — no token management in the frontend.
 */

// ─── Toast Notification ───────────────────────────────────────────────────────
function showToast(message, type = 'success', duration = 3000) {
  let toast = document.getElementById('toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast';
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.className = `show ${type}`;
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => { toast.className = ''; }, duration);
}

// ─── API Client ───────────────────────────────────────────────────────────────
async function api(endpoint, method = 'GET', body = null) {
  const opts = {
    method,
    credentials: 'include',          // send HttpOnly cookie automatically
    headers: { 'Content-Type': 'application/json' },
  };
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch('/api' + endpoint, opts);

  // Redirect to login on 401/403
  if (res.status === 401 || res.status === 403) {
    if (!window.location.pathname.includes('/login')) {
      window.location.href = '/login';
    }
    throw new Error('Not authenticated');
  }

  if (!res.ok) {
    const errData = await res.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(errData.detail || `HTTP ${res.status}`);
  }

  if (res.status === 204) return null;
  return res.json();
}

// ─── Auth Helpers ─────────────────────────────────────────────────────────────
async function getCurrentUser() {
  try {
    return await api('/auth/me');
  } catch {
    return null;
  }
}

async function logout() {
  try { await api('/auth/logout', 'POST'); } catch {}
  window.location.href = '/login';
}

// ─── Guard: redirect to login if not authenticated ────────────────────────────
async function requireAuth() {
  const user = await getCurrentUser();
  if (!user) {
    window.location.href = '/login';
    return null;
  }
  return user;
}

// ─── Page → nav link mapping ──────────────────────────────────────────────────
const NAV_PAGES = [
  { href: '/dashboard',   label: 'Dashboard'    },
  { href: '/portfolio',   label: 'Portfolio'    },
  { href: '/trades',      label: 'Trade History' },
  { href: '/place-trade', label: 'Place Trade'  },
];

// ─── Shared Navbar Renderer ───────────────────────────────────────────────────
async function renderNavbar(activePath) {
  const user = await getCurrentUser();
  const placeholder = document.getElementById('navbar-placeholder');
  if (!placeholder) return;

  const currentPath = activePath || window.location.pathname;

  const navLinks = NAV_PAGES.map(p => `
    <li><a href="${p.href}" class="${currentPath === p.href ? 'active' : ''}">${p.label}</a></li>
  `).join('');

  const userChip = user ? `
    <div class="nav-user-chip">
      <div class="avatar">${user.name.charAt(0).toUpperCase()}</div>
      <span style="font-weight:600;">${user.name.split(' ')[0]}</span>
      <span class="mono" style="color:var(--green);font-size:0.78rem;">₹${formatNum(user.wallet_balance)}</span>
    </div>
    <button onclick="logout()" class="btn-icon" title="Logout" id="btn-logout">⏏</button>
  ` : `<a href="/login" class="btn-secondary" style="font-size:0.82rem;padding:6px 14px;">Login</a>`;

  placeholder.innerHTML = `
    <nav class="navbar">
      <div class="nav-left">
        <a href="/dashboard" class="brand-logo">
          <span class="live-pulse"></span> STOCKNET
        </a>
        <ul class="nav-links">${navLinks}</ul>
      </div>
      <div class="nav-right">${userChip}</div>
    </nav>
  `;
}

// ─── Ticker ───────────────────────────────────────────────────────────────────
let prevPrices = {};

async function renderTicker() {
  const placeholder = document.getElementById('ticker-placeholder');
  if (!placeholder) return;

  placeholder.innerHTML = `
    <div class="ticker-container">
      <div class="ticker-wrap">
        <div id="ticker-slide-1" class="ticker"></div>
        <div id="ticker-slide-2" class="ticker"></div>
      </div>
    </div>
  `;

  await refreshTicker();
  setInterval(refreshTicker, 30000);
}

async function refreshTicker() {
  try {
    const stocks = await api('/stocks');
    renderTickerContent(stocks);
  } catch {}
}

function renderTickerContent(stocks) {
  const slide1 = document.getElementById('ticker-slide-1');
  const slide2 = document.getElementById('ticker-slide-2');
  if (!slide1 || !slide2) return;

  let html = '';
  stocks.forEach(s => {
    const prev   = prevPrices[s.symbol] || s.current_price;
    const change = ((s.current_price - prev) / prev) * 100;
    const isUp   = change >= 0;
    html += `
      <div class="ticker-item">
        <span class="ticker-symbol">${s.symbol}</span>
        <span class="ticker-price mono">₹${formatNum(s.current_price)}</span>
        <span class="ticker-change mono ${isUp ? 'up' : 'down'}">${isUp ? '▲' : '▼'} ${Math.abs(change).toFixed(2)}%</span>
      </div>
      <span class="ticker-sep">·</span>
    `;
    prevPrices[s.symbol] = s.current_price;
  });

  slide1.innerHTML = html;
  slide2.innerHTML = html;
}

// ─── Formatting Helpers ───────────────────────────────────────────────────────
function formatNum(n, decimals = 2) {
  return Number(n).toLocaleString('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

function formatDate(iso) {
  const d = new Date(iso);
  return d.toLocaleString('en-IN', {
    day: '2-digit', month: 'short',
    hour: '2-digit', minute: '2-digit',
  });
}

// ─── Page Init (call at top of every page's DOMContentLoaded) ─────────────────
async function initPage(activePath, requireLogin = true) {
  let user = null;

  if (requireLogin) {
    user = await requireAuth();
    if (!user) return null;
  }

  await renderNavbar(activePath);
  await renderTicker();

  return user;
}
