import numpy as np


class ConfidencePredictor:
    """
    Provides prediction confidence intervals using ensemble variance.
    Helps identify when the model is uncertain about predictions.
    """
    
    def __init__(self, confidence_level=0.9):
        """
        Args:
            confidence_level: Confidence level for intervals (0.9 = 90%)
        """
        self.confidence_level = confidence_level
    
    def predict_with_confidence(self, model, scaler, data):
        """
        Make prediction with confidence interval using ensemble variance.
        
        For RandomForest, we use individual tree predictions to estimate uncertainty.
        
        Returns:
            (prediction: float, lower_bound: float, upper_bound: float, std: float)
        """
        import pandas as pd
        
        # Prepare data
        df = pd.DataFrame([data])
        X = df.drop(columns=['RUL', 'unit', 'cycle'], errors='ignore')
        
        # Align features
        expected_features = getattr(scaler, "feature_names_in_", None)
        if expected_features is not None:
            missing = [c for c in expected_features if c not in X.columns]
            if missing:
                raise ValueError(f"Missing features: {missing}")
            X = X.loc[:, expected_features]
        
        X_scaled = scaler.transform(X)
        
        # Get predictions from all trees in the forest
        if hasattr(model, 'estimators_'):
            # RandomForest - get predictions from each tree
            tree_predictions = np.array([
                tree.predict(X_scaled)[0] 
                for tree in model.estimators_
            ])
            
            prediction = np.mean(tree_predictions)
            std = np.std(tree_predictions)
            
            # Calculate confidence interval using z-score
            z_score = 1.645 if self.confidence_level == 0.9 else 1.96  # 90% or 95%
            margin = z_score * std
            
            lower_bound = prediction - margin
            upper_bound = prediction + margin
            
        else:
            # Single model - can't estimate uncertainty
            prediction = model.predict(X_scaled)[0]
            std = 0.0
            lower_bound = prediction
            upper_bound = prediction
        
        return float(prediction), float(lower_bound), float(upper_bound), float(std)
    
    def is_high_uncertainty(self, std, threshold=10.0):
        """Check if prediction uncertainty is high"""
        return std > threshold
    
    def get_confidence_category(self, std):
        """Categorize prediction confidence"""
        if std < 5.0:
            return "high_confidence"
        elif std < 10.0:
            return "medium_confidence"
        else:
            return "low_confidence"
