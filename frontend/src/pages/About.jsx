import Navbar from "../components/Navbar";
import styles from "./About.module.css";

export default function About() {
  return (
    <>
      <Navbar />

      <main className={styles.page}>
        <section className={styles.hero}>
          <div>
            <p className={styles.kicker}>About Cockatoos</p>
            <h1>AI-Assisted Deepfake Image Forensics</h1>
            <p>
              Cockatoos is a forensic-style web platform designed to help users
              analyze facial images for possible deepfake manipulation. It
              combines face detection, AI prediction, visual forensic outputs,
              evidence hashing, and professional report generation.
            </p>
          </div>

          <img src="/images/11.png" alt="Face forensic analysis" />
        </section>

        <section className={styles.section}>
          <div className={styles.sectionHeader}>
            <p className={styles.kicker}>Why It Matters</p>
            <h2>The growing risk of manipulated media</h2>
            <p>
              Deepfake images can be used to spread misinformation, create fake
              identities, damage reputations, and mislead viewers. As AI-generated
              media becomes more realistic, image verification tools are becoming
              increasingly important.
            </p>
          </div>

          <div className={styles.cards}>
            <div className={styles.card}>
              <h3>Digital Trust</h3>
              <p>
                The system supports users in checking whether a facial image may
                contain signs of manipulation.
              </p>
            </div>

            <div className={styles.card}>
              <h3>Face-Level Analysis</h3>
              <p>
                If multiple faces are detected, each face can be analyzed
                separately with confidence scores.
              </p>
            </div>

            <div className={styles.card}>
              <h3>Forensic Reporting</h3>
              <p>
                Results are summarized in a downloadable report with technical
                details and evidence hash.
              </p>
            </div>
          </div>
        </section>

        <section className={styles.split}>
          <img src="/images/12.png" alt="Deepfake difference analysis" />

          <div>
            <p className={styles.kicker}>Analysis Pipeline</p>
            <h2>How Cockatoos works</h2>

            <div className={styles.steps}>
              <div>
                <span>01</span>
                <h3>Image Validation</h3>
                <p>
                  The file is checked for supported format, corruption, size,
                  and basic validity.
                </p>
              </div>

              <div>
                <span>02</span>
                <h3>Face Detection</h3>
                <p>
                  Human faces are detected, cropped, and checked for visibility,
                  blur, lighting, and face size.
                </p>
              </div>

              <div>
                <span>03</span>
                <h3>AI Prediction</h3>
                <p>
                  The model predicts whether each detected face is likely real
                  or fake using probability scores.
                </p>
              </div>

              <div>
                <span>04</span>
                <h3>Forensic Outputs</h3>
                <p>
                  ELA, noise residual maps, SHA-256 hash, and PDF report are
                  generated for review.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className={styles.techSection}>
          <div>
            <p className={styles.kicker}>System Capabilities</p>
            <h2>What the platform provides</h2>
          </div>

          <div className={styles.techGrid}>
            <div>Image upload with validation</div>
            <div>Face detection and cropping</div>
            <div>Multiple-face processing</div>
            <div>Real/Fake probability score</div>
            <div>Brightness and blur checks</div>
            <div>Error Level Analysis output</div>
            <div>Noise residual map</div>
            <div>SHA-256 evidence hash</div>
            <div>Downloadable forensic PDF</div>
          </div>
        </section>

        <section className={styles.warningSection}>
          <div>
            <p className={styles.kicker}>Important Note</p>
            <h2>AI results are supportive, not final legal proof</h2>
            <p>
              Cockatoos provides AI-assisted forensic analysis. The results are
              probabilistic and should be interpreted with confidence scores,
              image quality, and forensic outputs. For legal, investigative, or
              high-stakes decisions, results should be reviewed by qualified
              digital forensic experts.
            </p>
          </div>

          <img src="/images/13.png" alt="Face detection interface" />
        </section>
      </main>
    </>
  );
}