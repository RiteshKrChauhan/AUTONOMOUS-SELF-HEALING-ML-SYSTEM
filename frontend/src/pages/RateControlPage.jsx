import { useMemo } from "react";
import { useOutletContext } from "react-router-dom";
import StreamBacklogChart from "../charts/StreamBacklogChart";
import RateGaugeChart from "../charts/RateGaugeChart";
import RateLimitChart from "../charts/RateLimitChart";
import AuditLogTable from "../components/AuditLogTable";
import MetricCard from "../components/MetricCard";
import SectionCard from "../components/SectionCard";

export default function RateControlPage() {
  const { dashboardData, controls, connectionState, onControlsChange } = useOutletContext();
  const controlsDisabled = connectionState !== "live";
  const rateLimitLogs = useMemo(
    () => (dashboardData?.auditLogs ?? []).filter((log) => log.eventType === "RATE_LIMIT"),
    [dashboardData?.auditLogs]
  );

  if (!dashboardData?.rateControl || !controls) {
    return (
      <div className="page-stack">
        <SectionCard
          title={connectionState === "offline" ? "Backend offline" : "Waiting for live data"}
          subtitle="Rate control only appears once the backend publishes processed metrics."
        >
          <div className="inset-card">
            <p className="inset-text">
              {connectionState === "offline"
                ? "No processed rate-control snapshot is available."
                : "Live rate-control data is still loading."}
            </p>
          </div>
        </SectionCard>
      </div>
    );
  }

  const rateControl = dashboardData.rateControl;
  const activeProcessingLimit = rateControl.appliedRateLimit ?? rateControl.workerCapacity ?? controls.rateLimit;
  const gaugeMax = Math.max(activeProcessingLimit, rateControl.currentRate ?? 0, 1);
  const backlogCapacity = rateControl.queueCapacity ?? 500;
  const loadSheddingActive =
    rateControl.loadSheddingActive ||
    rateControl.loadSheddingRecent > 0 ||
    rateControl.streamBacklog >= backlogCapacity;

  return (
    <div className="page-stack">
      <div className="dashboard-grid dashboard-grid-3">
        <SectionCard
          title="Processed Ingestion Rate"
          subtitle="Events admitted into the ML pipeline"
        >
          <RateGaugeChart
            value={rateControl.currentRate}
            max={gaugeMax}
            capacityLabel="active limit"
          />
        </SectionCard>

        <SectionCard
          title="Rate Controls"
          subtitle="Live stream pressure and throttling policy"
        >
          <div className="control-stack">
            <div>
              <div className="control-row">
                <span>Current incoming rate</span>
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
                <span>Operator rate limit</span>
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
            label="Applied Limit"
            value={`${rateControl.appliedRateLimit} eps`}
            hint={rateControl.controllerState}
          />
          <MetricCard
            label="Deferred Backlog"
            value={`${rateControl.streamBacklog}/${backlogCapacity}`}
            hint={
              loadSheddingActive
                ? `Load shedding active: ${rateControl.loadSheddingTotal ?? 0} stale packets discarded`
                : `${rateControl.throttledRate} eps held back`
            }
            status={loadSheddingActive ? "Critical" : undefined}
          />
        </div>
      </div>

      <div className="dashboard-grid dashboard-grid-3">
        <MetricCard
          label="Incoming Rate"
          value={`${rateControl.incomingRate} eps`}
          hint="Traffic offered to ingestion"
        />
        <MetricCard
          label="Processed Rate"
          value={`${rateControl.processedRate} eps`}
          hint="Traffic consumed by ML workers"
        />
        <MetricCard
          label="Overload Risk"
          value={`${rateControl.overloadRisk}%`}
          hint={rateControl.controllerReason}
        />
      </div>

      <div className="dashboard-grid dashboard-grid-2">
        <SectionCard
          title="Incoming vs Applied Rate"
          subtitle="Adaptive controller behavior"
        >
          <RateLimitChart
            data={rateControl.actualVsLimitSeries}
            enabled={rateControl.rateLimitEnabled}
          />
        </SectionCard>

        <SectionCard
          title="Stream Backlog"
          subtitle="Deferred events waiting for safe processing"
        >
          <StreamBacklogChart data={rateControl.streamBacklogSeries} />
        </SectionCard>
      </div>

      <div className="dashboard-grid dashboard-grid-2">
        <MetricCard
          label="CPU Usage"
          value={`${rateControl.cpuUsage}%`}
          hint="Streaming workers"
        />
        <MetricCard
          label="Memory Usage"
          value={`${rateControl.memoryUsage}%`}
          hint="Inference and buffering"
        />
      </div>

      <SectionCard
        title="Rate Limit Logs"
        subtitle="Rate-control policy updates, throttling, and shedding events"
        className="governance-log-card"
      >
        <AuditLogTable logs={rateLimitLogs} />
      </SectionCard>
    </div>
  );
}
