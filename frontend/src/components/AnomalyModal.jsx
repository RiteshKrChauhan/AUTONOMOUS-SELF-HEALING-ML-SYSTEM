import { useEffect, useRef, useState } from "react";
import { X } from "lucide-react";
import { fetchScenarios } from "../services/api";

const SEVERITY_ORDER = ["Critical", "High", "Medium", "Low"];

const STATIC_SCENARIOS = [
  {
    id: "sudden_spike",
    name: "Sudden Drift (Critical)",
    severity: "Critical",
    duration: 45,
    description: "All 21 sensors shift +8σ immediately. Simulates catastrophic environmental change.",
    expectedBehavior: "RETRAIN_URGENT within seconds. Performance gate evaluates candidate. Shadow A/B test begins.",
  },
  {
    id: "drift_recovery",
    name: "Drift → Recovery",
    severity: "Critical",
    duration: 60,
    description: "Severe +6σ drift for 30 cycles, then gradual recovery to baseline over 30 cycles.",
    expectedBehavior: "Full self-healing arc: detect → retrain → shadow → promote → stabilize. No retrain during recovery.",
  },
  {
    id: "sensor_failure",
    name: "Sensor Failure (Stuck)",
    severity: "High",
    duration: 80,
    description: "2 sensors stuck at 0.0, simulating disconnected hardware.",
    expectedBehavior: "KS test detects zero-variance on stuck sensors. Isolation Forest flags every point. Retrain begins.",
  },
  {
    id: "concept_drift",
    name: "Concept Drift (Label Shift)",
    severity: "High",
    duration: 150,
    description: "Engine degrades 60 cycles faster than historical fleet. Features look normal — only RUL is shifted.",
    expectedBehavior: "ADWIN detects rising error after ~60-80 cycles. Feature Drift chart stays flat (KS test silent). Error-based retrain triggered.",
  },

  {
    id: "correlated_drift",
    name: "Correlated Multi-Sensor Drift",
    severity: "High",
    duration: 60,
    description: "6 temperature/pressure sensors drift +3σ together, simulating a thermal event.",
    expectedBehavior: "Feature drift ratio fires quickly. Multiple sensors highlighted in drift report.",
  },
  {
    id: "gradual_drift",
    name: "Gradual Sensor Drift",
    severity: "Medium",
    duration: 100,
    description: "4 sensors slowly drift +0.3σ every 10 cycles, simulating progressive wear.",
    expectedBehavior: "ADWIN detects rising error after ~40-60 cycles. KS test fires eventually.",
  },
  {
    id: "high_noise",
    name: "High Sensor Noise",
    severity: "Medium",
    duration: 60,
    description: "Sensor variance ×5 with no mean shift. Simulates electrical interference.",
    expectedBehavior: "Confidence intervals widen. Performance gate likely REJECTS retrain candidate.",
  },
  {
    id: "intermittent_spikes",
    name: "Intermittent Sensor Spikes",
    severity: "Low",
    duration: 90,
    description: "2 random sensors spike ±12σ every 7 cycles. Normal between spikes.",
    expectedBehavior: "Isolation Forest flags spike cycles. ADWIN may not detect (too infrequent). No retrain expected.",
  },
];

function SeverityBadge({ severity }) {
  const cls = {
    Critical: "severity-badge--critical",
    High: "severity-badge--high",
    Medium: "severity-badge--medium",
    Low: "severity-badge--low",
  }[severity] ?? "severity-badge--low";
  return <span className={`severity-badge ${cls}`}>{severity}</span>;
}

export default function AnomalyModal({ isOpen, onClose, onInject, isInjecting }) {
  const [scenarios, setScenarios] = useState(STATIC_SCENARIOS);
  const [selected, setSelected] = useState(null);
  const overlayRef = useRef(null);

  // Fetch live scenarios from backend on open
  useEffect(() => {
    if (!isOpen) return;
    setSelected(null);
    fetchScenarios()
      .then((data) => {
        if (data?.scenarios?.length) {
          const sorted = [...data.scenarios].sort(
            (a, b) => SEVERITY_ORDER.indexOf(a.severity) - SEVERITY_ORDER.indexOf(b.severity)
          );
          setScenarios(sorted);
        }
      })
      .catch(() => {
        // Fallback to static scenarios already set
      });
  }, [isOpen]);

  // Close on Escape
  useEffect(() => {
    if (!isOpen) return;
    const handler = (e) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [isOpen, onClose]);

  // Close on overlay click
  function handleOverlayClick(e) {
    if (e.target === overlayRef.current) onClose();
  }

  function handleInject() {
    if (!selected) return;
    onInject({ scenario: selected });
    onClose();
  }

  if (!isOpen) return null;

  const selectedMeta = scenarios.find((s) => s.id === selected);

  return (
    <div className="modal-overlay" ref={overlayRef} onClick={handleOverlayClick}>
      <div className="modal-panel" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        {/* Header */}
        <div className="modal-header">
          <div className="modal-header-row">
            <div>
              <h2 id="modal-title" className="modal-title">Inject Anomaly Scenario</h2>
              <p className="modal-subtitle">
                Each scenario tests a different aspect of the self-healing pipeline.
                Select one to simulate and observe the system's autonomous response.
              </p>
            </div>
            <button className="modal-close-btn" onClick={onClose} aria-label="Close">
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Scenario grid */}
        <div className="modal-body">
          <div className="scenario-grid">
            {scenarios.map((scenario) => (
              <button
                key={scenario.id}
                type="button"
                className={`scenario-card${selected === scenario.id ? " selected" : ""}`}
                onClick={() => setSelected(scenario.id === selected ? null : scenario.id)}
              >
                <SeverityBadge severity={scenario.severity} />
                <p className="scenario-name">{scenario.name}</p>
                <p className="scenario-description">{scenario.description}</p>
                <div className="scenario-footer">
                  <span className="scenario-tag">{scenario.duration} cycles</span>
                </div>
                <div className="scenario-expected">
                  <p className="scenario-expected-label">Expected response</p>
                  <p className="scenario-expected-text">{scenario.expectedBehavior}</p>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="modal-footer">
          {selectedMeta && (
            <span className="modal-selection-hint">
              Selected: <strong>{selectedMeta.name}</strong> ({selectedMeta.duration} cycles)
            </span>
          )}
          <button type="button" className="secondary-action-btn" onClick={onClose}>
            Cancel
          </button>
          <button
            type="button"
            className="primary-action-btn"
            disabled={!selected || isInjecting}
            onClick={handleInject}
          >
            {isInjecting ? "Injecting..." : "Inject Selected Scenario"}
          </button>
        </div>
      </div>
    </div>
  );
}
