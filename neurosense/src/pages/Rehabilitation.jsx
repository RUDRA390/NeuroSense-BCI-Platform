import { useMemo, useState } from "react";

const exercises = [
  { id: "left", label: "Left-hand imagery", cue: "Imagine gently closing your left hand", color: "cyan" },
  { id: "right", label: "Right-hand imagery", cue: "Imagine gently closing your right hand", color: "violet" },
  { id: "feet", label: "Feet imagery", cue: "Imagine flexing both feet", color: "green" },
];

function Rehabilitation() {
  const [active, setActive] = useState("left");
  const [running, setRunning] = useState(false);
  const [sessions, setSessions] = useState(3);
  const selected = useMemo(() => exercises.find((item) => item.id === active), [active]);

  const finishSession = () => {
    setRunning(false);
    setSessions((value) => value + 1);
  };

  return (
    <main className="page rehab-page">
      <div className="page-heading-row">
        <div><p className="eyebrow">RESEARCH MODULE / REHABILITATION</p><h1>Train the signal.</h1><p className="muted">Turn motor imagery into guided visual feedback for BCI-assisted rehabilitation research.</p></div>
        <div className="research-badge">Research prototype</div>
      </div>
      <section className="rehab-grid">
        <div className="panel exercise-panel">
          <div className="panel-header"><div><span className="panel-kicker">TODAY&apos;S EXERCISE</span><h2>{selected.label}</h2></div><span className={`status-dot ${running ? "live" : ""}`}>{running ? "LIVE" : "READY"}</span></div>
          <div className={`neural-orb ${selected.color} ${running ? "is-running" : ""}`}><div className="orb-core">{running ? "FOCUS" : "BEGIN"}</div></div>
          <p className="exercise-cue">{selected.cue}</p>
          <p className="muted small">Keep your attention steady. The visual field responds to a future classifier stream when an EEG session is connected.</p>
          <div className="exercise-actions"><button className="primary-button" onClick={() => setRunning((value) => !value)}>{running ? "Pause exercise" : "Start exercise"}</button>{running && <button className="secondary-button" onClick={finishSession}>Complete session</button>}</div>
        </div>
        <aside className="panel exercise-list"><div className="panel-header"><div><span className="panel-kicker">PROTOCOL</span><h2>Imagery sets</h2></div></div>{exercises.map((exercise) => <button key={exercise.id} className={`exercise-option ${active === exercise.id ? "selected" : ""}`} onClick={() => { setActive(exercise.id); setRunning(false); }}><span className={`option-icon ${exercise.color}`}>{exercise.id === "left" ? "L" : exercise.id === "right" ? "R" : "F"}</span><span><strong>{exercise.label}</strong><small>{exercise.id === active ? "Current focus" : "2 min guided set"}</small></span><span className="option-arrow">→</span></button>)}</aside>
      </section>
      <section className="rehab-stats"><div className="panel stat-panel"><span className="panel-kicker">WEEKLY STREAK</span><strong>{sessions} sessions</strong><span className="muted">+1 from last week</span></div><div className="panel stat-panel"><span className="panel-kicker">SESSION TARGET</span><strong>10 min</strong><span className="muted">Low-pressure practice</span></div><div className="panel stat-panel"><span className="panel-kicker">SAFETY NOTE</span><strong>Not clinical care</strong><span className="muted">For research demonstration only</span></div></section>
    </main>
  );
}
export default Rehabilitation;
