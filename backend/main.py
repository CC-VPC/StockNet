"""
StockNet — Simulated Trading Platform
FastAPI application entry point.
"""
import os
import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import OperationalError

from database import engine, SessionLocal
from models import Base, Stock
from routes import auth, stocks, trades, portfolio, transactions, watchlist

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("stocknet")


def wait_for_db(retries: int = 10, delay: float = 3.0):
    """Wait for PostgreSQL to be ready before starting."""
    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                logger.info("✅ Database connection established.")
                return
        except OperationalError:
            logger.warning(f"DB not ready (attempt {attempt}/{retries}). Retrying in {delay}s…")
            time.sleep(delay)
    raise RuntimeError("Could not connect to database after multiple retries.")


# ─── Lifespan ─────────────────────────────────────────────────────────────────
def seed_demo_users():
    """Seed demo users with proper bcrypt hashes on first boot."""
    from models import User
    from auth import hash_password

    DEMO_USERS = [
        {"name": "Demo Trader",  "email": "demo@stocknet.io",  "password": "demo1234",  "wallet_balance": 100_000.00},
        {"name": "Admin User",   "email": "admin@stocknet.io", "password": "admin1234", "wallet_balance": 500_000.00},
    ]

    db = SessionLocal()
    try:
        for u in DEMO_USERS:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if not existing:
                user = User(
                    name=u["name"],
                    email=u["email"],
                    password_hash=hash_password(u["password"]),
                    wallet_balance=u["wallet_balance"],
                )
                db.add(user)
                db.commit()
                logger.info(f"  ✅ Created demo user: {u['email']}")
            else:
                logger.info(f"  ⏭  Demo user exists: {u['email']}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 StockNet starting up…")
    wait_for_db()
    Base.metadata.create_all(bind=engine)
    logger.info("📊 Database tables verified.")
    logger.info("🌱 Seeding demo users…")
    seed_demo_users()
    yield
    logger.info("🛑 StockNet shutting down.")


# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="StockNet API",
    description=(
        "**StockNet** is a simulated stock trading platform.\n\n"
        "### Quick Start\n"
        "1. `POST /api/auth/register` — create your account (starts with ₹1,00,000)\n"
        "2. `POST /api/auth/login` — authenticate and receive a JWT cookie\n"
        "3. Click **Authorize** (top right) and paste your token\n"
        "4. `GET /api/stocks` — browse available stocks\n"
        "5. `POST /api/trades/buy` — buy shares\n"
        "6. `GET /api/portfolio` — view your holdings and P&L\n"
        "7. `POST /api/trades/sell` — sell shares\n"
        "8. `GET /api/transactions` — full trade history\n\n"
        "---\n"
        "Price simulation runs every **30 seconds** automatically.\n\n"
        "**Frontend:** Access the web app at [/login](/login)"
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
# Must list explicit origins when allow_credentials=True (no wildcard allowed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Static Assets ────────────────────────────────────────────────────────────
# Serves CSS, JS, and other assets at /static/*
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# ─── API Routers (all under /api) ─────────────────────────────────────────────
app.include_router(auth.router,         prefix="/api")
app.include_router(stocks.router,       prefix="/api")
app.include_router(trades.router,       prefix="/api")
app.include_router(portfolio.router,    prefix="/api")
app.include_router(transactions.router, prefix="/api")
app.include_router(watchlist.router,    prefix="/api")


# ─── Health Check ─────────────────────────────────────────────────────────────
@app.get("/api/health", tags=["System"])
def health():
    """Service health check."""
    return {"status": "ok", "service": "stocknet-backend"}


# ─── Frontend Page Routes (clean URLs) ────────────────────────────────────────
STATIC_DIR = "static"

def _page(filename: str):
    """Return a FileResponse for a static HTML page."""
    return FileResponse(os.path.join(STATIC_DIR, filename))


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root():
    """Redirect root to dashboard (login guard handled by JS)."""
    return RedirectResponse(url="/dashboard")


@app.get("/login",       response_class=HTMLResponse, include_in_schema=False)
def page_login():        return _page("login.html")

@app.get("/register",    response_class=HTMLResponse, include_in_schema=False)
def page_register():     return _page("login.html")  # same page, tab switches

@app.get("/dashboard",   response_class=HTMLResponse, include_in_schema=False)
def page_dashboard():    return _page("index.html")

@app.get("/portfolio",   response_class=HTMLResponse, include_in_schema=False)
def page_portfolio():    return _page("portfolio.html")

@app.get("/trades",      response_class=HTMLResponse, include_in_schema=False)
def page_trades():       return _page("trades.html")

@app.get("/place-trade", response_class=HTMLResponse, include_in_schema=False)
def page_place_trade():  return _page("place-trade.html")

@app.get("/profile",     response_class=HTMLResponse, include_in_schema=False)
def page_profile():      return _page("profile.html")
