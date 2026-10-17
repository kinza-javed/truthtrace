import { useCallback, useEffect, useState } from "react";
import {
  getReviewCase,
  investigateReviewCase,
  markReviewHighImpact,
  recordReviewVerdict,
} from "../services/reviewApi";
import styles from "./ReviewPanel.module.css";

const API = "http://127.0.0.1:8000";

const verdicts = [
  ["authenticity_supported", "Authenticity supported by available evidence"],
  ["manipulation_supported", "Manipulation supported by available evidence"],
  ["inconclusive", "Inconclusive — further investigation required"],
];

function currentUserId() {
  try {
    return JSON.parse(localStorage.getItem("user") || "null")?.id;
  } catch {
    return null;
  }
}

function EvidenceLinks({ evidence }) {
  const links = [
    ["Original uploaded image", evidence?.image],
    ["ELA visualization", evidence?.ela],
    ["Noise visualization", evidence?.noise],
  ].filter(([, path]) => path);

  const faceEvidence = evidence?.faces || evidence?.face_results || [];
  faceEvidence.forEach((face) => {
    if (face.marked_gradcam || face.gradcam) {
      links.push([
        `Grad-CAM for face ${face.face_index}`,
        face.marked_gradcam || face.gradcam,
      ]);
    }
  });

  return (
    <>
      {links.map(([label, path]) => (
        <a
          key={`${label}-${path}`}
          href={`${API}${path}`}
          target="_blank"
          rel="noreferrer"
        >
          {label}
        </a>
      ))}
      {evidence?.interpretation && <p>{evidence.interpretation}</p>}
      {evidence?.exif && (
        <pre className={styles.evidenceJson}>
          {JSON.stringify(evidence.exif, null, 2)}
        </pre>
      )}
      {evidence?.face_quality && (
        <pre className={styles.evidenceJson}>
          {JSON.stringify(evidence.face_quality, null, 2)}
        </pre>
      )}
    </>
  );
}

export default function ReviewPanel({ analysisId, faceResults = [] }) {
  const reviewerUserId = currentUserId();
  const [review, setReview] = useState(null);
  const [loadError, setLoadError] = useState("");
  const [actionError, setActionError] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [concern, setConcern] = useState("possible_splicing");
  const [faceIndex, setFaceIndex] = useState("");
  const [investigationReason, setInvestigationReason] = useState("");
  const [verdict, setVerdict] = useState("inconclusive");
  const [verdictReason, setVerdictReason] = useState("");
  const [impactReason, setImpactReason] = useState("");

  const loadReview = useCallback(async () => {
    if (!reviewerUserId) {
      setLoadError("Sign in again to load your human review case.");
      setLoading(false);
      return;
    }
    try {
      const data = await getReviewCase(analysisId, reviewerUserId);
      setReview(data);
      setLoadError("");
    } catch (error) {
      setLoadError(
        error.response?.data?.detail || "Failed to load the human review case."
      );
    } finally {
      setLoading(false);
    }
  }, [analysisId, reviewerUserId]);

  useEffect(() => {
    loadReview();
  }, [loadReview]);

  const submitAction = async (action, successMessage) => {
    if (!reviewerUserId) {
      setActionError("Sign in again before recording a review action.");
      return false;
    }
    setSaving(true);
    setActionError("");
    setNotice("");
    try {
      const data = await action();
      setReview(data);
      setNotice(successMessage);
      return true;
    } catch (error) {
      setActionError(
        error.response?.data?.detail || "Unable to save this review action."
      );
      return false;
    } finally {
      setSaving(false);
    }
  };

  const submitInvestigation = async (event) => {
    event.preventDefault();
    const saved = await submitAction(
      () =>
        investigateReviewCase(analysisId, {
          reviewer_user_id: reviewerUserId,
          concern,
          reason: investigationReason,
          ...(faceIndex ? { face_index: Number(faceIndex) } : {}),
        }),
      "Investigation evidence was added to the case history."
    );
    if (saved) setInvestigationReason("");
  };

  const submitVerdict = async (event) => {
    event.preventDefault();
    const saved = await submitAction(
      () =>
        recordReviewVerdict(analysisId, {
          reviewer_user_id: reviewerUserId,
          verdict,
          reason: verdictReason,
        }),
      "Human verdict recorded separately from the AI prediction."
    );
    if (saved) setVerdictReason("");
  };

  const submitHighImpact = async (event) => {
    event.preventDefault();
    const saved = await submitAction(
      () =>
        markReviewHighImpact(analysisId, {
          reviewer_user_id: reviewerUserId,
          reason: impactReason,
        }),
      "Case marked high-impact; human review is now required."
    );
    if (saved) setImpactReason("");
  };

  if (loading) {
    return <section className={styles.panel}>Loading adaptive human review…</section>;
  }

  if (loadError) {
    return (
      <section className={styles.panel}>
        <h2>Adaptive Human Review</h2>
        <p className={styles.error}>{loadError}</p>
      </section>
    );
  }

  if (!review) return null;

  const initialEvent = review.events.find(
    (event) =>
      event.action === "analysis_completed" ||
      event.action === "legacy_review_case_created"
  );
  const availableFaces =
    faceResults.length > 0
      ? faceResults
      : initialEvent?.evidence?.face_results || [];

  return (
    <section className={styles.panel} aria-labelledby="review-heading">
      <div className={styles.heading}>
        <div>
          <p className={styles.kicker}>Human-in-the-loop workflow</p>
          <h2 id="review-heading">Adaptive Human Review</h2>
        </div>
        <span
          className={
            review.required_review && review.status !== "concluded"
              ? styles.requiredBadge
              : styles.statusBadge
          }
        >
          {review.status.replaceAll("_", " ")}
        </span>
      </div>

      <p className={styles.disclaimer}>
        The AI prediction above remains unchanged. Its scores are not calibrated
        authenticity probabilities, and attention maps are not proof of
        manipulation. A human conclusion is stored separately below.
      </p>

      {review.routing_reasons.length > 0 && (
        <div className={styles.reasonBox}>
          <strong>Why this case was routed</strong>
          <ul>
            {review.routing_reasons.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
        </div>
      )}

      <div className={styles.aiSummary}>
        <strong>Original AI assessment</strong>
        <span>Prediction: {review.ai_prediction}</span>
        <span>
          Model score: {(Number(review.ai_confidence || 0) * 100).toFixed(2)}%
          (not calibrated)
        </span>
        <span>
          Initial evidence is preserved in the event history and is not
          overwritten by reviewer actions.
        </span>
      </div>

      {review.human_verdict && (
        <div className={styles.verdictBox}>
          <p className={styles.kicker}>Latest human verdict</p>
          <h3>{review.human_verdict.label}</h3>
          <p>{review.human_verdict.reason}</p>
          <small>
            Recorded by {review.human_verdict.reviewer || "reviewer"} ·{" "}
            {new Date(review.human_verdict.decided_at).toLocaleString()}
          </small>
        </div>
      )}

      <div className={styles.forms}>
        <form className={styles.formCard} onSubmit={submitInvestigation}>
          <h3>Direct another investigation</h3>
          <label>
            Concern
            <select
              value={concern}
              onChange={(event) => setConcern(event.target.value)}
            >
              <option value="possible_splicing">Possible image splicing</option>
              <option value="inconsistent_lighting">
                Inconsistent lighting
              </option>
              <option value="face_manipulation">Possible face manipulation</option>
              <option value="image_metadata">Image metadata / EXIF</option>
            </select>
          </label>
          {(concern === "face_manipulation" ||
            concern === "inconsistent_lighting") &&
            availableFaces.length > 0 && (
              <label>
                Face (optional)
                <select
                  value={faceIndex}
                  onChange={(event) => setFaceIndex(event.target.value)}
                >
                  <option value="">All detected faces</option>
                  {availableFaces.map((face) => (
                    <option key={face.face_index} value={face.face_index}>
                      Face #{face.face_index}
                    </option>
                  ))}
                </select>
              </label>
            )}
          <label>
            Why investigate this concern? (required)
            <textarea
              value={investigationReason}
              onChange={(event) => setInvestigationReason(event.target.value)}
              minLength={10}
              maxLength={2000}
              required
            />
          </label>
          <button type="submit" disabled={saving}>
            {saving ? "Running…" : "Run investigation"}
          </button>
        </form>

        {!review.high_impact && (
          <form className={styles.formCard} onSubmit={submitHighImpact}>
            <h3>Flag high-impact case</h3>
            <p>
              Use for legal proceedings, serious allegations, or other
              high-stakes decisions. This forces human review regardless of
              model score.
            </p>
            <label>
              Why is this case high-impact? (required)
              <textarea
                value={impactReason}
                onChange={(event) => setImpactReason(event.target.value)}
                minLength={10}
                maxLength={2000}
                required
              />
            </label>
            <button type="submit" disabled={saving}>
              {saving ? "Saving…" : "Require human review"}
            </button>
          </form>
        )}

        <form className={styles.formCard} onSubmit={submitVerdict}>
          <h3>Record a human verdict</h3>
          <label>
            Conclusion
            <select
              value={verdict}
              onChange={(event) => setVerdict(event.target.value)}
            >
              {verdicts.map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Evidence-based reason (required)
            <textarea
              value={verdictReason}
              onChange={(event) => setVerdictReason(event.target.value)}
              minLength={10}
              maxLength={2000}
              required
            />
          </label>
          <button type="submit" disabled={saving}>
            {saving ? "Saving…" : "Record human verdict"}
          </button>
        </form>
      </div>

      {actionError && <p className={styles.error}>{actionError}</p>}
      {notice && <p className={styles.notice}>{notice}</p>}

      <div className={styles.timeline}>
        <h3>Evidence and decision history</h3>
        {review.events.map((event) => (
          <article className={styles.event} key={event.id}>
            <div className={styles.eventHeading}>
              <strong>{event.action.replaceAll("_", " ")}</strong>
              <time>{new Date(event.created_at).toLocaleString()}</time>
            </div>
            <p>
              {event.actor || "System"}
              {event.concern
                ? ` · ${event.concern.replaceAll("_", " ")}`
                : ""}
            </p>
            {event.reason && <p>{event.reason}</p>}
            {event.action === "investigation_requested" && (
              <EvidenceLinks evidence={event.evidence} />
            )}
            {(event.action === "analysis_completed" ||
              event.action === "legacy_review_case_created") && (
              <>
                <p>
                  {event.evidence.legacy_record
                    ? "Legacy AI assessment imported; detailed original analysis evidence was not saved. "
                    : "Original AI assessment and source evidence captured. "}
                  SHA-256: {event.evidence.sha256 || "unavailable"}
                </p>
                {!event.evidence.legacy_record && (
                  <EvidenceLinks evidence={event.evidence.artifacts} />
                )}
                {!event.evidence.legacy_record &&
                  event.evidence.face_results?.length > 0 && (
                    <EvidenceLinks
                      evidence={{ face_results: event.evidence.face_results }}
                    />
                  )}
              </>
            )}
            {event.action === "human_verdict_recorded" && (
              <p>
                {event.evidence.label}; original AI prediction at decision:{" "}
                {event.evidence.ai_prediction_at_decision}.
              </p>
            )}
          </article>
        ))}
        {initialEvent?.evidence?.limitations?.length > 0 && (
          <p className={styles.limitation}>
            {initialEvent.evidence.limitations.join(" ")}
          </p>
        )}
      </div>
    </section>
  );
}
