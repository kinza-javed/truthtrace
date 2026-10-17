import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import styles from "./Profile.module.css";

export default function Profile() {
  const user = JSON.parse(localStorage.getItem("user"));

  const initials = user?.username
    ? user.username.slice(0, 2).toUpperCase()
    : "US";

  return (
    <>
      <Navbar />

      <main className={styles.page}>
        <section className={styles.hero}>
          <div className={styles.avatar}>{initials}</div>

          <div>
            <p className={styles.kicker}>Account Center</p>
            <h1>{user?.username || "User Profile"}</h1>
            <p>
              Manage your account identity, review saved forensic activity, and
              keep your analysis workflow secure.
            </p>
          </div>
        </section>

        <section className={styles.grid}>
          <div className={styles.card}>
            <h2>Account Information</h2>

            <div className={styles.infoRow}>
              <span>Username</span>
              <strong>{user?.username}</strong>
            </div>

            <div className={styles.infoRow}>
              <span>Email Address</span>
              <strong>{user?.email}</strong>
            </div>

            <div className={styles.infoRow}>
              <span>User ID</span>
              <strong>#{user?.id}</strong>
            </div>
          </div>

          <div className={styles.card}>
            <h2>Security Status</h2>

            <div className={styles.statusBox}>
              <span className={styles.dot}></span>
              <div>
                <strong>Protected account</strong>
                <p>
                  Your account uses email verification, secure login, and
                  password recovery links.
                </p>
              </div>
            </div>

            <Link to="/forgot-password" className={styles.secondaryBtn}>
              Reset Password
            </Link>
          </div>
        </section>

        <section className={styles.actionsCard}>
          <div>
            <h2>Quick Actions</h2>
            <p>Continue your forensic workflow from here.</p>
          </div>

          <div className={styles.actions}>
            <Link to="/detect" className={styles.primaryBtn}>
              Analyze Image
            </Link>
            <Link to="/history" className={styles.secondaryBtn}>
              View History
            </Link>
          </div>
        </section>
      </main>
    </>
  );
}