import { Moon, Sun } from "lucide-react";

export default function TopNavbar({ theme, onThemeToggle, modelVersion }) {
  return (
    <header className="topbar panel-card">
      <div className="topbar-row">
        <div>
          <p className="topbar-kicker">Autonomous Self-Healing Streaming ML System</p>
          <h2 className="topbar-title">Industrial IoT Predictive Maintenance</h2>
        </div>
        <div className="topbar-actions">
          <button
            type="button"
            onClick={onThemeToggle}
            className="topbar-theme-btn"
          >
            {theme === "dark" ? <Sun size={14} /> : <Moon size={14} />}
            {theme === "dark" ? "Light" : "Dark"}
          </button>
        </div>
      </div>
    </header>
  );
}
