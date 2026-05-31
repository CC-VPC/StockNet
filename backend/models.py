from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Numeric, Text,
    ForeignKey, DateTime, CheckConstraint
)
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    wallet_balance = Column(Numeric(15, 2), default=100000.00, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    holdings = relationship("Holding", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    watchlist_items = relationship("WatchlistItem", back_populates="user", cascade="all, delete-orphan")


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    company_name = Column(String(150), nullable=False)
    current_price = Column(Numeric(10, 2), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    holdings = relationship("Holding", back_populates="stock")
    transactions = relationship("Transaction", back_populates="stock")


class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    quantity = Column(Integer, default=0, nullable=False)
    avg_buy_price = Column(Numeric(10, 2), nullable=False)
    realized_pnl = Column(Numeric(15, 2), default=0.00, nullable=False)

    user = relationship("User", back_populates="holdings")
    stock = relationship("Stock", back_populates="holdings")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    type = Column(String(4), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("type IN ('BUY', 'SELL')", name="check_transaction_type"),
    )

    user = relationship("User", back_populates="transactions")
    stock = relationship("Stock", back_populates="transactions")
    risk_log = relationship("RiskLog", back_populates="transaction", uselist=False)


class RiskLog(Base):
    __tablename__ = "risk_logs"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    status = Column(String(20), nullable=False)  # FLAGGED / APPROVED
    reason = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    transaction = relationship("Transaction", back_populates="risk_log")


class WatchlistItem(Base):
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="watchlist_items")
    stock = relationship("Stock")
