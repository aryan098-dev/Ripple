
import React, { useEffect, useState } from "react";
import "./App.css";

const API_URL = import.meta.env.DEV
  ? "http://127.0.0.1:8000"
  : "/api";

function App() {
  const [active, setActive] = useState("Overview");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const navItems = [
    ["Overview", "◫"],
    ["Impact Analysis", "⌘"],
    ["Test Recommendations", "✓"],
    ["Activity", "◷"],
  ];

  async function fetchAnalysis() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(
  import.meta.env.DEV ? `${API_URL}/analyze` : `${API_URL}/analyze`,
  {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }

      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err.message || "Unable to connect to Ripple API.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchAnalysis();
  }, []);

  const summary = data?.summary || {};
  const changedFiles = data?.changed_files || [];
  const impactedModules = Object.entries(
    data?.impacted_modules || {}
  );
  const recommendations = data?.recommendations || [];
  const testResults = data?.test_results || {};

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">R</div>
          <div>
            <h2>Ripple</h2>
            <span>CHANGE INTELLIGENCE</span>
          </div>
        </div>

        <div className="workspace-label">WORKSPACE</div>

        <div className="repo-box">
          <span className="repo-icon">⌘</span>
          <div>
            <strong>My Workspace</strong>
            <small>Developer environment</small>
          </div>
        </div>

        <div className="workspace-label nav-label">ANALYSIS</div>

        <nav>
          {navItems.map(([name, icon]) => (
            <button
              key={name}
              className={`nav-item ${active === name ? "active" : ""}`}
              onClick={() => setActive(name)}
            >
              <span>{icon}</span>
              {name}
              {name === "Impact Analysis" && (
                <small className="nav-count">
                  {impactedModules.length}
                </small>
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className={`status-dot ${error ? "error" : ""}`} />
          <span>{error ? "API connection failed" : "Analysis engine ready"}</span>
          <small>v1.0.0</small>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <span className="breadcrumb">Workspace /</span>
            <strong>{active}</strong>
          </div>

          <div className="top-actions">
            <span className="online">
              <i />
              {error ? "Offline" : "System online"}
            </span>
            <div className="avatar">A</div>
          </div>
        </header>

        <section className="page-content">
          <div className="page-heading">
            <div>
              <span className="eyebrow">
                DEVELOPER INTELLIGENCE PLATFORM
              </span>
              <h1>
                {active === "Overview" ? "Analysis Overview" : active}
              </h1>
              <p>
                Understand the impact of every code change before it becomes
                a problem.
              </p>
            </div>

            <button
              className="primary-button"
              onClick={fetchAnalysis}
              disabled={loading}
            >
              {loading ? "⟳ Analyzing..." : "↻ Run analysis"}
            </button>
          </div>

          {error && (
            <div className="panel" role="alert">
              <strong>Unable to load analysis</strong>
              <p>{error}</p>
              <button onClick={fetchAnalysis}>Try again</button>
            </div>
          )}

          <div className="repository-bar">
            <div>
              <span className="repo-symbol">⌘</span>
              <div>
                <small>ACTIVE REPOSITORY</small>
                <strong>Ripple workspace</strong>
              </div>
            </div>

            <span className="demo-tag">LIVE API</span>
          </div>

          <div className="section-heading">
            <div>
              <h2>Project overview</h2>
              <p>Results returned by the Ripple analysis engine</p>
            </div>
            <span className="demo-tag">
              {loading ? "ANALYZING" : "LIVE RESULTS"}
            </span>
          </div>

          <div className="metrics-grid">
            <Metric
              label="Changed modules"
              value={summary.changed_modules ?? "—"}
              change="Detected by Git"
              icon="▤"
            />
            <Metric
              label="Impacted modules"
              value={summary.impacted_modules ?? "—"}
              change="Dependency analysis"
              icon="⌘"
            />
            <Metric
              label="Tests recommended"
              value={summary.tests_recommended ?? "—"}
              change="Engine recommendations"
              icon="✓"
            />
            <Metric
              label="Tests passed"
              value={
                summary.tests_passed !== undefined
                  ? `${summary.tests_passed}/${(summary.tests_passed || 0) + (summary.tests_failed || 0)}`
                  : "—"
              }
              change={
                testResults.success
                  ? "Execution successful"
                  : "Execution status"
              }
              icon="◷"
            />
          </div>

          <div className="content-grid">
            <section className="panel modules-panel">
              <div className="panel-heading">
                <div>
                  <h3>Impacted modules</h3>
                  <p>Modules affected by detected code changes</p>
                </div>
              </div>

              {loading ? (
                <p>Analyzing dependencies...</p>
              ) : impactedModules.length === 0 ? (
                <p>No downstream impacted modules detected.</p>
              ) : (
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>MODULE</th>
                        <th>IMPACT DEPTH</th>
                        <th>IMPACT TYPE</th>
                      </tr>
                    </thead>
                    <tbody>
                      {impactedModules.map(([name, details]) => (
                        <tr key={name}>
                          <td><strong>{name}</strong></td>
                          <td>{details.depth ?? "—"}</td>
                          <td>
                            <ImpactBadge value={details.impact_type || "affected"} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>

            <section className="panel tests-panel">
              <div className="panel-heading">
                <div>
                  <h3>Recommended tests</h3>
                  <p>Tests selected by dependency analysis</p>
                </div>
              </div>

              {loading ? (
                <p>Finding recommended tests...</p>
              ) : recommendations.length === 0 ? (
                <p>No tests recommended for the detected changes.</p>
              ) : (
                <div className="test-list">
                  {recommendations.map((test) => (
                    <div className="test-item" key={test.test_file}>
                      <div className="test-check">✓</div>
                      <div className="test-info">
                        <strong>{test.test_file}</strong>
                        <small>{test.reason}</small>
                      </div>
                      <ImpactBadge value={test.priority} />
                    </div>
                  ))}
                </div>
              )}
            </section>
          </div>

          <section className="panel activity-panel">
            <div className="panel-heading">
              <div>
                <h3>Detected file changes</h3>
                <p>Files detected by Git status</p>
              </div>
              <span>{changedFiles.length} files</span>
            </div>

            <div className="activity-list">
              {loading ? (
                <p>Loading changed files...</p>
              ) : changedFiles.length === 0 ? (
                <p>No changed files detected.</p>
              ) : (
                changedFiles.map((file) => (
                  <Activity
                    key={file.file}
                    title={`${file.change_type} file`}
                    file={file.file}
                    impact={file.change_type}
                  />
                ))
              )}
            </div>
          </section>

          <section className="panel activity-panel">
            <div className="panel-heading">
              <div>
                <h3>Test execution results</h3>
                <p>Output from the automated test runner</p>
              </div>
              <ImpactBadge
                value={testResults.success ? "Passed" : "Failed"}
              />
            </div>

            <p>
              Passed: {testResults.passed ?? 0} · Failed:{" "}
              {testResults.failed ?? 0}
            </p>

            <pre style={{ whiteSpace: "pre-wrap", overflowX: "auto" }}>
              {testResults.output || "Test output will appear here."}
            </pre>
          </section>

          <footer>
            <span>Ripple · Change Impact Intelligence</span>
            <span>Built for developers, by developers.</span>
          </footer>
        </section>
      </main>
    </div>
  );
}

function Metric({ label, value, change, icon }) {
  return (
    <div className="metric-card">
      <div className="metric-top">
        <span>{label}</span>
        <div className="metric-icon">{icon}</div>
      </div>
      <h2>{value}</h2>
      <small>{change}</small>
    </div>
  );
}

function ImpactBadge({ value }) {
  const safeValue = String(value || "unknown");
  const className = safeValue.toLowerCase().replace(/[^a-z0-9-]/g, "");

  return (
    <span className={`impact-badge ${className}`}>
      {safeValue}
    </span>
  );
}

function Activity({ title, file, impact }) {
  return (
    <div className="activity-item">
      <div className="activity-indicator" />
      <div className="activity-description">
        <strong>{title}</strong>
        <small>{file}</small>
      </div>
      <ImpactBadge value={impact} />
    </div>
  );
}

export default App;
