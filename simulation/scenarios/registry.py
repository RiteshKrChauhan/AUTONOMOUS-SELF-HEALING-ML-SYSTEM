"""
Central registry for all controlled fault scenarios.
Each scenario is a class with a META dict and a static apply() method.
"""

from simulation.scenarios.gradual_drift import GradualDrift
from simulation.scenarios.sudden_spike import SuddenSpike
from simulation.scenarios.high_noise import HighNoise
from simulation.scenarios.sensor_failure import SensorFailure
from simulation.scenarios.concept_drift import ConceptDrift
from simulation.scenarios.correlated_drift import CorrelatedDrift
from simulation.scenarios.intermittent_spikes import IntermittentSpikes
from simulation.scenarios.drift_recovery import DriftRecovery

SCENARIO_REGISTRY = {
    "gradual_drift": GradualDrift,
    "sudden_spike": SuddenSpike,
    "high_noise": HighNoise,
    "sensor_failure": SensorFailure,
    "concept_drift": ConceptDrift,
    "correlated_drift": CorrelatedDrift,
    "intermittent_spikes": IntermittentSpikes,
    "drift_recovery": DriftRecovery,
}


def get_scenario_list():
    """Return metadata for all registered scenarios (used by GET /api/scenarios)."""
    return [cls.META for cls in SCENARIO_REGISTRY.values()]
