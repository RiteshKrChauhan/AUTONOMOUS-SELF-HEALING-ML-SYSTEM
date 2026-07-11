"""
Intermittent Spikes scenario.
Every 7th cycle, 2 randomly selected sensors spike ±12σ.
All other cycles are completely normal.

This tests the Isolation Forest anomaly detector — it should flag the spiked cycles
as outliers. ADWIN may or may not fire depending on how frequently errors spike.
It models electrical transients or measurement glitches in the sensor network.
"""

_ALL_SENSORS = [f"sensor_{i}" for i in range(1, 22)]


class IntermittentSpikes:
    META = {
        "id": "intermittent_spikes",
        "name": "Intermittent Sensor Spikes",
        "severity": "Low",
        "duration": 90,
        "description": "2 random sensors spike ±12σ every 7 cycles. Normal between spikes.",
        "expectedBehavior": "Isolation Forest flags spike cycles as anomalies. ADWIN may not detect (too infrequent). No retrain expected.",
        "tags": ["anomaly", "intermittent", "isolation-forest"],
    }

    @staticmethod
    def apply(data, cycle_index, baseline_stds, rng):
        if cycle_index % 7 == 0:
            chosen = rng.choice(_ALL_SENSORS, size=2, replace=False)
            for sensor in chosen:
                std = baseline_stds.get(sensor, 1.0)
                direction = 1 if rng.random() > 0.5 else -1
                data[sensor] = float(data[sensor] + direction * 12.0 * std)
