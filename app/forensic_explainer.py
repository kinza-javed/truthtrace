def _region_sentence(region, prediction):
    label = region.get("label", "face region")
    score = region.get("score", 0)

    if label == "Left Eye Region" or label == "Right Eye Region":
        feature = "eye region"
        reason = "eye alignment, reflections, eyelid texture, and local facial consistency"
    elif label == "Nose Bridge Region":
        feature = "nose bridge"
        reason = "central facial alignment and texture continuity"
    elif label == "Mouth and Lip Region":
        feature = "mouth and lip region"
        reason = "lip boundary, expression shape, and lower-face texture consistency"
    elif label == "Jawline Boundary":
        feature = "jawline boundary"
        reason = "face-edge continuity and blending consistency"
    elif label == "Left Cheek Texture" or label == "Right Cheek Texture":
        feature = "cheek texture region"
        reason = "skin texture smoothness and pixel-level consistency"
    elif label == "Forehead and Hairline":
        feature = "forehead and hairline"
        reason = "hairline boundary and upper-face texture consistency"
    else:
        feature = label
        reason = "localized facial evidence"

    if prediction == "FAKE":
        return (
            f"The model used the {feature} as an evidence region "
            f"({score}% attention). This region contributed to the fake classification because it relates to {reason}."
        )

    return (
        f"The model used the {feature} as an authenticity-supporting region "
        f"({score}% attention). This region contributed to the real classification because it shows usable evidence for {reason}."
    )


def generate_forensic_explanation(face, result, attention_regions=None):
    prediction = result["prediction"]
    real_prob = result["probabilities"]["real"]
    fake_prob = result["probabilities"]["fake"]

    quality = face.get("quality", {})
    brightness = quality.get("brightness", 0)
    blur_score = quality.get("blur_score", 0)
    warnings = quality.get("warnings", [])

    valid_regions = [
        r for r in (attention_regions or [])
        if r.get("bbox") is not None and r.get("score", 0) > 0
    ]

    explanation = {
        "verdict_summary": "",
        "authenticity_indicators": [],
        "manipulation_indicators": [],
        "quality_observations": [],
        "recommendation": "",
    }

    if prediction == "REAL":
        explanation["verdict_summary"] = (
            f"The selected face is classified as REAL with {real_prob * 100:.2f}% real probability. "
            "The explanation is based only on detected face-landmark regions, not background areas."
        )

        if valid_regions:
            for region in valid_regions[:3]:
                explanation["authenticity_indicators"].append(
                    _region_sentence(region, prediction)
                )
        else:
            explanation["authenticity_indicators"].append(
                "No high-attention facial landmark region crossed the marking threshold; the real classification is based on distributed facial evidence."
            )

        explanation["authenticity_indicators"].append(
            "No strong face-boundary manipulation evidence crossed the landmark attention threshold."
        )

        explanation["recommendation"] = (
            "Treat this result as authenticity-supporting evidence. For high-stakes cases, confirm with source verification and metadata review."
        )

    else:
        explanation["verdict_summary"] = (
            f"The selected face is classified as FAKE with {fake_prob * 100:.2f}% fake probability. "
            "The explanation is restricted to face-landmark regions only."
        )

        if valid_regions:
            for region in valid_regions[:3]:
                explanation["manipulation_indicators"].append(
                    _region_sentence(region, prediction)
                )
        else:
            explanation["manipulation_indicators"].append(
                "The model classified the face as fake, but no single facial landmark region crossed the marking threshold. The evidence is distributed across the face."
            )

        explanation["recommendation"] = (
            "Review the highlighted face-landmark regions first. These are model attention zones, not confirmed fake pixels."
        )

    if 55 <= brightness <= 190:
        explanation["quality_observations"].append(
            "Brightness is within the acceptable analysis range."
        )
    elif brightness < 55:
        explanation["quality_observations"].append(
            "Brightness is low and may reduce model reliability."
        )
    else:
        explanation["quality_observations"].append(
            "Brightness is high and may affect interpretation."
        )

    if blur_score >= 100:
        explanation["quality_observations"].append(
            "Blur score is acceptable for facial analysis."
        )
    else:
        explanation["quality_observations"].append(
            "Blur score is low; the result should be interpreted with caution."
        )

    if warnings:
        explanation["quality_observations"].extend(warnings)

    return explanation