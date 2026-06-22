import pandas as pd
from typing import Dict, Any, List
from sklearn.ensemble import GradientBoostingRegressor
from ai.models import PredictionOutput

class DepotLoadPredictor:
    """
    Predicts future load and queue lengths at depots.
    Enables proactive scaling of charging slots and fleet reallocation.
    """
    
    def __init__(self):
        self.queue_model = GradientBoostingRegressor(n_estimators=100)
        self.utilization_model = GradientBoostingRegressor(n_estimators=100)

    def train(self, df: pd.DataFrame):
        """
        Trains on historical depot metrics.
        Features: hour, incoming_demand, active_fleet, charging_drones
        Targets: queue_length, utilization_pct
        """
        X = df.drop(columns=['queue_length', 'utilization_pct', 'depot_id', 'timestamp'], errors='ignore')
        
        if 'queue_length' in df.columns:
            self.queue_model.fit(X, df['queue_length'])
        
        if 'utilization_pct' in df.columns:
            self.utilization_model.fit(X, df['utilization_pct'])

    def predict_load(self, features: pd.DataFrame, depot_id: str) -> Dict[str, PredictionOutput]:
        """Predicts queue length and utilization for the next 4 hours."""
        X = features.drop(columns=['depot_id', 'timestamp'], errors='ignore')
        
        queue_pred = float(self.queue_model.predict(X)[0])
        util_pred = float(self.utilization_model.predict(X)[0])
        
        return {
            "queue_length": PredictionOutput(
                model_id="depot_queue_v1",
                target_id=depot_id,
                prediction_value=max(0.0, queue_pred)
            ),
            "utilization_pct": PredictionOutput(
                model_id="depot_util_v1",
                target_id=depot_id,
                prediction_value=max(0.0, min(100.0, util_pred))
            )
        }
