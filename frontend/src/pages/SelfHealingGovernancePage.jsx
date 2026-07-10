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

export default function SelfHealingGovernancePage() {
  const { dashboardData, eventTypes } = useOutletContext();
  const [eventFilter, setEventFilter] = useState("ALL");
  const [timeFilter, setTimeFilter] = useState("ALL");

  const filteredLogs = useMemo(() => {
    const now = Date.now();

    return dashboardData.auditLogs.filter((log) => {
      const matchesEvent = eventFilter === "ALL" || log.eventType === eventFilter;
      if (!matchesEvent) {
        return false;
      }

      if (timeFilter === "ALL") {
        return true;
      }

      const ts = parseTimestamp(log.timestamp).getTime();
      const diffMinutes = (now - ts) / (1000 * 60);

      if (timeFilter === "1H") {
        return diffMinutes <= 60;
      }
      if (timeFilter === "6H") {
        return diffMinutes <= 360;
      }
      if (timeFilter === "24H") {
        return diffMinutes <= 1440;
      }
      return true;
    });
  }, [dashboardData.auditLogs, eventFilter, timeFilter]);

  return (
    <div className="page-stack">
      <div className="dashboard-grid dashboard-grid-2">
        <SectionCard
          title="Self-Healing Timeline"
          subtitle="Decision flow and automated interventions"
        >
          <ul className="timeline-list">
            {dashboardData.selfHealing.timeline.map((item) => (
              <li
                key={`${item.time}-${item.event}`}
                className="timeline-item"
              >
                <div className="timeline-head">
                  <span className="mono-text timeline-time">{item.time}</span>
                  <StatusPill value={item.state} />
                </div>
                <p className="timeline-message">{item.event}</p>
              </li>
            ))}
          </ul>
        </SectionCard>

        <SectionCard
          title="Model Version History"
          subtitle="Deployment progression over time"
        >
          <ModelVersionChart data={dashboardData.selfHealing.modelHistory} />
        </SectionCard>
      </div>

      <div className="dashboard-grid dashboard-grid-3">
        <SectionCard
          title="Action Reasons"
          subtitle="Why autonomous actions were triggered"
        >
          <ActionReasonsPieChart data={dashboardData.selfHealing.actionReasons} />
        </SectionCard>

        <SectionCard
          title="Last Action Taken"
          subtitle="Most recent governance outcome"
        >
          <div className="inset-card">
            <p className="inset-text">{dashboardData.selfHealing.lastActionTaken}</p>
          </div>
        </SectionCard>

        <SectionCard
          title="Current System State"
          subtitle="Runtime governance posture"
        >
          <div className="inset-card">
            <StatusPill value={dashboardData.selfHealing.currentSystemState} />
          </div>
        </SectionCard>
      </div>

      <SectionCard
        title="Governance Logs"
        subtitle="Unified audit trail for self-healing decisions and operational actions"
        action={
          <div className="filter-group">
            <select
              value={eventFilter}
              onChange={(event) => setEventFilter(event.target.value)}
              className="filter-select"
            >
              <option value="ALL">All events</option>
              {eventTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>

            <select
              value={timeFilter}
              onChange={(event) => setTimeFilter(event.target.value)}
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
