from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserRegister, UserLogin, TokenResponse, ProfileUpdate, WalletTransaction
from auth import (
    hash_password, verify_password, create_access_token,
    COOKIE_NAME, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

COOKIE_MAX_AGE = ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: UserRegister, response: Response, db: Session = Depends(get_db)):
    """
    Register a new user. Starts with $100,000 wallet.
    Sets an HttpOnly cookie for browser-based auth.
    """
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        wallet_balance=100_000.00,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})

    # Set HttpOnly cookie for browser clients
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=COOKIE_MAX_AGE,
        path="/",
    )

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        name=user.name,
        wallet_balance=float(user.wallet_balance),
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    """
    Authenticate user and set HttpOnly cookie.
    Also returns the token in the response body for API clients.
    """
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token({"sub": str(user.id)})

    # Set HttpOnly cookie for browser clients
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=COOKIE_MAX_AGE,
        path="/",
    )

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        name=user.name,
        wallet_balance=float(user.wallet_balance),
    )


@router.post("/logout", status_code=200)
def logout(response: Response):
    """Clear the authentication cookie."""
    response.delete_cookie(key=COOKIE_NAME, path="/")
    return {"message": "Logged out successfully"}


@router.get("/me", tags=["Authentication"])
def me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return {
        "user_id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "wallet_balance": float(current_user.wallet_balance),
    }


@router.put("/profile", tags=["Authentication"])
def update_profile(
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update name, email, and/or password.
    """
    if payload.email and payload.email != current_user.email:
        # Check if email is already taken
        existing = db.query(User).filter(User.email == payload.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        current_user.email = payload.email

    if payload.name:
        current_user.name = payload.name

    if payload.password:
        current_user.password_hash = hash_password(payload.password)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return {
        "message": "Profile updated successfully",
        "name": current_user.name,
        "email": current_user.email,
        "wallet_balance": float(current_user.wallet_balance)
    }


@router.post("/deposit", tags=["Authentication"])
def deposit(
    payload: WalletTransaction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deposit simulated funds.
    """
    from decimal import Decimal
    amount = Decimal(str(payload.amount))
    current_user.wallet_balance += amount
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return {
        "message": f"Deposited ₹{float(amount):,.2f} successfully",
        "wallet_balance": float(current_user.wallet_balance)
    }


@router.post("/withdraw", tags=["Authentication"])
def withdraw(
    payload: WalletTransaction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Withdraw simulated funds.
    """
    from decimal import Decimal
    amount = Decimal(str(payload.amount))
    if current_user.wallet_balance < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient funds for withdrawal. Available: ₹{float(current_user.wallet_balance):,.2f}"
        )
    current_user.wallet_balance -= amount
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return {
        "message": f"Withdrew ₹{float(amount):,.2f} successfully",
        "wallet_balance": float(current_user.wallet_balance)
    }
