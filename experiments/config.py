"""Centralized configuration for reproducible research experiments."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


VALID_STRATEGIES = {"static", "scheduled", "naive_adaptive", "proposed"}


@dataclass(frozen=True)
class ExperimentConfig:
    seed: int = 42
    strategy: str = "proposed"
    scenario: str = "gradual_drift"
    stream_length: int = 320
    stream_mode: str = "research"
    scenario_start_index: int = 80
    train_fraction: float = 0.76
    validation_fraction: float = 0.25
    retraining_interval: int = 100
    data_drift_window: int = 20
    data_drift_p_threshold: float = 0.05
    data_drift_feature_ratio_threshold: float = 0.12
    data_drift_min_effect_size: float = 0.08
    error_window: int = 8
    error_threshold: float = 75.0
    retrain_error_threshold: float = 45.0
    retrain_drift_score_threshold: float = 0.55
    performance_gate_threshold: float = 0.95
    shadow_window: int = 20
    cooldown: int = 30
    minimum_retraining_samples: int = 55
    # --- Candidate validation-quality policy ---
    # minimum_validation_rows: the common-validation set must contain at least
    # this many rows for the performance gate to be considered meaningful.
    # Derived from stream analysis: at buf=80 with a single engine unit and
    # 25% fraction, the temporal-tail split yields 20 validation rows.
    # 14 rows (buf=55) produced the cand_mae=0.0 artifact in the first run.
    minimum_validation_rows: int = 20
    # minimum_validation_units: require at least this many distinct engine
    # units in the validation set.  The FD001 research stream (seed=42,
    # stream_length=320) has only one engine unit in the buffer for the entire
    # 320-sample window, so the default is 1 (no multi-unit requirement).
    # Callers running longer streams or legacy-mode can raise this.
    minimum_validation_units: int = 1
    output_dir: Path = Path("experiments/results")

    def __post_init__(self) -> None:
        if self.strategy not in VALID_STRATEGIES:
            raise ValueError(f"Unknown strategy: {self.strategy}")
        if self.stream_mode not in {"research", "legacy"}:
            raise ValueError(f"Unknown stream_mode: {self.stream_mode}")
        if self.stream_length <= 0:
            raise ValueError("stream_length must be positive")
        if self.minimum_retraining_samples < 10:
            raise ValueError("minimum_retraining_samples must be at least 10")
        if self.cooldown < 0:
            raise ValueError("cooldown must be non-negative")
        if self.minimum_validation_rows < 1:
            raise ValueError("minimum_validation_rows must be at least 1")
        if self.minimum_validation_units < 1:
            raise ValueError("minimum_validation_units must be at least 1")

    @property
    def raw_dir(self) -> Path:
        return self.output_dir / "raw"

    @property
    def aggregated_dir(self) -> Path:
        return self.output_dir / "aggregated"

    @property
    def figures_dir(self) -> Path:
        return self.output_dir / "figures"

    @property
    def adaptation_start_index(self) -> int:
        """First sample where adaptive strategies may update models.

        Samples before the controlled scenario starts are treated as detector
        warm-up/calibration for experiments, preventing pre-scenario model
        updates from contaminating the first degradation trial.
        """

        return max(0, self.scenario_start_index)

    def ensure_output_dirs(self) -> None:
        for path in [self.raw_dir, self.aggregated_dir, self.figures_dir]:
            path.mkdir(parents=True, exist_ok=True)

