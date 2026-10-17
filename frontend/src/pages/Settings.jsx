import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import styles from "./Settings.module.css";

export default function Settings() {
  const [settings, setSettings] = useState({
    allowMultipleFaces: true,
    enableReportGeneration: true,
  });

  useEffect(() => {
    const saved = localStorage.getItem("detectionSettings");
    if (saved) setSettings(JSON.parse(saved));
  }, []);

  const updateSetting = (key) => {
    const updated = { ...settings, [key]: !settings[key] };
    setSettings(updated);
    localStorage.setItem("detectionSettings", JSON.stringify(updated));
  };

  return (
    <>
      <Navbar />

      <main className={styles.page}>
        <section className={styles.hero}>
          <p className={styles.kicker}>Detection Preferences</p>
          <h1>Settings</h1>
          <p>
            Control how Cockatoos handles face analysis and report generation.
          </p>
        </section>

        <section className={styles.card}>
          <div className={styles.settingRow}>
            <div>
              <h2>Allow Multiple Face Analysis</h2>
              <p>
                If enabled, the system analyzes every detected face. If disabled,
                only the most prominent face is analyzed.
              </p>
            </div>

            <label className={styles.switch}>
              <input
                type="checkbox"
                checked={settings.allowMultipleFaces}
                onChange={() => updateSetting("allowMultipleFaces")}
              />
              <span></span>
            </label>
          </div>

          <div className={styles.settingRow}>
            <div>
              <h2>Enable Report Generation</h2>
              <p>
                If enabled, the system generates a downloadable PDF forensic
                report after analysis.
              </p>
            </div>

            <label className={styles.switch}>
              <input
                type="checkbox"
                checked={settings.enableReportGeneration}
                onChange={() => updateSetting("enableReportGeneration")}
              />
              <span></span>
            </label>
          </div>
        </section>
      </main>
    </>
  );
}