from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import os


def safe(value, default="N/A"):
    if value is None or value == "":
        return default
    return str(value)


def percent(value):
    try:
        return f"{float(value) * 100:.2f}%"
    except Exception:
        return "0.00%"


def build_forensic_pdf(result, output_path, api_base_path=""):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=14
    )

    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#1d4ed8"),
        spaceBefore=12,
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["BodyText"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b")
    )

    small_style = ParagraphStyle(
        "SmallStyle",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#475569")
    )

    story = []

    story.append(Paragraph("Deepfake Forensic Analysis Report", title_style))
    story.append(Paragraph(
        "AI-assisted forensic report generated from model prediction, Grad-CAM attention, quality analysis, and explainable AI interpretation.",
        normal_style
    ))
    story.append(Spacer(1, 14))

    face_results = result.get("face_results", [])
    selected_face = face_results[0] if face_results else result

    prediction = selected_face.get("prediction", result.get("prediction", "N/A"))
    confidence = selected_face.get("confidence", result.get("confidence", 0))

    probabilities = selected_face.get("probabilities", result.get("probabilities", {}))
    real_prob = probabilities.get("real", 0)
    fake_prob = probabilities.get("fake", 0)

    quality = selected_face.get("quality", {})
    gradcam_explanation = selected_face.get("gradcam_explanation", {})
    forensic_explanation = selected_face.get("forensic_explanation", {})
    attention_regions = selected_face.get("attention_regions", [])

    risk_level = gradcam_explanation.get("risk_level", "UNKNOWN")

    story.append(Paragraph("1. Case Information", heading_style))

    case_data = [
        ["Analysis ID", safe(result.get("analysis_id"))],
        ["Filename", safe(result.get("filename"))],
        ["Final Prediction", safe(prediction)],
        ["Confidence", percent(confidence)],
        ["Faces Detected", safe(result.get("faces_detected"))],
        ["Selected Face", f"Face #{safe(selected_face.get('face_index'))}"],
    ]

    case_table = Table(case_data, colWidths=[1.8 * inch, 4.8 * inch])
    case_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef2ff")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0f172a")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(case_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("2. Model Result Summary", heading_style))

    result_data = [
        ["Real Probability", percent(real_prob)],
        ["Fake Probability", percent(fake_prob)],
        ["Brightness", safe(quality.get("brightness"))],
        ["Blur Score", safe(quality.get("blur_score"))],
        ["Risk Level", safe(risk_level)],
    ]

    result_table = Table(result_data, colWidths=[1.8 * inch, 4.8 * inch])
    result_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8fafc")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(result_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("3. Grad-CAM Heatmap Evidence", heading_style))

    heatmap_path = (
        selected_face.get("marked_gradcam")
        or selected_face.get("gradcam")
        or result.get("marked_gradcam")
        or result.get("gradcam")
        or result.get("ela")
    )

    if heatmap_path:
        clean_path = heatmap_path.replace("\\", "/")
        if clean_path.startswith("/"):
            clean_path = clean_path[1:]

        possible_path = os.path.join(api_base_path, clean_path)

        if os.path.exists(possible_path):
            story.append(Image(possible_path, width=4.8 * inch, height=3.2 * inch))
            story.append(Spacer(1, 8))
        else:
            story.append(Paragraph(f"Heatmap path: {safe(heatmap_path)}", small_style))
    else:
        story.append(Paragraph("No Grad-CAM heatmap was available for this analysis.", normal_style))

    story.append(Paragraph(
        "Highlighted regions show where the model focused during prediction. These regions represent AI attention zones, not confirmed manipulated areas.",
        small_style
    ))
    story.append(Spacer(1, 12))

    story.append(Paragraph("4. Region Attention Analysis", heading_style))

    if attention_regions:
        region_rows = [["Region", "Label", "Attention Score"]]

        for region in attention_regions:
            region_rows.append([
                safe(region.get("id")),
                safe(region.get("label")),
                f"{safe(region.get('score'))}%"
            ])

        region_table = Table(region_rows, colWidths=[1.2 * inch, 3.6 * inch, 1.4 * inch])
        region_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d4ed8")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("PADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(region_table)
    else:
        story.append(Paragraph("No strong localized attention region was detected.", normal_style))

    story.append(Spacer(1, 12))

    story.append(Paragraph("5. XAI Textual Explanation", heading_style))

    summary_lines = gradcam_explanation.get("summary", [])

    if summary_lines:
        for line in summary_lines:
            story.append(Paragraph(f"• {safe(line)}", normal_style))
    else:
        story.append(Paragraph(
            "The system analyzed model attention, visual quality, and probability distribution to generate the prediction.",
            normal_style
        ))

    story.append(Spacer(1, 12))

    story.append(Paragraph("6. Forensic Explanation", heading_style))

    verdict_summary = forensic_explanation.get("verdict_summary")
    if verdict_summary:
        story.append(Paragraph(safe(verdict_summary), normal_style))

    manipulation_indicators = forensic_explanation.get("manipulation_indicators", [])
    authenticity_indicators = forensic_explanation.get("authenticity_indicators", [])
    quality_observations = forensic_explanation.get("quality_observations", [])
    recommendation = forensic_explanation.get("recommendation")

    if manipulation_indicators:
        story.append(Paragraph("Manipulation Indicators", heading_style))
        for item in manipulation_indicators:
            story.append(Paragraph(f"• {safe(item)}", normal_style))

    if authenticity_indicators:
        story.append(Paragraph("Authenticity Indicators", heading_style))
        for item in authenticity_indicators:
            story.append(Paragraph(f"• {safe(item)}", normal_style))

    if quality_observations:
        story.append(Paragraph("Quality Observations", heading_style))
        for item in quality_observations:
            story.append(Paragraph(f"• {safe(item)}", normal_style))

    if recommendation:
        story.append(Paragraph("Recommendation", heading_style))
        story.append(Paragraph(safe(recommendation), normal_style))

    story.append(Spacer(1, 12))

    story.append(Paragraph("7. Audit Trail", heading_style))

    audit_data = [
        ["Stored Image", safe(result.get("image_path"))],
        ["SHA-256", safe(result.get("sha256"))],
        ["Report Type", "Automated forensic analysis report"],
    ]

    audit_table = Table(audit_data, colWidths=[1.8 * inch, 4.8 * inch])
    audit_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f8fafc")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("PADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(audit_table)

    story.append(Spacer(1, 16))
    story.append(Paragraph(
        "Disclaimer: This report is generated by an automated AI-based forensic system. The result should be reviewed by a qualified digital forensic expert before use in formal investigation or legal proceedings.",
        small_style
    ))

    doc.build(story)

    return output_path