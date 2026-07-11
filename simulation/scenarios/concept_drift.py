"""
Concept Drift scenario.
Sensor features remain entirely unchanged but the RUL label is shifted downward
by 60 cycles, simulating a turbofan that degrades much faster than the historical fleet.

This tests ADWIN exclusively — the KS test on features should NOT detect any drift
because the input distribution is unchanged. Only the prediction error will rise
because the model was trained on a different label distribution.

Duration is 150 cycles (≈19s at 8 eps) so ADWIN has enough samples to accumulate
statistical evidence of the rising error stream before the scenario ends.
"""


class ConceptDrift:
    META = {
        "id": "concept_drift",
        "name": "Concept Drift (Label Shift)",
        "severity": "High",
        "duration": 150,
        "description": "Engine degrades 60 cycles faster than historical fleet. Features look normal — only RUL is shifted.",
        "expectedBehavior": "ADWIN detects rising error after ~60-80 cycles. Feature Drift chart stays flat (KS test silent). Error-based retrain triggered.",
        "tags": ["adwin", "concept-drift", "label-shift"],
    }

    @staticmethod
    def apply(data, cycle_index, baseline_stds, rng):
        # Shift ground-truth RUL downward (engine degrades faster).
        # A -60 shift produces a larger prediction error sooner, giving ADWIN
        # (delta=0.1) enough signal within the 150-cycle window to detect drift.
        data["RUL"] = float(max(0.0, data["RUL"] - 60.0))
