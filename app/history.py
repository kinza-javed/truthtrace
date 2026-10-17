from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Analysis, ReviewCase

router = APIRouter()


@router.get("/history/{user_id}")
def get_user_history(user_id: int, db: Session = Depends(get_db)):
    records = (
        db.query(Analysis, ReviewCase)
        .outerjoin(ReviewCase, ReviewCase.analysis_id == Analysis.id)
        .filter(Analysis.user_id == user_id)
        .order_by(Analysis.created_at.desc())
        .all()
    )

    return [
        {
            "id": analysis.id,
            "filename": analysis.filename,
            "prediction": analysis.prediction,
            "confidence": analysis.confidence,
            "real_prob": analysis.real_prob,
            "fake_prob": analysis.fake_prob,
            "sha256": analysis.sha256,
            "report": analysis.report_path.replace("app/", "/")
            if analysis.report_path
            else None,
            "created_at": analysis.created_at,
            "human_review": (
                {
                    "status": review_case.status,
                    "required_review": review_case.required_review,
                    "high_impact": review_case.high_impact,
                    "verdict": review_case.verdict,
                }
                if review_case
                else None
            ),
        }
        for analysis, review_case in records
    ]


@router.get("/history/detail/{analysis_id}")
def get_analysis_detail(analysis_id: int, db: Session = Depends(get_db)):
    item = db.query(Analysis).filter(Analysis.id == analysis_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Analysis not found")

    review_case = (
        db.query(ReviewCase)
        .filter(ReviewCase.analysis_id == item.id)
        .first()
    )

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
        "human_review": (
            {
                "status": review_case.status,
                "required_review": review_case.required_review,
                "high_impact": review_case.high_impact,
                "verdict": review_case.verdict,
            }
            if review_case
            else None
        ),
    }