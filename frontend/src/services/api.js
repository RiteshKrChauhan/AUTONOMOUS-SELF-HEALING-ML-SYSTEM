export const EVENT_TYPES = ["DRIFT", "RATE_LIMIT", "MODEL", "OVERLOAD", "CONFIDENCE"];

export const STATIC_CONTROLS = {
  simulatedRate: 8,
  rateLimit: 14,
  rateLimitEnabled: true,
};

const makeSeries = () =>
  Array.from({ length: 24 }, (_, index) => {
    const driftScore = Number((0.08 + index * 0.012).toFixed(3));
    const error = Number((0.08 + index * 0.004).toFixed(3));
    return {
      time: `08:${String(20 + index).padStart(2, "0")}:00`,
      sampleIndex: index,
      dataRate: 8,
      latency: 52 + index,
      driftScore,
      confidence: Number((0.94 - index * 0.006).toFixed(3)),
      confidenceCategory: "high_confidence",
      error,
      mae: Number((error * 125).toFixed(2)),
      rollingMae: Number((error * 110).toFixed(2)),
      accuracy: Number((1 - error).toFixed(3)),
      kafkaLag: Math.max(0, index - 8),
      prediction: 96 - index,
      actual: 98 - index,
      predLower: 88 - index,
      predUpper: 104 - index,
      action: driftScore > 0.32 ? "WATCH" : "STABLE",
      status: driftScore > 0.32 ? "Warning" : "Healthy",
      adwinDrift: false,
      dataDrift: false,
      anomalyDetected: false,
      anomalyScore: 0.0,
      scenarioActive: false,
      cooldownElapsed: index,
      cooldownRequired: 45,
    };
  });

const fallbackSeries = makeSeries();

export const STATIC_DASHBOARD_DATA = {
  overview: {
    systemStatus: "Healthy",
    activeModelVersion: "v1.0.1",
    series: fallbackSeries,
    confidenceHistogram: [
      { bucket: "0.30-0.50", count: 0 },
      { bucket: "0.50-0.60", count: 1 },
      { bucket: "0.60-0.70", count: 3 },
      { bucket: "0.70-0.80", count: 7 },
      { bucket: "0.80-0.90", count: 18 },
      { bucket: "0.90-1.00", count: 35 },
    ],
    latestSample: {
      prediction: 73.8,
      actual: 75,
      interval: [68.2, 80.1],
      action: "STABLE",
      sampleIndex: 23,
      confidenceCategory: "high_confidence",
      adwinDrift: false,
      dataDrift: false,
      anomalyDetected: false,
      anomalyScore: 0.0,
    },
    scenario: {
      active: false,
      remaining: 0,
      id: null,
      name: null,
      severity: null,
    },
  },
  drift: {
    featureDistributionShift: [
      { feature: "sensor_2", baseline: 0.5, current: 0.53 },
      { feature: "sensor_4", baseline: 0.5, current: 0.56 },
      { feature: "sensor_7", baseline: 0.5, current: 0.59 },
      { feature: "sensor_11", baseline: 0.5, current: 0.6 },
      { feature: "sensor_15", baseline: 0.5, current: 0.57 },
      { feature: "sensor_20", baseline: 0.5, current: 0.55 },
    ],
    featureScores: [
      { feature: "sensor_11", score: 0.28 },
      { feature: "sensor_7", score: 0.24 },
      { feature: "sensor_15", score: 0.2 },
      { feature: "sensor_4", score: 0.17 },
      { feature: "sensor_20", score: 0.14 },
      { feature: "sensor_2", score: 0.1 },
    ],
    conceptSeries: fallbackSeries,
    alerts: [
      { timestamp: "08:42:00", severity: "Healthy", message: "Baseline stream initialized" },
    ],
  },
  rateControl: {
    ...STATIC_CONTROLS,
    currentRate: 8,
    cpuUsage: 41,
    memoryUsage: 52,
    actualVsLimitSeries: fallbackSeries.map((p) => ({ time: p.time, actualRate: p.dataRate, rateLimit: 14 })),
    kafkaLagSeries: fallbackSeries.map((p) => ({ time: p.time, kafkaLag: p.kafkaLag })),
  },
  selfHealing: {
    timeline: [
      { time: "08:42:00", event: "Runtime started", state: "Healthy" },
      { time: "08:42:00", event: "Initial model serving", state: "Monitoring" },
    ],
    modelHistory: [{ time: "08:42:00", versionIndex: 1, modelVersion: "v1.0.1" }],
    actionReasons: [{ reason: "Monitoring", value: 1 }],
    lastActionTaken: "System initialized and monitoring live stream",
    currentSystemState: "Monitoring",
    shadowEvaluation: {
      is_evaluating: false,
      samples_collected: 0,
      samples_needed: 20,
      production_mae: null,
      shadow_mae: null,
      ready_to_decide: false,
    },
  },
  auditLogs: [
    {
      timestamp: "2026-07-10 08:42:00",
      event: "Runtime Ready",
      reason: "Initial model trained on baseline engine units",
      actionTaken: "Serving model v1.0.1",
      status: "Healthy",
      eventType: "MODEL",
    },
  ],
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers ?? {}) },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json();
}

export function getDashboard() {
  return request("/dashboard");
}

export function fetchScenarios() {
  return request("/scenarios");
}

export function injectAnomalies(payload = {}) {
  return request("/anomalies", {
    method: "POST",
    body: JSON.stringify({ scenario: "sudden_spike", ...payload }),
  });
}

export function updateControls(payload) {
  return request("/controls", { method: "POST", body: JSON.stringify(payload) });
}

export function resetRuntime() {
  return request("/reset", { method: "POST" });
}
