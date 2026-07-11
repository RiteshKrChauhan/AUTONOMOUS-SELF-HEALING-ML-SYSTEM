"""
Sudden Drift scenario.
All 21 sensors immediately shift +8σ, simulating a catastrophic environmental change
or a major mechanical failure event.
"""

_ALL_SENSORS = [f"sensor_{i}" for i in range(1, 22)]


class SuddenSpike:
    META = {
        "id": "sudden_spike",
        "name": "Sudden Drift (Critical)",
        "severity": "Critical",
        "duration": 45,
        "description": "All 21 sensors shift +8σ immediately. Simulates catastrophic environmental change.",
        "expectedBehavior": "RETRAIN_URGENT within seconds. Performance gate evaluates candidate. Shadow A/B test begins.",
        "tags": ["adwin", "data-drift", "concept-drift", "critical"],
    }

    @staticmethod
    def apply(data, cycle_index, baseline_stds, rng):
        for sensor in _ALL_SENSORS:
            std = baseline_stds.get(sensor, 1.0)
            data[sensor] = float(data[sensor] + 8.0 * std)
