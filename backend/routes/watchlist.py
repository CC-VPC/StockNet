from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User, WatchlistItem, Stock
from schemas import WatchlistToggle, StockOut
from auth import get_current_user

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])


@router.get("", response_model=List[StockOut])
def get_watchlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all stocks in the user's watchlist.
    """
    items = (
        db.query(WatchlistItem)
        .filter(WatchlistItem.user_id == current_user.id)
        .all()
    )
    # Extract stocks
    stocks = [item.stock for item in items]
    return stocks


@router.post("", status_code=status.HTTP_200_OK)
def toggle_watchlist_item(
    payload: WatchlistToggle,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Toggle watch status for a stock.
    If already watched, remove it. If not, add it.
    """
    # Verify stock exists
    stock = db.query(Stock).filter(Stock.id == payload.stock_id).first()
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock not found"
        )

    # Check if already in watchlist
    item = (
        db.query(WatchlistItem)
        .filter(
            WatchlistItem.user_id == current_user.id,
            WatchlistItem.stock_id == payload.stock_id
        )
        .first()
    )

    if item:
        db.delete(item)
        db.commit()
        return {"watched": False, "message": f"Removed {stock.symbol} from watchlist"}
    else:
        new_item = WatchlistItem(
            user_id=current_user.id,
            stock_id=payload.stock_id
        )
        db.add(new_item)
        db.commit()
        return {"watched": True, "message": f"Added {stock.symbol} to watchlist"}
