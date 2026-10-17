from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Analysis

router = APIRouter()


@router.get("/history/{user_id}")
def get_user_history(user_id: int, db: Session = Depends(get_db)):
    records = (
        db.query(Analysis)
        .filter(Analysis.user_id == user_id)
        .order_by(Analysis.created_at.desc())
        .all()
    )

    return [
        {
            "id": item.id,
            "filename": item.filename,
            "prediction": item.prediction,
            "confidence": item.confidence,
            "real_prob": item.real_prob,
            "fake_prob": item.fake_prob,
            "sha256": item.sha256,
            "report": item.report_path.replace("app/", "/") if item.report_path else None,
            "created_at": item.created_at,
        }
        for item in records
    ]


@router.get("/history/detail/{analysis_id}")
def get_analysis_detail(analysis_id: int, db: Session = Depends(get_db)):
    item = db.query(Analysis).filter(Analysis.id == analysis_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "id": item.id,
        "user_id": item.user_id,
        "filename": item.filename,
        "prediction": item.prediction,
        "confidence": item.confidence,
        "real_prob": item.real_prob,
        "fake_prob": item.fake_prob,
        "sha256": item.sha256,
        "report": item.report_path.replace("app/", "/") if item.report_path else None,
        "created_at": item.created_at,
    }