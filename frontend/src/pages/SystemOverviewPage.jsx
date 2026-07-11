import { useState } from "react";
import { useOutletContext } from "react-router-dom";
import DataRateLatencyChart from "../charts/DataRateLatencyChart";
import DriftScoreLineChart from "../charts/DriftScoreLineChart";
import ConfidenceHistogramChart from "../charts/ConfidenceHistogramChart";
import AnomalyModal from "../components/AnomalyModal";
import MetricCard from "../components/MetricCard";
import SectionCard from "../components/SectionCard";
import StatusPill from "../components/StatusPill";

export default function SystemOverviewPage() {
  const { dashboardData, connectionState, isInjecting, onInjectAnomalies } = useOutletContext();
  const [modalOpen, setModalOpen] = useState(false);

  const latest = dashboardData.overview.series.at(-1);
  const latestSample = dashboardData.overview.latestSample;
  const scenario = dashboardData.overview.scenario;

  const adwinLabel = latestSample.adwinDrift ? "🔴 Concept Drift" : "✅ Stable";
  const ksLabel = latestSample.dataDrift ? "🔴 Feature Drift" : "✅ Stable";
  const anomalyLabel = latestSample.anomalyDetected ? "⚠️ Anomaly" : "✅ Normal";

  return (
    <div className="page-stack">
      {/* Anomaly Scenario Modal */}
      <AnomalyModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onInject={onInjectAnomalies}
        isInjecting={isInjecting}
      />

      {/* Active scenario banner */}
      {scenario?.active && (
        <div className={`scenario-banner scenario-banner--${(scenario.severity ?? "medium").toLowerCase()}`}>
          <span className="scenario-banner-icon">⚡</span>
          <span>
            <strong>{scenario.name}</strong> scenario active —{" "}
            <span className="mono-text">{scenario.remaining} cycles remaining</span>
          </span>
        </div>
      )}

      <div className="dashboard-grid dashboard-grid-3">
        <MetricCard label="System Status" value={dashboardData.overview.systemStatus} hint="Composite health signal" status={dashboardData.overview.systemStatus} />
        <MetricCard label="Data Rate" value={`${latest.dataRate} eps`} hint="Current stream ingress" />
        <MetricCard label="Drift Score" value={latest.driftScore} hint="Combined KS + ADWIN drift score" />
        <MetricCard label="Active Model Version" value={dashboardData.overview.activeModelVersion} hint="Serving model in production" />
        <MetricCard label="Latency" value={`${latest.latency} ms`} hint="End-to-end processing latency" />
        <MetricCard label="Kafka Lag" value={`${latest.kafkaLag}`} hint="Unprocessed backlog count" />
      </div>

      <div className="dashboard-grid dashboard-grid-3">
        {/* Live prediction card */}
        <SectionCard title="Live Prediction" subtitle="Latest turbine RUL inference">
          <div className="live-sample-grid">
            <div>
              <p className="mini-label">Predicted RUL</p>
              <p className="sample-value">{latestSample.prediction}</p>
            </div>
            <div>
              <p className="mini-label">Actual RUL</p>
              <p className="sample-value">{latestSample.actual}</p>
            </div>
            <div>
              <p className="mini-label">Decision</p>
              <StatusPill value={latestSample.action} />
            </div>
          </div>
          <p className="sample-meta">
            Sample #{latestSample.sampleIndex} | interval [{latestSample.interval[0]} – {latestSample.interval[1]}]
          </p>
          <div className="drift-indicators">
            <span className="drift-indicator-pill">{adwinLabel}</span>
            <span className="drift-indicator-pill">{ksLabel}</span>
            <span className="drift-indicator-pill">{anomalyLabel}</span>
          </div>
        </SectionCard>

        {/* Anomaly injection card */}
        <SectionCard title="Anomaly Scenario Injection" subtitle="Simulate real-world fault conditions">
          <div className="action-panel">
            <div>
              <p className="action-title">
                {scenario?.active ? `Scenario active: ${scenario.name}` : "Baseline stream running"}
              </p>
              <p className="action-copy">
                {scenario?.active
                  ? `${scenario.remaining} cycles remaining — severity: ${scenario.severity}`
                  : "Choose a scenario to stress-test the self-healing pipeline."}
              </p>
            </div>
            <button
              type="button"
              className="primary-action-btn full-width"
              onClick={() => setModalOpen(true)}
              disabled={isInjecting || connectionState !== "live"}
            >
              {isInjecting ? "Injecting..." : "⚡ Choose & Inject Scenario"}
            </button>
          </div>
        </SectionCard>

        {/* Runtime state card */}
        <SectionCard title="Runtime State" subtitle="API and stream execution status">
          <div className="runtime-list">
            <div className="runtime-row">
              <span>Backend</span>
              <StatusPill value={connectionState === "live" ? "Healthy" : "Warning"} />
            </div>
            <div className="runtime-row">
              <span>Model action</span>
              <span className="mono-text">{latest.action}</span>
            </div>
            <div className="runtime-row">
              <span>ADWIN drift</span>
              <span className="mono-text">{latest.adwinDrift ? "Detected" : "Clear"}</span>
            </div>
            <div className="runtime-row">
              <span>KS drift</span>
              <span className="mono-text">{latest.dataDrift ? "Detected" : "Clear"}</span>
            </div>
            <div className="runtime-row">
              <span>Cooldown</span>
              <span className="mono-text">
                {latest.cooldownElapsed}/{latest.cooldownRequired}
              </span>
            </div>
          </div>
        </SectionCard>
      </div>

      <div className="dashboard-grid dashboard-grid-2">
        <SectionCard title="Data Rate vs Latency" subtitle="Real-time throughput and responsiveness">
          <DataRateLatencyChart data={dashboardData.overview.series} />
        </SectionCard>
        <SectionCard title="Drift Score Over Time" subtitle="Watch early drift escalation">
          <DriftScoreLineChart data={dashboardData.overview.series} />
        </SectionCard>
      </div>

      <SectionCard title="Confidence Distribution" subtitle="Prediction confidence histogram">
        <ConfidenceHistogramChart data={dashboardData.overview.confidenceHistogram} />
      </SectionCard>
    </div>
  );
}
