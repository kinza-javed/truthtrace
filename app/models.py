from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    is_verified = Column(Boolean, default=False)


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)

    filename = Column(String)
    image_path = Column(String)
    sha256 = Column(String)

    prediction = Column(String)
    confidence = Column(Float)

    real_prob = Column(Float)
    fake_prob = Column(Float)

    report_path = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)


class ReviewCase(Base):
    __tablename__ = "review_cases"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(
        Integer, ForeignKey("analyses.id"), nullable=False, unique=True, index=True
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    status = Column(String, nullable=False, default="provisional")
    required_review = Column(Boolean, nullable=False, default=False)
    high_impact = Column(Boolean, nullable=False, default=False)
    routing_reasons = Column(JSON, nullable=False, default=list)

    verdict = Column(String, nullable=True)
    verdict_reason = Column(Text, nullable=True)
    decided_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    decided_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class ReviewEvent(Base):
    __tablename__ = "review_events"

    id = Column(Integer, primary_key=True, index=True)
    review_case_id = Column(
        Integer, ForeignKey("review_cases.id"), nullable=False, index=True
    )
    actor_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    concern = Column(String, nullable=True)
    reason = Column(Text, nullable=True)
    evidence = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    token_hash = Column(String, nullable=False)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    token_hash = Column(String, nullable=False)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)