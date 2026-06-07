import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.ensemble import GradientBoostingRegressor
from ai.models import PredictionOutput

class BatteryPredictor:
    """
    Predicts Battery State of Health (SOH) and Remaining Useful Life (RUL).
    Essential for predictive maintenance of the TiranaFly fleet.
    """
    
    def __init__(self):
        self.soh_model = GradientBoostingRegressor(n_estimators=100)
        self.rul_model = GradientBoostingRegressor(n_estimators=100)

    def train(self, df: pd.DataFrame):
        """
        Trains models on historical battery telemetry.
        Features: cycle_count, avg_temp, depth_of_discharge, internal_resistance
        """
        X = df.drop(columns=['soh_pct', 'rul_cycles', 'battery_id'], errors='ignore')
        
        if 'soh_pct' in df.columns:
            self.soh_model.fit(X, df['soh_pct'])
        
        if 'rul_cycles' in df.columns:
            self.rul_model.fit(X, df['rul_cycles'])

    def predict_health(self, features: pd.DataFrame, battery_id: str) -> Dict[str, PredictionOutput]:
        """Predicts both SOH and RUL for a specific battery."""
        X = features.drop(columns=['battery_id'], errors='ignore')
        
        soh_pred = float(self.soh_model.predict(X)[0])
        rul_pred = float(self.rul_model.predict(X)[0])
        
        return {
            "SOH": PredictionOutput(
                model_id="battery_soh_v1",
                target_id=battery_id,
                prediction_value=max(0.0, min(100.0, soh_pred)),
                timestamp=pd.to_datetime('now').timestamp()
            ),
            "RUL": PredictionOutput(
                model_id="battery_rul_v1",
                target_id=battery_id,
                prediction_value=max(0.0, rul_pred),
                timestamp=pd.to_datetime('now').timestamp()
            )
        }

    def assess_risk(self, battery_id: str, soh_val: float, rul_val: float) -> str:
        """Categorizes battery risk based on predictions."""
        if soh_val < 70 or rul_val < 50:
            return "CRITICAL_REPLACE"
        if soh_val < 85 or rul_val < 200:
            return "WATCH_CAREFULLY"
        return "OPTIMAL"
