from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator


# ─── Auth Schemas ────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    wallet_balance: float


# ─── Stock Schemas ────────────────────────────────────────────────────────────

class StockOut(BaseModel):
    id: int
    symbol: str
    company_name: str
    current_price: float
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ─── Trade Schemas ────────────────────────────────────────────────────────────

class BuyRequest(BaseModel):
    stock_id: int
    quantity: int

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be positive")
        return v


class SellRequest(BaseModel):
    stock_id: int
    quantity: int

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be positive")
        return v


class TradeResponse(BaseModel):
    message: str
    transaction_id: int
    type: str
    quantity: int
    price: float
    total_value: float
    wallet_balance: float
    risk_status: str


# ─── Portfolio Schemas ─────────────────────────────────────────────────────────

class HoldingOut(BaseModel):
    id: int
    stock_id: int
    symbol: str
    company_name: str
    quantity: int
    avg_buy_price: float
    current_price: float
    current_value: float
    pnl: float
    pnl_pct: float

    model_config = {"from_attributes": True}


class PortfolioOut(BaseModel):
    user_id: int
    name: str
    wallet_balance: float
    holdings: List[HoldingOut]
    total_invested: float
    total_current_value: float
    total_pnl: float


# ─── Transaction Schemas ───────────────────────────────────────────────────────

class TransactionOut(BaseModel):
    id: int
    stock_id: int
    symbol: str
    company_name: str
    type: str
    quantity: int
    price: float
    total_value: float
    timestamp: datetime
    risk_status: Optional[str] = None

    model_config = {"from_attributes": True}


# ─── Risk Log Schemas ─────────────────────────────────────────────────────────

class RiskLogOut(BaseModel):
    id: int
    transaction_id: int
    status: str
    reason: Optional[str]
    timestamp: datetime

    model_config = {"from_attributes": True}
