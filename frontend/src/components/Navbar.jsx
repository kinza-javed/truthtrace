import { Link, useNavigate } from "react-router-dom";
import styles from "./Navbar.module.css";

export default function Navbar() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user"));

  const handleLogout = () => {
    localStorage.removeItem("user");
    navigate("/login");
  };

  return (
    <nav className={styles.navbar}>
      <Link to="/dashboard" className={styles.logo}>
        Cockatoos
      </Link>

      <div className={styles.links}>
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/home">Home</Link>
        <Link to="/detect">Detect</Link>
        <Link to="/history">History</Link>
        <Link to="/about">About</Link>
        <Link to="/privacy">Privacy</Link>
        <Link to="/profile">Profile</Link>
        <Link to="/settings">Detection Settings</Link>
        <Link to="/live-detection">Live Detection</Link>
        
        <span className={styles.user}>{user?.email}</span>

        <button onClick={handleLogout}>Logout</button>
      </div>
    </nav>
  );
}