import { useState } from "react";

function Settings() {
  const [theme, setTheme] = useState("Dark");
  const [notifications, setNotifications] = useState(true);
  const [autoSave, setAutoSave] = useState(true);

  function handleSave() {
    alert("Settings Saved Successfully!");
  }

  return (
    <div className="settings">

      <h1>Settings</h1>

      <div className="settings-card">

        {/* Platform Status */}
        <div className="settings-section">
          <h2>Platform Status</h2>

          <div className="settings-info-row">
            <span>System Mode</span>
            <strong>Demo Mode</strong>
          </div>

          <div className="settings-info-row">
            <span>EEG Hardware</span>
            <strong>Not Connected</strong>
          </div>

          <div className="settings-info-row">
            <span>Data Source</span>
            <strong>Representative EEG Dataset</strong>
          </div>

          <div className="settings-demo-box">
            <strong>Demo Mode Active</strong>
            <span>
              Live EEG hardware is not connected. Representative EEG
              recordings are used to demonstrate the Motor Imagery and
              Stress Analysis pipelines.
            </span>
          </div>
        </div>

        {/* Analysis Configuration */}
        <div className="settings-section">
          <h2>Analysis Configuration</h2>

          <div className="settings-info-row">
            <span>Motor Imagery Pipeline</span>
            <strong>22 Channels • 250 Hz</strong>
          </div>

          <div className="settings-info-row">
            <span>Stress Analysis Pipeline</span>
            <strong>32 Channels • 128 Hz</strong>
          </div>

          <div className="settings-info-row">
            <span>Motor Imagery Model</span>
            <strong>EEGNet</strong>
          </div>

          <div className="settings-info-row">
            <span>Stress Model</span>
            <strong>XGBoost</strong>
          </div>
        </div>

        {/* User Preferences */}
        <div className="settings-section">
          <h2>User Preferences</h2>

          <label>Theme</label>

          <select
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
          >
            <option>Dark</option>
            <option>Light</option>
          </select>

          <div className="checkbox">

            <input
              type="checkbox"
              checked={notifications}
              onChange={() =>
                setNotifications(!notifications)
              }
            />

            <span>Enable Notifications</span>

          </div>

          <div className="checkbox">

            <input
              type="checkbox"
              checked={autoSave}
              onChange={() =>
                setAutoSave(!autoSave)
              }
            />

            <span>Auto Save Reports</span>

          </div>
        </div>

        <button
          className="save-btn"
          onClick={handleSave}
        >
          Save Settings
        </button>

      </div>

    </div>
  );
}

export default Settings;