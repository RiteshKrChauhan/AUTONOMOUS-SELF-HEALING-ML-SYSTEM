import { useEffect, useMemo, useState } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "./layout/AppLayout";
import DriftMonitoringPage from "./pages/DriftMonitoringPage";
import RateControlPage from "./pages/RateControlPage";
import SelfHealingGovernancePage from "./pages/SelfHealingGovernancePage";
import SystemOverviewPage from "./pages/SystemOverviewPage";
import { EVENT_TYPES, STATIC_CONTROLS, STATIC_DASHBOARD_DATA } from "./services/api";

export default function App() {
  const [theme, setTheme] = useState("dark");
  const dashboardData = STATIC_DASHBOARD_DATA;
  const controls = STATIC_CONTROLS;

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);

  const outletContext = useMemo(
    () => ({
      dashboardData,
      controls,
      eventTypes: EVENT_TYPES,
    }),
    [dashboardData, controls]
  );

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <AppLayout
              theme={theme}
              onThemeToggle={() => setTheme((prev) => (prev === "dark" ? "light" : "dark"))}
              modelVersion={dashboardData.overview.activeModelVersion}
              outletContext={outletContext}
            />
          }
        >
          <Route index element={<SystemOverviewPage />} />
          <Route path="drift-monitoring" element={<DriftMonitoringPage />} />
          <Route path="rate-control" element={<RateControlPage />} />
          <Route path="self-healing" element={<SelfHealingGovernancePage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
