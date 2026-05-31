# StockNet 📈

A simulated stock trading platform built with **FastAPI**, **PostgreSQL**, **Docker Compose**, and a clean browser-based frontend using **HttpOnly cookie authentication**.

> **No real money. No real APIs. Fully self-contained.**

---

## 🚀 Quick Start

```bash
git clone <repo>
cd StockNet
docker compose up --build -d
```

Open **[http://localhost:8000/login](http://localhost:8000/login)** in your browser.

**Demo credentials:**

| Account | Email | Password | Wallet |
|---|---|---|---|
| Demo Trader | `demo@stocknet.io` | `demo1234` | ₹1,00,000 |
| Admin User | `admin@stocknet.io` | `admin1234` | ₹5,00,000 |

API docs: **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## 📁 Folder Structure

```
StockNet/
├── docker-compose.yml          # Orchestrates all 3 services
├── .env.example                # Environment variable template
├── README.md
│
├── backend/                    # FastAPI application
│   ├── Dockerfile
│   ├── main.py                 # App entry point, routers, page routes
│   ├── auth.py                 # JWT + bcrypt + cookie auth utilities
│   ├── database.py             # SQLAlchemy engine & session
│   ├── models.py               # ORM models (User, Stock, Holding, Transaction, RiskLog)
│   ├── schemas.py              # Pydantic request/response models
│   ├── seed_users.py           # Standalone seeder script (optional)
│   ├── requirements.txt
│   │
│   ├── routes/                 # FastAPI routers (all mounted under /api)
│   │   ├── auth.py             # /api/auth/login, /register, /logout, /me
│   │   ├── stocks.py           # /api/stocks
│   │   ├── trades.py           # /api/trades/buy, /sell
│   │   ├── portfolio.py        # /api/portfolio
│   │   └── transactions.py     # /api/transactions
│   │
│   ├── services/               # Business logic layer
│   │   └── trade_service.py    # Buy/sell logic, risk checks, wallet updates
│   │
│   ├── static/                 # Frontend (served as static files + clean URL routes)
│   │   ├── app.css             # Shared design system (dark theme)
│   │   ├── app.js              # Shared API client, navbar, ticker renderer
│   │   ├── login.html          # Served at /login and /register
│   │   ├── index.html          # Served at /dashboard
│   │   ├── portfolio.html      # Served at /portfolio
│   │   ├── trades.html         # Served at /trades
│   │   └── place-trade.html    # Served at /place-trade
│   │
│   └── templates/              # Jinja2 templates (legacy landing page)
│
├── postgres/
│   └── init/
│       ├── 01_schema.sql       # Table definitions (auto-run on first boot)
│       └── 02_seed.sql         # 20 NSE stock seed data
│
└── simulation/                 # Standalone price simulation container
    ├── Dockerfile
    ├── cron_price_update.py    # ±2% random walk every 30 seconds
    └── requirements.txt
```

---

## 🌐 URL Reference

### Frontend Pages (Browser)

| URL | Description |
|---|---|
| `GET /` | Redirects to `/dashboard` |
| `GET /login` | Login page |
| `GET /register` | Register page (same page, tab switches) |
| `GET /dashboard` | Live stock prices + trades feed |
| `GET /portfolio` | Holdings table + P&L + wallet balance |
| `GET /trades` | Full transaction ledger with filters |
| `GET /place-trade` | Execute BUY / SELL orders |

### Backend API (JSON)

All API endpoints are prefixed with `/api`.

#### Authentication — `/api/auth`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/auth/register` | ❌ | Create account — sets HttpOnly cookie |
| `POST` | `/api/auth/login` | ❌ | Login — sets HttpOnly cookie |
| `POST` | `/api/auth/logout` | ✅ | Clear cookie |
| `GET` | `/api/auth/me` | ✅ | Get current user profile |

#### Stocks — `/api/stocks`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/stocks` | ❌ | List all 20 stocks with live prices |
| `GET` | `/api/stocks/{id}` | ❌ | Get single stock detail |

#### Trades — `/api/trades`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/trades/buy` | ✅ | Buy shares (deducts from wallet) |
| `POST` | `/api/trades/sell` | ✅ | Sell shares (credits to wallet) |

#### Portfolio — `/api/portfolio`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/portfolio` | ✅ | Holdings + P&L + wallet balance |

#### Transactions — `/api/transactions`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/transactions` | ✅ | Paginated trade history with risk status |

#### System

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/health` | ❌ | Service health check |
| `GET` | `/docs` | ❌ | Swagger UI (Bearer token auth) |

---

## 🔄 Data Flow

```
Browser                     FastAPI Backend              PostgreSQL
  │                               │                           │
  │── POST /api/auth/login ──────►│                           │
  │                               │── SELECT user by email ──►│
  │                               │◄── user row ──────────────│
  │◄── Set-Cookie: access_token ──│                           │
  │    (HttpOnly, SameSite=Lax)   │                           │
  │                               │                           │
  │── GET /api/stocks ───────────►│                           │
  │   (cookie sent automatically) │── SELECT * FROM stocks ──►│
  │◄── [{ symbol, price, ... }] ──│◄── stock rows ────────────│
  │                               │                           │
  │── POST /api/trades/buy ──────►│                           │
  │   { stock_id, quantity }      │── verify wallet balance ──►│
  │                               │── INSERT transaction ─────►│
  │                               │── UPDATE holdings ────────►│
  │                               │── UPDATE wallet_balance ──►│
  │                               │── INSERT risk_log ────────►│
  │◄── { trade receipt } ─────────│                           │
  │                               │                           │
  │── GET /api/portfolio ────────►│                           │
  │                               │── JOIN holdings+stocks ───►│
  │◄── { holdings, P&L, wallet } ─│◄── computed rows ──────────│
```

### Price Simulation (Separate Container)

```
simulation container
  └── every 30 seconds:
        for each stock:
          new_price = current_price × (1 ± random 0–2%)
          UPDATE stocks SET current_price = new_price, updated_at = NOW()
```

### Risk / Compliance Check (Auto on every trade)

```
trade_service.py
  └── after every BUY or SELL:
        total_value = price × quantity
        if total_value > 10,000:
          status = "FLAGGED"
        else:
          status = "APPROVED"
        INSERT INTO risk_logs (transaction_id, status, reason)
```

---

## 🗄️ Database Schema

```sql
users
  id              SERIAL PRIMARY KEY
  name            VARCHAR(100)
  email           VARCHAR(255) UNIQUE
  password_hash   TEXT
  wallet_balance  NUMERIC(15,2)   DEFAULT 100000.00

stocks
  id              SERIAL PRIMARY KEY
  symbol          VARCHAR(20) UNIQUE
  company_name    VARCHAR(255)
  current_price   NUMERIC(10,2)
  updated_at      TIMESTAMP

holdings
  id              SERIAL PRIMARY KEY
  user_id         INT   → users(id)
  stock_id        INT   → stocks(id)
  quantity        INT
  avg_buy_price   NUMERIC(10,2)
  UNIQUE(user_id, stock_id)

transactions
  id              SERIAL PRIMARY KEY
  user_id         INT   → users(id)
  stock_id        INT   → stocks(id)
  type            VARCHAR(4)    -- 'BUY' | 'SELL'
  quantity        INT
  price           NUMERIC(10,2)
  timestamp       TIMESTAMP

risk_logs
  id              SERIAL PRIMARY KEY
  transaction_id  INT   → transactions(id)
  status          VARCHAR(20)   -- 'APPROVED' | 'FLAGGED'
  reason          TEXT
  timestamp       TIMESTAMP
```

Schema auto-created from `postgres/init/01_schema.sql`.  
20 NSE stocks seeded from `postgres/init/02_seed.sql`.  
Demo users seeded in Python on first boot (via `main.py` lifespan).

---

## 🐳 Docker Services

| Service | Container | Port | Notes |
|---|---|---|---|
| PostgreSQL 15 | `stocknet-postgres` | `5432` | Data persisted in Docker volume |
| FastAPI | `stocknet-backend` | `8000` | API + static frontend |
| Simulation | `stocknet-simulation` | — | Price updater, no exposed port |

```bash
# Start all services
docker compose up -d

# Rebuild after code changes
docker compose up --build -d

# View backend logs
docker logs stocknet-backend -f

# Connect to database
docker exec -it stocknet-postgres psql -U stocknet -d stocknetdb

# Stop all
docker compose down

# Stop and wipe database volume
docker compose down -v
```

---

## 🔐 Authentication

StockNet uses **stateless JWT tokens** stored in **HttpOnly cookies**.

| Property | Value |
|---|---|
| Cookie name | `access_token` |
| HttpOnly | ✅ (not accessible via JavaScript) |
| SameSite | `Lax` |
| Expiry | 24 hours |
| Algorithm | `HS256` |

- **Browser frontend**: Cookie is set automatically on login/register, sent on every request, cleared on logout.
- **Swagger UI / API clients**: Use `Authorization: Bearer <token>` header — the backend accepts both.

---

## 📦 Stocks Included (20 NSE)

`TCS · RELIANCE · HDFCBANK · INFY · ICICIBANK · WIPRO · BAJFINANCE · MARUTI · TITAN · KOTAKBANK · HINDUNILVR · ASIANPAINT · NTPC · ONGC · POWERGRID · JSWSTEEL · TATAMOTORS · SUNPHARMA · ULTRACEMCO · NESTLEIND`
