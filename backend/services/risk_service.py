"""
Risk Service — flags large trades and inserts a risk_log entry.
A trade is flagged if total value > $10,000.
"""
from sqlalchemy.orm import Session
from models import RiskLog

LARGE_TRADE_THRESHOLD = 10_000.00


def evaluate_trade(db: Session, transaction_id: int, total_value: float) -> str:
    """
    Evaluate a completed transaction for risk compliance.
    Returns the risk status: 'APPROVED' or 'FLAGGED'.
    """
    if total_value > LARGE_TRADE_THRESHOLD:
        status = "FLAGGED"
        reason = (
            f"Large trade detected: total value ${total_value:,.2f} "
            f"exceeds threshold ${LARGE_TRADE_THRESHOLD:,.2f}."
        )
    else:
        status = "APPROVED"
        reason = "Trade within normal limits."

    risk_entry = RiskLog(
        transaction_id=transaction_id,
        status=status,
        reason=reason,
    )
    db.add(risk_entry)
    db.commit()
    db.refresh(risk_entry)

    return status
