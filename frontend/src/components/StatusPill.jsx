const CLASS_MAP = {
  Healthy: "status-pill status-healthy",
  Warning: "status-pill status-warning",
  Critical: "status-pill status-critical",
  Monitoring: "status-pill status-monitoring",
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
