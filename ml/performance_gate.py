import pandas as pd
from ml.predict import predict


class ModelPerformanceGate:
    """
    Ensures new models are better than current production model before deployment.
    Prevents model degradation by comparing performance on holdout data.
    """
    
    def __init__(self, improvement_threshold=0.95):
        """
        Args:
            improvement_threshold: New model must be at least this good (0.95 = 5% improvement)
        """
        self.improvement_threshold = improvement_threshold
    
    def evaluate_model_on_buffer(self, model, scaler, buffer_df):
        """Evaluate a model on buffered data"""
        if len(buffer_df) < 5:
            return None
        
        predictions = []
        actuals = []
        
        for _, row in buffer_df.iterrows():
            data = row.to_dict()
            if 'RUL' not in data:
                continue
            
            actual = data['RUL']
            try:
                pred = predict(model, scaler, data)
                predictions.append(pred)
                actuals.append(actual)
            except Exception:
                continue
        
        if len(predictions) < 5:
            return None
        
        # Calculate MAE
        mae = sum(abs(a - p) for a, p in zip(actuals, predictions)) / len(predictions)
        return mae
    
    def should_accept_new_model(self, current_model, current_scaler, 
                                 new_model, new_scaler, new_mae, 
                                 validation_buffer):
        """
        Compare current model vs new model on same validation data.
        
        Returns:
            (should_accept: bool, current_mae: float, new_mae: float, reason: str)
        """
        if new_model is None or new_scaler is None:
            return False, None, None, "new_model_is_none"
        
        if new_mae is None:
            return False, None, None, "new_mae_is_none"
        
        # Evaluate current model on validation buffer
        current_mae = self.evaluate_model_on_buffer(
            current_model, current_scaler, validation_buffer
        )
        
        if current_mae is None:
            # Can't compare, accept new model (first retrain scenario)
            return True, None, new_mae, "no_baseline_comparison"
        
        # Accept if new model is better by threshold
        threshold_mae = current_mae * self.improvement_threshold
        
        if new_mae < threshold_mae:
            improvement_pct = ((current_mae - new_mae) / current_mae) * 100
            return True, current_mae, new_mae, f"improved_by_{improvement_pct:.1f}%"
        else:
            degradation_pct = ((new_mae - current_mae) / current_mae) * 100
            return False, current_mae, new_mae, f"degraded_by_{degradation_pct:.1f}%"
