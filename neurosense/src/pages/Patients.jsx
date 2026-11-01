import { useState } from "react";
import { useNavigate } from "react-router-dom";

function Patients({ onStartSession }) {
  const navigate = useNavigate();

  const [patientId, setPatientId] = useState("");
  const [name, setName] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("");
  const [condition, setCondition] = useState("");
  const [notes, setNotes] = useState("");
  const [motorImagery, setMotorImagery] = useState(false);
  const [stressAnalysis, setStressAnalysis] = useState(false);

  const handleStartSession = (event) => {
    event.preventDefault();

    if (!patientId || !name || !age || !gender || !condition) {
      alert("Please fill in all required patient details.");
      return;
    }

    if (!motorImagery && !stressAnalysis) {
      alert("Please select at least one analysis.");
      return;
    }

    const patient = {
      id: patientId,
      name,
      age: Number(age),
      gender,
      condition,
      notes,
      sessionStatus: "Active",
      dataSource: "Demo Dataset",
      analyses: {
        motorImagery,
        stressAnalysis,
      },
    };

    if (onStartSession) {
      onStartSession(patient);
    }

    if (motorImagery) {
      navigate("/eeg");
    } else {
      navigate("/stress");
    }
  };

  return (
    <div className="patient-session-page">
      <div className="stress-header">
        <h1>Start Patient Session</h1>

        <p>
          Enter patient information before starting EEG-based analysis.
        </p>
      </div>

      <div className="stress-card">
        <h2>Patient Information</h2>

        <form onSubmit={handleStartSession}>
          <div className="form-grid">

            <div className="form-group">
              <label>Patient ID *</label>
              <input
                type="text"
                placeholder="e.g. P001"
                value={patientId}
                onChange={(e) => setPatientId(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Patient Name *</label>
              <input
                type="text"
                placeholder="Enter patient name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Age *</label>
              <input
                type="number"
                min="1"
                max="120"
                placeholder="Enter age"
                value={age}
                onChange={(e) => setAge(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Gender *</label>
              <select
                value={gender}
                onChange={(e) => setGender(e.target.value)}
              >
                <option value="">Select gender</option>
                <option value="Female">Female</option>
                <option value="Male">Male</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div className="form-group">
              <label>Condition *</label>
              <select
                value={condition}
                onChange={(e) => setCondition(e.target.value)}
              >
                <option value="">Select condition</option>
                <option value="Stroke Rehabilitation">
                  Stroke Rehabilitation
                </option>
                <option value="Traumatic Brain Injury">
                  Traumatic Brain Injury
                </option>
                <option value="Parkinson's Disease">
                  Parkinson's Disease
                </option>
                <option value="Aphasia Rehabilitation">
                  Aphasia Rehabilitation
                </option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div className="form-group form-group-full">
              <label>Session Notes</label>
              <textarea
                placeholder="Add optional clinical/session notes..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows="4"
              />
            </div>

          </div>

          <div className="analysis-selection">
            <h3>Select Analysis</h3>

            <label className="analysis-option">
              <input
                type="checkbox"
                checked={motorImagery}
                onChange={(e) => setMotorImagery(e.target.checked)}
              />
              <span>Motor Imagery</span>
            </label>

            <label className="analysis-option">
              <input
                type="checkbox"
                checked={stressAnalysis}
                onChange={(e) => setStressAnalysis(e.target.checked)}
              />
              <span>Stress Analysis</span>
            </label>
          </div>

          <div className="demo-mode-box">
            <strong>Demo Mode</strong>

            <span>
              EEG hardware is not connected. Dataset recordings will be used
              to demonstrate the Motor Imagery and Stress Analysis pipelines.
            </span>
          </div>

          <button
            type="submit"
            className="stress-analyze-btn"
          >
            Start Session
          </button>
        </form>
      </div>
    </div>
  );
}

export default Patients;