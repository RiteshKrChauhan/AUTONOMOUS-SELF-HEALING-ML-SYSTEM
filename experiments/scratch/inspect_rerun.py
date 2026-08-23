"""Inspect the rerun experiment output."""
import csv
import numpy as np
from pathlib import Path

p = sorted(Path("experiments/results/raw").glob("proposed_gradual_drift_seed42_20260823_*.csv"))[-1]
print(f"Reading: {p.name}")
with open(p, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print("\n=== KEY LIFECYCLE EVENTS (RERUN) ===")
for r in rows:
    flags = []
    if r["retraining_triggered"] == "True":
        flags.append("RETRAIN_TRIGGERED")
    if r.get("validation_skipped") == "True":
        flags.append(f"VAL_SKIP:{r['validation_skip_reason']}")
    if r.get("candidate_generated") == "True":
        flags.append("CANDIDATE_GENERATED")
    if r["gate_passed"] not in ("", "None"):
        res = "PASS" if r["gate_passed"] == "True" else "FAIL"
        prod = float(r["production_mae"] or 0)
        cand = float(r["candidate_mae"] or 0)
        flags.append(f"GATE={res} prod={prod:.1f} cand={cand:.1f}")
    if r.get("shadow_passed") == "True":
        flags.append("SHADOW_PASSED")
    if r.get("shadow_rejected") == "True":
        flags.append("SHADOW_REJECTED")
    if r.get("model_promoted") == "True":
        flags.append("MODEL_PROMOTED v" + str(r["model_version"]))
    if r.get("gate_rejected") == "True":
        flags.append("GATE_REJECTED")
    if flags:
        scn = "SCN" if r["scenario_active"] == "True" else "---"
        print(f"  idx={r['sample_index']:>4} {scn} | {' | '.join(flags)}")

pre = [float(r["absolute_error"]) for r in rows if int(r["sample_index"]) < 80]
during = [float(r["absolute_error"]) for r in rows if 80 <= int(r["sample_index"]) < 180]
post = [float(r["absolute_error"]) for r in rows if int(r["sample_index"]) >= 180]
print("\n=== ERROR BY PHASE ===")
print(f"  Pre-scenario  idx   0- 79: MAE={np.mean(pre):.2f}")
print(f"  During scenario idx 80-179: MAE={np.mean(during):.2f}")
print(f"  Post-scenario idx 180-319: MAE={np.mean(post):.2f}")
print(f"  Overall MAE: {np.mean([float(r['absolute_error']) for r in rows]):.2f}")

print("\n=== METRIC VERIFICATION ===")
print(f"  validation_skipped_events : {sum(1 for r in rows if r.get('validation_skipped') == 'True')}")
print(f"  candidates_generated      : {sum(1 for r in rows if r.get('candidate_generated') == 'True')}")
print(f"  model_promoted            : {sum(1 for r in rows if r.get('model_promoted') == 'True')}")
print(f"  gate_rejected             : {sum(1 for r in rows if r.get('gate_rejected') == 'True')}")
print(f"  shadow_passed             : {sum(1 for r in rows if r.get('shadow_passed') == 'True')}")
print(f"  shadow_rejected           : {sum(1 for r in rows if r.get('shadow_rejected') == 'True')}")

# Check that the first candidate validation set
retrain_rows = [r for r in rows if r.get("candidate_generated") == "True"]
print("\n=== CANDIDATE GATE EVALUATIONS ===")
for r in retrain_rows:
    print(f"  idx={r['sample_index']:>4} prod_mae={float(r['production_mae'] or 0):.2f}"
          f"  cand_mae={float(r['candidate_mae'] or 0):.2f}"
          f"  gate={'PASS' if r['gate_passed']=='True' else 'FAIL'}")
