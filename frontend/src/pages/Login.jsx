import { useState } from "react";
import { loginUser } from "../services/authApi";
import { Link, useNavigate } from "react-router-dom";
import styles from "../styles/Auth.module.css";

export default function Login() {
  const navigate = useNavigate();

  const [form, setForm] = useState({ email: "", password: "" });
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setMessage("");
    setIsError(false);
    setLoading(true);

    try {
      const data = await loginUser(form);
      localStorage.setItem("user", JSON.stringify(data.user));
      navigate("/dashboard");;
    } catch (error) {
      setIsError(true);
      setMessage(error.response?.data?.detail || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <form className={styles.card} onSubmit={handleLogin}>
        <div className={styles.brand}>Cockatoos</div>

        <h2 className={styles.title}>Welcome back</h2>
        <p className={styles.subtitle}>
          Login to continue your forensic image analysis.
        </p>

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

        <button className={styles.button} type="submit" disabled={loading}>
          {loading ? "Logging in..." : "Login"}
        </button>

        {message && (
          <p className={`${styles.message} ${isError ? styles.error : styles.success}`}>
            {message}
          </p>
        )}

        <div className={styles.links}>
          <p>
            Don’t have an account? <Link to="/signup">Create account</Link>
          </p>
          <p>
            <Link to="/forgot-password">Forgot password?</Link>
          </p>
        </div>
      </form>
    </div>
  );
}