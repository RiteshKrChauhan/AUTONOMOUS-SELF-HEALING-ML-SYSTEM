import { Activity, Moon, RotateCw, Sun, Zap } from "lucide-react";

export default function TopNavbar({
  theme,
  onThemeToggle,
  modelVersion,
  connectionState,
  anomaly,
  isInjecting,
  onInjectAnomalies,
}) {
  const isLive = connectionState === "live";
  const connectionLabel =
    connectionState === "live"
      ? "Live"
      : connectionState === "connecting"
        ? "Connecting"
        : "Fallback";

  return (
    <header className="topbar panel-card">
      <div className="topbar-row">
        <div>
          <p className="topbar-kicker">Autonomous Self-Healing Streaming ML System</p>
          <h2 className="topbar-title">Industrial IoT Predictive Maintenance</h2>
        </div>
        <div className="topbar-actions">
          <span className={`topbar-badge ${isLive ? "badge-live" : "badge-muted"}`}>
            <Activity size={14} />
            {connectionLabel}
          </span>
          <span className="topbar-badge topbar-hide-mobile">Model {modelVersion}</span>
          {anomaly?.active && (
            <span className="topbar-badge badge-critical topbar-hide-mobile">
              Drift active: {anomaly.remaining} samples
            </span>
          )}
          <button
            type="button"
            onClick={() => onInjectAnomalies()}
            className="primary-action-btn"
            disabled={isInjecting || !isLive}
            title="Inject synthetic sensor anomalies"
          >
            {isInjecting ? <RotateCw size={15} /> : <Zap size={15} />}
            {isInjecting ? "Injecting" : "Inject Anomalies"}
          </button>
          <button
            type="button"
            onClick={onThemeToggle}
            className="topbar-theme-btn"
            title="Toggle color theme"
          >
            {theme === "dark" ? <Sun size={14} /> : <Moon size={14} />}
            {theme === "dark" ? "Light" : "Dark"}
          </button>
        </div>
      </div>
    </header>
  );
}
