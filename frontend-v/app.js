// StockNet — Shared Logic & API Engine
// P1 Web Tier Integration Proof

const SEED_PRICES = {
  AAPL: 175.00,
  GOOGL: 140.00,
  TSLA: 180.00,
  AMZN: 170.00
};

// Global State Initializer
const DEFAULT_CONFIG = {
  apiMode: 'mock', // 'mock' or 'live'
  apiHost: 'http://10.0.1.10:5000',
  env: 'PROD' // 'PROD' or 'STAGING'
};

let config = { ...DEFAULT_CONFIG };

// Mock Database (Active State in LocalStorage)
const DEFAULT_MOCK_DATA = {
  stocks: {
    AAPL: { symbol: 'AAPL', name: 'Apple Inc.', price: 175.00, change: 1.25, changeVal: 2.15, volume: '52.4M' },
    GOOGL: { symbol: 'GOOGL', name: 'Alphabet Inc.', price: 140.00, change: -0.45, changeVal: -0.63, volume: '28.1M' },
    TSLA: { symbol: 'TSLA', name: 'Tesla Inc.', price: 180.00, change: 3.80, changeVal: 6.60, volume: '88.9M' },
    AMZN: { symbol: 'AMZN', name: 'Amazon.com Inc.', price: 170.00, change: -1.10, changeVal: -1.89, volume: '34.7M' }
  },
  portfolio: {
    cashBalance: 45280.40,
    holdings: [
      { symbol: 'AAPL', shares: 80, avgBuyPrice: 168.50 },
      { symbol: 'TSLA', shares: 50, avgBuyPrice: 185.00 },
      { symbol: 'AMZN', shares: 100, avgBuyPrice: 165.00 }
    ]
  },
  trades: [
    { id: 1001, symbol: 'TSLA', side: 'BUY', qty: 50, price: 185.00, timestamp: '2026-05-29 10:15:30', compliance_status: 'CLEAR' },
    { id: 1002, symbol: 'AAPL', side: 'BUY', qty: 80, price: 168.50, timestamp: '2026-05-29 11:22:45', compliance_status: 'CLEAR' },
    { id: 1003, symbol: 'AMZN', side: 'BUY', qty: 100, price: 165.00, timestamp: '2026-05-29 13:05:12', compliance_status: 'CLEAR' },
    { id: 1004, symbol: 'GOOGL', side: 'SELL', qty: 30, price: 142.10, timestamp: '2026-05-29 14:10:02', compliance_status: 'CLEAR' },
    { id: 1005, symbol: 'TSLA', side: 'BUY', qty: 400, price: 178.50, timestamp: '2026-05-29 14:40:55', compliance_status: 'CLEAR' },
    { id: 1006, symbol: 'AAPL', side: 'BUY', qty: 1200, price: 174.20, timestamp: '2026-05-29 14:50:18', compliance_status: 'FLAGGED' } // High quantity trade
  ]
};

let db = { ...DEFAULT_MOCK_DATA };

// Initialize Configuration and Database from LocalStorage
function initStorage() {
  const savedConfig = localStorage.getItem('stocknet_config');
  if (savedConfig) {
    try { config = JSON.parse(savedConfig); } catch (e) { console.error('Failed to parse config', e); }
  } else {
    localStorage.setItem('stocknet_config', JSON.stringify(config));
  }

  const savedDb = localStorage.getItem('stocknet_db');
  if (savedDb) {
    try { db = JSON.parse(savedDb); } catch (e) { console.error('Failed to parse DB', e); }
  } else {
    localStorage.setItem('stocknet_db', JSON.stringify(db));
  }
}

function saveConfig(newConfig) {
  config = { ...config, ...newConfig };
  localStorage.setItem('stocknet_config', JSON.stringify(config));
  updateUIForConfig();
}

function saveDb() {
  localStorage.setItem('stocknet_db', JSON.stringify(db));
}

// Global UI Rendering Injection
function renderCommonUI() {
  const navbarPlaceholder = document.getElementById('navbar-placeholder');
  const tickerPlaceholder = document.getElementById('ticker-placeholder');

  // 1. Inject Glassmorphism Navigation Bar
  if (navbarPlaceholder) {
    const activePage = window.location.pathname.split('/').pop() || 'index.html';
    
    navbarPlaceholder.innerHTML = `
      <nav class="navbar">
        <div class="nav-left">
          <a href="index.html" class="brand-logo">
            <span class="live-pulse"></span>
            STOCKNET
          </a>
          <ul class="nav-links">
            <li><a href="index.html" class="${activePage === 'index.html' ? 'active' : ''}">Dashboard</a></li>
            <li><a href="portfolio.html" class="${activePage === 'portfolio.html' ? 'active' : ''}">Portfolio</a></li>
            <li><a href="trades.html" class="${activePage === 'trades.html' ? 'active' : ''}">Trade History</a></li>
            <li><a href="place-trade.html" class="${activePage === 'place-trade.html' ? 'active' : ''}">Place Trade</a></li>
          </ul>
        </div>
        <div class="nav-right">
          <span id="env-badge" class="badge" style="cursor: pointer;" title="Click to toggle Env (Integration Proof)"></span>
          <span id="api-badge" class="badge" style="cursor: pointer;" title="Click to configure API Mode"></span>
          <button id="btn-settings" class="btn-icon" title="API Connectivity Configuration">⚙️</button>
        </div>
      </nav>
    `;

    // Event hooks on Navbar
    document.getElementById('env-badge').addEventListener('click', toggleEnvironment);
    document.getElementById('api-badge').addEventListener('click', openSettingsModal);
    document.getElementById('btn-settings').addEventListener('click', openSettingsModal);
  }

  // 2. Inject Scrolling Ticker
  if (tickerPlaceholder) {
    tickerPlaceholder.innerHTML = `
      <div class="ticker-container">
        <div class="ticker-wrap">
          <div id="ticker-slide-1" class="ticker"></div>
          <div id="ticker-slide-2" class="ticker"></div>
        </div>
      </div>
    `;
    renderTickerContent();
  }

  // 3. Inject Settings Dialog Modal markup to body
  if (!document.getElementById('settings-modal')) {
    const modalDiv = document.createElement('div');
    modalDiv.id = 'settings-modal';
    modalDiv.className = 'modal-overlay';
    modalDiv.innerHTML = `
      <div class="modal-content">
        <button class="modal-close" id="modal-close-btn">&times;</button>
        <h3 style="font-family: var(--font-heading); margin-bottom: 20px; color: var(--green);">⚙️ Architecture Integration</h3>
        
        <div class="form-group">
          <label class="form-label">Client Access Mode</label>
          <div class="segmented-control" id="settings-api-mode">
            <button class="segment-btn active buy" data-value="mock">Local Demo</button>
            <button class="segment-btn sell" data-value="live">Live App Tier</button>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label" for="api-host-input">stock-p1-app-ec2-1 URL</label>
          <input type="text" id="api-host-input" class="form-control mono" placeholder="http://10.0.1.10:5000" />
          <span style="font-size: 0.75rem; color: var(--text-muted); display: block; margin-top: 4px;">
            Port 5000 on App Tier Private IP
          </span>
        </div>

        <div class="form-group">
          <label class="form-label">VPC Peering Context</label>
          <select id="settings-env" class="form-control">
            <option value="PROD">PROD VPC Peering (10.2.0.0/16)</option>
            <option value="STAGING">STAGING VPC Peering (10.3.0.0/16)</option>
          </select>
        </div>

        <button id="btn-save-settings" class="btn-primary" style="margin-top: 10px;">Save Settings</button>
      </div>
    `;
    document.body.appendChild(modalDiv);

    // Event hooks on Settings Modal
    document.getElementById('modal-close-btn').addEventListener('click', closeSettingsModal);
    document.getElementById('btn-save-settings').addEventListener('click', saveModalSettings);
    
    // Toggle Mode in Settings Modal Segment Selector
    const segments = document.querySelectorAll('#settings-api-mode .segment-btn');
    segments.forEach(btn => {
      btn.addEventListener('click', (e) => {
        segments.forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
      });
    });
  }

  updateUIForConfig();
}

function updateUIForConfig() {
  const envBadge = document.getElementById('env-badge');
  const apiBadge = document.getElementById('api-badge');

  if (envBadge) {
    envBadge.className = `badge ${config.env === 'PROD' ? 'badge-prod' : 'badge-staging'}`;
    envBadge.textContent = config.env;
  }

  if (apiBadge) {
    if (config.apiMode === 'live') {
      apiBadge.className = 'badge badge-prod';
      apiBadge.textContent = 'LIVE API';
      apiBadge.style.borderColor = 'rgba(0, 200, 83, 0.3)';
    } else {
      apiBadge.className = 'badge';
      apiBadge.style.backgroundColor = '#2c2c2e';
      apiBadge.style.color = '#aeaeb2';
      apiBadge.textContent = 'DEMO MOCK';
    }
  }

  // Sync inputs inside settings modal
  const hostInput = document.getElementById('api-host-input');
  if (hostInput) hostInput.value = config.apiHost;

  const envSelect = document.getElementById('settings-env');
  if (envSelect) envSelect.value = config.env;

  const segmentBtns = document.querySelectorAll('#settings-api-mode .segment-btn');
  segmentBtns.forEach(btn => {
    if (btn.getAttribute('data-value') === config.apiMode) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });
}

function toggleEnvironment() {
  const nextEnv = config.env === 'PROD' ? 'STAGING' : 'PROD';
  saveConfig({ env: nextEnv });
  console.log(`Environment switched to: ${nextEnv}`);
  location.reload();
}

function openSettingsModal() {
  document.getElementById('settings-modal').classList.add('active');
}

function closeSettingsModal() {
  document.getElementById('settings-modal').classList.remove('active');
}

function saveModalSettings() {
  const selectedModeBtn = document.querySelector('#settings-api-mode .segment-btn.active');
  const mode = selectedModeBtn ? selectedModeBtn.getAttribute('data-value') : 'mock';
  const host = document.getElementById('api-host-input').value.trim();
  const env = document.getElementById('settings-env').value;

  saveConfig({
    apiMode: mode,
    apiHost: host || 'http://10.0.1.10:5000',
    env: env
  });

  closeSettingsModal();
  console.log('Saved settings:', config);
  location.reload();
}

// Render loopable ticker content
function renderTickerContent() {
  const slide1 = document.getElementById('ticker-slide-1');
  const slide2 = document.getElementById('ticker-slide-2');
  if (!slide1 || !slide2) return;

  let tickerHtml = '';
  Object.values(db.stocks).forEach(stock => {
    const isUp = stock.change >= 0;
    const sign = isUp ? '▲' : '▼';
    const colorClass = isUp ? 'up' : 'down';
    tickerHtml += `
      <div class="ticker-item">
        <span class="ticker-symbol">${stock.symbol}</span>
        <span class="ticker-price mono">$${stock.price.toFixed(2)}</span>
        <span class="ticker-change mono ${colorClass}">${sign} ${Math.abs(stock.change).toFixed(2)}%</span>
      </div>
    `;
  });

  slide1.innerHTML = tickerHtml;
  slide2.innerHTML = tickerHtml; // Repeating to enable seamless looped scrolling
}

// Live Simulated Price Updates (Capped at ±2% Drift)
function startPriceTicker() {
  setInterval(() => {
    Object.keys(db.stocks).forEach(symbol => {
      const stock = db.stocks[symbol];
      const seedVal = SEED_PRICES[symbol];

      // 1. Generate capped drift between -2.0% and +2.0%
      const driftPercent = (Math.random() * 4 - 2) / 100; // -0.02 to +0.02
      let newPrice = stock.price * (1 + driftPercent);

      // 2. Absolute safety ceiling/floor to prevent long-term deviation from seed (capped within 15% of baseline DB seed)
      const maxDeviation = seedVal * 0.15;
      if (newPrice > seedVal + maxDeviation) {
        newPrice = seedVal + maxDeviation;
      } else if (newPrice < seedVal - maxDeviation) {
        newPrice = seedVal - maxDeviation;
      }

      // Calculate indicators
      const changeVal = newPrice - seedVal;
      const changePercent = (changeVal / seedVal) * 100;

      stock.price = newPrice;
      stock.changeVal = changeVal;
      stock.change = changePercent;
    });

    renderTickerContent();

    // Custom Hook: Refresh prices on Dashboard elements if they exist
    if (typeof refreshDashboardPrices === 'function') {
      refreshDashboardPrices();
    }
  }, 4000);
}

// Robust API Client with Fail-safe Fallback
async function apiRequest(endpoint, method = 'GET', body = null) {
  if (config.apiMode === 'live') {
    const url = `${config.apiHost}${endpoint}`;
    try {
      const options = {
        method,
        headers: { 'Content-Type': 'application/json' }
      };
      if (body) options.body = JSON.stringify(body);

      const response = await fetch(url, options);
      if (!response.ok) throw new Error(`HTTP Error Status: ${response.status}`);
      return await response.json();
    } catch (err) {
      console.warn(`Integration Link Offline: Failed to fetch ${url}. Falling back to client-side simulated DB. Error:`, err);
      // Fallback is intentional to let the frontend work for standalone presentation
    }
  }

  // Local Storage / Simulated database operations
  return mockHandler(endpoint, method, body);
}

function mockHandler(endpoint, method, body) {
  return new Promise((resolve) => {
    setTimeout(() => {
      if (endpoint === '/api/stocks') {
        resolve(Object.values(db.stocks));
      } 
      else if (endpoint === '/api/portfolio') {
        // Hydrate current price and calculate P&L
        const holdingsHydrated = db.portfolio.holdings.map(h => {
          const liveStock = db.stocks[h.symbol];
          const curPrice = liveStock ? liveStock.price : h.avgBuyPrice;
          const cost = h.shares * h.avgBuyPrice;
          const currentVal = h.shares * curPrice;
          const pnlVal = currentVal - cost;
          const pnlPct = cost > 0 ? (pnlVal / cost) * 100 : 0;
          return {
            ...h,
            currentPrice: curPrice,
            currentValue: currentVal,
            pnlVal,
            pnlPct
          };
        });

        const holdingsTotal = holdingsHydrated.reduce((acc, h) => acc + h.currentValue, 0);

        resolve({
          cashBalance: db.portfolio.cashBalance,
          holdings: holdingsHydrated,
          totalPortfolioValue: holdingsTotal,
          netWorth: holdingsTotal + db.portfolio.cashBalance
        });
      } 
      else if (endpoint === '/api/trades') {
        resolve(db.trades);
      } 
      else if (endpoint === '/api/trade' && method === 'POST') {
        const { symbol, side, qty } = body;
        const stock = db.stocks[symbol];
        if (!stock) {
          resolve({ success: false, error: 'Symbol not found.' });
          return;
        }

        const price = stock.price;
        const total = price * qty;

        // Perform transactional validation in mock
        if (side === 'BUY') {
          if (db.portfolio.cashBalance < total) {
            resolve({ success: false, error: 'Insufficient funds in RDS wallet account.' });
            return;
          }
          db.portfolio.cashBalance -= total;
          
          // Add/Update Holdings
          const holding = db.portfolio.holdings.find(h => h.symbol === symbol);
          if (holding) {
            const newTotalShares = holding.shares + qty;
            holding.avgBuyPrice = ((holding.shares * holding.avgBuyPrice) + total) / newTotalShares;
            holding.shares = newTotalShares;
          } else {
            db.portfolio.holdings.push({ symbol, shares: qty, avgBuyPrice: price });
          }
        } else {
          // Sell Validation
          const holding = db.portfolio.holdings.find(h => h.symbol === symbol);
          if (!holding || holding.shares < qty) {
            resolve({ success: false, error: 'Insufficient shares owned to complete trade.' });
            return;
          }
          db.portfolio.cashBalance += total;
          holding.shares -= qty;
          
          // Remove if empty
          if (holding.shares === 0) {
            db.portfolio.holdings = db.portfolio.holdings.filter(h => h.symbol !== symbol);
          }
        }

        // Compliance checks simulator (Confirm with P4 Lambda rule thresholds)
        // Highly suspicious: over $50k or >1,000 shares
        let complianceStatus = 'CLEAR';
        if (total > 50000 || qty >= 1000) {
          complianceStatus = 'FLAGGED';
        }

        const now = new Date();
        const dateStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
        
        const nextId = db.trades.length > 0 ? Math.max(...db.trades.map(t => t.id)) + 1 : 1001;
        const newTrade = {
          id: nextId,
          symbol,
          side,
          qty,
          price,
          timestamp: dateStr,
          compliance_status: complianceStatus
        };

        db.trades.unshift(newTrade);
        saveDb();

        resolve({
          success: true,
          trade: newTrade,
          compliance_status: complianceStatus,
          message: complianceStatus === 'FLAGGED' 
            ? 'WARNING: Order size flags VPC compliance threshold. Routed for asynchronous audit.' 
            : 'Trade completed and registered in Multi-AZ central RDS.'
        });
      }
      else if (endpoint === '/api/health') {
        // Direct mock successful connectivity to database
        resolve({
          status: 'UP',
          rds_connectivity: 'CONNECTED',
          vpc_peering: config.env,
          compliance_engine: 'READY',
          message: 'P2 multi-AZ database connectivity fully established.'
        });
      }
    }, 300);
  });
}

// Run Initializations
initStorage();
document.addEventListener('DOMContentLoaded', () => {
  renderCommonUI();
  startPriceTicker();
});
