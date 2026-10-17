# Setup

## Backend

Create and activate a Python virtual environment, then install the backend dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create a local `.env` file for the application's configuration and credentials. Do not commit this file.

The model weights are stored with Git LFS. Install Git LFS before cloning, then run `git lfs pull` if the model files are not downloaded automatically. The ONNX model is at `export/cockatoos_vitb32_best.onnx`; the Grad-CAM checkpoint is at `exports/phase3_best.pt`.

## Adaptive human review

After each analysis, the system creates a separate review case. Cases are routed to **Needs review** when the highest model score is below `0.75`, detected faces disagree on the prediction, or the uploader marks the case as high-impact. The score threshold is a conservative routing heuristic, not a calibrated probability of authenticity. Other cases remain provisional and may still be reviewed.

Open the analysis from **History** to:

- Ask for ELA/noise evidence for possible splicing or inconsistent lighting, inspect existing Grad-CAM evidence for a face, or review available EXIF metadata.
- Mark an existing case high-impact, which requires human review regardless of model score.
- Record one of the three evidence-backed human verdicts with a required reason.
- Inspect the append-only event history, including the original AI evidence, reviewer actions, timestamps, and verdict history.

Reviewer decisions are stored separately from the immutable AI prediction. The current app attributes a reviewer to the signed-in account ID and restricts review to the account that created the analysis; the app's existing login system does not issue server-verified authentication tokens, so this attribution is not a substitute for authenticated forensic case management.

## Frontend

From the project root, install the frontend dependencies and start the React app:

```bash
npm install
npm start
```

To create a production build, run:

```bash
npm run build
```