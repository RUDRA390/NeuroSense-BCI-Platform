import io
import os
import tempfile

import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS

from Mentor.inference import ModelRegistry
from Mentor.stress_inference import predict_stress_from_mat

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "Mentor", "models")

app = Flask(__name__)
CORS(app)
registry = ModelRegistry(MODELS_DIR)


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/predict")
def predict():
    uploaded_file = request.files.get("trial_file")
    model_name = request.form.get("model_name")

    if uploaded_file is None or not uploaded_file.filename:
        return jsonify({"error": "Upload a .npy EEG trial as trial_file."}), 400
    if not model_name:
        return jsonify({"error": "model_name is required."}), 400

    try:
        raw_trial = np.load(io.BytesIO(uploaded_file.read()))
        if raw_trial.ndim != 2:
            return jsonify({
                "error": f"Expected a 2D array (channels, samples), got shape {raw_trial.shape}."
            }), 400
        return jsonify(registry.get(model_name).predict(raw_trial))
    except (KeyError, ValueError) as error:
        return jsonify({"error": str(error)}), 422
    except Exception:
        app.logger.exception("Motor imagery prediction failed")
        return jsonify({"error": "Motor imagery prediction failed."}), 500


@app.post("/predict_stress")
def predict_stress():
    uploaded_file = request.files.get("eeg_file")
    if uploaded_file is None or not uploaded_file.filename:
        return jsonify({"error": "Upload an EEG .mat file as eeg_file."}), 400

    if not uploaded_file.filename.lower().endswith(".mat"):
        return jsonify({"error": "Only .mat EEG files are supported."}), 415

    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".mat", delete=False) as temporary_file:
            uploaded_file.save(temporary_file)
            temporary_path = temporary_file.name

        return jsonify(predict_stress_from_mat(temporary_path))
    except (KeyError, ValueError, FileNotFoundError) as error:
        return jsonify({"error": str(error)}), 422
    finally:
        if temporary_path:
            try:
                os.remove(temporary_path)
            except OSError:
                pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
