-- ============================================================
-- StockNet — PostgreSQL Schema
-- File: 01_schema.sql
-- Executed automatically on first postgres container boot.
-- ============================================================

-- Drop tables if they exist (for clean re-init)
DROP TABLE IF EXISTS risk_logs CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS holdings CASCADE;
DROP TABLE IF EXISTS stocks CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ─── users ────────────────────────────────────────────────────
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100)    NOT NULL,
    email           VARCHAR(150)    NOT NULL UNIQUE,
    password_hash   TEXT            NOT NULL,
    wallet_balance  NUMERIC(15,2)   NOT NULL DEFAULT 100000.00,
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

-- ─── stocks ───────────────────────────────────────────────────
CREATE TABLE stocks (
    id              SERIAL PRIMARY KEY,
    symbol          VARCHAR(10)     NOT NULL UNIQUE,
    company_name    VARCHAR(150)    NOT NULL,
    current_price   NUMERIC(10,2)   NOT NULL,
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_stocks_symbol ON stocks(symbol);

-- ─── holdings ─────────────────────────────────────────────────
CREATE TABLE holdings (
    id              SERIAL PRIMARY KEY,
    user_id         INT             NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stock_id        INT             NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    quantity        INT             NOT NULL DEFAULT 0,
    avg_buy_price   NUMERIC(10,2)   NOT NULL,
    UNIQUE(user_id, stock_id)
);

CREATE INDEX idx_holdings_user ON holdings(user_id);

-- ─── transactions ─────────────────────────────────────────────
CREATE TABLE transactions (
    id              SERIAL PRIMARY KEY,
    user_id         INT             NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stock_id        INT             NOT NULL REFERENCES stocks(id),
    type            VARCHAR(4)      NOT NULL CHECK (type IN ('BUY', 'SELL')),
    quantity        INT             NOT NULL,
    price           NUMERIC(10,2)   NOT NULL,
    timestamp       TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_transactions_user ON transactions(user_id);
CREATE INDEX idx_transactions_timestamp ON transactions(timestamp DESC);

-- ─── risk_logs ────────────────────────────────────────────────
CREATE TABLE risk_logs (
    id              SERIAL PRIMARY KEY,
    transaction_id  INT             NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    status          VARCHAR(20)     NOT NULL,   -- APPROVED | FLAGGED
    reason          TEXT,
    timestamp       TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_risk_logs_transaction ON risk_logs(transaction_id);
CREATE INDEX idx_risk_logs_status ON risk_logs(status);
