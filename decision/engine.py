class DecisionEngine:
    def __init__(self, error_threshold=45): 
        self.error_threshold = error_threshold

    def decide(self, drift, rolling_avg, trend, drift_score=0.0):
        """
        Enhanced decision engine with multiple states based on drift severity.

        MAE thresholds (all derived from error_threshold=45):
          - ALERT:   MAE > 67.5  (threshold * 1.5) — critically high error
          - MONITOR: MAE > 45.0  (threshold * 1.0) — error above threshold and trending up
          - WATCH:   MAE > 36.0  (threshold * 0.8) — error approaching threshold

        Drift states:
          - RETRAIN_URGENT: drift_score > 0.8
          - RETRAIN:        drift_score > 0.5  or any drift signal
          - STABLE:         no drift, no error concerns
        """
        
        # Case 1: Severe drift → retrain immediately
        if drift and drift_score > 0.8:
            return "RETRAIN_URGENT"
        
        # Case 2: Moderate drift → retrain
        if drift and drift_score > 0.5:
            return "RETRAIN"
        
        # Case 3: Mild drift → retrain with caution
        if drift:
            return "RETRAIN"
        
        # Case 4: Error critically high → alert
        if rolling_avg is not None and rolling_avg > self.error_threshold * 1.5:
            return "ALERT"
        
        # Case 5: Error increasing and above threshold → monitor closely
        if trend and rolling_avg is not None and rolling_avg > self.error_threshold:
            return "MONITOR"
        
        # Case 6: Error approaching threshold → watch
        if rolling_avg is not None and rolling_avg > self.error_threshold * 0.8:
            return "WATCH"
        
        # Case 7: Everything fine
        return "STABLE"