from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Stock
from schemas import StockOut

router = APIRouter(prefix="/stocks", tags=["Stocks"])


@router.get("", response_model=List[StockOut])
def list_stocks(db: Session = Depends(get_db)):
    """
    Return all stocks with their current simulated prices.
    No authentication required — public endpoint.
    """
    stocks = db.query(Stock).order_by(Stock.symbol).all()
    return stocks


@router.get("/{stock_id}", response_model=StockOut)
def get_stock(stock_id: int, db: Session = Depends(get_db)):
    """
    Return details for a single stock by ID.
    """
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock
