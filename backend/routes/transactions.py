from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User, Transaction, Stock, RiskLog
from schemas import TransactionOut
from auth import get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=List[TransactionOut])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0,
):
    """
    Return paginated transaction history for the authenticated user.
    Most recent transactions first. Includes risk/compliance status.
    """
    txns = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    result = []
    for txn in txns:
        stock: Stock = db.query(Stock).filter(Stock.id == txn.stock_id).first()
        risk_log: RiskLog = db.query(RiskLog).filter(RiskLog.transaction_id == txn.id).first()
        result.append(
            TransactionOut(
                id=txn.id,
                stock_id=txn.stock_id,
                symbol=stock.symbol if stock else "UNKNOWN",
                company_name=stock.company_name if stock else "Unknown Company",
                type=txn.type,
                quantity=txn.quantity,
                price=float(txn.price),
                total_value=float(txn.price) * txn.quantity,
                timestamp=txn.timestamp,
                risk_status=risk_log.status if risk_log else None,
            )
        )
    return result
