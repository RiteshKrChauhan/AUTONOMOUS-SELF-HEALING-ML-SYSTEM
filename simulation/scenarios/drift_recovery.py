"""
Drift-Then-Recovery scenario.
First 30 cycles: all sensors shift severely by +6σ (mimicking a fault).
Next 30 cycles: sensors gradually recover back to baseline.

This tests the full self-healing arc end-to-end:
  1. Drift detected → retrain triggered → shadow evaluation → model promoted
  2. System stabilizes as data returns to normal
  3. No further retrain once recovered (cooldown prevents unnecessary retraining)
"""

_ALL_SENSORS = [f"sensor_{i}" for i in range(1, 22)]


class DriftRecovery:
    META = {
        "id": "drift_recovery",
        "name": "Drift → Recovery",
        "severity": "Critical",
        "duration": 60,
        "description": "Severe +6σ drift for 30 cycles, then gradual recovery to baseline over 30 cycles.",
        "expectedBehavior": "Full self-healing arc: detect → retrain → shadow → promote → stabilize. No retrain during recovery.",
        "tags": ["adwin", "data-drift", "recovery", "self-healing"],
    }

    @staticmethod
    def apply(data, cycle_index, baseline_stds, rng):
        if cycle_index < 30:
            # Fault phase — full +6σ shift
            shift = 6.0
        else:
            # Recovery phase — linearly reduce shift from 6σ → 0σ
            recovery_progress = (cycle_index - 30) / 30.0
            shift = 6.0 * (1.0 - recovery_progress)

        for sensor in _ALL_SENSORS:
            std = baseline_stds.get(sensor, 1.0)
            data[sensor] = float(data[sensor] + shift * std)
