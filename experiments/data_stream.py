"""Deterministic C-MAPSS stream construction for research experiments."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import numpy as np
import pandas as pd

from dataset.processed.preprocess_module import add_rul, load_data
from metrics.calculator import FEATURE_COLUMNS
from scenarios.registry import SCENARIO_REGISTRY


@dataclass(frozen=True)
class StreamEvent:
    sample_index: int
    engine_id: int
    cycle: int
    data: dict
    scenario_active: bool
    scenario_cycle: int | None
    degradation_started: bool


def load_fd001_with_rul(base_path: Path) -> pd.DataFrame:
    raw_path = base_path / "dataset" / "raw" / "train_FD001.txt"
    df = add_rul(load_data(str(raw_path)))
    df["unit"] = df["unit"].astype(int)
    df["cycle"] = df["cycle"].astype(int)
    return df


def split_train_stream_units(
    df: pd.DataFrame,
    seed: int,
    train_fraction: float = 0.76,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    units = df["unit"].unique().tolist()
    shuffled = rng.permutation(units).tolist()
    split_at = int(len(shuffled) * train_fraction)
    train_units = set(shuffled[:split_at])
    stream_units = set(shuffled[split_at:])
    train_df = df[df["unit"].isin(train_units)].reset_index(drop=True)
    stream_df = df[df["unit"].isin(stream_units)].reset_index(drop=True)
    return train_df, stream_df


def build_stream_records(
    stream_df: pd.DataFrame,
    stream_mode: str = "research",
    seed: int = 42,
) -> list[dict]:
    """Return stream records under a documented ordering policy.

    research mode sorts by engine unit and cycle, preserving C-MAPSS temporal
    trajectories.  legacy mode reproduces the dashboard's historical behavior:
    individual rows are randomly permuted using the configured seed.
    """

    if stream_mode == "research":
        ordered = stream_df.sort_values(["unit", "cycle"]).reset_index(drop=True)
        return ordered.to_dict(orient="records")
    if stream_mode == "legacy":
        rng = np.random.default_rng(seed)
        records = stream_df.to_dict(orient="records")
        perm = rng.permutation(len(records)).tolist()
        return [records[i] for i in perm]
    raise ValueError(f"Unknown stream_mode: {stream_mode}")


def baseline_statistics(train_df: pd.DataFrame) -> tuple[dict[str, float], dict[str, float]]:
    means = {feature: float(train_df[feature].mean()) for feature in FEATURE_COLUMNS}
    stds = {feature: float(max(train_df[feature].std(), 0.5)) for feature in FEATURE_COLUMNS}
    return means, stds


def iter_stream_events(
    records: list[dict],
    baseline_stds: dict[str, float],
    scenario_id: str,
    seed: int,
    stream_length: int,
    scenario_start_index: int,
    sensor_noise_fraction: float = 0.015,
) -> Iterator[StreamEvent]:
    """Yield reproducible stream events with deterministic scenario positions."""

    if not records:
        return

    rng = np.random.default_rng(seed)
    scenario_cls = SCENARIO_REGISTRY[scenario_id]
    duration = int(scenario_cls.META["duration"])

    for sample_index in range(stream_length):
        row = dict(records[sample_index % len(records)])
        data = dict(row)
        for feature in FEATURE_COLUMNS:
            scale = baseline_stds.get(feature, 1.0)
            data[feature] = float(data[feature] + rng.normal(0, sensor_noise_fraction * scale))

        scenario_cycle = sample_index - scenario_start_index
        scenario_active = 0 <= scenario_cycle < duration
        if scenario_active:
            scenario_cls.apply(data, scenario_cycle, baseline_stds, rng)

        yield StreamEvent(
            sample_index=sample_index,
            engine_id=int(data["unit"]),
            cycle=int(data["cycle"]),
            data=data,
            scenario_active=scenario_active,
            scenario_cycle=int(scenario_cycle) if scenario_active else None,
            degradation_started=sample_index == scenario_start_index,
        )
