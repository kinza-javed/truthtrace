import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import styles from "./Dashboard.module.css";

export default function Dashboard() {
  const user = JSON.parse(localStorage.getItem("user"));

  return (
    <>
      <Navbar />

      <main className={styles.page}>
        <section className={styles.hero}>
          <p className={styles.kicker}>Dashboard</p>
          <h1>Welcome back, {user?.username || "User"}</h1>
          <p>
            Manage your image forensic workflow, run new analysis, review
            reports, and monitor your previous detections.
          </p>

          <div className={styles.actions}>
            <Link to="/detect" className={styles.primaryBtn}>
              Analyze New Image
            </Link>
            <Link to="/history" className={styles.secondaryBtn}>
              View History
            </Link>
          </div>
        </section>

        <section className={styles.cards}>
          <div className={styles.card}>
            <h3>Image Detection</h3>
            <p>Upload JPG, JPEG, or PNG images for face-level deepfake analysis.</p>
          </div>

          <div className={styles.card}>
            <h3>Forensic Outputs</h3>
            <p>Review ELA, noise residual maps, face quality, and probabilities.</p>
          </div>

          <div className={styles.card}>
            <h3>PDF Reports</h3>
            <p>Download professional system-generated forensic reports.</p>
          </div>
        </section>
      </main>
    </>
  );
}