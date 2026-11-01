import { useNavigate } from "react-router-dom";

function Reports({ activePatient, miPrediction, stressPrediction }) {
  const navigate = useNavigate();

  const hasReport =
    activePatient && (miPrediction || stressPrediction);

  const downloadReport = () => {
    if (!hasReport) return;

    let report = "";

    report += "NEUROSENSE BCI PLATFORM\n";
    report += "PATIENT SESSION REPORT\n";
    report += "====================================\n\n";

    report += "PATIENT INFORMATION\n";
    report += "------------------------------------\n";
    report += `Patient ID: ${activePatient.id}\n`;
    report += `Patient Name: ${activePatient.name}\n`;
    report += `Age: ${activePatient.age}\n`;
    report += `Gender: ${activePatient.gender}\n`;
    report += `Condition: ${activePatient.condition}\n`;

    if (activePatient.notes) {
      report += `Session Notes: ${activePatient.notes}\n`;
    }

    report += "\n";

    if (miPrediction) {
      const confidence =
        Math.max(...Object.values(miPrediction.probabilities)) * 100;

      report += "MOTOR IMAGERY ANALYSIS\n";
      report += "------------------------------------\n";
      report += `Prediction: ${miPrediction.predicted_class}\n`;
      report += `Prediction Confidence: ${confidence.toFixed(2)}%\n\n`;
    }

    if (stressPrediction) {
      report += "STRESS ANALYSIS\n";
      report += "------------------------------------\n";
      report += `Detected State: ${stressPrediction.label}\n`;
      report += `Stress Probability: ${(
        stressPrediction.stress_probability * 100
      ).toFixed(2)}%\n`;
      report += `Non-Stress Probability: ${(
        stressPrediction.non_stress_probability * 100
      ).toFixed(2)}%\n\n`;
    }

    report += "SESSION STATUS\n";
    report += "------------------------------------\n";
    report += "Completed\n";
    report += "Data Source: Demo Dataset\n\n";

    report +=
      "Note: This prototype uses representative EEG dataset recordings because live EEG hardware is not currently connected.\n";

    const blob = new Blob([report], {
      type: "text/plain",
    });

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = `${activePatient.id}_NeuroSense_Report.txt`;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  };

  if (!hasReport) {
    return (
      <div className="report-page">
        <div className="report-empty">
          <h1>Session Reports</h1>
          <p>
            No completed analysis report is available yet.
          </p>

          <button
            className="stress-analyze-btn"
            onClick={() => navigate("/patients")}
          >
            Start New Session
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="report-page">

      <div className="report-header">
        <h1>Session Report</h1>
        <p>
          Summary of the completed NeuroSense patient analysis.
        </p>
      </div>

      <div className="report-card">

        <div className="report-title">
          <div>
            <span>NEUROSENSE</span>
            <h2>Patient Session Report</h2>
          </div>

          <div className="report-status">
            Completed
          </div>
        </div>

        <div className="report-section">
          <h3>Patient Information</h3>

          <div className="report-grid">
            <div>
              <span>Patient ID</span>
              <strong>{activePatient.id}</strong>
            </div>

            <div>
              <span>Patient Name</span>
              <strong>{activePatient.name}</strong>
            </div>

            <div>
              <span>Age</span>
              <strong>{activePatient.age}</strong>
            </div>

            <div>
              <span>Gender</span>
              <strong>{activePatient.gender}</strong>
            </div>

            <div className="report-full">
              <span>Condition</span>
              <strong>{activePatient.condition}</strong>
            </div>
          </div>
        </div>

        {miPrediction && (
          <div className="report-section">
            <h3>Motor Imagery Analysis</h3>

            <div className="analysis-result-box">
              <span>Predicted Motor Imagery</span>
              <strong>
                {miPrediction.predicted_class}
              </strong>
            </div>

            <div className="report-metric">
              <span>Prediction Confidence</span>
              <strong>
                {(
                  Math.max(
                    ...Object.values(miPrediction.probabilities)
                  ) * 100
                ).toFixed(2)}
                %
              </strong>
            </div>
          </div>
        )}

        {stressPrediction && (
          <div className="report-section">
            <h3>Stress Analysis</h3>

            <div className="analysis-result-box">
              <span>Detected State</span>
              <strong>
                {stressPrediction.label}
              </strong>
            </div>

            <div className="report-metric">
              <span>Stress Probability</span>
              <strong>
                {(
                  stressPrediction.stress_probability * 100
                ).toFixed(2)}
                %
              </strong>
            </div>

            <div className="report-metric">
              <span>Non-Stress Probability</span>
              <strong>
                {(
                  stressPrediction.non_stress_probability * 100
                ).toFixed(2)}
                %
              </strong>
            </div>
          </div>
        )}

        <div className="report-section">
          <h3>Session Information</h3>

          <div className="report-metric">
            <span>Data Source</span>
            <strong>Demo Dataset</strong>
          </div>

          <div className="report-note">
            This prototype uses representative EEG dataset recordings
            because live EEG hardware is not currently connected.
          </div>
        </div>

        <div className="report-actions">
          <button
            className="stress-analyze-btn"
            onClick={downloadReport}
          >
            Download Report
          </button>

          <button
            className="report-secondary-btn"
            onClick={() => navigate("/patients")}
          >
            New Patient Session
          </button>
        </div>

      </div>
    </div>
  );
}

export default Reports;