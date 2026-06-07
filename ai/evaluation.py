import numpy as np
from typing import Dict, Any, List
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    precision_score, recall_score, f1_score, roc_auc_score
)

class ModelEvaluator:
    """
    Standardizes evaluation across all TiranaFly ML models.
    """
    
    @staticmethod
    def evaluate_regression(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        return {
            "MAE": float(mean_absolute_error(y_true, y_pred)),
            "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
            "MAPE": float(np.mean(np.abs((y_true - y_pred) / np.maximum(1.0, y_true))) * 100),
            "R2": float(r2_score(y_true, y_pred))
        }

    @staticmethod
    def evaluate_classification(y_true: np.ndarray, y_prob: np.ndarray, threshold: float = 0.5) -> Dict[str, float]:
        y_pred = (y_prob >= threshold).astype(int)
        metrics = {
            "Precision": float(precision_score(y_true, y_pred, zero_division=0)),
            "Recall": float(recall_score(y_true, y_pred, zero_division=0)),
            "F1": float(f1_score(y_true, y_pred, zero_division=0))
        }
        
        try:
            metrics["AUC"] = float(roc_auc_score(y_true, y_prob))
        except ValueError:
            metrics["AUC"] = 0.5
            
        return metrics
