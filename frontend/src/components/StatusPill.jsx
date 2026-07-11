const CLASS_MAP = {
  Healthy: "status-pill status-healthy",
  Warning: "status-pill status-warning",
  Critical: "status-pill status-critical",
  Monitoring: "status-pill status-monitoring",
  STABLE: "status-pill status-healthy",
  WATCH: "status-pill status-warning",
  MONITOR: "status-pill status-warning",
  ALERT: "status-pill status-critical",
  RETRAIN: "status-pill status-critical",
  RETRAIN_URGENT: "status-pill status-critical",
};

export default function StatusPill({ value }) {
  return (
    <span
      className={CLASS_MAP[value] || "status-pill status-neutral"}
    >
      {value}
    </span>
  );
}
