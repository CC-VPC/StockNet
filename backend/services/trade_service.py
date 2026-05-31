"""
Trade Service — handles core buy/sell business logic:
  - Wallet validation
  - Stock lookup
  - Holding creation/update
  - Transaction recording
  - Risk evaluation
"""
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models import User, Stock, Holding, Transaction
from services import risk_service


def buy_stock(db: Session, user: User, stock_id: int, quantity: int) -> dict:
    """
    Execute a BUY order:
      1. Fetch stock, validate it exists
      2. Check user has sufficient wallet balance
      3. Deduct wallet
      4. Update or create holding (recalculate avg_buy_price)
      5. Insert transaction record
      6. Run risk check
    """
    # 1. Fetch stock
    stock: Stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    total_cost = Decimal(str(stock.current_price)) * quantity

    # 2. Wallet check
    if user.wallet_balance < total_cost:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Insufficient funds. Required: ${total_cost:,.2f}, "
                f"Available: ${user.wallet_balance:,.2f}"
            ),
        )

    # 3. Deduct wallet
    user.wallet_balance -= total_cost
    db.add(user)

    # 4. Update or create holding
    holding: Holding = (
        db.query(Holding)
        .filter(Holding.user_id == user.id, Holding.stock_id == stock_id)
        .first()
    )
    if holding:
        # Recalculate weighted average buy price
        old_total = Decimal(str(holding.avg_buy_price)) * holding.quantity
        new_total = Decimal(str(stock.current_price)) * quantity
        holding.quantity += quantity
        holding.avg_buy_price = (old_total + new_total) / holding.quantity
        db.add(holding)
    else:
        holding = Holding(
            user_id=user.id,
            stock_id=stock_id,
            quantity=quantity,
            avg_buy_price=stock.current_price,
        )
        db.add(holding)

    # 5. Record transaction
    txn = Transaction(
        user_id=user.id,
        stock_id=stock_id,
        type="BUY",
        quantity=quantity,
        price=stock.current_price,
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    db.refresh(user)

    # 6. Risk check
    risk_status = risk_service.evaluate_trade(
        db, txn.id, float(total_cost)
    )

    return {
        "message": "Stock purchased successfully",
        "transaction_id": txn.id,
        "type": "BUY",
        "quantity": quantity,
        "price": float(stock.current_price),
        "total_value": float(total_cost),
        "wallet_balance": float(user.wallet_balance),
        "risk_status": risk_status,
    }


def sell_stock(db: Session, user: User, stock_id: int, quantity: int) -> dict:
    """
    Execute a SELL order:
      1. Fetch stock, validate it exists
      2. Verify user holds enough shares
      3. Credit wallet
      4. Update or remove holding
      5. Insert transaction record
      6. Run risk check
    """
    # 1. Fetch stock
    stock: Stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    # 2. Holding check
    holding: Holding = (
        db.query(Holding)
        .filter(Holding.user_id == user.id, Holding.stock_id == stock_id)
        .first()
    )
    if not holding or holding.quantity < quantity:
        owned = holding.quantity if holding else 0
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient shares. Requested: {quantity}, Owned: {owned}",
        )

    total_proceeds = Decimal(str(stock.current_price)) * quantity

    # 3. Credit wallet
    user.wallet_balance += total_proceeds
    db.add(user)

    # 4. Update holding
    holding.quantity -= quantity
    if holding.quantity == 0:
        db.delete(holding)
    else:
        db.add(holding)

    # 5. Record transaction
    txn = Transaction(
        user_id=user.id,
        stock_id=stock_id,
        type="SELL",
        quantity=quantity,
        price=stock.current_price,
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    db.refresh(user)

    # 6. Risk check
    risk_status = risk_service.evaluate_trade(
        db, txn.id, float(total_proceeds)
    )

    return {
        "message": "Stock sold successfully",
        "transaction_id": txn.id,
        "type": "SELL",
        "quantity": quantity,
        "price": float(stock.current_price),
        "total_value": float(total_proceeds),
        "wallet_balance": float(user.wallet_balance),
        "risk_status": risk_status,
    }
