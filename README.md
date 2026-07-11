# Autonomous Self-Healing ML System

Production-style streaming ML dashboard for predictive maintenance. The system simulates live turbofan sensor data, detects drift, lets an operator inject synthetic anomalies, and automatically retrains a Random Forest model when self-healing policy conditions are met.

## Core Capabilities

- Live-like sensor stream from NASA CMAPSS turbofan data.
- FastAPI backend serving dashboard-ready operational metrics.
- React dashboard with system health, throughput, latency, drift, confidence, feature shift, model version history, and governance logs.
- Manual **Inject Anomalies** action to create sensor drift on demand.
- Random Forest regression model for Remaining Useful Life prediction.
- Ensemble-based confidence interval from Random Forest tree variance.
- Drift-aware retraining and automatic model promotion.
- Rate controls for simulated stream pressure and throttling behavior.

## Architecture

```text
.
├── api_server.py              # FastAPI live runtime, model training, drift policy, dashboard API
├── dataset/
│   ├── raw/                   # CMAPSS turbofan source data
│   └── processed/             # Reusable preprocessing helpers
├── decision/                  # Self-healing decision engine and adaptive cooldown
├── drift/                     # Feature drift and error monitoring
├── frontend/                  # React + Vite dashboard
├── governance/                # Audit logging helpers
├── ml/                        # Model helper modules retained for extension
├── simulation/                # Streaming and anomaly utility modules
└── streaming/                 # Optional Kafka integration helpers
```

## Run Locally

Install backend dependencies:

```bash
pip install --upgrade --force-reinstall -r requirements.txt
```

Start the backend:

```bash
uvicorn api_server:app --host 127.0.0.1 --port 8000
```

Start the dashboard:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

The frontend proxies `/api` requests to `http://127.0.0.1:8000`.

## Dashboard Workflow

1. Confirm the top bar shows `Live`.
2. Watch the stream charts update in real time.
3. Click **Inject Anomalies** to shift sensor values and trigger drift.
4. Monitor drift score, feature-level shift, confidence, and alerts.
5. When policy thresholds and cooldown rules are satisfied, the backend retrains and promotes a new `v1.0.x` model.
6. Review the self-healing timeline and governance logs for the full decision trail.

## Backend API

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/health` | Health check and active model version |
| `GET` | `/api/dashboard` | Complete live dashboard payload |
| `POST` | `/api/anomalies` | Inject synthetic sensor drift |
| `POST` | `/api/controls` | Update stream rate and rate-limit settings |
| `POST` | `/api/reset` | Reset runtime state and retrain the baseline model |

Example anomaly request:

```bash
curl -X POST http://127.0.0.1:8000/api/anomalies ^
  -H "Content-Type: application/json" ^
  -d "{\"intensity\":14,\"duration\":55,\"feature_count\":7}"
```

## Production Notes

- Runtime artifacts are intentionally ignored: `__pycache__`, logs, frontend builds, MLflow stores, and local databases.
- The active dashboard path is `api_server.py` plus `frontend/`; old CLI entry points have been removed.
- Random Forest is used for both initial serving and retrained candidate models.
- Model promotion is gated by drift severity, rolling error, adaptive cooldown, and candidate validation error.
