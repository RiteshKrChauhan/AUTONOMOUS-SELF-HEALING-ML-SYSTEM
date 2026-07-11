"""
Correlated Multi-Sensor Drift scenario.
Six temperature-related sensors drift together by +3σ, simulating a thermal event
like overheating or a cooling system failure where multiple correlated channels
shift simultaneously.

This tests the KS feature drift ratio threshold — when multiple features drift
together, the ratio of drifted features exceeds the threshold faster than
isolated single-sensor drift.
"""

# These sensors are temperature and pressure related in CMAPSS FD001
_CORRELATED_SENSORS = [
    "sensor_2",   # Total temperature at fan inlet (°R)
    "sensor_3",   # Total temperature at LPC outlet (°R)
    "sensor_4",   # Total temperature at HPC outlet (°R)
    "sensor_11",  # Static pressure at HPC outlet (psia)
    "sensor_12",  # Ratio of fuel flow to Ps30
    "sensor_13",  # Corrected core speed (rpm)
]


class CorrelatedDrift:
    META = {
        "id": "correlated_drift",
        "name": "Correlated Multi-Sensor Drift",
        "severity": "High",
        "duration": 60,
        "description": "6 temperature/pressure sensors drift +3σ together, simulating a thermal event.",
        "expectedBehavior": "Feature drift ratio fires quickly. Multiple sensors highlighted in drift report. Retrain triggered.",
        "tags": ["data-drift", "correlated", "feature-drift"],
    }

    @staticmethod
    def apply(data, cycle_index, baseline_stds, rng):
        for sensor in _CORRELATED_SENSORS:
            std = baseline_stds.get(sensor, 1.0)
            noise = rng.normal(0, 0.15 * std)
            data[sensor] = float(data[sensor] + 3.0 * std + noise)
