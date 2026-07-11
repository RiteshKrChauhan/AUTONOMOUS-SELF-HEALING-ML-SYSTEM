"""
High Noise scenario.
Multiplies all sensor variance by ×5 without shifting the mean.
Tests whether the performance gate correctly REJECTS a candidate model
trained on high-noise data because it will have higher validation MAE.
"""

_ALL_SENSORS = [f"sensor_{i}" for i in range(1, 22)]


class HighNoise:
    META = {
        "id": "high_noise",
        "name": "High Sensor Noise",
        "severity": "Medium",
        "duration": 60,
        "description": "Sensor variance ×5 with no mean shift. Simulates electrical interference.",
        "expectedBehavior": "Confidence intervals widen. Performance gate likely REJECTS retrain candidate (noisy training data → higher validation MAE).",
        "tags": ["confidence", "noise", "gate-rejection"],
    }

    @staticmethod
    def apply(data, cycle_index, baseline_stds, rng):
        for sensor in _ALL_SENSORS:
            std = baseline_stds.get(sensor, 1.0)
            data[sensor] = float(data[sensor] + rng.normal(0, 4.5 * std))
