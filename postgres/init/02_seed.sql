-- ============================================================
-- StockNet — Seed Data
-- File: 02_seed.sql
-- Populates stocks and a demo user.
-- ============================================================

-- ─── Seed Stocks (20 realistic Indian market simulacra) ───────
INSERT INTO stocks (symbol, company_name, current_price) VALUES
    ('RELIANCE',  'Reliance Industries Ltd',          2847.50),
    ('TCS',       'Tata Consultancy Services Ltd',    3924.75),
    ('HDFCBANK',  'HDFC Bank Ltd',                   1672.30),
    ('INFY',      'Infosys Ltd',                     1456.80),
    ('HINDUNILVR','Hindustan Unilever Ltd',           2534.60),
    ('ICICIBANK', 'ICICI Bank Ltd',                   1089.40),
    ('KOTAKBANK', 'Kotak Mahindra Bank Ltd',          1823.55),
    ('WIPRO',     'Wipro Ltd',                         478.90),
    ('BAJFINANCE', 'Bajaj Finance Ltd',               7145.25),
    ('ASIANPAINT','Asian Paints Ltd',                 3267.80),
    ('MARUTI',    'Maruti Suzuki India Ltd',          11234.50),
    ('SUNPHARMA', 'Sun Pharmaceutical Industries',    1167.35),
    ('TITAN',     'Titan Company Ltd',                3489.20),
    ('ULTRACEMCO','UltraTech Cement Ltd',             9867.45),
    ('NESTLEIND', 'Nestle India Ltd',                24567.00),
    ('POWERGRID', 'Power Grid Corporation of India',   267.80),
    ('NTPC',      'NTPC Ltd',                          389.25),
    ('ONGC',      'Oil & Natural Gas Corporation',     287.60),
    ('JSWSTEEL',  'JSW Steel Ltd',                     876.40),
    ('TATAMOTORS','Tata Motors Ltd',                   945.30)
ON CONFLICT (symbol) DO NOTHING;

-- ─── Demo Users ───────────────────────────────────────────────
-- Demo users are created by the backend seed_users.py script
-- which generates proper bcrypt hashes at runtime.
--
-- To seed demo users after first boot, run:
--   docker exec stocknet-backend python seed_users.py
--
-- Credentials:
--   demo@stocknet.io  / demo1234   ($100,000 wallet)
--   admin@stocknet.io / admin1234  ($500,000 wallet)
