import os
import secrets
import hashlib
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.database import get_db
from app.models import User, PasswordResetToken
from app.schemas import ForgotPasswordRequest, ResetPasswordRequest
from app.security import hash_password, validate_password_strength
from app.email_service import send_password_reset_email

load_dotenv()

router = APIRouter()
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


def hash_token(token: str):
    return hashlib.sha256(token.encode()).hexdigest()


@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    generic_response = {
        "message": "If this email exists, a password reset link has been sent."
    }

    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        return generic_response

    token = secrets.token_urlsafe(32)
    token_hash = hash_token(token)

    reset_record = PasswordResetToken(
        email=request.email,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(minutes=15),
        is_used=False
    )

    db.add(reset_record)
    db.commit()

    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"

    send_password_reset_email(request.email, reset_link)

    return generic_response


@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    password_error = validate_password_strength(request.new_password)
    if password_error:
        raise HTTPException(status_code=400, detail=password_error)

    token_hash = hash_token(request.token)

    reset_record = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.is_used == False
        )
        .first()
    )

    if not reset_record:
        raise HTTPException(status_code=400, detail="Invalid or expired reset link")

    if reset_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Reset link has expired")

    user = db.query(User).filter(User.email == reset_record.email).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset request")

    user.password = hash_password(request.new_password)
    reset_record.is_used = True

    db.commit()

    return {"message": "Password reset successfully"}