#!/usr/bin/env python3
"""
StockNet — Database Seed Script
Run this ONCE after first boot to create demo users with proper bcrypt hashes.
The SQL seed creates stocks; this script creates the demo users.

Usage (inside running backend container):
  docker exec stocknet-backend python seed_users.py
"""
import sys
import os

sys.path.insert(0, "/app")

from database import SessionLocal
from models import User
from auth import hash_password

DEMO_USERS = [
    {
        "name": "Demo Trader",
        "email": "demo@stocknet.io",
        "password": "demo1234",
        "wallet_balance": 100_000.00,
    },
    {
        "name": "Admin User",
        "email": "admin@stocknet.io",
        "password": "admin1234",
        "wallet_balance": 500_000.00,
    },
]


def seed():
    db = SessionLocal()
    created = 0
    try:
        for u in DEMO_USERS:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if existing:
                print(f"  ⏭  User already exists: {u['email']}")
                continue
            user = User(
                name=u["name"],
                email=u["email"],
                password_hash=hash_password(u["password"]),
                wallet_balance=u["wallet_balance"],
            )
            db.add(user)
            db.commit()
            print(f"  ✅ Created user: {u['email']} (password: {u['password']})")
            created += 1
    finally:
        db.close()

    print(f"\nDone. {created} user(s) created.")


if __name__ == "__main__":
    print("🌱 Seeding demo users…")
    seed()
