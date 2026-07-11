import { RotateCcw } from "lucide-react";
import { useMemo, useState } from "react";
import { useOutletContext } from "react-router-dom";
import ActionReasonsPieChart from "../charts/ActionReasonsPieChart";
import ModelVersionChart from "../charts/ModelVersionChart";
import AuditLogTable from "../components/AuditLogTable";
import SectionCard from "../components/SectionCard";
import StatusPill from "../components/StatusPill";

function parseTimestamp(logTimestamp) {
  return new Date(logTimestamp.replace(" ", "T"));
}

function ShadowEvaluationCard({ shadow }) {
  if (!shadow?.is_evaluating) return null;

  const progress = shadow.samples_needed > 0
    ? Math.min(100, Math.round((shadow.samples_collected / shadow.samples_needed) * 100))
    : 0;

  const prodMae = shadow.production_mae != null ? shadow.production_mae.toFixed(2) : "—";
  const shadowMae = shadow.shadow_mae != null ? shadow.shadow_mae.toFixed(2) : "—";

  const isBetter = shadow.shadow_mae != null && shadow.production_mae != null
    && shadow.shadow_mae < shadow.production_mae;

  return (
    <div className="shadow-eval-card">
      <div className="shadow-eval-header">
        <span className="shadow-eval-title">⚗️ Shadow A/B Evaluation in Progress</span>
        <span className="shadow-eval-cycles">
          {shadow.samples_collected} / {shadow.samples_needed} cycles
        </span>
      </div>
      <div className="shadow-progress-bar">
        <div className="shadow-progress-fill" style={{ width: `${progress}%` }} />
      </div>
      {(shadow.production_mae != null || shadow.shadow_mae != null) && (
        <div className="shadow-mae-compare">
          <div className="shadow-mae-item">
            <span className="mini-label">Production MAE</span>
            <span className="shadow-mae-value">{prodMae}</span>
          </div>
          <div className="shadow-mae-item">
            <span className="mini-label">Shadow MAE</span>
            <span className={`shadow-mae-value ${isBetter ? "shadow-mae-better" : "shadow-mae-worse"}`}>
              {shadowMae}
              {isBetter ? " ✓" : " ✗"}
            </span>
          </div>
          <div className="shadow-mae-item">
            <span className="mini-label">Outcome</span>
            <span className="mono-text" style={{ fontSize: "0.78rem" }}>
              {shadow.ready_to_decide
                ? (isBetter ? "Ready to promote" : "Will be rejected")
                : "Evaluating…"}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

export default function SelfHealingGovernancePage() {
  const { dashboardData, eventTypes, onResetRuntime } = useOutletContext();
  const [eventFilter, setEventFilter] = useState("ALL");
  const [timeFilter, setTimeFilter] = useState("ALL");

  const shadow = dashboardData.selfHealing.shadowEvaluation;

  const filteredLogs = useMemo(() => {
    const now = Date.now();
    return dashboardData.auditLogs.filter((log) => {
      const matchesEvent = eventFilter === "ALL" || log.eventType === eventFilter;
      if (!matchesEvent) return false;
      if (timeFilter === "ALL") return true;
      const ts = parseTimestamp(log.timestamp).getTime();
      const diffMinutes = (now - ts) / (1000 * 60);
      if (timeFilter === "1H") return diffMinutes <= 60;
      if (timeFilter === "6H") return diffMinutes <= 360;
      if (timeFilter === "24H") return diffMinutes <= 1440;
      return true;
    });
  }, [dashboardData.auditLogs, eventFilter, timeFilter]);

  return (
    <div className="page-stack">
      {/* Shadow evaluation live card (only visible during shadow eval) */}
      {shadow?.is_evaluating && (
        <ShadowEvaluationCard shadow={shadow} />
      )}

      <div className="dashboard-grid dashboard-grid-2">
        <SectionCard title="Self-Healing Timeline" subtitle="Decision flow and automated interventions">
          <ul className="timeline-list">
            {dashboardData.selfHealing.timeline.map((item) => (
              <li key={`${item.time}-${item.event}`} className="timeline-item">
                <div className="timeline-head">
                  <span className="mono-text timeline-time">{item.time}</span>
                  <StatusPill value={item.state} />
                </div>
                <p className="timeline-message">{item.event}</p>
              </li>
            ))}
          </ul>
        </SectionCard>

        <SectionCard title="Model Version History" subtitle="Deployment progression over time">
          <ModelVersionChart data={dashboardData.selfHealing.modelHistory} />
        </SectionCard>
      </div>

      <div className="dashboard-grid dashboard-grid-3">
        <SectionCard title="Action Reasons" subtitle="Why autonomous actions were triggered">
          <ActionReasonsPieChart data={dashboardData.selfHealing.actionReasons} />
        </SectionCard>

        <SectionCard title="Last Action Taken" subtitle="Most recent governance outcome">
          <div className="inset-card">
            <p className="inset-text">{dashboardData.selfHealing.lastActionTaken}</p>
          </div>
        </SectionCard>

        <SectionCard title="Current System State" subtitle="Runtime governance posture">
          <div className="inset-card">
            <StatusPill value={dashboardData.selfHealing.currentSystemState} />
            {shadow?.is_evaluating && (
              <p className="mini-label" style={{ marginTop: "8px", color: "var(--accent-cyan)" }}>
                Shadow evaluation: {shadow.samples_collected}/{shadow.samples_needed} cycles
              </p>
            )}
          </div>
        </SectionCard>
      </div>

      <SectionCard
        title="Governance Logs"
        subtitle="Unified audit trail for self-healing decisions and operational actions"
        action={
          <div className="filter-group">
            <button
              type="button"
              className="secondary-action-btn"
              onClick={onResetRuntime}
              title="Restart the demo runtime"
            >
              <RotateCcw size={14} />
              Reset Runtime
            </button>
            <select
              value={eventFilter}
              onChange={(e) => setEventFilter(e.target.value)}
              className="filter-select"
            >
              <option value="ALL">All events</option>
              {eventTypes.map((type) => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
            <select
              value={timeFilter}
              onChange={(e) => setTimeFilter(e.target.value)}
              className="filter-select"
            >
              <option value="ALL">All time</option>
              <option value="1H">Last 1 hour</option>
              <option value="6H">Last 6 hours</option>
              <option value="24H">Last 24 hours</option>
            </select>
          </div>
        }
      >
        <AuditLogTable logs={filteredLogs} />
      </SectionCard>
    </div>
  );
}
