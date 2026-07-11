import { useOutletContext } from "react-router-dom";
import KafkaLagChart from "../charts/KafkaLagChart";
import RateGaugeChart from "../charts/RateGaugeChart";
import RateLimitChart from "../charts/RateLimitChart";
import MetricCard from "../components/MetricCard";
import SectionCard from "../components/SectionCard";

export default function RateControlPage() {
  const { dashboardData, controls, connectionState, onControlsChange } = useOutletContext();
  const controlsDisabled = connectionState !== "live";

  return (
    <div className="page-stack">
      <div className="dashboard-grid dashboard-grid-3">
        <SectionCard
          title="Current Ingestion Rate"
          subtitle="Gauge view of stream pressure"
        >
          <RateGaugeChart value={dashboardData.rateControl.currentRate} />
        </SectionCard>

        <SectionCard
          title="Rate Controls"
          subtitle="Live stream pressure and throttling policy"
        >
          <div className="control-stack">
            <div>
              <div className="control-row">
                <span>Simulated data rate</span>
                <span className="mono-text accent-cyan">{controls.simulatedRate} eps</span>
              </div>
              <input
                type="range"
                min={1}
                max={30}
                step={1}
                value={controls.simulatedRate}
                disabled={controlsDisabled}
                onChange={(event) =>
                  onControlsChange({ simulatedRate: Number(event.target.value) })
                }
                className="range-input"
              />
            </div>

            <div className="inset-card">
              <label className="toggle-row">
                <span>Enable rate limiting</span>
                <button
                  type="button"
                  disabled={controlsDisabled}
                  onClick={() =>
                    onControlsChange({ rateLimitEnabled: !controls.rateLimitEnabled })
                  }
                  className={`toggle-pill ${controls.rateLimitEnabled ? "is-on" : "is-off"}`}
                  title="Toggle rate limiting"
                >
                  <span
                    className={`toggle-knob ${controls.rateLimitEnabled ? "is-on" : "is-off"}`}
                  />
                </button>
              </label>
            </div>

            <div>
              <div className="control-row">
                <span>Rate limit</span>
                <span className="mono-text accent-amber">{controls.rateLimit} eps</span>
              </div>
              <input
                type="range"
                min={1}
                max={40}
                step={1}
                disabled={controlsDisabled}
                value={controls.rateLimit}
                onChange={(event) =>
                  onControlsChange({ rateLimit: Number(event.target.value) })
                }
                className="range-input"
              />
            </div>
          </div>
        </SectionCard>

        <div className="dashboard-grid dashboard-grid-single-gap">
          <MetricCard
            label="CPU Usage"
            value={`${dashboardData.rateControl.cpuUsage}%`}
            hint="Streaming workers"
          />
          <MetricCard
            label="Memory Usage"
            value={`${dashboardData.rateControl.memoryUsage}%`}
            hint="Inference and buffering"
          />
        </div>
      </div>

      <div className="dashboard-grid dashboard-grid-2">
        <SectionCard
          title="Actual Rate vs Rate Limit"
          subtitle="Ingestion control policy behavior"
        >
          <RateLimitChart
            data={dashboardData.rateControl.actualVsLimitSeries}
            enabled={dashboardData.rateControl.rateLimitEnabled}
          />
        </SectionCard>

        <SectionCard
          title="Kafka Consumer Lag"
          subtitle="Backlog trend for streaming workers"
        >
          <KafkaLagChart data={dashboardData.rateControl.kafkaLagSeries} />
        </SectionCard>
      </div>
    </div>
  );
}
