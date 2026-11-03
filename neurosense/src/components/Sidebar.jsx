import { NavLink } from "react-router-dom";
import { FaChartLine, FaCloudUploadAlt, FaCogs, FaFileAlt, FaHeartbeat, FaHistory, FaHome, FaInfoCircle, FaWaveSquare } from "react-icons/fa";

const links = [
  ["/", FaHome, "Dashboard"],
  ["/eeg", FaWaveSquare, "EEG Analysis"],
  ["/eeg", FaCloudUploadAlt, "Upload EEG"],
  ["/eeg", FaChartLine, "Motor Imagery"],
  ["/rehabilitation", FaHeartbeat, "Rehabilitation"],
  ["/reports", FaHistory, "Analysis History"],
  ["/about", FaInfoCircle, "About NeuraHeal"],
  ["/settings", FaCogs, "Settings"],
];

function Sidebar() {
  return <aside className="sidebar">
    <div>
      <div className="brand"><span className="brand-mark"><FaWaveSquare /></span><div><strong>NeuraHeal</strong><small>BCI NEUROREHABILITATION</small></div></div>
      <nav aria-label="Primary navigation"><p className="nav-label">WORKSPACE</p><ul>{links.map(([to, Icon, label]) => <li key={label}><NavLink to={to} end={to === "/"}><Icon /><span>{label}</span></NavLink></li>)}</ul></nav>
    </div>
    <div className="sidebar-footer"><span className="online-dot" /> <div><strong>System operational</strong><small>Inference engine ready</small></div></div>
  </aside>;
}
export default Sidebar;
