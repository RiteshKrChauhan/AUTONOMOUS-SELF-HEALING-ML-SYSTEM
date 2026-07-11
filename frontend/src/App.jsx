import { useEffect, useMemo, useState } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "./layout/AppLayout";
import DriftMonitoringPage from "./pages/DriftMonitoringPage";
import RateControlPage from "./pages/RateControlPage";
import SelfHealingGovernancePage from "./pages/SelfHealingGovernancePage";
import SystemOverviewPage from "./pages/SystemOverviewPage";
import {
  EVENT_TYPES,
  STATIC_CONTROLS,
  STATIC_DASHBOARD_DATA,
  getDashboard,
  injectAnomalies,
  resetRuntime,
  updateControls,
} from "./services/api";

export default function App() {
  const [theme, setTheme] = useState("dark");
  const [dashboardData, setDashboardData] = useState(STATIC_DASHBOARD_DATA);
  const [controls, setControls] = useState(STATIC_CONTROLS);
  const [connectionState, setConnectionState] = useState("connecting");
  const [isInjecting, setIsInjecting] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);

  useEffect(() => {
    let mounted = true;

    async function refresh() {
      try {
        const data = await getDashboard();
        if (!mounted) {
          return;
        }
        setDashboardData(data);
        setControls({
          simulatedRate: data.rateControl.simulatedRate,
          rateLimit: data.rateControl.rateLimit,
          rateLimitEnabled: data.rateControl.rateLimitEnabled,
        });
        setConnectionState("live");
      } catch (error) {
        if (mounted) {
          setConnectionState("offline");
        }
      }
    }

    refresh();
    const intervalId = window.setInterval(refresh, 1000);

    return () => {
      mounted = false;
      window.clearInterval(intervalId);
    };
  }, []);

  async function handleInjectAnomalies(payload) {
    setIsInjecting(true);
    try {
      await injectAnomalies(payload);
      const data = await getDashboard();
      setDashboardData(data);
      setConnectionState("live");
    } finally {
      setIsInjecting(false);
    }
  }

  async function handleControlsChange(nextControls) {
    const optimisticControls = { ...controls, ...nextControls };
    setControls(optimisticControls);
    setDashboardData((prev) => ({
      ...prev,
      rateControl: {
        ...prev.rateControl,
        ...optimisticControls,
      },
    }));

    try {
      await updateControls(nextControls);
      const data = await getDashboard();
      setDashboardData(data);
      setConnectionState("live");
    } catch (error) {
      setConnectionState("offline");
    }
  }

  async function handleResetRuntime() {
    await resetRuntime();
    const data = await getDashboard();
    setDashboardData(data);
    setConnectionState("live");
  }

  const outletContext = useMemo(
    () => ({
      dashboardData,
      controls,
      eventTypes: EVENT_TYPES,
      connectionState,
      isInjecting,
      onInjectAnomalies: handleInjectAnomalies,
      onControlsChange: handleControlsChange,
      onResetRuntime: handleResetRuntime,
    }),
    [dashboardData, controls, connectionState, isInjecting]
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
              connectionState={connectionState}
              anomaly={dashboardData.overview.scenario}
              isInjecting={isInjecting}
              onInjectAnomalies={handleInjectAnomalies}
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
