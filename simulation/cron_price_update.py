"""
StockNet — Price Simulation Service
Runs as a standalone container.
Every 30 seconds: price *= random.uniform(0.98, 1.02)
This keeps price movement realistic (±2% per tick).
"""
import os
import time
import random
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# ─── Config ──────────────────────────────────────────────────────────────────
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "stocknetdb")
DB_USER = os.getenv("DB_USER", "stocknet")
DB_PASS = os.getenv("DB_PASS", "stocknet123")
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL_SECONDS", "30"))

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("price-simulator")


def get_connection():
    """Create a fresh psycopg2 connection."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
    )


def wait_for_db(retries: int = 15, delay: float = 3.0):
    """Wait for PostgreSQL to be available."""
    for attempt in range(1, retries + 1):
        try:
            conn = get_connection()
            conn.close()
            logger.info("✅ Connected to PostgreSQL.")
            return
        except psycopg2.OperationalError:
            logger.warning(f"DB not ready (attempt {attempt}/{retries}). Retrying in {delay}s…")
            time.sleep(delay)
    raise RuntimeError("Could not connect to database after multiple retries.")


def update_prices(conn):
    """
    Apply a ±2% random walk to every stock's current_price.
    Each stock moves independently.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id, symbol, current_price FROM stocks")
        stocks = cur.fetchall()

        updates = []
        for stock in stocks:
            factor = random.uniform(0.98, 1.02)
            new_price = round(float(stock["current_price"]) * factor, 2)
            # Ensure price never goes below $0.01
            new_price = max(new_price, 0.01)
            updates.append((new_price, datetime.utcnow(), stock["id"]))
            logger.debug(
                f"  {stock['symbol']:12s}  "
                f"${float(stock['current_price']):>10.2f}  →  ${new_price:>10.2f}  "
                f"(factor: {factor:.4f})"
            )

        cur.executemany(
            "UPDATE stocks SET current_price = %s, updated_at = %s WHERE id = %s",
            updates,
        )
        conn.commit()

    logger.info(f"📈 Updated prices for {len(stocks)} stocks.")


def main():
    logger.info("🚀 StockNet Price Simulation Service starting…")
    logger.info(f"   Interval: {UPDATE_INTERVAL}s | DB: {DB_HOST}:{DB_PORT}/{DB_NAME}")

    wait_for_db()

    conn = None
    while True:
        try:
            if conn is None or conn.closed:
                conn = get_connection()

            update_prices(conn)
            time.sleep(UPDATE_INTERVAL)

        except psycopg2.OperationalError as e:
            logger.error(f"DB connection lost: {e}. Reconnecting…")
            if conn and not conn.closed:
                conn.close()
            conn = None
            time.sleep(5)

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(UPDATE_INTERVAL)


if __name__ == "__main__":
    main()
