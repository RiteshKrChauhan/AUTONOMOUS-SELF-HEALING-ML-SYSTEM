"""Quick inspection script for the first experiment run."""
import csv
import json
import numpy as np
from pathlib import Path

CSV = Path("experiments/results/raw/proposed_gradual_drift_seed42_20260822_221231_events.csv")
JSON = Path("experiments/results/aggregated/proposed_gradual_drift_seed42_20260822_221231_summary.json")

with open(CSV, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print("=== KEY LIFECYCLE EVENTS ===")
for r in rows:
    flags = []
    if r["retraining_triggered"] == "True":
        flags.append("RETRAIN_TRIGGERED")
    if r["retraining_completed"] == "True":
        flags.append("RETRAIN_COMPLETED")
    if r["gate_passed"] not in ("", "None"):
        result = "PASS" if r["gate_passed"] == "True" else "FAIL"
        prod = float(r["production_mae"] or 0)
        cand = float(r["candidate_mae"] or 0)
        flags.append(f"GATE={result} prod={prod:.1f} cand={cand:.1f}")
    if r["shadow_started"] == "True":
        flags.append("SHADOW_START")
    if r["shadow_completed"] == "True":
        flags.append(f"SHADOW_DONE result={r['shadow_result']}")
    if r["promotion_decision"] not in ("", "None"):
        flags.append(f"DECISION={r['promotion_decision']}")
    if r["feature_drift_detected"] == "True":
        flags.append("KS_DRIFT")
    if r["concept_drift_detected"] == "True":
        flags.append("ADWIN_DRIFT")
    if flags:
        scenario = "SCN" if r["scenario_active"] == "True" else "---"
        print(f"  idx={r['sample_index']:>4} {scenario} | {' | '.join(flags)}")

pre = [float(r["absolute_error"]) for r in rows if int(r["sample_index"]) < 80]
during = [float(r["absolute_error"]) for r in rows if 80 <= int(r["sample_index"]) < 180]
post = [float(r["absolute_error"]) for r in rows if int(r["sample_index"]) >= 180]

print("\n=== PREDICTION ERROR SUMMARY ===")
if pre:
    print(f"  Pre-scenario  (idx   0-79 ): MAE={np.mean(pre):.2f}")
if during:
    print(f"  During scenario (idx 80-179): MAE={np.mean(during):.2f}")
if post:
    print(f"  Post-scenario (idx 180-319): MAE={np.mean(post):.2f}")
print(f"  Overall: MAE={np.mean([float(r['absolute_error']) for r in rows]):.2f}")

fp = [r for r in rows if int(r["sample_index"]) < 80 and r["retraining_triggered"] == "True"]
print(f"\n  False-positive retrains (before idx=80): {len(fp)}")

# Detection delay check
first_drift = next(
    (r for r in rows if r["feature_drift_detected"] == "True" or r["concept_drift_detected"] == "True"),
    None,
)
if first_drift:
    idx = int(first_drift["sample_index"])
    delay = idx - 80
    legit = "AFTER scenario start" if idx >= 80 else "BEFORE scenario start (FP)"
    print(f"\n  First detection at idx={idx} (delay={delay} cycles from start): {legit}")

print("\n=== SUMMARY JSON ===")
with open(JSON, encoding="utf-8") as f:
    data = json.load(f)
print(json.dumps(data["summary"], indent=2))
