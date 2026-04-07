export const EVENT_TYPES = ["DRIFT", "RATE_LIMIT", "MODEL", "OVERLOAD", "CONFIDENCE"];

export const STATIC_CONTROLS = {
  simulatedRate: 2400,
  rateLimit: 2600,
  rateLimitEnabled: true,
};

export const STATIC_DASHBOARD_DATA = {
  overview: {
    systemStatus: "Warning",
    activeModelVersion: "v2.3.1",
    series: [
      { time: "08:21", dataRate: 2120, latency: 102, driftScore: 0.18, confidence: 0.91, error: 0.09, accuracy: 0.91, kafkaLag: 92 },
      { time: "08:22", dataRate: 2180, latency: 108, driftScore: 0.19, confidence: 0.9, error: 0.1, accuracy: 0.9, kafkaLag: 98 },
      { time: "08:23", dataRate: 2250, latency: 114, driftScore: 0.21, confidence: 0.89, error: 0.11, accuracy: 0.89, kafkaLag: 112 },
      { time: "08:24", dataRate: 2310, latency: 118, driftScore: 0.24, confidence: 0.88, error: 0.12, accuracy: 0.88, kafkaLag: 126 },
      { time: "08:25", dataRate: 2360, latency: 122, driftScore: 0.27, confidence: 0.87, error: 0.13, accuracy: 0.87, kafkaLag: 138 },
      { time: "08:26", dataRate: 2420, latency: 126, driftScore: 0.31, confidence: 0.86, error: 0.14, accuracy: 0.86, kafkaLag: 151 },
      { time: "08:27", dataRate: 2480, latency: 132, driftScore: 0.36, confidence: 0.84, error: 0.16, accuracy: 0.84, kafkaLag: 174 },
      { time: "08:28", dataRate: 2530, latency: 139, driftScore: 0.39, confidence: 0.82, error: 0.18, accuracy: 0.82, kafkaLag: 196 },
      { time: "08:29", dataRate: 2570, latency: 146, driftScore: 0.42, confidence: 0.81, error: 0.19, accuracy: 0.81, kafkaLag: 214 },
      { time: "08:30", dataRate: 2620, latency: 154, driftScore: 0.46, confidence: 0.79, error: 0.21, accuracy: 0.79, kafkaLag: 236 },
      { time: "08:31", dataRate: 2580, latency: 161, driftScore: 0.49, confidence: 0.77, error: 0.23, accuracy: 0.77, kafkaLag: 252 },
      { time: "08:32", dataRate: 2510, latency: 168, driftScore: 0.53, confidence: 0.75, error: 0.25, accuracy: 0.75, kafkaLag: 268 },
      { time: "08:33", dataRate: 2460, latency: 174, driftScore: 0.56, confidence: 0.74, error: 0.26, accuracy: 0.74, kafkaLag: 286 },
      { time: "08:34", dataRate: 2390, latency: 179, driftScore: 0.59, confidence: 0.72, error: 0.28, accuracy: 0.72, kafkaLag: 304 },
      { time: "08:35", dataRate: 2350, latency: 184, driftScore: 0.63, confidence: 0.7, error: 0.3, accuracy: 0.7, kafkaLag: 326 },
      { time: "08:36", dataRate: 2310, latency: 188, driftScore: 0.66, confidence: 0.69, error: 0.31, accuracy: 0.69, kafkaLag: 349 },
      { time: "08:37", dataRate: 2280, latency: 194, driftScore: 0.69, confidence: 0.67, error: 0.33, accuracy: 0.67, kafkaLag: 371 },
      { time: "08:38", dataRate: 2240, latency: 198, driftScore: 0.72, confidence: 0.65, error: 0.35, accuracy: 0.65, kafkaLag: 394 },
      { time: "08:39", dataRate: 2190, latency: 204, driftScore: 0.74, confidence: 0.63, error: 0.37, accuracy: 0.63, kafkaLag: 418 },
      { time: "08:40", dataRate: 2140, latency: 211, driftScore: 0.76, confidence: 0.61, error: 0.39, accuracy: 0.61, kafkaLag: 446 }
    ],
    confidenceHistogram: [
      { bucket: "0.40-0.50", count: 12 },
      { bucket: "0.50-0.60", count: 24 },
      { bucket: "0.60-0.70", count: 41 },
      { bucket: "0.70-0.80", count: 57 },
      { bucket: "0.80-0.90", count: 49 },
      { bucket: "0.90-1.00", count: 22 }
    ]
  },
  drift: {
    featureDistributionShift: [
      { feature: "sensor_1", baseline: 0.44, current: 0.52 },
      { feature: "sensor_4", baseline: 0.48, current: 0.61 },
      { feature: "sensor_7", baseline: 0.53, current: 0.72 },
      { feature: "sensor_11", baseline: 0.57, current: 0.76 },
      { feature: "sensor_15", baseline: 0.61, current: 0.83 },
      { feature: "sensor_20", baseline: 0.66, current: 0.88 }
    ],
    featureScores: [
      { feature: "sensor_1", score: 0.24 },
      { feature: "sensor_4", score: 0.36 },
      { feature: "sensor_7", score: 0.52 },
      { feature: "sensor_11", score: 0.61 },
      { feature: "sensor_15", score: 0.67 },
      { feature: "sensor_20", score: 0.74 }
    ],
    conceptSeries: [
      { time: "08:21", accuracy: 0.91, error: 0.09, confidence: 0.91 },
      { time: "08:22", accuracy: 0.9, error: 0.1, confidence: 0.9 },
      { time: "08:23", accuracy: 0.89, error: 0.11, confidence: 0.89 },
      { time: "08:24", accuracy: 0.88, error: 0.12, confidence: 0.88 },
      { time: "08:25", accuracy: 0.87, error: 0.13, confidence: 0.87 },
      { time: "08:26", accuracy: 0.86, error: 0.14, confidence: 0.86 },
      { time: "08:27", accuracy: 0.84, error: 0.16, confidence: 0.84 },
      { time: "08:28", accuracy: 0.82, error: 0.18, confidence: 0.82 },
      { time: "08:29", accuracy: 0.81, error: 0.19, confidence: 0.81 },
      { time: "08:30", accuracy: 0.79, error: 0.21, confidence: 0.79 },
      { time: "08:31", accuracy: 0.77, error: 0.23, confidence: 0.77 },
      { time: "08:32", accuracy: 0.75, error: 0.25, confidence: 0.75 },
      { time: "08:33", accuracy: 0.74, error: 0.26, confidence: 0.74 },
      { time: "08:34", accuracy: 0.72, error: 0.28, confidence: 0.72 },
      { time: "08:35", accuracy: 0.7, error: 0.3, confidence: 0.7 },
      { time: "08:36", accuracy: 0.69, error: 0.31, confidence: 0.69 },
      { time: "08:37", accuracy: 0.67, error: 0.33, confidence: 0.67 },
      { time: "08:38", accuracy: 0.65, error: 0.35, confidence: 0.65 },
      { time: "08:39", accuracy: 0.63, error: 0.37, confidence: 0.63 },
      { time: "08:40", accuracy: 0.61, error: 0.39, confidence: 0.61 }
    ],
    alerts: [
      { timestamp: "08:32:09", severity: "Warning", message: "KS-test drift detected in sensor_7 and sensor_11" },
      { timestamp: "08:35:42", severity: "Warning", message: "Confidence trend dropped below 0.72" },
      { timestamp: "08:38:10", severity: "Critical", message: "Drift score crossed critical threshold (0.70)" }
    ]
  },
  rateControl: {
    rateLimitEnabled: true,
    rateLimit: 2600,
    simulatedRate: 2400,
    currentRate: 2140,
    cpuUsage: 72,
    memoryUsage: 67,
    actualVsLimitSeries: [
      { time: "08:21", actualRate: 2120, rateLimit: 2600 },
      { time: "08:22", actualRate: 2180, rateLimit: 2600 },
      { time: "08:23", actualRate: 2250, rateLimit: 2600 },
      { time: "08:24", actualRate: 2310, rateLimit: 2600 },
      { time: "08:25", actualRate: 2360, rateLimit: 2600 },
      { time: "08:26", actualRate: 2420, rateLimit: 2600 },
      { time: "08:27", actualRate: 2480, rateLimit: 2600 },
      { time: "08:28", actualRate: 2530, rateLimit: 2600 },
      { time: "08:29", actualRate: 2570, rateLimit: 2600 },
      { time: "08:30", actualRate: 2620, rateLimit: 2600 },
      { time: "08:31", actualRate: 2580, rateLimit: 2600 },
      { time: "08:32", actualRate: 2510, rateLimit: 2600 },
      { time: "08:33", actualRate: 2460, rateLimit: 2600 },
      { time: "08:34", actualRate: 2390, rateLimit: 2600 },
      { time: "08:35", actualRate: 2350, rateLimit: 2600 },
      { time: "08:36", actualRate: 2310, rateLimit: 2600 },
      { time: "08:37", actualRate: 2280, rateLimit: 2600 },
      { time: "08:38", actualRate: 2240, rateLimit: 2600 },
      { time: "08:39", actualRate: 2190, rateLimit: 2600 },
      { time: "08:40", actualRate: 2140, rateLimit: 2600 }
    ],
    kafkaLagSeries: [
      { time: "08:21", kafkaLag: 92 },
      { time: "08:22", kafkaLag: 98 },
      { time: "08:23", kafkaLag: 112 },
      { time: "08:24", kafkaLag: 126 },
      { time: "08:25", kafkaLag: 138 },
      { time: "08:26", kafkaLag: 151 },
      { time: "08:27", kafkaLag: 174 },
      { time: "08:28", kafkaLag: 196 },
      { time: "08:29", kafkaLag: 214 },
      { time: "08:30", kafkaLag: 236 },
      { time: "08:31", kafkaLag: 252 },
      { time: "08:32", kafkaLag: 268 },
      { time: "08:33", kafkaLag: 286 },
      { time: "08:34", kafkaLag: 304 },
      { time: "08:35", kafkaLag: 326 },
      { time: "08:36", kafkaLag: 349 },
      { time: "08:37", kafkaLag: 371 },
      { time: "08:38", kafkaLag: 394 },
      { time: "08:39", kafkaLag: 418 },
      { time: "08:40", kafkaLag: 446 }
    ]
  },
  selfHealing: {
    timeline: [
      { time: "08:32:09", event: "Drift detected", state: "Warning" },
      { time: "08:32:31", event: "Retrain triggered", state: "Warning" },
      { time: "08:34:22", event: "Model deployed: v2.3.1", state: "Healthy" },
      { time: "08:38:10", event: "Rate control tightened due to overload", state: "Critical" }
    ],
    modelHistory: [
      { time: "08:10", versionIndex: 1, modelVersion: "v2.1.0" },
      { time: "08:18", versionIndex: 1, modelVersion: "v2.1.0" },
      { time: "08:24", versionIndex: 2, modelVersion: "v2.2.0" },
      { time: "08:30", versionIndex: 2, modelVersion: "v2.2.0" },
      { time: "08:34", versionIndex: 3, modelVersion: "v2.3.1" },
      { time: "08:40", versionIndex: 3, modelVersion: "v2.3.1" }
    ],
    actionReasons: [
      { reason: "Drift", value: 54 },
      { reason: "Confidence drop", value: 28 },
      { reason: "Overload", value: 18 }
    ],
    lastActionTaken: "Rate control tightened and retrain policy escalated",
    currentSystemState: "Monitoring"
  },
  auditLogs: [
    {
      timestamp: "2026-04-07 08:32:09",
      event: "Drift Spike",
      reason: "Feature shift detected on sensor_7",
      actionTaken: "Retrain queued",
      status: "Warning",
      eventType: "DRIFT"
    },
    {
      timestamp: "2026-04-07 08:33:15",
      event: "Rate Limit",
      reason: "Input burst above policy",
      actionTaken: "Ingress throttled to 2600 eps",
      status: "Healthy",
      eventType: "RATE_LIMIT"
    },
    {
      timestamp: "2026-04-07 08:34:22",
      event: "Model Deploy",
      reason: "Retrain candidate passed quality gate",
      actionTaken: "Deployed model v2.3.1",
      status: "Healthy",
      eventType: "MODEL"
    },
    {
      timestamp: "2026-04-07 08:35:42",
      event: "Confidence Drop",
      reason: "Prediction confidence below 0.72",
      actionTaken: "Raised monitor severity",
      status: "Warning",
      eventType: "CONFIDENCE"
    },
    {
      timestamp: "2026-04-07 08:38:10",
      event: "Overload",
      reason: "Kafka lag crossed 400",
      actionTaken: "Autoscaler expanded consumers",
      status: "Critical",
      eventType: "OVERLOAD"
    }
  ]
};
