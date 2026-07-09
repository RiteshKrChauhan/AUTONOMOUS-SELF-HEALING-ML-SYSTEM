from sklearn.ensemble import IsolationForest
import numpy as np


class AnomalyDetector:
    """
    Detects anomalous data points that might cause bad predictions.
    Uses Isolation Forest to identify outliers in feature space.
    """
    
    def __init__(self, contamination=0.05, random_state=42):
        """
        Args:
            contamination: Expected proportion of outliers (0.05 = 5%)
            random_state: Random seed for reproducibility
        """
        self.contamination = contamination
        self.random_state = random_state
        self.detector = None
        self.is_fitted = False
        self.feature_names = None
    
    def fit(self, train_df):
        """Train anomaly detector on baseline data"""
        features = train_df.drop(columns=['RUL', 'unit', 'cycle'], errors='ignore')
        
        if len(features) < 10:
            return False
        
        self.feature_names = features.columns.tolist()
        
        self.detector = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=100
        )
        
        self.detector.fit(features)
        self.is_fitted = True
        return True
    
    def is_anomaly(self, data_point):
        """
        Check if a data point is anomalous.
        
        Returns:
            (is_anomaly: bool, anomaly_score: float)
        """
        if not self.is_fitted or self.detector is None:
            return False, 0.0
        
        try:
            # Extract features in same order as training
            features = [data_point.get(f, 0.0) for f in self.feature_names]
            features_array = np.array(features).reshape(1, -1)
            
            # Predict: -1 = anomaly, 1 = normal
            prediction = self.detector.predict(features_array)[0]
            
            # Get anomaly score (lower = more anomalous)
            score = self.detector.score_samples(features_array)[0]
            
            is_anomaly = (prediction == -1)
            
            return is_anomaly, float(score)
        
        except Exception:
            return False, 0.0
    
    def get_decision_function(self, data_point):
        """Get raw anomaly score (for logging/debugging)"""
        if not self.is_fitted:
            return None
        
        try:
            features = [data_point.get(f, 0.0) for f in self.feature_names]
            features_array = np.array(features).reshape(1, -1)
            return self.detector.decision_function(features_array)[0]
        except Exception:
            return None
