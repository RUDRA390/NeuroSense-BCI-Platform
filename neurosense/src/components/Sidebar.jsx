import { NavLink } from "react-router-dom";

import {
  FaHome,
  FaUserInjured,
  FaChartBar,
  FaCog,
  FaBrain,
} from "react-icons/fa";

function Sidebar() {
  return (
    <div className="sidebar">

      <div className="logo">
        <FaBrain className="logo-icon" />
        <div>
          <h2>NeuroSense</h2>
          <span>BCI Platform</span>
        </div>
      </div>

      <ul>

        <li>
          <NavLink to="/">
            <FaHome />
            <span>Home</span>
          </NavLink>
        </li>

        <li>
          <NavLink to="/patients">
            <FaUserInjured />
            <span>Patients</span>
          </NavLink>
        </li>

        <li>
          <NavLink to="/reports">
            <FaChartBar />
            <span>Reports</span>
          </NavLink>
        </li>

        <li>
          <NavLink to="/settings">
            <FaCog />
            <span>Settings</span>
          </NavLink>
        </li>

      </ul>

    </div>
  );
}

export default Sidebar;