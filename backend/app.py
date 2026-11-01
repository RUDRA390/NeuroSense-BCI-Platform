from flask import Flask, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

@app.route("/predict")
def predict():

    data = {
        "status": "Connected",
        "load": random.choice(["Inactive", "Optimal", "Burnout"]),
        "attention": f"{random.randint(70,99)}%",
        "emotion": random.choice(["😊 Calm", "😟 Stressed"]),
        "engagement": f"{random.randint(65,98)}%",
        "therapy": random.choice([
            "Running",
            "Adjusting",
            "Completed"
        ])
    }

    return jsonify(data)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)