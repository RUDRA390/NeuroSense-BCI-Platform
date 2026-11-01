from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "project": "NeuroSense BCI Platform",
        "message": "Backend API is running"
    })