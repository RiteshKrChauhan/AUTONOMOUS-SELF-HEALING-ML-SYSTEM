"""Feasibility analysis for minimum buffer/validation defaults."""
import numpy as np
from pathlib import Path
import pandas as pd

from experiments.data_stream import (
    load_fd001_with_rul,
    split_train_stream_units,
    build_stream_records,
    baseline_statistics,
)
from ml.evaluation import split_training_and_validation
from metrics.calculator import FEATURE_COLUMNS

base = Path(".")
df = load_fd001_with_rul(base)
train_df, stream_df = split_train_stream_units(df, seed=42, train_fraction=0.76)
records = build_stream_records(stream_df, "research", 42)

print("=== STREAM STRUCTURE ===")
print(f"Stream units: {stream_df['unit'].nunique()} unique engine IDs")
print(f"Stream records total: {len(records)}")
print(f"Stream unique units: {sorted(set(r['unit'] for r in records))}")

for n in [55, 80, 100, 120, 160, 200, 240]:
    units = set(r["unit"] for r in records[:n])
    print(f"  First {n:>3} records -> {len(units)} unique units")

print("\n=== VALIDATION SPLIT FEASIBILITY (at buffer sizes) ===")
all_cols = ["unit", "cycle", "RUL"] + FEATURE_COLUMNS
for buf_size in [55, 80, 100, 120, 160, 200, 240]:
    chunk = records[:buf_size]
    buf_df = pd.DataFrame(chunk)
    avail = [c for c in all_cols if c in buf_df.columns]
    buf_df = buf_df[avail]
    train_p, val_p = split_training_and_validation(
        buf_df, validation_fraction=0.25, random_state=42
    )
    u_val = val_p["unit"].nunique() if "unit" in val_p.columns else 0
    u_train = train_p["unit"].nunique() if "unit" in train_p.columns else 0
    print(
        f"  buf={buf_size:>3}: train={len(train_p):>3} rows ({u_train}u),"
        f" val={len(val_p):>3} rows ({u_val}u)"
    )

print("\n=== UNIT LIFECYCLE LENGTHS in stream ===")
for uid in sorted(set(r["unit"] for r in records))[:6]:
    cycles = [r["cycle"] for r in records if r["unit"] == uid]
    print(f"  unit {uid}: {len(cycles)} cycles, cycle range {min(cycles)}-{max(cycles)}")
