import StatusPill from "./StatusPill";

export default function AlertsTimeline({ alerts }) {
  return (
    <ul className="timeline-list">
      {alerts.map((alert) => (
        <li
          key={`${alert.timestamp}-${alert.message}`}
          className="timeline-item"
        >
          <div className="timeline-head">
            <span className="mono-text timeline-time">{alert.timestamp}</span>
            <StatusPill value={alert.severity} />
          </div>
          <p className="timeline-message">{alert.message}</p>
        </li>
      ))}
    </ul>
  );
}
