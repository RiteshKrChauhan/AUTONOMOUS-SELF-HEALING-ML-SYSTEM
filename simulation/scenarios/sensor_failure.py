"""
Sensor Failure scenario.
Two sensors are stuck at a constant value (0.0), simulating hardware failure
such as a disconnected sensor wire or a grounded sensor.

The KS test will detect this immediately since the stuck sensor's distribution
has zero variance vs the historical reference which has real variance.
The Isolation Forest anomaly detector will also flag these points.
"""

_STUCK_SENSORS = ["sensor_3", "sensor_9"]


class SensorFailure:
    META = {
        "id": "sensor_failure",
        "name": "Sensor Failure (Stuck)",
        "severity": "High",
        "duration": 80,
        "description": "2 sensors stuck at 0.0, simulating disconnected hardware.",
        "expectedBehavior": "KS test detects zero-variance on stuck sensors. Isolation Forest flags every point. Retrain begins.",
        "tags": ["data-drift", "anomaly", "sensor-fault"],
    }

    @staticmethod
    def apply(data, cycle_index, baseline_stds, rng):
        for sensor in _STUCK_SENSORS:
            data[sensor] = 0.0
