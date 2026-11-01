import { FaBrain } from "react-icons/fa";

function Header() {
  return (
    <div className="header">
      <div className="header-icon">
        <FaBrain />
      </div>

      <h1>NeuroSense BCI Platform</h1>

      <p>
        AI-Powered EEG Neurorehabilitation & Motor Imagery Analysis
      </p>

      <div className="header-line"></div>
    </div>
  );
}

export default Header;