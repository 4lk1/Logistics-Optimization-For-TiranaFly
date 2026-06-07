import pandas as pd
from typing import Dict, Any, List, Optional
from ai.model_registry import ModelRegistry
from ai.feature_store import FeatureStore
from ai.models import PredictionOutput

class InferenceService:
    """
    Exposes ML models for real-time predictions.
    Used by the Backend and Digital Twin Simulation.
    """
    
    def __init__(self, registry: ModelRegistry, feature_store: FeatureStore):
        self.registry = registry
        self.fs = feature_store
        self._model_cache: Dict[str, Any] = {}

    def get_demand_forecast(self, h3_index: str) -> PredictionOutput:
        """Retrieves a demand forecast for an H3 cell."""
        model = self._get_cached_model("demand_random_forest")
        features = self.fs.get_online_features("h3", h3_index)
        
        if features:
            df_features = pd.DataFrame([features])
            return model.predict(df_features, h3_index)
        
        return PredictionOutput(model_id="none", target_id=h3_index, prediction_value=0.0)

    def get_battery_health(self, battery_id: str) -> Dict[str, PredictionOutput]:
        """Retrieves predicted SOH and RUL for a battery."""
        model = self._get_cached_model("battery_v1")
        features = self.fs.get_online_features("battery", battery_id)
        
        if features:
            df_features = pd.DataFrame([features])
            return model.predict_health(df_features, battery_id)
            
        return {}

    def get_maintenance_risk(self, drone_id: str) -> PredictionOutput:
        """Retrieves failure probability for a drone."""
        model = self._get_cached_model("maintenance_v1")
        features = self.fs.get_online_features("drone", drone_id)
        
        if features:
            df_features = pd.DataFrame([features])
            return model.predict_failure_prob(df_features, drone_id)
            
        return PredictionOutput(model_id="none", target_id=drone_id, prediction_value=0.0)

    def _get_cached_model(self, model_id: str) -> Any:
        if model_id not in self._model_cache:
            model = self.registry.load_model(model_id)
            if model is None:
                raise ValueError(f"Model {model_id} not found in registry.")
            self._model_cache[model_id] = model
        return self._model_cache[model_id]
