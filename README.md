# Autonomous Self-Healing ML System

Production-grade autonomous machine learning system with drift detection, automatic retraining, and self-healing capabilities.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the System
```bash
python main.py
```

That's it! The system will:
- Train initial model
- Stream data and make predictions
- Detect drift automatically
- Retrain when needed
- Generate visualizations
- Create audit logs

---

## 📊 What to Expect

### Console Output
You'll see real-time monitoring:
```
Cycle: 45 | Error: 12.34 | Pred: 45.0 [42.2, 47.8] (high_confidence) | 
Rolling Avg: 13.5 | Drift Score: 0.650 | Action: RETRAIN | Cooldown: 25/35

⚠️ ANOMALY DETECTED (score: -0.823)

🔍 RETRAIN TRIGGERED
🔒 PERFORMANCE GATE: ACCEPT (improved_by_7.2%)
🔄 Starting shadow model evaluation...
🎯 SHADOW MODEL PROMOTION
```

### Final Summary
```
============================================================
📊 PIPELINE SUMMARY
============================================================
Total Cycles: 200
Retrain Attempts: 3
Models Promoted: 2
Rejected by Performance Gate: 1
Anomalies Detected: 8
Success Rate: 66.7%
============================================================
```

---

## 🔍 How to Verify Everything Works

### 1. Check Console Output
✅ Should see predictions with confidence intervals  
✅ Should see drift detection messages  
✅ Should see retrain events (2-3 times)  
✅ Should see performance gate decisions  
✅ Should see shadow model promotions  
✅ Should see final summary with metrics  

### 2. Check Generated Files

#### Logs (Governance Trail)
```bash
ls logs/
# Should see:
# - cycles_TIMESTAMP.jsonl
# - decisions_TIMESTAMP.jsonl
# - retrains_TIMESTAMP.jsonl
```

View retrain audit trail:
```bash
cat logs/retrains_*.jsonl
```

#### Plots (Visualizations)
```bash
ls plots/
# Should see:
# - monitoring_dashboard.png
# - drift_scores.png
# - retrain_analysis.png
```

Open plots to see:
- Error over time with retrain points
- Drift detection timeline
- Retrain frequency analysis

#### MLflow Database
```bash
ls mlflow.db
# Should exist
```

---

## 📈 View MLflow Logs

### Start MLflow UI
```bash
mlflow ui
```

Then open browser: http://localhost:5000

### What You'll See in MLflow

#### Experiments Tab
- **Default** experiment with all runs
- Initial training run
- Multiple retrain attempts

#### Each Run Shows
- **Parameters**: model type, n_estimators, max_depth, training mode
- **Metrics**: MAE, validation_mae
- **Artifacts**: Trained model files
- **Tags**: Status (executed/skipped), logging warnings

#### Filter Runs
```
# In MLflow UI search bar:
params.status = "executed"  # Only successful retrains
metrics.validation_mae < 15  # Only good models
```

#### Compare Runs
1. Select multiple runs (checkbox)
2. Click "Compare"
3. See metric trends over time

---

## 🧪 Testing the System

### Run Unit Tests
```bash
pytest tests/
```

Expected output:
```
tests/test_decision_engine.py ✓✓✓
tests/test_drift_detector.py ✓✓
tests/test_error_monitor.py ✓✓✓
tests/test_predict.py ✓✓
tests/test_preprocess.py ✓✓✓

========== 12 passed in 2.34s ==========
```

### Manual Verification Checklist

#### ✅ Initial Training
- [ ] Model trains successfully
- [ ] MLflow logs initial run
- [ ] No errors in console

#### ✅ Streaming & Prediction
- [ ] Data streams cycle by cycle
- [ ] Predictions include confidence intervals: `[lower, pred, upper]`
- [ ] Confidence category shown: `high_confidence`, `medium_confidence`, or `low_confidence`

#### ✅ Drift Detection
- [ ] ADWIN drift detected (should happen ~2-3 times)
- [ ] Data drift detected (KS-test)
- [ ] Drift scores logged (0.0 to 1.0+)

#### ✅ Anomaly Detection
- [ ] Anomalies detected (should see ⚠️ warnings)
- [ ] Anomaly scores logged
- [ ] Count shown in final summary

#### ✅ Adaptive Cooldown
- [ ] Cooldown shown as `elapsed/required` (e.g., `25/35`)
- [ ] Required cooldown changes based on drift score
- [ ] Severe drift → 20 cycles
- [ ] Moderate drift → 35 cycles
- [ ] Mild drift → 50 cycles

#### ✅ Retrain Process
- [ ] Retrain triggered by drift
- [ ] Buffer validation passes
- [ ] New model trained with holdout validation
- [ ] Performance gate evaluates model
- [ ] Decision logged: ACCEPT or REJECT

#### ✅ Performance Gate
- [ ] Compares current vs new model MAE
- [ ] Shows improvement/degradation percentage
- [ ] Rejects models that don't improve by ≥5%
- [ ] Logs rejection reason

#### ✅ Shadow Evaluation
- [ ] Shadow evaluation starts after retrain
- [ ] Runs for 20 cycles
- [ ] Compares production vs shadow MAE
- [ ] Promotes if shadow is ≥5% better
- [ ] Logs promotion event

#### ✅ Logging
- [ ] `logs/` directory created
- [ ] 3 JSONL files created (cycles, decisions, retrains)
- [ ] Timestamps in ISO format
- [ ] All events logged

#### ✅ Visualization
- [ ] `plots/` directory created
- [ ] 3 PNG files generated
- [ ] Plots show error trends, drift points, retrain events

#### ✅ MLflow
- [ ] `mlflow.db` exists
- [ ] Runs logged with parameters and metrics
- [ ] Models saved as artifacts

---

## 🐛 Troubleshooting

### Issue: No retrains happening
**Cause**: Drift not severe enough or cooldown not elapsed  
**Solution**: Check drift scores in console. Should see scores > 0.5 for retrains

### Issue: All retrains rejected by performance gate
**Cause**: New models not improving by ≥5%  
**Solution**: This is working correctly! Gate is protecting production

### Issue: MLflow UI shows no runs
**Cause**: Database path issue  
**Solution**: Check `mlflow.db` exists. Run `mlflow ui --backend-store-uri sqlite:///mlflow.db`

### Issue: Plots not generated
**Cause**: matplotlib backend issue  
**Solution**: Install: `pip install matplotlib pillow`

### Issue: Import errors
**Cause**: Missing dependencies  
**Solution**: `pip install -r requirements.txt`

---

## 📊 Expected Metrics

After running on 200 cycles:

| Metric | Expected Range |
|--------|----------------|
| Retrain Attempts | 2-4 |
| Models Promoted | 1-3 |
| Rejected by Gate | 0-2 |
| Anomalies Detected | 5-15 |
| Success Rate | 50-80% |

---

## 🔧 Advanced Usage

### Run with Kafka (Optional)
```bash
# Terminal 1: Start Kafka
docker run -p 9092:9092 apache/kafka

# Terminal 2: Start producer
python KAFKA_USAGE.py

# Terminal 3: Modify main.py to use Kafka consumer
# (See KAFKA_USAGE.py for integration code)
```

### Adjust Hyperparameters

Edit `main.py`:
```python
# Retrain cooldown
adaptive_cooldown = AdaptiveCooldown(
    min_cooldown=15,  # Faster response
    max_cooldown=60   # More conservative
)

# Performance gate threshold
performance_gate = ModelPerformanceGate(
    improvement_threshold=0.90  # Require 10% improvement
)

# Shadow evaluation window
shadow_evaluator = ShadowModelEvaluator(
    window_size=30  # Longer evaluation period
)
```

---

## 📁 Project Structure

```
.
├── dataset/          # Data loading and preprocessing
├── decision/         # Decision engine + adaptive cooldown
├── drift/            # Drift detection (ADWIN, KS-test, anomaly)
├── logging/          # Governance logger
├── ml/               # Training, prediction, performance gate, shadow eval
├── simulation/       # Data streaming + chaos engineering
├── streaming/        # Kafka producer/consumer (optional)
├── tests/            # Unit tests
├── visualization/    # Plotting dashboards
├── main.py           # Main pipeline
└── requirements.txt  # Dependencies
```

---

## 🎯 Key Features

✅ **Dual Drift Detection** - ADWIN + KS-test  
✅ **Model Performance Gating** - No bad deployments  
✅ **Shadow Model Evaluation** - Zero-risk A/B testing  
✅ **Adaptive Cooldown** - Smart retrain scheduling  
✅ **Anomaly Detection** - Outlier protection  
✅ **Confidence Intervals** - Prediction uncertainty  
✅ **Multi-Stage Decisions** - 6-state engine  
✅ **Structured Logging** - Full audit trail  
✅ **MLflow Integration** - Experiment tracking  
✅ **Visualization** - Real-time dashboards  

---

## 📚 Documentation

- Run `python main.py` and check console output
- View plots in `plots/` directory
- Check logs in `logs/` directory
- Open MLflow UI: `mlflow ui`

---

## 🚀 Production Deployment

This system is production-ready with:
- Zero-risk model deployment (shadow evaluation)
- No model degradation (performance gate)
- Full observability (logging + MLflow)
- Automatic drift response (adaptive cooldown)
- Outlier protection (anomaly detection)

Deploy with confidence! 🎉
