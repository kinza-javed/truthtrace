import { useRef, useState } from "react";
import Navbar from "../components/Navbar";
import detectImage from "../services/detectApi";
import styles from "./LiveDetection.module.css";

export default function LiveDetection() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const [streaming, setStreaming] = useState(false);
  const [capturedImage, setCapturedImage] = useState(null);
  const [result, setResult] = useState(null);
  const [message, setMessage] = useState("");

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = stream;
      setStreaming(true);
      setMessage("");
    } catch {
      setMessage("Camera access denied or unavailable.");
    }
  };

  const captureImage = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    canvas.toBlob((blob) => {
      const file = new File([blob], "live_capture.jpg", {
        type: "image/jpeg",
      });

      setCapturedImage(file);
      setMessage("Frame captured. Click Analyze Snapshot.");
    }, "image/jpeg");
  };

  const analyzeSnapshot = async () => {
    if (!capturedImage) {
      setMessage("Please capture a frame first.");
      return;
    }

    try {
      setMessage("Analyzing captured frame...");
      const data = await detectImage(capturedImage);
      setResult(data);
      setMessage("Analysis complete.");
    } catch (err) {
      setMessage(
        err.response?.data?.detail ||
          "Analysis failed. Capture a clearer face image."
      );
    }
  };

  return (
    <>
      <Navbar />

      <main className={styles.page}>
        <section className={styles.hero}>
          <p className={styles.kicker}>Live Camera Snapshot</p>
          <h1>Live Detection</h1>
          <p>
            Capture a webcam frame and analyze it using the same forensic
            detection pipeline.
          </p>
        </section>

        <section className={styles.card}>
          <div className={styles.cameraBox}>
            <video ref={videoRef} autoPlay playsInline className={styles.video} />
            <canvas ref={canvasRef} style={{ display: "none" }} />
          </div>

          <div className={styles.actions}>
            <button onClick={startCamera}>
              {streaming ? "Camera Active" : "Start Camera"}
            </button>

            <button onClick={captureImage} disabled={!streaming}>
              Capture Frame
            </button>

            <button onClick={analyzeSnapshot} disabled={!capturedImage}>
              Analyze Snapshot
            </button>
          </div>

          {message && <p className={styles.message}>{message}</p>}
        </section>

        {result && (
          <section className={styles.resultCard}>
            <h2>Result: {result.prediction}</h2>
            <p>Confidence: {(result.confidence * 100).toFixed(2)}%</p>
            <p>Faces Detected: {result.faces_detected}</p>

            {result.report && (
              <a
                href={`http://127.0.0.1:8000${result.report}`}
                target="_blank"
                rel="noreferrer"
              >
                Download Report
              </a>
            )}
          </section>
        )}
      </main>
    </>
  );
}