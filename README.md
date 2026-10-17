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