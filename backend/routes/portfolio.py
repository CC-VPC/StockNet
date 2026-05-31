from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User, Holding, Stock
from schemas import PortfolioOut, HoldingOut
from auth import get_current_user

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


@router.get("", response_model=PortfolioOut)
def get_portfolio(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return the authenticated user's current portfolio:
    - Each holding with quantity, avg buy price, current value, and P&L
    - Total invested, total current value, total P&L
    - Wallet balance
    """
    holdings = (
        db.query(Holding)
        .filter(Holding.user_id == current_user.id)
        .all()
    )

    holding_list = []
    total_invested = Decimal("0")
    total_current_value = Decimal("0")
    total_realized_pnl = Decimal("0")

    for h in holdings:
        stock: Stock = db.query(Stock).filter(Stock.id == h.stock_id).first()
        avg = Decimal(str(h.avg_buy_price))
        price = Decimal(str(stock.current_price))
        qty = h.quantity
        realized = Decimal(str(h.realized_pnl))

        buy_val = avg * qty
        current_val = price * qty
        unrealized = current_val - buy_val
        unrealized_pct = (unrealized / buy_val * 100) if buy_val > 0 else Decimal("0")

        if qty > 0:
            total_invested += buy_val
            total_current_value += current_val
        total_realized_pnl += realized

        pnl = unrealized if qty > 0 else realized
        pnl_pct = unrealized_pct if qty > 0 else Decimal("0")

        holding_list.append(
            HoldingOut(
                id=h.id,
                stock_id=stock.id,
                symbol=stock.symbol,
                company_name=stock.company_name,
                quantity=qty,
                avg_buy_price=float(avg),
                current_price=float(price),
                buy_value=float(buy_val),
                current_value=float(current_val),
                unrealized_pnl=float(unrealized),
                unrealized_pnl_pct=float(unrealized_pct),
                realized_pnl=float(realized),
                pnl=float(pnl),
                pnl_pct=float(pnl_pct),
            )
        )

    total_unrealized_pnl = total_current_value - total_invested
    total_pnl = total_unrealized_pnl + total_realized_pnl

    return PortfolioOut(
        user_id=current_user.id,
        name=current_user.name,
        wallet_balance=float(current_user.wallet_balance),
        holdings=holding_list,
        total_invested=float(total_invested),
        total_current_value=float(total_current_value),
        total_unrealized_pnl=float(total_unrealized_pnl),
        total_realized_pnl=float(total_realized_pnl),
        total_pnl=float(total_pnl),
    )
