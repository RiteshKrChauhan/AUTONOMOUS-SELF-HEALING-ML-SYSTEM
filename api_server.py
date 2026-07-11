"""
api_server.py — Autonomous Self-Healing ML Dashboard Backend

Full pipeline:
  - Random Forest (sklearn) trained via ml/train.py
  - ADWIN concept drift detection (river) via drift/adwin_detector.py
  - KS-test feature drift detection via drift/data_drift.py
  - Isolation Forest anomaly detection via drift/anomaly_detector.py
  - Rolling error monitor via drift/error_monitor.py
  - Confidence intervals from RF tree variance via ml/confidence_predictor.py
  - Performance gate before shadow evaluation via ml/performance_gate.py
  - Shadow A/B evaluation before model promotion via ml/shadow_evaluator.py
  - Adaptive cooldown via decision/adaptive_cooldown.py
  - Decision engine via decision/engine.py
  - 8 injectable anomaly scenarios via simulation/scenarios/
"""

from collections import Counter, deque
from datetime import datetime
from pathlib import Path
from threading import Lock
import time

import numpy as np
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from dataset.processed.preprocess_module import load_data, add_rul
from decision.adaptive_cooldown import AdaptiveCooldown
from decision.engine import DecisionEngine
from drift.adwin_detector import DriftDetector
from drift.anomaly_detector import AnomalyDetector
from drift.data_drift import DataDriftDetector
from drift.error_monitor import ErrorMonitor
from governance.audit_log import AuditLog
from ml.confidence_predictor import ConfidencePredictor
from ml.performance_gate import ModelPerformanceGate
from ml.shadow_evaluator import ShadowModelEvaluator
from ml.train import train_model_with_holdout
from simulation.scenarios.registry import SCENARIO_REGISTRY, get_scenario_list


FEATURE_COLUMNS = [f"op_setting_{i}" for i in range(1, 4)] + [
    f"sensor_{i}" for i in range(1, 22)
]


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class AnomalyRequest(BaseModel):
    scenario: str = Field(default="sudden_spike")


class ControlRequest(BaseModel):
    simulatedRate: float | None = Field(default=None, ge=0.5, le=30.0)
    rateLimit: float | None = Field(default=None, ge=1.0, le=40.0)
    rateLimitEnabled: bool | None = None


# ---------------------------------------------------------------------------
# Streaming ML Runtime
# ---------------------------------------------------------------------------

class StreamingMLRuntime:
    def __init__(self):
        self.lock = Lock()
        self.rng = np.random.default_rng(42)
        self.base_path = Path(__file__).resolve().parent

        # Stream controls
        self.stream_rate = 8.0
        self.rate_limit = 14.0
        self.rate_limit_enabled = True
        self.kafka_lag = 0.0

        # Model state
        self.model = None
        self.scaler = None
        self.model_version = 1
        self.expected_train_columns: list = []

        # Counters
        self.sample_index = 0
        self.pointer = 0
        self.last_advance = time.monotonic()
        self.last_action = "System initialized and monitoring live stream"
        self.system_state = "Monitoring"

        # Active scenario state
        self.active_scenario_id = None
        self.active_scenario_remaining = 0
        self.active_scenario_cycle = 0

        # Ring buffers
        self.series = deque(maxlen=80)
        self.buffer = deque(maxlen=240)
        self.confidences = deque(maxlen=120)
        self.current_feature_window = deque(maxlen=60)
        self.action_reasons = Counter()

        # Governance — audit trail, alerts, timeline, model history
        self.audit = AuditLog()

        # Pipeline components
        self.anomaly_detector = AnomalyDetector(contamination=0.05)
        self.adwin_detector = DriftDetector()
        self.data_drift_detector = DataDriftDetector(
            window_size=45,
            p_threshold=0.01,
            drift_feature_ratio_threshold=0.45,
            min_effect_size=0.12,
        )
        self.error_monitor = ErrorMonitor(window_size=8)
        self.confidence_predictor = ConfidencePredictor(confidence_level=0.9)
        self.performance_gate = ModelPerformanceGate(improvement_threshold=0.95)
        self.shadow_evaluator = ShadowModelEvaluator(window_size=20)
        self.engine = DecisionEngine(error_threshold=75)
        self.cooldown = AdaptiveCooldown(min_cooldown=30, max_cooldown=75)

        # Load data and train initial model
        self._load_and_train()

        # Populate initial audit trail
        self.audit.append_timeline("Runtime started", "Healthy")
        self.audit.append_model_history(self.model_version)
        self.audit.append_audit(
            "Runtime Ready",
            "Initial Random Forest model trained on baseline engine units",
            f"Serving model v1.0.{self.model_version}",
            "Healthy",
            "MODEL",
        )

    # -----------------------------------------------------------------------
    # Data loading and initial training
    # -----------------------------------------------------------------------

    def _load_and_train(self):
        raw_path = self.base_path / "dataset" / "raw" / "train_FD001.txt"
        print(f"Loading dataset from {raw_path} ...")
        df = load_data(str(raw_path))
        df = add_rul(df)
        df["unit"] = df["unit"].astype(int)
        df["cycle"] = df["cycle"].astype(int)

        # Split units 76/24 train/stream
        units = df["unit"].unique().tolist()
        shuffled = self.rng.permutation(units).tolist()
        split_at = int(len(shuffled) * 0.76)
        train_units = set(shuffled[:split_at])
        stream_units = set(shuffled[split_at:])

        train_df = df[df["unit"].isin(train_units)].reset_index(drop=True)
        stream_df = df[df["unit"].isin(stream_units)].reset_index(drop=True)
        self.expected_train_columns = train_df.columns.tolist()

        print(f"Training baseline RF on {len(train_df)} rows ({len(train_units)} units) ...")
        self.model, self.scaler, _ = train_model_with_holdout(
            train_df, min_retrain_rows=30
        )
        print("Baseline model ready.")

        # Stream records (shuffled)
        stream_records = stream_df.to_dict(orient="records")
        perm = self.rng.permutation(len(stream_records)).tolist()
        self.stream_records = [stream_records[i] for i in perm]

        # Baseline statistics for drift display and scenario scaling
        self.baseline_means = {f: float(train_df[f].mean()) for f in FEATURE_COLUMNS}
        self.baseline_stds = {
            f: float(max(train_df[f].std(), 0.5)) for f in FEATURE_COLUMNS
        }

        # Fit Isolation Forest on training data
        self.anomaly_detector.fit(train_df)
        print("Anomaly detector fitted. Runtime ready.")

    # -----------------------------------------------------------------------
    # Utility helpers
    # -----------------------------------------------------------------------

    def _now_parts(self):
        """Convenience timestamp helper (used for latency/point timestamps)."""
        from datetime import datetime as _dt
        now = _dt.now()
        return now.strftime("%H:%M:%S"), now.strftime("%Y-%m-%d %H:%M:%S")

    # -----------------------------------------------------------------------
    # Stream helpers
    # -----------------------------------------------------------------------

    def _next_row(self):
        row = dict(self.stream_records[self.pointer % len(self.stream_records)])
        self.pointer += 1
        return row

    def _apply_stream_noise(self, row):
        data = dict(row)
        for feature in FEATURE_COLUMNS:
            scale = self.baseline_stds.get(feature, 1.0)
            data[feature] = float(data[feature] + self.rng.normal(0, 0.015 * scale))
        return data

    def _apply_active_scenario(self, data):
        if self.active_scenario_id is None or self.active_scenario_remaining <= 0:
            return False
        scenario_cls = SCENARIO_REGISTRY.get(self.active_scenario_id)
        if scenario_cls is None:
            return False

        scenario_cls.apply(data, self.active_scenario_cycle, self.baseline_stds, self.rng)
        self.active_scenario_cycle += 1
        self.active_scenario_remaining -= 1

        if self.active_scenario_remaining <= 0:
            name = scenario_cls.META["name"]
            self.audit.append_timeline(f"Scenario '{name}' completed", "Healthy")
            self.audit.append_audit(
                "Scenario Completed",
                f"Scenario '{name}' ran for {scenario_cls.META['duration']} cycles",
                "Returning to baseline stream",
                "Healthy",
                "DRIFT",
            )
            self.active_scenario_id = None
            self.active_scenario_cycle = 0

        return True

    # -----------------------------------------------------------------------
    # Metrics helpers
    # -----------------------------------------------------------------------

    def _confidence_value(self, std, error):
        return float(np.clip(1.0 - (std / 95.0) - (error / 320.0), 0.35, 0.99))

    def _status_from_metrics(self, drift_score, rolling_avg, action):
        if action in {"RETRAIN_URGENT", "ALERT"} or drift_score >= 0.82:
            return "Critical"
        if action in {"RETRAIN", "MONITOR", "WATCH"} or drift_score >= 0.48:
            return "Warning"
        if rolling_avg is not None and rolling_avg > 70:
            return "Warning"
        return "Healthy"

    def _feature_scores(self):
        if not self.current_feature_window:
            return [
                {"feature": f, "score": 0.0}
                for f in ["sensor_2", "sensor_4", "sensor_7", "sensor_11", "sensor_15", "sensor_20"]
            ]
        scores = []
        for feature in FEATURE_COLUMNS:
            values = [row[feature] for row in self.current_feature_window]
            bm = self.baseline_means.get(feature, 0.0)
            bs = max(self.baseline_stds.get(feature, 1.0), 0.5)
            score = min(abs(float(np.mean(values)) - bm) / (3.0 * bs), 1.0)
            scores.append({"feature": feature, "score": round(float(score), 3)})
        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores[:8]

    def _distribution_shift(self, feature_scores):
        output = []
        for item in feature_scores[:6]:
            feature = item["feature"]
            values = [row[feature] for row in self.current_feature_window]
            bm = self.baseline_means.get(feature, 0.0)
            bs = max(self.baseline_stds.get(feature, 1.0), 0.5)
            current_mean = float(np.mean(values)) if values else bm
            output.append(
                {
                    "feature": feature,
                    "baseline": 0.5,
                    "current": round(
                        float(np.clip(0.5 + (current_mean - bm) / (6 * bs), 0, 1)), 3
                    ),
                }
            )
        return output

    def _histogram(self):
        buckets = [(0.3, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.01)]
        values = list(self.confidences)
        return [
            {
                "bucket": f"{low:.2f}-{high if high < 1 else 1.0:.2f}",
                "count": sum(1 for v in values if low <= v < high),
            }
            for low, high in buckets
        ]

    # -----------------------------------------------------------------------
    # Retraining pipeline: performance gate → shadow evaluation
    # -----------------------------------------------------------------------

    def _maybe_retrain(self, action, drift_score, rolling_avg):
        should_retrain_now, required, elapsed = self.cooldown.should_retrain(
            self.sample_index, drift_score
        )

        # Block new retrain while shadow evaluation is in progress
        if self.shadow_evaluator.is_evaluating:
            return required, elapsed

        strong_signal = action in {"RETRAIN", "RETRAIN_URGENT"} or drift_score > 0.68
        retrain_signal = (rolling_avg is not None and rolling_avg > 45) or drift_score > 0.72

        if not (strong_signal and should_retrain_now and retrain_signal and len(self.buffer) >= 55):
            return required, elapsed

        # Build candidate training DataFrame from buffer
        buffer_list = list(self.buffer)
        try:
            buffer_df = pd.DataFrame(buffer_list)
        except Exception:
            return required, elapsed

        # Schema guard
        missing = [c for c in self.expected_train_columns if c not in buffer_df.columns]
        if missing:
            self._append_audit(
                "Retrain Skipped",
                f"Schema mismatch — missing columns: {missing[:3]}",
                "Kept current production model",
                "Warning",
                "MODEL",
            )
            return required, elapsed

        buffer_df = buffer_df[
            [c for c in self.expected_train_columns if c in buffer_df.columns]
        ]

        # Train candidate model
        try:
            new_model, new_scaler, new_mae = train_model_with_holdout(
                buffer_df, min_retrain_rows=30
            )
        except Exception as err:
            self.audit.append_audit(
                "Retrain Failed",
                f"Training error: {str(err)[:120]}",
                "Kept current production model",
                "Warning",
                "MODEL",
            )
            return required, elapsed

        if new_model is None:
            return required, elapsed

        # Performance gate: compare candidate vs current model on validation slice
        validation_df = pd.DataFrame(buffer_list[-20:])
        validation_df = validation_df[
            [c for c in self.expected_train_columns if c in validation_df.columns]
        ]
        should_accept, current_mae, candidate_mae, gate_reason = (
            self.performance_gate.should_accept_new_model(
                self.model, self.scaler, new_model, new_scaler, new_mae, validation_df
            )
        )

        cand_str = f"{candidate_mae:.2f}" if candidate_mae is not None else "N/A"
        curr_str = f"{current_mae:.2f}" if current_mae is not None else "N/A"

        if should_accept:
            # Gate passed → start shadow A/B evaluation
            self.shadow_evaluator.start_shadow_evaluation(new_model, new_scaler)
            self.cooldown.mark_retrain(self.sample_index)
            self.system_state = "Shadowing"
            self.last_action = (
                f"Shadow evaluation started — gate passed ({gate_reason})"
            )
            self.action_reasons["Shadow evaluation"] += 1
            self.audit.append_timeline("Shadow A/B evaluation started", "Warning")
            self.audit.append_audit(
                "Shadow Started",
                f"Candidate MAE {cand_str} vs production MAE {curr_str} — {gate_reason}",
                f"Running A/B test over {self.shadow_evaluator.window_size} live cycles",
                "Warning",
                "MODEL",
            )
        else:
            # Gate rejected candidate immediately — rollback
            self.action_reasons["Quality gate"] += 1
            self.audit.append_audit(
                "Retrain Rejected",
                f"Performance gate: candidate {cand_str} vs production {curr_str} — {gate_reason}",
                "Production model retained — no shadow evaluation",
                "Warning",
                "MODEL",
            )
            self.audit.append_alert(
                "Warning",
                f"Retrain candidate rejected by gate: {gate_reason}",
            )

        return required, elapsed

    # -----------------------------------------------------------------------
    # Per-sample processing loop
    # -----------------------------------------------------------------------

    def _process_one(self):
        raw = self._next_row()
        data = self._apply_stream_noise(raw)
        scenario_active = self._apply_active_scenario(data)

        self.buffer.append(data.copy())
        self.current_feature_window.append(
            {f: data[f] for f in FEATURE_COLUMNS}
        )

        actual = float(data["RUL"])

        # --- Isolation Forest anomaly detection ---
        try:
            is_anomaly, anomaly_score = self.anomaly_detector.is_anomaly(data)
        except Exception:
            is_anomaly, anomaly_score = False, 0.0

        # --- RF prediction with confidence intervals ---
        try:
            pred, pred_lower, pred_upper, pred_std = (
                self.confidence_predictor.predict_with_confidence(
                    self.model, self.scaler, data
                )
            )
        except Exception:
            pred = float(actual)
            pred_lower = pred - 10.0
            pred_upper = pred + 10.0
            pred_std = 5.0

        confidence_category = self.confidence_predictor.get_confidence_category(pred_std)
        error = abs(actual - pred)

        # --- Rolling error monitoring ---
        rolling_avg = self.error_monitor.update(error)
        trend = self.error_monitor.is_increasing()

        # --- Shadow model A/B evaluation ---
        if self.shadow_evaluator.is_evaluating:
            should_promote, prod_mae, shadow_mae = self.shadow_evaluator.evaluate_both(
                self.model, self.scaler, data, actual
            )
            if should_promote:
                self.model = self.shadow_evaluator.shadow_model
                self.scaler = self.shadow_evaluator.shadow_scaler
                self.model_version += 1
                self.shadow_evaluator.stop_evaluation()
                self.system_state = "Monitoring"
                self.last_action = (
                    f"Shadow model promoted → v1.0.{self.model_version}"
                )
                self.action_reasons["Shadow promoted"] += 1
                self.audit.append_model_history(self.model_version)
                self.audit.append_timeline(
                    f"Model v1.0.{self.model_version} promoted via shadow evaluation",
                    "Healthy",
                )
                self.audit.append_audit(
                    "Shadow Promoted",
                    f"Shadow MAE {shadow_mae:.2f} < Production MAE {prod_mae:.2f} (20-cycle window)",
                    self.last_action,
                    "Healthy",
                    "MODEL",
                )
            elif prod_mae is not None:
                # Window complete but shadow wasn't better → implicit rollback
                self.shadow_evaluator.stop_evaluation()
                self.system_state = "Monitoring"
                self.last_action = "Shadow candidate rejected — production model retained"
                self.action_reasons["Shadow rejected"] += 1
                self.audit.append_timeline(
                    "Shadow model rejected — production retained", "Warning"
                )
                self.audit.append_audit(
                    "Shadow Rejected",
                    f"Shadow MAE {shadow_mae:.2f} ≥ Production MAE {prod_mae:.2f} (20-cycle window)",
                    "Production model retained (implicit rollback)",
                    "Warning",
                    "MODEL",
                )

        # --- ADWIN concept drift detection (error stream) ---
        adwin_drift = self.adwin_detector.update(
            rolling_avg if rolling_avg is not None else error
        )

        # --- KS-test feature drift detection ---
        drift_result = self.data_drift_detector.update_with_details(data)
        data_drift = bool(drift_result["drift_detected"])
        ks_drift_score = float(drift_result["drift_score"])
        combined_drift = adwin_drift or data_drift

        # --- Composite drift score ---
        drift_score = ks_drift_score
        if rolling_avg is not None:
            drift_score = max(drift_score, min(rolling_avg / 70.0, 1.0) * 0.65)
        if adwin_drift:
            drift_score = max(drift_score, 0.72)
        drift_score = float(drift_score)

        # --- Decision engine ---
        action = self.engine.decide(combined_drift, rolling_avg, trend, drift_score)
        required_cooldown, elapsed_cooldown = self._maybe_retrain(
            action, drift_score, rolling_avg
        )

        # --- Confidence and status ---
        confidence = self._confidence_value(pred_std, error)
        self.confidences.append(confidence)
        status = self._status_from_metrics(drift_score, rolling_avg, action)

        # Update system state
        if not self.shadow_evaluator.is_evaluating:
            if action.startswith("RETRAIN"):
                self.system_state = "Self-healing"
            elif self.system_state != "Shadowing":
                self.system_state = "Monitoring"

        # --- Scenario audit (throttled) ---
        if scenario_active and self.active_scenario_cycle % 12 == 0:
            sc = SCENARIO_REGISTRY.get(self.active_scenario_id)
            if sc:
                self.action_reasons["Scenario injection"] += 1
                self.audit.append_alert(
                    "Critical" if drift_score > 0.8 else "Warning",
                    f"Scenario '{sc.META['name']}' — {self.active_scenario_remaining} cycles remaining",
                )
                self.audit.append_audit(
                    "Scenario Active",
                    sc.META["description"],
                    "Drift monitors escalated",
                    status,
                    "DRIFT",
                )

        # --- Decision audit (throttled) ---
        if action in {"RETRAIN", "RETRAIN_URGENT", "ALERT", "MONITOR"} and self.sample_index % 10 == 0:
            event_type = "DRIFT" if action.startswith("RETRAIN") else "CONFIDENCE"
            self.audit.append_timeline(f"{action.replace('_', ' ').title()} decision", status)
            self.audit.append_audit(
                action.replace("_", " ").title(),
                f"Drift {drift_score:.2f}, MAE {error:.2f}, ADWIN={'Yes' if adwin_drift else 'No'}, DataDrift={'Yes' if data_drift else 'No'}",
                "Autonomous policy evaluated retraining",
                status,
                event_type,
            )
            self.action_reasons[
                "Drift" if event_type == "DRIFT" else "Confidence drop"
            ] += 1

        # --- Rate control / Kafka lag simulation ---
        effective_limit = self.rate_limit if self.rate_limit_enabled else self.stream_rate
        if self.rate_limit_enabled and self.stream_rate > self.rate_limit:
            self.kafka_lag += (self.stream_rate - self.rate_limit) * 0.8
            self.action_reasons["Overload"] += 1
        else:
            self.kafka_lag = max(0.0, self.kafka_lag - max(1.0, effective_limit * 0.2))

        clock, _ = self._now_parts()
        latency = int(
            np.clip(42 + self.stream_rate * 2 + drift_score * 80 + self.kafka_lag / 3, 35, 420)
        )

        point = {
            "time": clock,
            "sampleIndex": self.sample_index,
            "dataRate": round(self.stream_rate, 1),
            "latency": latency,
            "driftScore": round(drift_score, 3),
            "confidence": round(confidence, 3),
            "confidenceCategory": confidence_category,
            "error": round(min(error / 125.0, 1.0), 3),
            "mae": round(error, 2),
            "rollingMae": None if rolling_avg is None else round(float(rolling_avg), 2),
            "accuracy": round(max(0.0, 1.0 - min(error / 125.0, 1.0)), 3),
            "kafkaLag": int(self.kafka_lag),
            "prediction": round(pred, 2),
            "actual": round(actual, 2),
            "predLower": round(pred_lower, 2),
            "predUpper": round(pred_upper, 2),
            "action": action,
            "status": status,
            "adwinDrift": bool(adwin_drift),
            "dataDrift": bool(data_drift),
            "anomalyDetected": bool(is_anomaly),
            "anomalyScore": round(float(anomaly_score), 3),
            "scenarioActive": scenario_active,
            "cooldownElapsed": elapsed_cooldown,
            "cooldownRequired": required_cooldown,
        }
        self.series.append(point)
        self.sample_index += 1

    # -----------------------------------------------------------------------
    # Time-driven advance (called on each dashboard poll)
    # -----------------------------------------------------------------------

    def advance(self):
        now = time.monotonic()
        elapsed = now - self.last_advance
        due = int(elapsed * self.stream_rate)
        if not self.series:
            due = max(due, 24)
        due = max(0, min(due, 35))
        if due == 0:
            return
        for _ in range(due):
            self._process_one()
        self.last_advance = now

    # -----------------------------------------------------------------------
    # Public API methods
    # -----------------------------------------------------------------------

    def inject_anomaly(self, request):
        with self.lock:
            scenario_cls = SCENARIO_REGISTRY.get(request.scenario)
            if scenario_cls is None:
                return {"ok": False, "error": f"Unknown scenario: {request.scenario}"}
            meta = scenario_cls.META
            self.active_scenario_id = request.scenario
            self.active_scenario_remaining = meta["duration"]
            self.active_scenario_cycle = 0
            self.last_action = (
                f"Scenario '{meta['name']}' injected ({meta['severity']} severity)"
            )
            self.system_state = "Self-healing"
            self.audit.append_timeline(f"Scenario: {meta['name']}", "Critical")
            self.audit.append_audit(
                "Scenario Injected",
                meta["description"],
                f"Active for {meta['duration']} cycles — {meta['severity']} severity",
                "Critical",
                "DRIFT",
            )
            self.audit.append_alert(
                "Critical" if meta["severity"] in {"Critical", "High"} else "Warning",
                f"Scenario '{meta['name']}': {meta['description'][:70]}",
            )
            return {"ok": True, "scenario": meta}

    def update_controls(self, request):
        with self.lock:
            if request.simulatedRate is not None:
                self.stream_rate = float(request.simulatedRate)
            if request.rateLimit is not None:
                self.rate_limit = float(request.rateLimit)
            if request.rateLimitEnabled is not None:
                self.rate_limit_enabled = bool(request.rateLimitEnabled)
            self.audit.append_audit(
                "Rate Policy Updated",
                "Operator changed streaming controls",
                f"Rate {self.stream_rate:.1f} eps, limit {self.rate_limit:.1f} eps",
                "Healthy",
                "RATE_LIMIT",
            )
            return {"ok": True}

    def dashboard(self):
        with self.lock:
            self.advance()
            latest = self.series[-1] if self.series else {}
            feature_scores = self._feature_scores()
            series = list(self.series)
            action_reasons = (
                [
                    {"reason": r, "value": v}
                    for r, v in self.action_reasons.items()
                    if v > 0
                ]
                or [{"reason": "Monitoring", "value": 1}]
            )

            # Active scenario metadata for dashboard
            sc_meta = (
                SCENARIO_REGISTRY[self.active_scenario_id].META
                if self.active_scenario_id
                else None
            )

            return {
                "overview": {
                    "systemStatus": latest.get("status", "Healthy"),
                    "activeModelVersion": f"v1.0.{self.model_version}",
                    "series": series,
                    "confidenceHistogram": self._histogram(),
                    "latestSample": {
                        "prediction": latest.get("prediction", 0),
                        "actual": latest.get("actual", 0),
                        "interval": [
                            latest.get("predLower", 0),
                            latest.get("predUpper", 0),
                        ],
                        "action": latest.get("action", "STABLE"),
                        "sampleIndex": latest.get("sampleIndex", 0),
                        "confidenceCategory": latest.get(
                            "confidenceCategory", "medium_confidence"
                        ),
                        "adwinDrift": latest.get("adwinDrift", False),
                        "dataDrift": latest.get("dataDrift", False),
                        "anomalyDetected": latest.get("anomalyDetected", False),
                        "anomalyScore": latest.get("anomalyScore", 0.0),
                    },
                    "scenario": {
                        "active": self.active_scenario_remaining > 0,
                        "remaining": self.active_scenario_remaining,
                        "id": self.active_scenario_id,
                        "name": sc_meta["name"] if sc_meta else None,
                        "severity": sc_meta["severity"] if sc_meta else None,
                    },
                },
                "drift": {
                    "featureDistributionShift": self._distribution_shift(feature_scores),
                    "featureScores": feature_scores,
                    "conceptSeries": series,
                    "alerts": self.audit.get_alerts(),
                },
                "rateControl": {
                    "rateLimitEnabled": self.rate_limit_enabled,
                    "rateLimit": round(self.rate_limit, 1),
                    "simulatedRate": round(self.stream_rate, 1),
                    "currentRate": round(
                        min(
                            self.stream_rate,
                            self.rate_limit if self.rate_limit_enabled else self.stream_rate,
                        ),
                        1,
                    ),
                    "cpuUsage": int(
                        np.clip(
                            28 + self.stream_rate * 2.1 + latest.get("driftScore", 0) * 24,
                            20,
                            96,
                        )
                    ),
                    "memoryUsage": int(
                        np.clip(
                            38 + len(self.buffer) / 6 + latest.get("driftScore", 0) * 18,
                            30,
                            92,
                        )
                    ),
                    "actualVsLimitSeries": [
                        {
                            "time": p["time"],
                            "actualRate": p["dataRate"],
                            "rateLimit": round(self.rate_limit, 1),
                        }
                        for p in series
                    ],
                    "kafkaLagSeries": [
                        {"time": p["time"], "kafkaLag": p["kafkaLag"]} for p in series
                    ],
                },
                "selfHealing": {
                    "timeline": self.audit.get_timeline(),
                    "modelHistory": self.audit.get_model_history(),
                    "actionReasons": action_reasons,
                    "lastActionTaken": self.last_action,
                    "currentSystemState": self.system_state,
                    "shadowEvaluation": self.shadow_evaluator.get_status(),
                },
                "auditLogs": self.audit.get_audit_logs(),
            }


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

runtime = StreamingMLRuntime()
app = FastAPI(title="Autonomous Self-Healing ML API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "modelVersion": f"v1.0.{runtime.model_version}"}


@app.get("/api/dashboard")
def dashboard():
    return runtime.dashboard()


@app.get("/api/scenarios")
def get_scenarios():
    return {"scenarios": get_scenario_list()}


@app.post("/api/anomalies")
def inject_anomaly(request: AnomalyRequest):
    return runtime.inject_anomaly(request)


@app.post("/api/controls")
def update_controls(request: ControlRequest):
    return runtime.update_controls(request)


@app.post("/api/reset")
def reset_runtime():
    global runtime
    runtime = StreamingMLRuntime()
    return {"ok": True}
