import { useState } from "react";
import { forgotPassword } from "../services/authApi";
import { Link } from "react-router-dom";
import styles from "../styles/Auth.module.css";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setIsError(false);
    setLoading(true);

    try {
      const data = await forgotPassword({ email });
      setMessage(
        data.message || "If this email exists, a password reset link has been sent."
      );
    } catch (error) {
      setIsError(true);
      setMessage("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <form className={styles.card} onSubmit={handleSubmit}>
        <div className={styles.brand}>Cockatoos</div>

        <h2 className={styles.title}>Forgot password</h2>
        <p className={styles.subtitle}>
          Enter your email and we’ll send a secure reset link if the account exists.
        </p>

        <input
          className={styles.input}
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <button className={styles.button} type="submit" disabled={loading}>
          {loading ? "Sending..." : "Send Reset Link"}
        </button>

        {message && (
          <p className={`${styles.message} ${isError ? styles.error : styles.success}`}>
            {message}
          </p>
        )}

        <div className={styles.links}>
          <p>
            Remember your password? <Link to="/login">Back to login</Link>
          </p>
        </div>
      </form>
    </div>
  );
}