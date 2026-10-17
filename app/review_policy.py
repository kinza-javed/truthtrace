REVIEW_SCORE_THRESHOLD = 0.75


def assess_review_route(report: dict, high_impact: bool = False) -> dict:
    probabilities = report.get("probabilities") or {}
    model_score = max(
        float(probabilities.get("real", 0)),
        float(probabilities.get("fake", 0)),
    )
    reasons = []

    if model_score < REVIEW_SCORE_THRESHOLD:
        reasons.append(
            "The highest model score is below the review threshold "
            f"({model_score:.3f} < {REVIEW_SCORE_THRESHOLD:.2f}); this score is "
            "not a calibrated probability."
        )

    face_predictions = {
        face.get("prediction")
        for face in report.get("face_results", [])
        if face.get("prediction")
    }
    if len(face_predictions) > 1:
        reasons.append(
            "Different detected faces received conflicting model predictions."
        )

    if high_impact:
        reasons.append("This case was marked high-impact and requires human review.")

    required = bool(reasons)
    return {
        "status": "needs_review" if required else "provisional",
        "required_review": required,
        "high_impact": high_impact,
        "model_score": model_score,
        "score_threshold": REVIEW_SCORE_THRESHOLD,
        "score_is_calibrated": False,
        "routing_reasons": reasons,
    }
