
"""
app.py

Flask backend for the NeuroSense BCI Platform.

Supports:
1. Motor Imagery prediction using EEGNet (.npy files).
2. Stress Classification using XGBoost (.mat files).

Run locally:
    python app.py

Open:
    http://localhost:5000
"""

import os
import io
import tempfile
import numpy as np

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

from inference import ModelRegistry
from stress_inference import predict_stress_from_mat


# --------------------------------------------------
# PATH CONFIGURATION
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")


# --------------------------------------------------
# FLASK INITIALIZATION
# --------------------------------------------------

app = Flask(__name__)

# We will restrict CORS to the deployed frontend
# after obtaining its public URL.
CORS(app)

# Load Motor Imagery models
registry = ModelRegistry(MODELS_DIR)


# --------------------------------------------------
# HOME ROUTE
# --------------------------------------------------

@app.route("/")
def index():
    return render_template(
        "index.html",
        model_names=registry.list_models()
    )


# --------------------------------------------------
# AVAILABLE MODELS
# --------------------------------------------------

@app.route("/models", methods=["GET"])
def list_models():
    return jsonify({
        "models": registry.list_models()
    })


# --------------------------------------------------
# MOTOR IMAGERY PREDICTION
# --------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():

    if "trial_file" not in request.files:
        return jsonify({
            "error": "No file uploaded. Attach a .npy trial under 'trial_file'."
        }), 400

    model_name = request.form.get("model_name")

    if not model_name:
        return jsonify({
            "error": "No model_name specified."
        }), 400

    file = request.files["trial_file"]

    try:
        buffer = io.BytesIO(file.read())
        raw_trial = np.load(buffer)

    except Exception:
        return jsonify({
            "error": "Could not read the uploaded .npy file."
        }), 400

    if raw_trial.ndim != 2:
        return jsonify({
            "error": (
                f"Expected a 2D array (channels, samples), "
                f"got shape {raw_trial.shape}."
            )
        }), 400

    try:
        model = registry.get(model_name)
        result = model.predict(raw_trial)

        return jsonify(result)

    except KeyError as e:
        return jsonify({
            "error": str(e)
        }), 404

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400

    except Exception:
        app.logger.exception("Motor Imagery prediction failed")

        return jsonify({
            "error": "Motor Imagery prediction failed."
        }), 500


# --------------------------------------------------
# STRESS CLASSIFICATION
# --------------------------------------------------

@app.route("/predict_stress", methods=["POST"])
def predict_stress():

    if "eeg_file" not in request.files:
        return jsonify({
            "error": "No EEG file uploaded. Attach a .mat file under 'eeg_file'."
        }), 400

    file = request.files["eeg_file"]

    if not file.filename:
        return jsonify({
            "error": "No filename provided."
        }), 400

    temp_path = None

    try:
        # Create a unique temporary file for each request.
        # This prevents simultaneous uploads from overwriting
        # each other's EEG recordings.

        with tempfile.NamedTemporaryFile(
            suffix=".mat",
            delete=False
        ) as temp_file:

            temp_path = temp_file.name
            file.save(temp_file)

        # Run the existing stress inference pipeline.
        result = predict_stress_from_mat(temp_path)

        return jsonify(result)

    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 400

    except Exception:
        app.logger.exception("Stress prediction failed")

        return jsonify({
            "error": "Stress prediction failed. Please check the uploaded EEG file."
        }), 500

    finally:
        # Always attempt to delete the temporary EEG file.
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                app.logger.exception(
                    "Could not delete temporary EEG file."
                )


# --------------------------------------------------
# LOCAL DEVELOPMENT SERVER
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
