import os
import tempfile

from flask import Flask, jsonify, request
from flask_cors import CORS

from Mentor.stress_inference import predict_stress_from_mat

app = Flask(__name__)
CORS(app)


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


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
