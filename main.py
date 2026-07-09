from dataset.processed.preprocess_module import load_data, add_rul
from simulation.data_generator import stream_data
from simulation.chaos_controller import inject_noise, inject_drift
from ml.train import train_model, train_model_with_holdout
from ml.predict import predict
from ml.performance_gate import ModelPerformanceGate
from ml.shadow_evaluator import ShadowModelEvaluator
from ml.confidence_predictor import ConfidencePredictor
from drift.error_monitor import ErrorMonitor
from drift.adwin_detector import DriftDetector
from drift.anomaly_detector import AnomalyDetector
from decision.engine import DecisionEngine
from decision.adaptive_cooldown import AdaptiveCooldown
from governance.governance_logger import GovernanceLogger
from visualization.plotter import SystemVisualizer
from sklearn.model_selection import train_test_split
from collections import deque
from drift.data_drift import DataDriftDetector
import mlflow
import numpy as np
import pandas as pd


def split_by_unit(df, stream_fraction=0.2, random_state=42):
    units = df['unit'].unique()
    train_units, stream_units = train_test_split(
        units,
        test_size=stream_fraction,
        random_state=random_state,
    )

    train_df = df[df['unit'].isin(train_units)].copy()
    stream_df = df[df['unit'].isin(stream_units)].copy()

    return train_df, stream_df


def is_retrain_buffer_valid(df, min_rows=30, min_units=1):
    if len(df) <= min_rows:
        return False, f"need > {min_rows} buffered samples"

    if 'unit' not in df.columns or df['unit'].nunique() < min_units:
        return False, f"need at least {min_units} distinct units"

    if 'RUL' not in df.columns:
        return False, "missing RUL column"

    feature_df = df.drop(columns=['RUL', 'unit', 'cycle'], errors='ignore')

    if feature_df.empty:
        return False, "no features available for training"

    if feature_df.isnull().any().any() or df['RUL'].isnull().any():
        return False, "missing values found in retrain buffer"

    # Ensure we do not retrain on corrupted non-numeric values.
    finite_mask = np.isfinite(feature_df.to_numpy(dtype=float)).all()
    if not finite_mask:
        return False, "non-finite feature values found"

    return True, "ok"


def run_pipeline():
    # load data
    df = load_data("dataset/raw/train_FD001.txt")
    df = add_rul(df)

    train_df, stream_df = split_by_unit(df, stream_fraction=0.2, random_state=42)
    expected_retrain_columns = train_df.columns.tolist()

    # train model
    model, scaler = train_model(train_df)

    # HIGH PRIORITY: Model performance gating
    performance_gate = ModelPerformanceGate(improvement_threshold=0.95)
    
    # MEDIUM PRIORITY: Shadow model evaluation
    shadow_evaluator = ShadowModelEvaluator(window_size=20)
    
    # MEDIUM PRIORITY: Confidence intervals
    confidence_predictor = ConfidencePredictor(confidence_level=0.9)
    
    # MEDIUM PRIORITY: Anomaly detection
    anomaly_detector = AnomalyDetector(contamination=0.05)
    anomaly_detector.fit(train_df)

    # monitors
    monitor = ErrorMonitor(window_size=5)
    detector = DriftDetector()
    data_drift_detector = DataDriftDetector(window_size=30)
    engine = DecisionEngine(error_threshold=25)
    
    # MEDIUM PRIORITY: Adaptive cooldown
    adaptive_cooldown = AdaptiveCooldown(min_cooldown=20, max_cooldown=50)
    
    buffer = deque(maxlen=100)
    retrain_error_threshold = engine.error_threshold
    skipped_retrains = 0
    rejected_retrains = 0
    anomaly_count = 0
    logs = []
    
    # Phase 14: Structured logging
    logger = GovernanceLogger(log_dir="logs")

    print("\n--- STREAM + DRIFT DETECTION ---\n")

    for i, data in enumerate(stream_data(stream_df.head(200))):

        # chaos
        data = inject_noise(data)
        if i > 10:
            data = inject_drift(data, shift=10)

        # Keep latest stream samples for possible drift-aware retraining.
        buffer.append(data.copy())
        
        # MEDIUM PRIORITY: Anomaly detection
        is_anomaly, anomaly_score = anomaly_detector.is_anomaly(data)
        if is_anomaly:
            anomaly_count += 1
            print(f"WARNING: ANOMALY DETECTED (score: {anomaly_score:.3f})")

        # prediction with confidence intervals
        actual = data['RUL']
        
        # MEDIUM PRIORITY: Confidence intervals
        pred, pred_lower, pred_upper, pred_std = confidence_predictor.predict_with_confidence(
            model, scaler, data
        )
        confidence_category = confidence_predictor.get_confidence_category(pred_std)
        
        error = abs(actual - pred)
        
        # Shadow model evaluation (if active)
        if shadow_evaluator.is_evaluating:
            should_promote, prod_mae, shadow_mae = shadow_evaluator.evaluate_both(
                model, scaler, data, actual
            )
            if should_promote:
                print(f"\nSHADOW MODEL PROMOTION")
                print(f"Production MAE: {prod_mae:.2f}")
                print(f"Shadow MAE: {shadow_mae:.2f}")
                print(f"Promoting shadow model to production\n")
                
                model = shadow_evaluator.shadow_model
                scaler = shadow_evaluator.shadow_scaler
                shadow_evaluator.stop_evaluation()
                
                logs.append({
                    "event": "shadow_promoted",
                    "index": i,
                    "cycle": int(data["cycle"]),
                    "production_mae": prod_mae,
                    "shadow_mae": shadow_mae
                })

        # monitoring
        rolling_avg = monitor.update(error)
        trend = monitor.is_increasing()

        # ADWIN
        drift_input = rolling_avg if rolling_avg is not None else error
        drift = detector.update(drift_input)
        data_drift_result = data_drift_detector.update_with_details(data)
        data_drift = data_drift_result["drift_detected"]
        drift_score = data_drift_result["drift_score"]
        drifted_features = data_drift_result["drifted_features"]
        combined_drift = drift or data_drift

        # MEDIUM PRIORITY: Enhanced decision engine with drift_score
        action = engine.decide(combined_drift, rolling_avg, trend, drift_score)
        
        # MEDIUM PRIORITY: Adaptive cooldown check
        should_retrain, required_cooldown, cycles_elapsed = adaptive_cooldown.should_retrain(
            i, drift_score
        )
        
        cycle_log = {
            "event": "cycle",
            "index": i,
            "cycle": int(data["cycle"]),
            "error": float(error),
            "prediction": float(pred),
            "pred_lower": float(pred_lower),
            "pred_upper": float(pred_upper),
            "pred_std": float(pred_std),
            "confidence": confidence_category,
            "is_anomaly": bool(is_anomaly),
            "anomaly_score": float(anomaly_score),
            "rolling_avg": None if rolling_avg is None else float(rolling_avg),
            "trend": bool(trend),
            "drift": bool(drift),
            "data_drift": bool(data_drift),
            "combined_drift": bool(combined_drift),
            "data_drift_score": float(drift_score),
            "drifted_features": list(drifted_features),
            "action": action,
            "adaptive_cooldown_elapsed": cycles_elapsed,
            "adaptive_cooldown_required": required_cooldown,
        }
        logs.append(cycle_log)
        logger.log_cycle(cycle_log)
        # print
        print(
            f"Cycle: {int(data['cycle'])} | "
            f"Error: {error:.2f} | "
            f"Pred: {pred:.1f} [{pred_lower:.1f}, {pred_upper:.1f}] ({confidence_category}) | "
            f"Rolling Avg: {rolling_avg if rolling_avg is not None else '...'} | "
            f"Drift Score: {drift_score:.3f} | "
            f"Action: {action} | "
            f"Cooldown: {cycles_elapsed}/{required_cooldown}"
        )

        # MEDIUM PRIORITY: Use adaptive cooldown instead of fixed
        if (
            action in ["RETRAIN", "RETRAIN_URGENT"]
            and should_retrain
            and rolling_avg is not None
            and rolling_avg > retrain_error_threshold
        ):
            print("\nRETRAIN TRIGGERED")
            print(f"Cycle: {int(data['cycle'])}")
            print(f"Rolling Avg: {rolling_avg:.2f}")
            print(f"Drift Score: {drift_score:.3f}")
            print(f"Cooldown: {cycles_elapsed}/{required_cooldown} cycles")
            print(f"Buffer Size: {len(buffer)}")
            print("\nRetrain candidate accepted\n")
            logs.append(
                {
                    "event": "retrain_candidate",
                    "index": i,
                    "cycle": int(data["cycle"]),
                    "buffer_size": len(buffer),
                }
            )

            import pandas as pd
            new_df = pd.DataFrame(buffer)

            # Keep retrain preprocessing compatible with original training schema.
            if 'RUL' not in new_df.columns:
                new_df = add_rul(new_df)

            missing_cols = [c for c in expected_retrain_columns if c not in new_df.columns]
            if missing_cols:
                reason = f"schema mismatch, missing columns: {missing_cols}"
                print(f"Skipping retrain: {reason}\n")
                logs.append(
                    {
                        "event": "retrain_skipped",
                        "index": i,
                        "cycle": int(data["cycle"]),
                        "reason": reason,
                    }
                )
                continue

            # Drop unexpected fields from streaming payload and keep training schema.
            new_df = new_df.loc[:, expected_retrain_columns]

            is_valid, reason = is_retrain_buffer_valid(new_df, min_rows=30, min_units=1)
            if not is_valid:
                print(f"Skipping retrain: {reason}\n")
                logs.append(
                    {
                        "event": "retrain_skipped",
                        "index": i,
                        "cycle": int(data["cycle"]),
                        "reason": reason,
                    }
                )
                continue

            min_retrain_rows = 30
            retrain_data_size = len(new_df)
            new_model, new_scaler, new_mae = None, None, None
            print(f"Retrain decision -> data size: {retrain_data_size}")

            try:
                with mlflow.start_run(run_name="retrain_attempt"):
                    mlflow.log_param("trigger", "drift")
                    mlflow.log_metric("data_size", retrain_data_size)

                    if retrain_data_size < min_retrain_rows:
                        mlflow.log_param("status", "skipped")
                        print("❌ Retrain skipped: insufficient data")
                        print("Reason: insufficient data")
                    else:
                        mlflow.log_param("status", "executed")
                        print("✅ Retrain executed")
                        # train + holdout + model logging happens in train_model_with_holdout.
                        new_model, new_scaler, new_mae = train_model_with_holdout(
                            new_df,
                            min_retrain_rows=min_retrain_rows,
                        )
                        
                        # HIGH PRIORITY: Model performance gating
                        if new_model and new_scaler and new_mae:
                            validation_buffer = new_df.tail(20)
                            should_accept, current_mae, candidate_mae, reason = performance_gate.should_accept_new_model(
                                model, scaler, new_model, new_scaler, new_mae, validation_buffer
                            )
                            
                            print(f"\nPERFORMANCE GATE")
                            print(f"Current MAE: {current_mae if current_mae else 'N/A'}")
                            print(f"Candidate MAE: {candidate_mae:.2f}")
                            print(f"Decision: {'ACCEPT' if should_accept else 'REJECT'} ({reason})")
                            
                            if not should_accept:
                                rejected_retrains += 1
                                logs.append({
                                    "event": "retrain_rejected_by_gate",
                                    "index": i,
                                    "cycle": int(data["cycle"]),
                                    "current_mae": current_mae,
                                    "candidate_mae": candidate_mae,
                                    "reason": reason
                                })
                                logger.log_retrain({
                                    "status": "rejected",
                                    "reason": reason,
                                    "current_mae": current_mae,
                                    "candidate_mae": candidate_mae
                                })
                                new_model, new_scaler, new_mae = None, None, None
            except Exception as err:
                print(f"MLflow retrain_attempt logging warning: {err}")
                if retrain_data_size >= min_retrain_rows:
                    new_model, new_scaler, new_mae = train_model_with_holdout(
                        new_df,
                        min_retrain_rows=min_retrain_rows,
                    )
                    
                    # HIGH PRIORITY: Model performance gating
                    if new_model and new_scaler and new_mae:
                        validation_buffer = new_df.tail(20)
                        should_accept, current_mae, candidate_mae, reason = performance_gate.should_accept_new_model(
                            model, scaler, new_model, new_scaler, new_mae, validation_buffer
                        )
                        
                        if not should_accept:
                            rejected_retrains += 1
                            new_model, new_scaler, new_mae = None, None, None

            if retrain_data_size < min_retrain_rows:
                skipped_retrains += 1
                logs.append(
                    {
                        "event": "retrain_skipped",
                        "index": i,
                        "cycle": int(data["cycle"]),
                        "reason": f"insufficient retrain data (< {min_retrain_rows})",
                        "buffer_size": retrain_data_size,
                    }
                )
                continue

            if new_mae is not None:
                print(f"Validation MAE: {new_mae:.2f}")

            if new_model is not None and new_scaler is not None:
                # MEDIUM PRIORITY: Start shadow evaluation instead of immediate swap
                print("\nStarting shadow model evaluation...")
                shadow_evaluator.start_shadow_evaluation(new_model, new_scaler)
                adaptive_cooldown.mark_retrain(i)
                
                retrain_log = {
                    "event": "shadow_evaluation_started",
                    "index": i,
                    "cycle": int(data["cycle"]),
                    "buffer_size": len(buffer),
                    "validation_mae": new_mae,
                }
                logs.append(retrain_log)
                logger.log_retrain(retrain_log)

                print("Shadow model will be evaluated over next 20 cycles\n")
            else:
                print("Retrain rejected - model not valid\n")
                logs.append(
                    {
                        "event": "retrain_rejected",
                        "index": i,
                        "cycle": int(data["cycle"]),
                        "buffer_size": len(buffer),
                        "candidate_mae": new_mae,
                        "reason": "insufficient retrain data or invalid candidate",
                    }
                )

    retrain_count = sum(1 for entry in logs if entry["event"] == "shadow_evaluation_started")
    promoted_count = sum(1 for entry in logs if entry["event"] == "shadow_promoted")
    skipped_count = sum(1 for entry in logs if entry["event"] == "retrain_skipped")
    
    print("\n" + "="*60)
    print("PIPELINE SUMMARY")
    print("="*60)
    print(f"Total Cycles: {i+1}")
    print(f"Retrain Attempts: {retrain_count}")
    print(f"Models Promoted: {promoted_count}")
    print(f"Rejected by Performance Gate: {rejected_retrains}")
    print(f"Skipped Retrains: {skipped_count}")
    print(f"Anomalies Detected: {anomaly_count}")
    print(f"Success Rate: {(promoted_count/retrain_count*100) if retrain_count > 0 else 0:.1f}%")
    print("="*60)
    
    # Phase 15: Generate visualizations
    print("\nGenerating visualizations...")
    visualizer = SystemVisualizer(output_dir="plots")
    visualizer.plot_monitoring_dashboard(logs, save=True)
    visualizer.plot_drift_score_timeline(logs, save=True)
    visualizer.plot_retrain_analysis(logs, save=True)
    print("Visualizations saved to 'plots/' directory\n")


if __name__ == "__main__":
    run_pipeline()