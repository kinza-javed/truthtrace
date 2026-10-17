import { useState } from "react";
import { signupUser } from "../services/authApi";
import { Link } from "react-router-dom";
import styles from "../styles/Auth.module.css";

export default function Signup() {
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
  });

  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  const isStrongPassword = (password) => {
    return (
      password.length >= 8 &&
      /[A-Z]/.test(password) &&
      /[a-z]/.test(password) &&
      /\d/.test(password) &&
      /[!@#$%^&*(),.?":{}|<>_\-+=\[\]/\\]/.test(password)
    );
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setMessage("");
    setIsError(false);

    if (!isStrongPassword(form.password)) {
      setIsError(true);
      setMessage(
        "Password must be 8+ characters and include uppercase, lowercase, number, and special character."
      );
      return;
    }

    setLoading(true);

    try {
      const data = await signupUser(form);
      setMessage(
        data.message ||
          "Account created. Please check your email to verify your account."
      );
    } catch (error) {
      setIsError(true);
      setMessage(error.response?.data?.detail || "Signup failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <form className={styles.card} onSubmit={handleSignup}>
        <div className={styles.brand}>Cockatoos</div>

        <h2 className={styles.title}>Create account</h2>
        <p className={styles.subtitle}>
          Start analyzing images with AI-assisted forensic tools.
        </p>

        <input
          className={styles.input}
          name="username"
          placeholder="Username"
          value={form.username}
          onChange={handleChange}
          required
        />

        <input
          className={styles.input}
          name="email"
          type="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
          required
        />

        <input
          className={styles.input}
          name="password"
          type="password"
          placeholder="Password"
          value={form.password}
          onChange={handleChange}
          required
        />

        <p className={styles.smallText}>
          Password must be at least 8 characters and include uppercase,
          lowercase, number, and special character.
        </p>

        <button className={styles.button} type="submit" disabled={loading}>
          {loading ? "Creating account..." : "Create Account"}
        </button>

        {message && (
          <p className={`${styles.message} ${isError ? styles.error : styles.success}`}>
            {message}
          </p>
        )}

        <div className={styles.links}>
          <p>
            Already have an account? <Link to="/login">Login</Link>
          </p>
        </div>
      </form>
    </div>
  );
}