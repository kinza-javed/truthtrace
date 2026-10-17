import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import axios from "axios";
import styles from "./AnalysisDetail.module.css";

const API = "http://127.0.0.1:8000";

export default function AnalysisDetail() {
  const { id } = useParams();

  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDetail = async () => {
      try {
        const res = await axios.get(`${API}/api/history/detail/${id}`);
        setAnalysis(res.data);
      } catch {
        setError("Failed to load analysis details.");
      } finally {
        setLoading(false);
      }
    };

    loadDetail();
  }, [id]);

  return (
    <>
      <Navbar />

      <main className={styles.page}>
        <section className={styles.header}>
          <p className={styles.kicker}>Analysis Detail</p>
          <h1>Forensic Record #{id}</h1>
          <p>View saved metadata and download the generated forensic report.</p>
        </section>

        {loading && <div className={styles.card}>Loading details...</div>}

        {error && <div className={styles.error}>{error}</div>}

        {analysis && (
          <section className={styles.card}>
            <div className={styles.topRow}>
              <div>
                <h2>{analysis.filename}</h2>
                <p>{new Date(analysis.created_at).toLocaleString()}</p>
              </div>

              <span
                className={
                  analysis.prediction === "FAKE"
                    ? styles.fakeBadge
                    : styles.realBadge
                }
              >
                {analysis.prediction}
              </span>
            </div>

            <div className={styles.grid}>
              <div className={styles.metric}>
                <span>Confidence</span>
                <strong>{(analysis.confidence * 100).toFixed(2)}%</strong>
              </div>

              <div className={styles.metric}>
                <span>Real Probability</span>
                <strong>{(analysis.real_prob * 100).toFixed(2)}%</strong>
              </div>

              <div className={styles.metric}>
                <span>Fake Probability</span>
                <strong>{(analysis.fake_prob * 100).toFixed(2)}%</strong>
              </div>
            </div>

            <div className={styles.hashBox}>
              <h3>SHA-256 Evidence Hash</h3>
              <p>{analysis.sha256}</p>
            </div>

            <div className={styles.actions}>
              {analysis.report && (
                <a
                  href={`${API}${analysis.report}`}
                  target="_blank"
                  rel="noreferrer"
                  className={styles.primaryBtn}
                >
                  Download Report
                </a>
              )}

              <Link to="/history" className={styles.secondaryBtn}>
                Back to History
              </Link>
            </div>
          </section>
        )}
      </main>
    </>
  );
}