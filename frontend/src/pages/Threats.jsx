import styles from "./Threats.module.css";

export default function Threats() {
  const placeholderImg = (title) =>
    `data:image/svg+xml;utf8,${encodeURIComponent(`<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="675" viewBox="0 0 1200 675">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#111827"/>
      <stop offset="1" stop-color="#1f2937"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="675" fill="url(#g)"/>
  <rect x="60" y="60" width="1080" height="555" rx="24" fill="none" stroke="#374151" stroke-width="4"/>
  <text x="600" y="330" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="44" fill="#e5e7eb">${title}</text>
  <text x="600" y="390" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="24" fill="#9ca3af">Image placeholder (add file in public/images to replace)</text>
</svg>`)}`

  return (
    <div className={styles.page}>
      <div className={styles.container}>
        <h1>Threats of Deepfakes</h1>
        <p className={styles.subtitle}>
          Real-world deepfake cases demonstrating how AI-generated media can spread misinformation, manipulate public perception, and undermine trust.
        </p>

        {/* Case 1 */}
        <div className={styles.card}>
          <img src={placeholderImg("Case 1")} alt="Netanyahu Deepfake" />

          <div>
            <h2>Case 1: Netanyahu Image Manipulation (2026)</h2>

            <p>
              A widely circulated image falsely depicting Israeli Prime Minister Benjamin Netanyahu
              showed a visible anatomical anomaly — six fingers on one hand.
            </p>

            <ul>
              <li>🧠 AI-generated image artifact (extra fingers)</li>
              <li>🌐 Rapid viral spread across social platforms</li>
              <li>⚠️ Misled viewers into believing authenticity</li>
            </ul>

            <p className={styles.highlight}>
              This case highlights how subtle visual inconsistencies can go unnoticed,
              especially when images align with existing narratives.
            </p>
          </div>
        </div>

        {/* Case 2 */}
        <div className={styles.card}>
          <img src={placeholderImg("Case 2")} alt="Imran Khan Deepfake" />

          <div>
            <h2>Case 2: Imran Khan Jail Exercise Deepfake (Dec 2025)</h2>

            <p>
              A fabricated video surfaced showing former Prime Minister Imran Khan
              performing physical exercises inside jail.
            </p>

            <ul>
              <li>🎭 AI-generated body + face overlay</li>
              <li>📢 Spread widely via WhatsApp and social media</li>
              <li>🧾 No official verification or source confirmation</li>
            </ul>

            <p className={styles.highlight}>
              This deepfake was used to influence public perception about
              prison conditions and political narratives.
            </p>
          </div>
        </div>

        {/* Case 3 */}
        <div className={styles.card}>
          <img src={placeholderImg("Case 3")} alt="Rishi Sunak Deepfake" />

          <div>
            <h2>Case 3: Rishi Sunak Financial Scam Deepfake (2024)</h2>

            <p>
              Deepfake videos showed former UK Prime Minister Rishi Sunak promoting
              a fraudulent investment scheme allegedly “endorsed by Elon Musk.”
            </p>

            <ul>
              <li>📢 Reached over 400,000 users on Facebook</li>
              <li>💰 Used for financial fraud campaigns</li>
              <li>⚠️ Combined voice + face cloning</li>
            </ul>

            <p>
              These manipulated videos triggered major concerns among experts about
              the future of digital misinformation and election interference.
            </p>

            <p className={styles.highlight}>
              This case demonstrates how deepfakes can be weaponized for financial scams
              and political manipulation at scale.
            </p>
          </div>
        </div>

      </div>
    </div>
  );
}