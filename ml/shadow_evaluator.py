from collections import deque
import numpy as np
from ml.predict import predict


class ShadowModelEvaluator:
    """
    Runs production and candidate models in parallel to validate performance
    before promoting the candidate to production. This is A/B testing for ML models.
    """
    
    def __init__(self, window_size=20, improvement_threshold=0.95):
        """
        Args:
            window_size: Number of predictions to compare
            improvement_threshold: Shadow must be this good to promote (0.95 = 5% better)
        """
        self.window_size = window_size
        self.improvement_threshold = improvement_threshold
        self.production_errors = deque(maxlen=window_size)
        self.shadow_errors = deque(maxlen=window_size)
        self.shadow_model = None
        self.shadow_scaler = None
        self.is_evaluating = False
    
    def start_shadow_evaluation(self, shadow_model, shadow_scaler):
        """Begin evaluating a shadow model"""
        self.shadow_model = shadow_model
        self.shadow_scaler = shadow_scaler
        self.production_errors.clear()
        self.shadow_errors.clear()
        self.is_evaluating = True
    
    def evaluate_both(self, prod_model, prod_scaler, data, actual):
        """
        Run both production and shadow models on the same data.
        
        Returns:
            (should_promote: bool, prod_mae: float, shadow_mae: float)
        """
        if not self.is_evaluating or self.shadow_model is None:
            return False, None, None
        
        try:
            # Production prediction
            prod_pred = predict(prod_model, prod_scaler, data)
            prod_error = abs(actual - prod_pred)
            self.production_errors.append(prod_error)
            
            # Shadow prediction
            shadow_pred = predict(self.shadow_model, self.shadow_scaler, data)
            shadow_error = abs(actual - shadow_pred)
            self.shadow_errors.append(shadow_error)
        
        except Exception as e:
            # If either model fails, don't promote
            return False, None, None
        
        # Wait until we have enough samples
        if len(self.shadow_errors) < self.window_size:
            return False, None, None
        
        # Calculate MAE for both models
        prod_mae = np.mean(self.production_errors)
        shadow_mae = np.mean(self.shadow_errors)
        
        # Promote shadow if consistently better
        threshold_mae = prod_mae * self.improvement_threshold
        should_promote = shadow_mae < threshold_mae
        
        return should_promote, prod_mae, shadow_mae
    
    def stop_evaluation(self):
        """Stop shadow evaluation and clear state"""
        self.is_evaluating = False
        self.shadow_model = None
        self.shadow_scaler = None
        self.production_errors.clear()
        self.shadow_errors.clear()
    
    def get_status(self):
        """Get current evaluation status"""
        if not self.is_evaluating:
            return {
                "is_evaluating": False,
                "samples_collected": 0,
                "samples_needed": self.window_size
            }
        
        prod_mae = np.mean(self.production_errors) if self.production_errors else None
        shadow_mae = np.mean(self.shadow_errors) if self.shadow_errors else None
        
        return {
            "is_evaluating": True,
            "samples_collected": len(self.shadow_errors),
            "samples_needed": self.window_size,
            "production_mae": prod_mae,
            "shadow_mae": shadow_mae,
            "ready_to_decide": len(self.shadow_errors) >= self.window_size
        }
