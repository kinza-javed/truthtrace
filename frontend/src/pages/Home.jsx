import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import styles from "./Home.module.css";

export default function Home() {
  const user = JSON.parse(localStorage.getItem("user"));

  return (
    <>
      <Navbar />

      <main className={styles.page}>
        <section className={styles.hero}>
          <div className={styles.heroText}>
            <p className={styles.kicker}>AI Image Forensics</p>

            <h1>
              Detect Deepfake Images with
              <span> Face-Level Forensic Analysis</span>
            </h1>

            <p className={styles.subtitle}>
              Welcome, {user?.username || "User"}. Cockatoos helps identify
              manipulated facial media using AI prediction, face detection,
              image forensics, SHA-256 evidence hashing, and downloadable
              forensic reports.
            </p>

            <div className={styles.actions}>
              <Link to="/detect" className={styles.primaryBtn}>
                Start Image Analysis
              </Link>

              <a href="#manual" className={styles.secondaryBtn}>
                View User Manual
              </a>
            </div>
          </div>

          <div className={styles.heroImageWrap}>
            <img src="/images/2.png" alt="Deepfake forensic analysis" />
          </div>
        </section>

        <section className={styles.section}>
          <div className={styles.sectionHeader}>
            <p className={styles.kicker}>The Problem</p>
            <h2>Why deepfakes are dangerous</h2>
            <p>
              Deepfakes can manipulate faces, create false evidence, spread
              misinformation, damage reputations, and make it harder to trust
              digital media.
            </p>
          </div>

          <div className={styles.infoGrid}>
            <div className={styles.infoCard}>
              <img src="/images/4.png" alt="Face manipulation" />
              <h3>Face Manipulation</h3>
              <p>
                AI-generated or altered faces can appear realistic, making
                manual inspection difficult.
              </p>
            </div>

            <div className={styles.infoCard}>
              <img src="/images/5.png" alt="Deepfake warning" />
              <h3>False Digital Evidence</h3>
              <p>
                Manipulated images may be used to mislead viewers or support
                false claims.
              </p>
            </div>

            <div className={styles.infoCard}>
              <img src="/images/7.png" alt="AI face analysis" />
              <h3>Trust Issues</h3>
              <p>
                As fake media improves, reliable forensic tools become essential
                for verification.
              </p>
            </div>
          </div>
        </section>

        <section className={styles.splitSection}>
          <div>
            <p className={styles.kicker}>Our Solution</p>
            <h2>How Cockatoos counters deepfake images</h2>
            <p>
              Our system analyzes uploaded images using a deepfake detection
              model and supporting forensic techniques. It detects visible
              faces, checks image quality, predicts real or fake probability,
              generates ELA and noise analysis outputs, and stores results with
              a SHA-256 hash for integrity.
            </p>

            <div className={styles.featureList}>
              <div>Face detection and multi-face analysis</div>
              <div>Real/Fake probability score</div>
              <div>Error Level Analysis and noise residual output</div>
              <div>SHA-256 cryptographic evidence hash</div>
              <div>Downloadable forensic PDF report</div>
            </div>
          </div>

          <img src="/images/3.png" alt="Biometric face analysis" />
        </section>

        <section className={styles.section} id="manual">
          <div className={styles.sectionHeader}>
            <p className={styles.kicker}>User Manual</p>
            <h2>How detection works</h2>
            <p>
              The system is designed to be simple for users while keeping the
              analysis pipeline professional and traceable.
            </p>
          </div>

          <div className={styles.steps}>
            <div className={styles.stepCard}>
              <span>01</span>
              <h3>Upload Image</h3>
              <p>
                Select a JPG, JPEG, or PNG image containing a visible human
                face.
              </p>
            </div>

            <div className={styles.stepCard}>
              <span>02</span>
              <h3>Click Analyze</h3>
              <p>
                The system validates the file, detects faces, and checks image
                quality.
              </p>
            </div>

            <div className={styles.stepCard}>
              <span>03</span>
              <h3>Wait for Results</h3>
              <p>
                The AI model predicts real/fake probability and generates
                forensic outputs.
              </p>
            </div>

            <div className={styles.stepCard}>
              <span>04</span>
              <h3>Download Report</h3>
              <p>
                Download a professional PDF report with findings and evidence
                hash.
              </p>
            </div>
          </div>
        </section>

        <section className={styles.visualStrip}>
          <img src="/images/6.png" alt="Face recognition network" />
          <img src="/images/8.png" alt="Face forensic mesh" />
          <img src="/images/1.png" alt="Deepfake analysis interface" />
        </section>

        <section className={styles.cta}>
          <h2>Ready to analyze an image?</h2>
          <p>
            Start with a clear face image and generate a complete forensic
            result.
          </p>
          <Link to="/detect" className={styles.primaryBtn}>
            Open Detection Tool
          </Link>
        </section>
      </main>
    </>
  );
}