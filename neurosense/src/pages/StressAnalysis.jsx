import { useState } from "react";
import { useNavigate } from "react-router-dom";

function StressAnalysis({ onPrediction }) {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    setFile(selectedFile || null);
    setResult(null);
    setError("");
  };

  const handleAnalyze = async () => {
    if (!file) {
      setError("Please select an EEG .mat file first.");
      return;
    }

    setLoading(true);
    setResult(null);
    setError("");

    try {
      const formData = new FormData();
      formData.append("eeg_file", file);

      const API_URL = import.meta.env.VITE_API_URL || "/api";

      const response = await fetch(
        `${API_URL}/predict_stress`,
  {
    method: "POST",
    body: formData,
  }
);

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Stress prediction failed.");
      }

      setResult(data);
      if (onPrediction) {
        onPrediction(data);
      }
    } catch (err) {
      setError(err.message || "Could not connect to the stress analysis server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="stress-page">
      <div className="stress-header">
        <h1>Stress Analysis</h1>
        <p>
          Upload an EEG recording to analyze the current stress state.
        </p>
      </div>

      <div className="stress-card">
        <h2>EEG Stress Detection</h2>

        <p className="stress-description">
          Upload a raw EEG recording in <strong>.mat</strong> format.
          The system will preprocess the signal, extract EEG features,
          and classify the recording as Stress or Non-Stress.
        </p>

        <div className="upload-area">
          <input
            type="file"
            accept=".mat"
            onChange={handleFileChange}
          />

          {file && (
            <p className="selected-file">
              Selected: <strong>{file.name}</strong>
            </p>
          )}
        </div>

        <button
          className="stress-analyze-btn"
          onClick={handleAnalyze}
          disabled={loading || !file}
        >
          {loading ? "Analyzing..." : "Analyze Stress"}
        </button>

        {error && (
          <div className="stress-error">
            {error}
          </div>
        )}

        {result && (
          <div className="stress-result">
            <h2>Analysis Result</h2>

            <div className="stress-main-result">
              <span>Detected State</span>
              <strong>{result.label}</strong>
            </div>

            <div className="stress-probabilities">
              <div className="probability-row">
                <div className="probability-label">
                  <span>Stress</span>
                  <span>
                    {(result.stress_probability * 100).toFixed(2)}%
                  </span>
                </div>

                <div className="probability-bar">
                  <div
                    className="probability-fill"
                    style={{
                      width: `${result.stress_probability * 100}%`,
                    }}
                  />
                </div>
              </div>

              <div className="probability-row">
                <div className="probability-label">
                  <span>Non-Stress</span>
                  <span>
                    {(result.non_stress_probability * 100).toFixed(2)}%
                  </span>
                </div>

                <div className="probability-bar">
                  <div
                    className="probability-fill"
                    style={{
                      width: `${result.non_stress_probability * 100}%`,
                    }}
                  />
                </div>
              </div>
            </div>
            <button
            className="stress-analyze-btn"
            onClick={() => navigate("/reports")}
            >
            View Session Report
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default StressAnalysis;
