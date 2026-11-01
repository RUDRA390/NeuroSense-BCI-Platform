import { Routes, Route, useLocation } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Patients from "./pages/Patients";
import EEGMonitor from "./pages/EEGMonitor";
import Reports from "./pages/Reports";
import Settings from "./pages/Settings";
import StressAnalysis from "./pages/StressAnalysis";

import Sidebar from "./components/Sidebar";
import Header from "./components/Header";

import { useState } from "react";

import "./App.css";

function App() {
  const location = useLocation();
  const [eegData, setEegData] = useState({
    status: "🟢 Connected",
    load: "Optimal",
    attention: "87%",
    emotion: "😊 Calm",
    engagement: "91%",
    therapy: "Running",
  });
  const [miPrediction, setMiPrediction] = useState(null);
  const [stressPrediction, setStressPrediction] = useState(null);
  const [activePatient, setActivePatient] = useState(null);
  const handleStartSession = (patient) => {
    setMiPrediction(null);
    setStressPrediction(null);
    setActivePatient(patient);
  };
  return (
    <div className="layout">

      <Sidebar />

      <div className="main">

        {location.pathname !== "/" && <Header />}

        <Routes>

          <Route
            path="/"
            element={
              <Dashboard
                eegData={eegData}
                miPrediction={miPrediction}
                stressPrediction={stressPrediction}
                activePatient={activePatient}
              />
            }
          />

          <Route
            path="/patients"
            element={
              <Patients
                onStartSession={handleStartSession}
              />
            }
          />

          <Route
            path="/eeg"
            element={
              <EEGMonitor
                onPrediction={setMiPrediction}
                activePatient={activePatient}
              />
            }
          />

          <Route
            path="/stress"
            element={
              <StressAnalysis
                onPrediction={setStressPrediction}
              />
            }
          />

          <Route
            path="/reports"
            element={
              <Reports
                activePatient={activePatient}
                miPrediction={miPrediction}
                stressPrediction={stressPrediction}
              />
            }
          />

          <Route
            path="/settings"
            element={<Settings />}
          />

        </Routes>

      </div>

    </div>
  );
}

export default App;