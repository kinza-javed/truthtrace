import { useState } from "react";
import detectImage from "../services/detectApi";
import styles from "./Detect.module.css";
import Navbar from "../components/Navbar";

export default function Detect() {
  const API = "http://127.0.0.1:8000";

  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [displaySize, setDisplaySize] = useState({ width: 500, height: 1 });
  const [activeFaceIndex, setActiveFaceIndex] = useState(0);

  const handleFileSelect = (selectedFile) => {
    if (!selectedFile) return;

    setFile(selectedFile);
    setPreviewUrl(URL.createObjectURL(selectedFile));
    setError("");
    setResult(null);
    setActiveFaceIndex(0);
  };

  const handleExampleSelect = async (imagePath, fileName) => {
    try {
      const response = await fetch(imagePath);
      const blob = await response.blob();

      const exampleFile = new File([blob], fileName, {
        type: blob.type || "image/png",
      });

      setFile(exampleFile);
      setPreviewUrl(imagePath);
      setError("");
      setResult(null);
      setActiveFaceIndex(0);
    } catch {
      setError("Failed to load example image.");
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select an image first.");
      return;
    }

    setError("");
    setResult(null);
    setActiveFaceIndex(0);
    setLoading(true);

    try {
      const data = await detectImage(file);
      setResult(data);
      setActiveFaceIndex(0);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Image analysis failed. Please upload a clear image with a visible human face."
      );
    } finally {
      setLoading(false);
    }
  };

  const resetScan = () => {
    setFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError("");
    setActiveFaceIndex(0);
  };

  const activeFace = result?.face_results?.[activeFaceIndex];

  const scaleX = result?.image_width ? displaySize.width / result.image_width : 1;
  const scaleY = result?.image_height ? displaySize.height / result.image_height : 1;

  const activePrediction = activeFace?.prediction || result?.prediction || "UNKNOWN";
  const activeConfidence = activeFace?.confidence || result?.confidence || 0;
  const activeRealProb = activeFace?.probabilities?.real ?? result?.probabilities?.real ?? 0;
  const activeFakeProb = activeFace?.probabilities?.fake ?? result?.probabilities?.fake ?? 0;

  const heatmapUrl =
    activeFace?.marked_gradcam ||
    activeFace?.gradcam ||
    result?.marked_gradcam ||
    result?.gradcam ||
    result?.ela;

  const isFake = activePrediction === "FAKE";

  const percentNumber = (value) => Number((Number(value || 0) * 100).toFixed(2));
  const confidencePercent = percentNumber(activeConfidence);
  const realPercent = percentNumber(activeRealProb);
  const fakePercent = percentNumber(activeFakeProb);

  const formatPercent = (value, digits = 2) => {
    const safeValue = Number(value || 0);
    return `${(safeValue * 100).toFixed(digits)}%`;
  };

  const formatRawPercent = (value, digits = 2) => {
    const safeValue = Number(value || 0);
    return `${safeValue.toFixed(digits)}%`;
  };

  const getRiskLevel = () => {
    const risk = activeFace?.gradcam_explanation?.risk_level;
    if (risk) return risk;
    if (fakePercent >= 75) return "HIGH";
    if (fakePercent >= 45) return "MEDIUM";
    return "LOW";
  };

  const riskLevel = getRiskLevel();
  const attentionRegions = activeFace?.attention_regions || [];
  const summaryLines = activeFace?.gradcam_explanation?.summary || [];

  const explanationText =
    summaryLines.length > 0
      ? summaryLines.join(" ")
      : isFake
      ? "Model attention was strongest around localized facial regions. Texture, boundary, lighting, or structural inconsistencies contributed to the higher fake probability."
      : "The analyzed face shows stronger authentic indicators with lower fake probability across the selected regions.";

  const qualityBrightness = activeFace?.quality?.brightness ?? "N/A";
  const qualityBlurScore = activeFace?.quality?.blur_score ?? "N/A";

  const ProgressBar = ({ value, type = "purple" }) => (
    <div className={styles.progressTrack}>
      <div
        className={`${styles.progressFill} ${styles[type]}`}
        style={{ width: `${Math.min(Number(value || 0), 100)}%` }}
      />
    </div>
  );

  return (
    <>
      <Navbar />

      <div className={styles.page}>
        <header className={styles.header}>
          <h1 className={styles.title}>Cockatoos Forensic Dashboard</h1>
          <p className={styles.subtitle}>
            AI-assisted deepfake detection with face-level analysis, Grad-CAM heatmap,
            marked attention regions, and forensic report generation.
          </p>
        </header>

        <section className={styles.uploadSection}>
          <div className={styles.uploadHero}>
            <div className={styles.left}>
              <h2>Upload Evidence Image</h2>
              <p className={styles.subtitle}>
                Drag and drop an image or click to select a file for deepfake forensic analysis.
              </p>

              <label
                className={styles.dropZone}
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => {
                  e.preventDefault();
                  handleFileSelect(e.dataTransfer.files[0]);
                }}
              >
                <input
                  type="file"
                  className={styles.hiddenInput}
                  accept=".jpg,.jpeg,.png"
                  onChange={(e) => handleFileSelect(e.target.files[0])}
                />

                <div>
                  {previewUrl ? (
                    <div className={styles.previewBox}>
                      <button
                        type="button"
                        className={styles.previewClose}
                        onClick={(e) => {
                          e.preventDefault();
                          resetScan();
                        }}
                      >
                        ✕
                      </button>

                      <img src={previewUrl} alt="Selected preview" />
                    </div>
                  ) : (
                    <>
                      <div className={styles.uploadIcon}>⬆️</div>
                      <h3>Drag & drop an image or click</h3>
                      <p>PNG, JPG, JPEG up to 3MB</p>
                    </>
                  )}

                  {file && <div className={styles.uploadPreviewText}>{file.name}</div>}
                </div>
              </label>

              <div className={styles.exampleSection}>
                <p>Or try with example images:</p>

                <div className={styles.exampleGrid}>
                  {[16, 17, 18, 19].map((num) => (
                    <button
                      key={num}
                      type="button"
                      className={styles.exampleThumb}
                      onClick={() =>
                        handleExampleSelect(`/images/${num}.png`, `example-${num}.png`)
                      }
                    >
                      <img src={`/images/${num}.png`} alt={`Example ${num}`} />
                    </button>
                  ))}
                </div>
              </div>

              <button className={styles.detectBtn} onClick={handleUpload} disabled={loading}>
                {loading ? "Analyzing..." : "Detect Forgery"}
              </button>

              {error && <p className={styles.error}>{error}</p>}
            </div>

            <div className={styles.right}>
              <img src="/images/10.jpeg" alt="Detection preview" className={styles.fullImage} />
            </div>
          </div>
        </section>

        {result && activeFace && (
          <>
            <section className={styles.resultHero}>
              <div className={styles.heroCopy}>
                <div className={styles.heroIcon}>✦</div>

                <div>
                  <h2>What does this result mean?</h2>
                  <p>
                    The selected face was analyzed using AI prediction, Grad-CAM heatmap
                    visualization, and region-based attention marking. Highlighted areas
                    represent model attention zones, not confirmed fake regions.
                  </p>

                  <div className={styles.verdictNote}>
                    <span>✺</span>
                    <strong>
                      The selected face indicates a {isFake ? "higher probability of being a deepfake." : "higher probability of being authentic."}
                    </strong>
                  </div>
                </div>
              </div>

              <div className={styles.heroActions}>
                {result.report && (
                  <a href={`${API}${result.report}`} target="_blank" rel="noreferrer" className={styles.actionCard}>
                    <span>▣</span>
                    <strong>Download Report</strong>
                    <small>Download PDF forensic report</small>
                  </a>
                )}

                {result.report && (
                  <a href={`${API}${result.report}`} target="_blank" rel="noreferrer" className={styles.actionCard}>
                    <span>▤</span>
                    <strong>View Full Report</strong>
                    <small>View complete analysis details</small>
                  </a>
                )}

                <button type="button" className={`${styles.actionCard} ${styles.primaryAction}`} onClick={resetScan}>
                  <span>▧</span>
                  <strong>Scan Another Image</strong>
                  <small>Upload a new image to analyze</small>
                </button>
              </div>
            </section>

            <section className={styles.analysisCard}>
              <div className={styles.sectionTop}>
                <div>
                  <p className={styles.sectionKicker}>✦ Explainable AI Analysis</p>
                  <h2>Face-Level Forensic Interpretation</h2>
                </div>

                <div className={styles.targetPill}>Target: {result.filename?.toUpperCase() || file?.name?.toUpperCase()}</div>
              </div>

              <div className={styles.faceTabs}>
                {result.face_results?.map((face, index) => (
                  <button
                    key={face.face_index}
                    className={activeFaceIndex === index ? styles.activeFaceTab : styles.faceTab}
                    onClick={() => setActiveFaceIndex(index)}
                  >
                    Face #{face.face_index} · {face.prediction}
                  </button>
                ))}
              </div>

              <div className={styles.analysisGrid}>
                <div className={styles.heatmapPanel}>
                  <div className={styles.panelTitle}>
                    <h3>Marked Grad-CAM Attention</h3>
                    <span>Face #{activeFace.face_index}</span>
                  </div>

                  <div className={styles.heatmapImageWrap}>
                    {heatmapUrl ? (
                      <img src={`${API}${heatmapUrl}`} alt={`Marked Grad-CAM attention regions for Face ${activeFace.face_index}`} />
                    ) : (
                      <div className={styles.emptyHeatmap}>No marked Grad-CAM heatmap available.</div>
                    )}
                  </div>

                  <p className={styles.imageCaption}>
                    Highlighted zones represent model attention regions, not confirmed fake areas.
                  </p>
                </div>

                <div className={styles.middleColumn}>
                  <div className={styles.metricPanel}>
                    <div className={styles.panelTitle}>
                      <h3>Selected Face Verdict</h3>
                      <span className={isFake ? styles.fakeBadge : styles.realBadge}>{activePrediction}</span>
                    </div>

                    <div className={styles.metricRow}>
                      <span>Confidence</span>
                      <ProgressBar value={confidencePercent} type="pink" />
                      <b>{formatPercent(activeConfidence)}</b>
                    </div>

                    <div className={styles.metricRow}>
                      <span>Real Probability</span>
                      <ProgressBar value={realPercent} type="blue" />
                      <b>{formatPercent(activeRealProb)}</b>
                    </div>

                    <div className={styles.metricRow}>
                      <span>Fake Probability</span>
                      <ProgressBar value={fakePercent} type="pink" />
                      <b>{formatPercent(activeFakeProb)}</b>
                    </div>

                    <div className={styles.metricSimple}>
                      <span>Brightness</span>
                      <b>{qualityBrightness}</b>
                    </div>

                    <div className={styles.metricSimple}>
                      <span>Blur Score</span>
                      <b>{qualityBlurScore}</b>
                    </div>
                  </div>

                  <div className={styles.riskCard}>
                    <div>
                      <h3>Risk Level</h3>
                      <span className={styles[(riskLevel || "unknown").toLowerCase()] || styles.unknown}>{riskLevel}</span>
                    </div>

                    <p>
                      Risk level indicates how strongly the model detected suspicious visual attention patterns such as texture,
                      boundary, lighting, or structural inconsistencies.
                    </p>
                  </div>
                </div>

                <div className={styles.rightColumn}>
                  <div className={styles.metricPanel}>
                    <div className={styles.panelTitle}>
                      <h3>Key Indicators</h3>
                      <span>AI Signals</span>
                    </div>

                    <div className={styles.indicatorRow}>
                      <span>Fake Probability</span>
                      <b>{formatRawPercent(fakePercent)}</b>
                    </div>
                    <ProgressBar value={fakePercent} type="red" />

                    <div className={styles.indicatorRow}>
                      <span>Real Probability</span>
                      <b>{formatRawPercent(realPercent)}</b>
                    </div>
                    <ProgressBar value={realPercent} type="blue" />

                    <div className={styles.indicatorRow}>
                      <span>Detection Confidence</span>
                      <b>{formatRawPercent(confidencePercent)}</b>
                    </div>
                    <ProgressBar value={confidencePercent} type="green" />
                  </div>

                  <div className={styles.metricPanel}>
                    <div className={styles.panelTitle}>
                      <h3>Region Attention</h3>
                    </div>

                    {attentionRegions.length > 0 ? (
                      attentionRegions.map((region, index) => (
                        <div className={styles.regionScore} key={region.id || index}>
                          <div>
                            <span>{region.id || `R${index + 1}`}: {region.label}</span>
                            <b>{region.score ? `${region.score}%` : "N/A"}</b>
                          </div>
                          <ProgressBar value={Number(region.score || 0)} type={index === 0 ? "purple" : index === 1 ? "blue" : "cyan"} />
                        </div>
                      ))
                    ) : (
                      <p className={styles.emptyText}>No strong localized high activation region detected.</p>
                    )}
                  </div>
                </div>
              </div>

              <div className={styles.previewAuditGrid}>
                <div className={styles.metricPanel}>
                  <div className={styles.panelTitle}>
                    <h3>Detected Faces Preview</h3>
                    <span>{result.faces_detected} faces</span>
                  </div>

                  <div className={styles.imageWrap}>
                    <img
                      src={`data:image/jpeg;base64,${result.image}`}
                      alt="Uploaded evidence"
                      className={styles.mainImage}
                      onLoad={(e) => {
                        setDisplaySize({
                          width: e.currentTarget.clientWidth,
                          height: e.currentTarget.clientHeight,
                        });
                      }}
                    />

                    {result.face_results?.map((face) => {
                      const boxColor = face.prediction === "FAKE" ? "#ef4444" : "#22c55e";

                      return (
                        <div
                          key={face.face_index}
                          style={{
                            position: "absolute",
                            left: `${face.bbox.x1 * scaleX}px`,
                            top: `${face.bbox.y1 * scaleY}px`,
                            width: `${(face.bbox.x2 - face.bbox.x1) * scaleX}px`,
                            height: `${(face.bbox.y2 - face.bbox.y1) * scaleY}px`,
                            border: `3px solid ${boxColor}`,
                            borderRadius: "8px",
                            boxSizing: "border-box",
                            pointerEvents: "none",
                          }}
                        >
                          <span
                            style={{
                              position: "absolute",
                              top: "-28px",
                              left: "0",
                              background: boxColor,
                              color: "white",
                              padding: "4px 8px",
                              borderRadius: "8px",
                              fontSize: "12px",
                              fontWeight: "800",
                              whiteSpace: "nowrap",
                            }}
                          >
                            Face {face.face_index} · {face.prediction}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div className={styles.metricPanel}>
                  <div className={styles.panelTitle}>
                    <h3>Audit Trail</h3>
                    <span>Evidence Metadata</span>
                  </div>

                  <div className={styles.auditRows}>
                    <p><b>Analysis ID:</b> {result.analysis_id || "N/A"}</p>
                    <p><b>Stored Image:</b> {result.image_path || "N/A"}</p>
                    <p><b>SHA-256:</b></p>
                    <p className={styles.hashText}>{result.sha256 || "N/A"}</p>
                  </div>
                </div>
              </div>

              <div className={styles.xaiBox}>
                <div className={styles.panelTitle}>
                  <h3>XAI Textual Explanation</h3>
                  <span>Readable Summary</span>
                </div>

                <p>• {explanationText}</p>

                {activeFace?.forensic_explanation && (
                  <div className={styles.forensicExplainBox}>
                    <h4>Forensic Explanation</h4>
                    <p>{activeFace.forensic_explanation.verdict_summary}</p>

                    {activeFace.forensic_explanation.authenticity_indicators?.length > 0 && (
                      <>
                        <h5>Authenticity Indicators</h5>
                        {activeFace.forensic_explanation.authenticity_indicators.map((item, index) => (
                          <p key={index}>✓ {item}</p>
                        ))}
                      </>
                    )}

                    {activeFace.forensic_explanation.manipulation_indicators?.length > 0 && (
                      <>
                        <h5>Manipulation Indicators</h5>
                        {activeFace.forensic_explanation.manipulation_indicators.map((item, index) => (
                          <p key={index}>⚠ {item}</p>
                        ))}
                      </>
                    )}

                    {activeFace.forensic_explanation.quality_observations?.length > 0 && (
                      <>
                        <h5>Quality Observations</h5>
                        {activeFace.forensic_explanation.quality_observations.map((item, index) => (
                          <p key={index}>• {item}</p>
                        ))}
                      </>
                    )}

                    {activeFace.forensic_explanation.recommendation && (
                      <>
                        <h5>Recommendation</h5>
                        <p>{activeFace.forensic_explanation.recommendation}</p>
                      </>
                    )}
                  </div>
                )}
              </div>
            </section>
          </>
        )}
      </div>
    </>
  );
}
