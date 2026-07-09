class DecisionEngine:
    def __init__(self, error_threshold=50):
        self.error_threshold = error_threshold

    def decide(self, drift, rolling_avg, trend, drift_score=0.0):
        """
        Enhanced decision engine with multiple states based on drift severity.
        
        States:
        - RETRAIN_URGENT: Severe drift detected (drift_score > 0.8)
        - RETRAIN: Moderate drift detected (drift_score > 0.5)
        - ALERT: Error significantly above threshold
        - MONITOR: Error increasing and above threshold
        - WATCH: Error approaching threshold
        - STABLE: Everything normal
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