import os
from datetime import datetime
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.ela_service import generate_ela
from app.exif_service import extract_exif
from app.models import Analysis, ReviewCase, ReviewEvent, User
from app.noise_service import generate_noise
from app.review_policy import REVIEW_SCORE_THRESHOLD, assess_review_route

router = APIRouter()

VERDICTS = {
    "authenticity_supported": "Authenticity supported by the available evidence",
    "manipulation_supported": "Manipulation supported by the available evidence",
    "inconclusive": "Inconclusive — further investigation required",
}


class InvestigationRequest(BaseModel):
    reviewer_user_id: int
    concern: Literal[
        "possible_splicing",
        "inconsistent_lighting",
        "face_manipulation",
        "image_metadata",
    ]
    reason: str
    face_index: int | None = None


class VerdictRequest(BaseModel):
    reviewer_user_id: int
    verdict: Literal[
        "authenticity_supported",
        "manipulation_supported",
        "inconclusive",
    ]
    reason: str


class HighImpactRequest(BaseModel):
    reviewer_user_id: int
    reason: str


def create_review_case(
    db: Session,
    analysis: Analysis,
    report: dict,
    high_impact: bool = False,
) -> ReviewCase:
    routing = assess_review_route(report, high_impact=high_impact)
    review_case = ReviewCase(
        analysis_id=analysis.id,
        user_id=analysis.user_id,
        status=routing["status"],
        required_review=routing["required_review"],
        high_impact=high_impact,
        routing_reasons=routing["routing_reasons"],
    )
    db.add(review_case)
    db.flush()

    db.add(
        ReviewEvent(
            review_case_id=review_case.id,
            action=(
                "legacy_review_case_created"
                if report.get("legacy_record")
                else "analysis_completed"
            ),
            evidence={
                "analysis_id": analysis.id,
                "filename": analysis.filename,
                "sha256": analysis.sha256,
                "prediction": analysis.prediction,
                "confidence": analysis.confidence,
                "probabilities": report.get("probabilities", {}),
                "risk_level": report.get("risk_level"),
                "face_results": report.get("face_results", []),
                "exif": report.get("exif", {}),
                "artifacts": {
                    "image": report.get("image_path"),
                    "ela": report.get("ela"),
                    "noise": report.get("noise"),
                    "gradcam": report.get("gradcam"),
                    "marked_gradcam": report.get("marked_gradcam"),
                },
                "routing": routing,
                "limitations": [
                    "Model scores are not calibrated authenticity probabilities.",
                    "Grad-CAM shows model attention, not confirmed manipulated pixels.",
                    "An AI prediction is not a human-verified forensic conclusion.",
                ],
                "legacy_record": bool(report.get("legacy_record")),
            },
        )
    )
    return review_case


def _get_owned_review(
    db: Session, analysis_id: int, reviewer_user_id: int
) -> tuple[Analysis, ReviewCase, User]:
    reviewer = db.query(User).filter(User.id == reviewer_user_id).first()
    if not reviewer:
        raise HTTPException(status_code=401, detail="Reviewer account not found.")

    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    if analysis.user_id != reviewer.id:
        raise HTTPException(
            status_code=403,
            detail="Only the account that created this analysis can review it.",
        )

    review_case = (
        db.query(ReviewCase)
        .filter(ReviewCase.analysis_id == analysis.id)
        .first()
    )
    if not review_case:
        legacy_report = {
            "prediction": analysis.prediction,
            "confidence": analysis.confidence,
            "probabilities": {
                "real": analysis.real_prob or 0,
                "fake": analysis.fake_prob or 0,
            },
            "face_results": [],
            "legacy_record": True,
        }
        review_case = create_review_case(db, analysis, legacy_report)
        db.commit()
        db.refresh(review_case)

    return analysis, review_case, reviewer


def _review_payload(
    db: Session, analysis: Analysis, review_case: ReviewCase
) -> dict:
    events = (
        db.query(ReviewEvent)
        .filter(ReviewEvent.review_case_id == review_case.id)
        .order_by(ReviewEvent.created_at.asc(), ReviewEvent.id.asc())
        .all()
    )
    actor_ids = {event.actor_user_id for event in events if event.actor_user_id}
    actors = (
        {
            user.id: user.username
            for user in db.query(User).filter(User.id.in_(actor_ids)).all()
        }
        if actor_ids
        else {}
    )

    return {
        "analysis_id": analysis.id,
        "status": review_case.status,
        "required_review": review_case.required_review,
        "high_impact": review_case.high_impact,
        "routing_reasons": review_case.routing_reasons or [],
        "ai_prediction": analysis.prediction,
        "ai_confidence": analysis.confidence,
        "ai_probabilities": {
            "real": analysis.real_prob,
            "fake": analysis.fake_prob,
        },
        "human_verdict": (
            {
                "value": review_case.verdict,
                "label": VERDICTS.get(review_case.verdict, review_case.verdict),
                "reason": review_case.verdict_reason,
                "reviewer_user_id": review_case.decided_by_user_id,
                "reviewer": actors.get(review_case.decided_by_user_id),
                "decided_at": review_case.decided_at,
            }
            if review_case.verdict
            else None
        ),
        "events": [
            {
                "id": event.id,
                "action": event.action,
                "concern": event.concern,
                "reason": event.reason,
                "actor_user_id": event.actor_user_id,
                "actor": actors.get(event.actor_user_id, "System"),
                "evidence": event.evidence,
                "created_at": event.created_at,
            }
            for event in events
        ],
        "score_policy": {
            "threshold": REVIEW_SCORE_THRESHOLD,
            "calibrated": False,
            "note": (
                "Routing uses a conservative model-score heuristic, not a "
                "calibrated probability of authenticity."
            ),
        },
    }


def _require_reason(reason: str) -> str:
    cleaned = reason.strip()
    if len(cleaned) < 10:
        raise HTTPException(
            status_code=422,
            detail="Please provide a reason of at least 10 characters.",
        )
    if len(cleaned) > 2000:
        raise HTTPException(
            status_code=422,
            detail="Reason must be 2000 characters or fewer.",
        )
    return cleaned


def _clear_current_verdict(review_case: ReviewCase) -> None:
    review_case.verdict = None
    review_case.verdict_reason = None
    review_case.decided_by_user_id = None
    review_case.decided_at = None


def _initial_evidence(db: Session, review_case_id: int) -> dict:
    event = (
        db.query(ReviewEvent)
        .filter(
            ReviewEvent.review_case_id == review_case_id,
            ReviewEvent.action.in_(
                ("analysis_completed", "legacy_review_case_created")
            ),
        )
        .first()
    )
    if not event:
        raise HTTPException(
            status_code=500,
            detail="The original analysis evidence is missing from the review record.",
        )
    return event.evidence


def _source_image_path(image_path: str) -> str:
    upload_directory = os.path.abspath(os.path.join("app", "static", "uploads"))
    source_path = os.path.abspath(image_path)
    if os.path.commonpath([upload_directory, source_path]) != upload_directory:
        raise HTTPException(status_code=422, detail="Stored image path is invalid.")
    if not os.path.isfile(source_path):
        raise HTTPException(
            status_code=410,
            detail="The original uploaded image is no longer available for review.",
        )
    return source_path


def _public_path(path: str | None) -> str | None:
    if not path:
        return None
    return path.replace("app/", "/", 1).replace("\\", "/")


@router.get("/reviews/{analysis_id}")
def get_review_case(
    analysis_id: int,
    reviewer_user_id: int = Query(..., gt=0),
    db: Session = Depends(get_db),
):
    analysis, review_case, _ = _get_owned_review(db, analysis_id, reviewer_user_id)
    return _review_payload(db, analysis, review_case)


@router.post("/reviews/{analysis_id}/investigate")
def investigate_review_case(
    analysis_id: int,
    request: InvestigationRequest,
    db: Session = Depends(get_db),
):
    analysis, review_case, reviewer = _get_owned_review(
        db, analysis_id, request.reviewer_user_id
    )
    reason = _require_reason(request.reason)
    original = _initial_evidence(db, review_case.id)
    evidence = {}

    if request.concern == "possible_splicing":
        source_path = _source_image_path(analysis.image_path)
        image_bytes = Path(source_path).read_bytes()
        evidence = {
            "ela": _public_path(generate_ela(image_bytes)),
            "noise": _public_path(generate_noise(image_bytes)),
            "interpretation": (
                "ELA and noise visualizations were generated for reviewer inspection. "
                "They do not independently establish splicing."
            ),
        }
    elif request.concern == "inconsistent_lighting":
        source_path = _source_image_path(analysis.image_path)
        image_bytes = Path(source_path).read_bytes()
        face_results = original.get("face_results", [])
        if request.face_index is not None:
            face_results = [
                face
                for face in face_results
                if face.get("face_index") == request.face_index
            ]
            if not face_results:
                raise HTTPException(
                    status_code=422,
                    detail="The selected face is not part of this analysis.",
                )
        evidence = {
            "noise": _public_path(generate_noise(image_bytes)),
            "face_quality": [
                {
                    "face_index": face.get("face_index"),
                    "quality": face.get("quality", {}),
                }
                for face in face_results
            ],
            "interpretation": (
                "Noise visualization and recorded face-quality observations are "
                "provided for inspection; lighting consistency is not automatically "
                "confirmed by these indicators."
            ),
        }
    elif request.concern == "face_manipulation":
        face_results = original.get("face_results", [])
        if request.face_index is not None:
            face_results = [
                face
                for face in face_results
                if face.get("face_index") == request.face_index
            ]
            if not face_results:
                raise HTTPException(
                    status_code=422,
                    detail="The selected face is not part of this analysis.",
                )
        evidence = {
            "faces": [
                {
                    "face_index": face.get("face_index"),
                    "prediction": face.get("prediction"),
                    "gradcam": face.get("gradcam"),
                    "marked_gradcam": face.get("marked_gradcam"),
                    "attention_regions": face.get("attention_regions", []),
                }
                for face in face_results
            ],
            "interpretation": (
                "Existing Grad-CAM attention evidence is shown for review. "
                "Attention regions are not confirmed manipulation locations."
            ),
        }
    elif request.concern == "image_metadata":
        source_path = _source_image_path(analysis.image_path)
        evidence = {"exif": extract_exif(Path(source_path).read_bytes())}

    review_case.status = "investigating"
    _clear_current_verdict(review_case)
    db.add(
        ReviewEvent(
            review_case_id=review_case.id,
            actor_user_id=reviewer.id,
            action="investigation_requested",
            concern=request.concern,
            reason=reason,
            evidence=evidence,
        )
    )
    db.commit()
    db.refresh(review_case)
    return _review_payload(db, analysis, review_case)


@router.post("/reviews/{analysis_id}/verdict")
def record_human_verdict(
    analysis_id: int,
    request: VerdictRequest,
    db: Session = Depends(get_db),
):
    analysis, review_case, reviewer = _get_owned_review(
        db, analysis_id, request.reviewer_user_id
    )
    reason = _require_reason(request.reason)
    considered_event_ids = [
        event_id
        for (event_id,) in db.query(ReviewEvent.id)
        .filter(ReviewEvent.review_case_id == review_case.id)
        .order_by(ReviewEvent.id.asc())
        .all()
    ]

    review_case.status = "concluded"
    review_case.verdict = request.verdict
    review_case.verdict_reason = reason
    review_case.decided_by_user_id = reviewer.id
    review_case.decided_at = datetime.utcnow()
    db.add(
        ReviewEvent(
            review_case_id=review_case.id,
            actor_user_id=reviewer.id,
            action="human_verdict_recorded",
            reason=reason,
            evidence={
                "verdict": request.verdict,
                "label": VERDICTS[request.verdict],
                "ai_prediction_at_decision": analysis.prediction,
                "ai_confidence_at_decision": analysis.confidence,
                "ai_probabilities_at_decision": {
                    "real": analysis.real_prob,
                    "fake": analysis.fake_prob,
                },
                "analysis_sha256": analysis.sha256,
                "considered_evidence_event_ids": considered_event_ids,
            },
        )
    )
    db.commit()
    db.refresh(review_case)
    return _review_payload(db, analysis, review_case)


@router.post("/reviews/{analysis_id}/high-impact")
def mark_review_high_impact(
    analysis_id: int,
    request: HighImpactRequest,
    db: Session = Depends(get_db),
):
    analysis, review_case, reviewer = _get_owned_review(
        db, analysis_id, request.reviewer_user_id
    )
    reason = _require_reason(request.reason)
    review_case.high_impact = True
    review_case.required_review = True
    review_case.status = "needs_review"
    _clear_current_verdict(review_case)
    existing_reasons = review_case.routing_reasons or []
    impact_reason = "This case was marked high-impact and requires human review."
    if impact_reason not in existing_reasons:
        review_case.routing_reasons = [*existing_reasons, impact_reason]

    db.add(
        ReviewEvent(
            review_case_id=review_case.id,
            actor_user_id=reviewer.id,
            action="high_impact_review_required",
            reason=reason,
            evidence={"high_impact": True, "review_required": True},
        )
    )
    db.commit()
    db.refresh(review_case)
    return _review_payload(db, analysis, review_case)
