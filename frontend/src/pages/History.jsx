import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import { getUserHistory } from "../services/historyApi";
import styles from "./History.module.css";

export default function History() {
  const [history, setHistory] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const user = JSON.parse(localStorage.getItem("user"));

  useEffect(() => {
    const loadHistory = async () => {
      try {
        console.log("Logged in user:", user);
        console.log("Calling history for user id:", user.id);
  
        const data = await getUserHistory(user.id);
  
        console.log("History API response:", data);
  
        setHistory(data);
      } catch (err) {
        setError("Failed to load analysis history.");
      } finally {
        setLoading(false);
      }
    };

    if (user?.id) {
      loadHistory();
    } else {
      setError("User session not found. Please login again.");
      setLoading(false);
    }
  }, [user?.id]);

  return (
    <>
      <Navbar />

      <main className={styles.page}>
        <section className={styles.header}>
          <div>
            <p className={styles.kicker}>Analysis Records</p>
            <h1>History & Reports</h1>
            <p>
              Review your previous image analyses, confidence scores, evidence
              hashes, and forensic reports.
            </p>
          </div>
        </section>

        {loading && <div className={styles.card}>Loading history...</div>}

        {error && <div className={styles.error}>{error}</div>}

        {!loading && history.length === 0 && (
          <div className={styles.card}>
            <h2>No history found</h2>
            <p>You have not analyzed any image yet.</p>
          </div>
        )}

        {!loading && history.length > 0 && (
          <section className={styles.tableCard}>
            <table>
              <thead>
                <tr>
                  <th>File</th>
                  <th>Result</th>
                  <th>Confidence</th>
                  <th>Real</th>
                  <th>Fake</th>
                  <th>Date</th>
                  <th>Report</th>
                  <th>Details</th>
                </tr>
              </thead>

              <tbody>
                {history.map((item) => (
                  <tr key={item.id}>
                    <td>{item.filename}</td>

                    <td>
                      <span
                        className={
                          item.prediction === "FAKE"
                            ? styles.fakeBadge
                            : styles.realBadge
                        }
                      >
                        {item.prediction}
                      </span>
                    </td>

                    <td>{(item.confidence * 100).toFixed(2)}%</td>
                    <td>{(item.real_prob * 100).toFixed(2)}%</td>
                    <td>{(item.fake_prob * 100).toFixed(2)}%</td>

                    <td>{new Date(item.created_at).toLocaleString()}</td>

                    <td>
                      {item.report ? (
                        <a
                          href={`http://127.0.0.1:8000${item.report}`}
                          target="_blank"
                          rel="noreferrer"
                        >
                          Download
                        </a>
                      ) : (
                        "N/A"
                      )}
                    </td>

                    <td>
                      <Link to={`/history/${item.id}`}>View</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}
      </main>
    </>
  );
}