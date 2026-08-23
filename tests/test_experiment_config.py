from pathlib import Path

import pytest

from experiments.config import ExperimentConfig


def test_config_creates_output_directories(tmp_path):
    config = ExperimentConfig(output_dir=tmp_path)
    config.ensure_output_dirs()

    assert config.raw_dir.exists()
    assert config.aggregated_dir.exists()
    assert config.figures_dir.exists()


def test_invalid_strategy_raises():
    with pytest.raises(ValueError):
        ExperimentConfig(strategy="unknown")


def test_output_dir_is_path():
    config = ExperimentConfig(output_dir=Path("experiments/results"))

    assert config.raw_dir == Path("experiments/results/raw")
