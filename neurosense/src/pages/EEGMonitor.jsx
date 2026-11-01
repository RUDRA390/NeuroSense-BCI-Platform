import { useState } from "react";
import { useNavigate } from "react-router-dom";

function EEGMonitor({ onPrediction, activePatient }) {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handlePredict() {
    if (!file) {
      alert("Please upload an EEG trial.");
      return;
    }

    const formData = new FormData();
    formData.append("trial_file", file);
    formData.append("model_name", "generic_eegnet_package");

    setLoading(true);

    try {
      const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

const response = await fetch(`${API_URL}/predict`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.error) {
        alert(data.error);
      } else {
        setPrediction(data);

        if (onPrediction) {
          onPrediction(data);
        }
      }
    } catch (err) {
      alert("Cannot connect to Flask backend.");
    }

    setLoading(false);
  }

  return (
    <div className="mi-page">

      <h1 className="mi-title">
        🧠 Motor Imagery Prediction
      </h1>

      <p>
        Upload an EEG trial (.npy) to predict the imagined movement.
      </p>

      <div className="mi-card">

        <input
          type="file"
          accept=".npy"
          onChange={(e) => setFile(e.target.files[0])}
        />

        <button
          className="predict-btn"
          onClick={handlePredict}
          disabled={loading}
        >
          {loading ? "Predicting..." : "Predict"}
        </button>

      </div>

      {prediction && (

        <div className="result-card">

          <h2>Prediction Result</h2>

          <h1>{prediction.predicted_class}</h1>

          <p>
            Model:
            <strong> {prediction.model_used}</strong>
          </p>

          <h3>Class Probabilities</h3>

          {Object.entries(prediction.probabilities).map(([name, value]) => (

            <div key={name} className="probability">

              <div className="prob-label">
                {name}
                <span>{(value * 100).toFixed(2)}%</span>
              </div>

              <div className="bar">

                <div
                  className="fill"
                  style={{ width: `${value * 100}%` }}
                />

              </div>

            </div>

          ))}
          {!activePatient?.analyses?.stressAnalysis && (
            <button
              className="stress-analyze-btn"
              onClick={() => navigate("/reports")}
            >
              View Session Report
            </button>
          )}
          {activePatient?.analyses?.stressAnalysis && (
            <button
              className="stress-analyze-btn"
              onClick={() => navigate("/stress")}
            >
              Continue to Stress Analysis
            </button>
          )}

        </div>

      )}

    </div>
  );
}

export default EEGMonitor;