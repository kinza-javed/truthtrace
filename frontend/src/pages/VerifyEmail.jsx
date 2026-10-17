import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { verifyEmail } from "../services/authApi";
import styles from "../styles/Auth.module.css";

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");

  const [message, setMessage] = useState("Verifying your email...");
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    const verify = async () => {
      if (!token) {
        setIsError(true);
        setMessage("Invalid verification link.");
        return;
      }

      try {
        const data = await verifyEmail(token);
        setIsError(false);
        setMessage(data.message || "Email verified successfully. You can now login.");
      } catch (error) {
        setIsError(true);
        setMessage(
          "This verification link is invalid, expired, or already used. If your email is already verified, please login."
        );
      }
    };

    verify();
  }, [token]);

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.brand}>Cockatoos</div>

        <h2 className={styles.title}>Email verification</h2>

        <p className={`${styles.message} ${isError ? styles.error : styles.success}`}>
          {message}
        </p>

        <div className={styles.links}>
          <p>
            <Link to="/login">Go to login</Link>
          </p>
        </div>
      </div>
    </div>
  );
}