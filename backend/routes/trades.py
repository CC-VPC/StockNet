from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import BuyRequest, SellRequest, TradeResponse
from auth import get_current_user
from services import trade_service

router = APIRouter(prefix="/trades", tags=["Trades"])


@router.post("/buy", response_model=TradeResponse)
def buy(
    payload: BuyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Buy shares of a stock.
    - Deducts cost from wallet balance
    - Creates/updates holding with weighted average buy price
    - Records transaction
    - Runs risk compliance check
    """
    return trade_service.buy_stock(db, current_user, payload.stock_id, payload.quantity)


@router.post("/sell", response_model=TradeResponse)
def sell(
    payload: SellRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Sell shares of a stock.
    - Validates user owns sufficient shares
    - Credits proceeds to wallet balance
    - Updates/removes holding
    - Records transaction
    - Runs risk compliance check
    """
    return trade_service.sell_stock(db, current_user, payload.stock_id, payload.quantity)
