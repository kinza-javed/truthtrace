import Navbar from "../components/Navbar";
import styles from "./Privacy.module.css";

export default function Privacy() {
  return (
    <>
      <Navbar />

      <main className={styles.page}>
        <section className={styles.hero}>
          <div>
            <p className={styles.kicker}>Privacy & Security</p>
            <h1>Responsible Image Forensics</h1>
            <p>
              Cockatoos is designed to support forensic image analysis while
              keeping user data, analysis records, and evidence integrity clear
              and traceable.
            </p>
          </div>

          <img src="/images/15.webp" alt="Privacy and forensic security" />
        </section>

        <section className={styles.cards}>
          <div className={styles.card}>
            <h3>Image Handling</h3>
            <p>
              Uploaded images are processed by the backend to detect faces,
              generate forensic outputs, and produce reports. Raw images are not
              stored directly in the database.
            </p>
          </div>

          <div className={styles.card}>
            <h3>Stored Analysis Data</h3>
            <ul>
              <li>Filename</li>
              <li>Prediction result</li>
              <li>Confidence score</li>
              <li>Real/Fake probabilities</li>
              <li>SHA-256 hash</li>
              <li>Report path</li>
            </ul>
          </div>

          <div className={styles.card}>
            <h3>Evidence Integrity</h3>
            <p>
              SHA-256 hashing helps verify whether the analyzed image file is
              unchanged. This supports repeatability and report traceability.
            </p>
          </div>
        </section>

        <section className={styles.policy}>
          <p className={styles.kicker}>Security Practices</p>
          <h2>How the platform protects users</h2>

          <div className={styles.policyGrid}>
            <div>
              <span>01</span>
              <h3>Secure Accounts</h3>
              <p>
                Users sign in using verified email accounts and secure password
                recovery links.
              </p>
            </div>

            <div>
              <span>02</span>
              <h3>Password Protection</h3>
              <p>
                Passwords are hashed before storage and are never saved as plain
                text.
              </p>
            </div>

            <div>
              <span>03</span>
              <h3>User-Based History</h3>
              <p>
                Analysis records are linked to the authenticated user so each
                user can view only their own history.
              </p>
            </div>

            <div>
              <span>04</span>
              <h3>Report Traceability</h3>
              <p>
                Reports include prediction details and evidence hash for later
                verification.
              </p>
            </div>
          </div>
        </section>

        <section className={styles.notice}>
          <div>
            <p className={styles.kicker}>Important Notice</p>
            <h2>Forensic reports require expert review</h2>
            <p>
              Cockatoos provides AI-assisted results. These results should be
              treated as supportive analysis and reviewed by qualified forensic
              experts before legal, investigative, or high-impact decisions.
            </p>
          </div>

          <img src="/images/14.jpg" alt="Expert review required" />
        </section>
      </main>
    </>
  );
}