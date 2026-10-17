import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { resetPassword } from "../services/authApi";
import styles from "../styles/Auth.module.css";

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get("token");

  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  const isStrongPassword = (pwd) => {
    return (
      pwd.length >= 8 &&
      /[A-Z]/.test(pwd) &&
      /[a-z]/.test(pwd) &&
      /\d/.test(pwd) &&
      /[!@#$%^&*(),.?":{}|<>_\-+=\[\]/\\]/.test(pwd)
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setIsError(false);

    if (!token) {
      setIsError(true);
      setMessage("Invalid reset link.");
      return;
    }

    if (!isStrongPassword(password)) {
      setIsError(true);
      setMessage(
        "Password must be 8+ characters and include uppercase, lowercase, number, and special character."
      );
      return;
    }

    setLoading(true);

    try {
      const data = await resetPassword({ token, new_password: password });
      setMessage(data.message || "Password reset successfully.");
      setTimeout(() => navigate("/login"), 1200);
    } catch (error) {
      setIsError(true);
      setMessage(error.response?.data?.detail || "Reset failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <form className={styles.card} onSubmit={handleSubmit}>
        <div className={styles.brand}>Cockatoos</div>

        <h2 className={styles.title}>Reset password</h2>
        <p className={styles.subtitle}>
          Choose a new strong password for your account.
        </p>

        <input
          className={styles.input}
          type="password"
          placeholder="New password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <p className={styles.smallText}>
          Password must be at least 8 characters and include uppercase,
          lowercase, number, and special character.
        </p>

        <button className={styles.button} type="submit" disabled={loading}>
          {loading ? "Updating..." : "Update Password"}
        </button>

        {message && (
          <p className={`${styles.message} ${isError ? styles.error : styles.success}`}>
            {message}
          </p>
        )}

        <div className={styles.links}>
          <p>
            <Link to="/login">Back to login</Link>
          </p>
        </div>
      </form>
    </div>
  );
}