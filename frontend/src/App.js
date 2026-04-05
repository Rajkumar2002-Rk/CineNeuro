import React, { useState } from "react";
import { useDropzone } from "react-dropzone";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import { uploadTrailer, getJobStatus, getJobResult } from "./api";
import "./App.css";

function App() {
  const [status, setStatus] = useState("idle");
  const [jobId, setJobId] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
    const pollStatus = async (id) => {
    const poll = setInterval(async () => {
      try {
        const data = await getJobStatus(id);
        if (data.status === "completed") {
          clearInterval(poll);
          const resultData = await getJobResult(id);
          setResult(resultData);
          setStatus("completed");
        } else if (data.status === "failed") {
          clearInterval(poll);
          setError("Analysis failed");
          setStatus("failed");
        }
      } catch (err) {
        clearInterval(poll);
        setError("Connection lost");
        setStatus("failed");
      }
    }, 3000);
  };

  const onDrop = async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;
    try {
      setStatus("uploading");
      setError(null);
      const data = await uploadTrailer(file);
      setJobId(data.job_id);
      setStatus("processing");
      pollStatus(data.job_id);
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed");
      setStatus("failed");
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "video/*": [".mp4", ".avi", ".mkv", ".mov", ".webm"] },
    maxFiles: 1,
  });
    return (
    <div className="app">
      <h1>🎬 CineNeuro</h1>
      <p className="subtitle">AI-Powered Audience Intelligence Platform</p>

      {status === "idle" || status === "failed" ? (
        <div {...getRootProps()} className={`dropzone ${isDragActive ? "active" : ""}`}>
          <input {...getInputProps()} />
          <p>Drag & drop a movie trailer here, or click to select</p>
          <p className="hint">.mp4 .avi .mkv .mov .webm — Max 500MB</p>
        </div>
      ) : null}

      {error && <p className="error">{error}</p>}

      {status === "uploading" && <p className="loading">Uploading trailer...</p>}
      {status === "processing" && (
        <div className="loading">
          <p>Analyzing brain responses...</p>
          <p className="hint">This may take several minutes on CPU</p>
        </div>
      )}

      {status === "completed" && result && (
        <div className="results">
          <h2>Engagement Timeline</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={result.timeline}>
              <XAxis dataKey="second" label={{ value: "Second", position: "bottom" }} />
              <YAxis domain={[0, 1]} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="excitement" stroke="#e94560" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="fear" stroke="#800080" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="joy" stroke="#ffd700" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="suspense" stroke="#0080cc" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="boredom" stroke="#999999" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
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
                  <td>{b.difference_percent.toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>

          {result.pdf_url && (
            <a href={`http://localhost:8000${result.pdf_url}`} className="pdf-btn" download>
              Download PDF Report
            </a>
          )}
        </div>
      )}
    </div>
  );
}

export default App;


