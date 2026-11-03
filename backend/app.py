import csv
import os
import tempfile
import time
from datetime import datetime, timezone

import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename

from Mentor.inference import ModelRegistry

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024
CORS(app, resources={r"/api/*": {"origins": os.getenv("FRONTEND_ORIGIN", "*")}})
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "Mentor", "models")
registry = ModelRegistry(MODELS_DIR)
history = []
ALLOWED_EXTENSIONS = {"npy", "csv"}


def load_signal(path, extension):
    if extension == "npy":
        signal = np.load(path, allow_pickle=False)
    elif extension == "csv":
        signal = np.loadtxt(path, delimiter=",", dtype=np.float32)
    else:
        raise ValueError("This deployment supports .npy and .csv recordings. EDF/FIF/SET require an MNE loader and montage mapping.")
    if signal.ndim != 2:
        raise ValueError(f"Expected a 2D signal array (channels, samples), received shape {signal.shape}.")
    return signal.astype(np.float32)


def analyze_file(uploaded_file):
    filename = secure_filename(uploaded_file.filename or "")
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported EEG format. Use .npy or .csv for the packaged EEGNet pipeline.")
    started = time.perf_counter()
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=f".{extension}", delete=False) as temp:
            uploaded_file.save(temp)
            temporary_path = temp.name
        signal = load_signal(temporary_path, extension)
        if not registry.models:
            raise RuntimeError("No packaged inference model is available in Mentor/models.")
        model = registry.get(request.form.get("model_name", "generic_eegnet_package"))
        result = model.predict(signal)
        result.update({"filename": filename, "n_channels": int(signal.shape[0]), "n_samples": int(signal.shape[1]), "processing_ms": round((time.perf_counter() - started) * 1000), "status": "completed", "analyzed_at": datetime.now(timezone.utc).isoformat()})
        history.insert(0, result.copy())
        del history[20:]
        return result
    finally:
        if temporary_path and os.path.exists(temporary_path):
            os.remove(temporary_path)


@app.get("/api/health")
@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "neuraheal-inference", "models_loaded": registry.list_models()})


@app.post("/api/analyze")
@app.post("/api/upload")
def analyze():
    uploaded_file = request.files.get("trial_file") or request.files.get("eeg_file") or request.files.get("file")
    if not uploaded_file or not uploaded_file.filename:
        return jsonify({"error": "Attach an EEG recording using trial_file."}), 400
    try:
        return jsonify(analyze_file(uploaded_file))
    except (ValueError, KeyError) as error:
        return jsonify({"error": str(error)}), 422
    except Exception as error:
        app.logger.exception("EEG analysis failed")
        return jsonify({"error": "The recording could not be processed. Check its shape and model compatibility."}), 500


@app.get("/api/history")
def get_history():
    return jsonify({"items": history})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
