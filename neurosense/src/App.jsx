import { Routes, Route, useLocation } from "react-router-dom";
import { useState } from "react";
import Dashboard from "./pages/Dashboard";
import EEGMonitor from "./pages/EEGMonitor";
import Reports from "./pages/Reports";
import Settings from "./pages/Settings";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import Rehabilitation from "./pages/Rehabilitation";
import "./App.css";

function Placeholder({ title, text }) { return <main className="page placeholder-page"><p className="eyebrow">NEURAHEAL MODULE</p><h1>{title}</h1><p className="muted">{text}</p><div className="panel placeholder-panel">This workspace is ready for your next research session.</div></main>; }
function App() { const location = useLocation(); const [prediction, setPrediction] = useState(null); return <div className="layout"><Sidebar /><div className="main">{location.pathname !== "/" && <Header /> }<Routes><Route path="/" element={<Dashboard />} /><Route path="/eeg" element={<EEGMonitor onPrediction={setPrediction} />} /><Route path="/reports" element={<Reports miPrediction={prediction} />} /><Route path="/settings" element={<Settings />} /><Route path="/rehabilitation" element={<Rehabilitation />} /><Route path="/about" element={<Placeholder title="About NeuraHeal" text="Reconnect. Recover. Rehabilitate. A research-grade interface for exploring EEG-based motor imagery." />} /></Routes></div></div>; }
export default App;
