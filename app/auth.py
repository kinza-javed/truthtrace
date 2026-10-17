import os
import secrets
import hashlib
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.database import get_db
from app.models import User, EmailVerificationToken
from app.schemas import UserCreate, UserLogin
from app.security import hash_password, verify_password, validate_password_strength
from app.email_service import send_verification_email

load_dotenv()

router = APIRouter()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


def hash_token(token: str):
    return hashlib.sha256(token.encode()).hexdigest()


@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    password_error = validate_password_strength(user.password)
    if password_error:
        raise HTTPException(status_code=400, detail=password_error)

    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
        is_verified=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = secrets.token_urlsafe(32)
    token_hash = hash_token(token)

    verification_record = EmailVerificationToken(
        email=user.email,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(minutes=30),
        is_used=False
    )

    db.add(verification_record)
    db.commit()

    verify_link = f"{FRONTEND_URL}/verify-email?token={token}"
    send_verification_email(user.email, verify_link)

    return {
        "message": "Account created successfully. Please check your email to verify your account."
    }


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    token_hash = hash_token(token)

    verification_record = (
        db.query(EmailVerificationToken)
        .filter(
            EmailVerificationToken.token_hash == token_hash,
            EmailVerificationToken.is_used == False
        )
        .first()
    )

    if not verification_record:
        raise HTTPException(status_code=400, detail="Invalid or expired verification link")

    if verification_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Verification link has expired")

    user = db.query(User).filter(User.email == verification_record.email).first()

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    user.is_verified = True
    verification_record.is_used = True

    db.commit()

    return {"message": "Email verified successfully. You can now login."}


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not db_user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Please verify your email before logging in."
        )

    return {
        "message": "Login successful",
        "user": {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email
        }
    }