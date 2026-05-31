# StockNet — Public Trading Dashboard (P1 Web Tier)

This is the front-facing trading dashboard for **StockNet** (Static HTML + Vanilla JS + plain CSS) designed to run on the `stock-p1-web-ec2-1` web instance.

---

## 🚀 Key Features

*   **Dual-Mode Client**: Configurable Settings Drawer toggles between **Local Demo** (LocalStorage state) and **Live API** routing to App Tier IP `http://10.0.1.10:5000`.
*   **Simulated Price Drift**: Real-time stock prices drift within **±2%** every 4 seconds, bounded safely within 15% of initial seed values.
*   **VPC Peering Topology**: An animated, glowing SVG diagram illustrating P1 Hub connections to P2 RDS DB, P3 Staging environments, and P4 Compliance Lambdas over `pcx` private tunnels.
*   **Page Modules**:
    *   `index.html`: Stock ticker, market overview cards, last 10 trades feed, and `/api/health` check diagnostics.
    *   `portfolio.html`: Wealth overview and spaced list table calculating P&L returns in real-time.
    *   `trades.html`: Paginated transaction list (20 rows) with symbol search and buy/sell/compliance filters.
    *   `place-trade.html`: Buy/Sell picker with live invoice calculator and risk flagging warnings (> $50,000 / 1,000 shares) coordinated with P4 stream.

---

## 📡 Flask App Tier Endpoints (Port 5000)

Requests map to `stock-p1-app-ec2-1` inside the private VPC subnet:

*   **`GET /api/stocks`**: Retrieves current price, daily returns, and trading volumes.
*   **`GET /api/portfolio`**: Pulls wallet cash balance and active stock positions from database.
*   **`GET /api/trades`**: Retreives unified peer-connected trade records history.
*   **`POST /api/trade`**: Validates and submits order details (`symbol`, `side`, `qty`). Triggers P4 compliance checking.
*   **`GET /api/health`**: Conducts central RDS PostgreSQL database and compliance engine connection check.

---

## 📂 Deploy Coordinates

*   **Nginx Root Path on EC2**: `/var/www/html/`
*   **Local Run**: Simply open `index.html` in the browser and enable **Local Demo** mode.
