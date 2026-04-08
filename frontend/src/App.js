import React, { useState, useEffect } from "react";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import { getDemos, getDemoResult } from "./api";
import "./App.css";

function App() {
  const [status, setStatus] = useState("idle");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [demos, setDemos] = useState([]);
  const [activeDemo, setActiveDemo] = useState(null);

  useEffect(() => {
    getDemos().then(setDemos).catch(() => {});
  }, []);

  const onSelectDemo = async (trailerName) => {
    try {
      setActiveDemo(trailerName);
      setStatus("processing");
      setError(null);
      const data = await getDemoResult(trailerName);
      setResult(data);
      setStatus("completed");
    } catch (err) {
      setError("Failed to load demo");
      setStatus("failed");
    }
  };

  return (
    <div className="app">
      <div className="hero">
        <h1>CineNeuro</h1>
        <p className="tagline">AI-Powered Audience Intelligence Platform</p>
        <p className="hero-desc">
          Predicting neural audience responses to movie trailers using
          <strong> TRIBE v2</strong> brain encoding, <strong>V-JEPA2</strong> vision,
          <strong> Wav2Vec-BERT</strong> audio, and <strong>Llama 3.2</strong> language models.
        </p>
        <div className="tech-badges">
          <span className="badge">Meta FAIR TRIBE v2</span>
          <span className="badge">20,484 Brain Vertices</span>
          <span className="badge">fMRI Prediction</span>
          <span className="badge">5 Emotion Channels</span>
        </div>
      </div>

      <div className="demo-selector">
        <h3>Explore Pre-Analyzed Trailers</h3>
        <p className="hint">Select a trailer to see brain-predicted audience engagement</p>
        <div className="demo-buttons">
          {demos.map((d) => (
            <button
              key={d.id}
              onClick={() => onSelectDemo(d.id)}
              className={`demo-btn ${activeDemo === d.id ? "active" : ""}`}
            >
              {d.title}
            </button>
          ))}
        </div>
      </div>

      {error && <p className="error">{error}</p>}

      {status === "processing" && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading analysis...</p>
        </div>
      )}

      {status === "completed" && result && (
        <div className="results">
          <div className="section-animate" style={{animationDelay: "0.1s"}}>
            <h2>Engagement Timeline</h2>
            <div className="chart-card">
              <ResponsiveContainer width="100%" height={350}>
                <LineChart data={result.timeline}>
                  <XAxis dataKey="second" stroke="#6b7b8d" label={{ value: "Second", position: "bottom", fill: "#6b7b8d" }} />
                  <YAxis domain={[0, 1]} stroke="#6b7b8d" />
                  <Tooltip
                    contentStyle={{ background: "rgba(13,27,42,0.95)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "8px" }}
                    labelStyle={{ color: "#ffffff" }}
                    itemStyle={{ color: "#cccccc" }}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="excitement" stroke="#e94560" strokeWidth={2} dot={false} isAnimationActive={true} animationDuration={1500} />
                  <Line type="monotone" dataKey="fear" stroke="#9b59b6" strokeWidth={2} dot={false} isAnimationActive={true} animationDuration={1800} />
                  <Line type="monotone" dataKey="joy" stroke="#f1c40f" strokeWidth={2} dot={false} isAnimationActive={true} animationDuration={2100} />
                  <Line type="monotone" dataKey="suspense" stroke="#3498db" strokeWidth={2} dot={false} isAnimationActive={true} animationDuration={2400} />
                  <Line type="monotone" dataKey="boredom" stroke="#7f8c8d" strokeWidth={2} dot={false} isAnimationActive={true} animationDuration={2700} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="section-animate" style={{animationDelay: "0.3s"}}>
            <h2>Top 3 Strongest Scenes</h2>
            <table className="scene-table strong">
              <thead>
                <tr><th>Time</th><th>Emotion</th><th>Score</th><th>Explanation</th></tr>
              </thead>
              <tbody>
                {result.top_scenes.map((s, i) => (
                  <tr key={i}><td>{s.timestamp}</td><td>{s.emotion}</td><td>{s.score.toFixed(2)}</td><td>{s.explanation}</td></tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="section-animate" style={{animationDelay: "0.5s"}}>
            <h2>Top 3 Weakest Scenes</h2>
            <table className="scene-table weak">
              <thead>
                <tr><th>Time</th><th>Emotion</th><th>Score</th><th>Explanation</th></tr>
              </thead>
              <tbody>
                {result.weak_scenes.map((s, i) => (
                  <tr key={i}><td>{s.timestamp}</td><td>{s.emotion}</td><td>{s.score.toFixed(2)}</td><td>{s.explanation}</td></tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="section-animate" style={{animationDelay: "0.7s"}}>
            <h2>Audience Personas</h2>
            <table className="persona-table">
              <thead>
                <tr><th>Persona</th><th>Engagement</th><th>Peak Moment</th></tr>
              </thead>
              <tbody>
                {result.personas.map((p, i) => (
                  <tr key={i}><td>{p.persona_name}</td><td>{p.overall_engagement.toFixed(2)}</td><td>{p.peak_moment}</td></tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="section-animate" style={{animationDelay: "0.9s"}}>
            <h2>Competitive Benchmarks</h2>
            <table className="benchmark-table">
              <thead>
                <tr><th>Baseline</th><th>Genre</th><th>Your Score</th><th>Baseline</th><th>Diff %</th></tr>
              </thead>
              <tbody>
                {result.benchmarks.map((b, i) => (
                  <tr key={i}>
                    <td>{b.baseline_title}</td><td>{b.genre}</td>
                    <td>{b.your_score.toFixed(2)}</td><td>{b.baseline_score.toFixed(2)}</td>
                    <td className={b.difference_percent >= 0 ? "positive" : "negative"}>
                      {b.difference_percent >= 0 ? "+" : ""}{b.difference_percent.toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="section-animate" style={{animationDelay: "1.1s"}}>
            {result.pdf_url && (
              <a href={result.pdf_url} className="pdf-btn" download>
                Download PDF Report
              </a>
            )}
          </div>
        </div>
      )}

      <div className="contact-section">
        <h3>Want Your Trailer Analyzed?</h3>
        <p>Our neural analysis requires GPU infrastructure. Drop me a message and I'll run your trailer through the TRIBE v2 pipeline.</p>
        <form className="contact-form" action="https://formspree.io/f/xojpbozl" method="POST">
          <input type="text" name="name" placeholder="Your Name" required />
          <input type="email" name="email" placeholder="Your Email" required />
          <textarea name="message" placeholder="Tell me about your trailer..." rows="4" required></textarea>
          <button type="submit" className="submit-btn">Send Message</button>
        </form>
      </div>

      <footer className="footer">
        <p>Built by Raj Kumar Nelluri | TRIBE v2 by Meta FAIR | Powered by PyTorch + FastAPI + React</p>
      </footer>
    </div>
  );
}

export default App;
