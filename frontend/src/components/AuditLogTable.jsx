import StatusPill from "./StatusPill";

export default function AuditLogTable({ logs }) {
  return (
    <div className="table-wrap">
      <table className="audit-table">
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Event</th>
            <th>Reason</th>
            <th>Action Taken</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={`${log.timestamp}-${log.event}-${log.reason}`}>
              <td className="mono-text">{log.timestamp}</td>
              <td className="audit-event">{log.event}</td>
              <td>{log.reason}</td>
              <td>{log.actionTaken}</td>
              <td><StatusPill value={log.status} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
