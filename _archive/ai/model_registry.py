import pickle
import os
from typing import Dict, Any, Optional
from ai.models import ModelMetadata, ModelType

class ModelRegistry:
    """
    Manages versioning, metadata, and persistence of ML models.
    """
    
    def __init__(self, storage_path: str = "./models"):
        self.storage_path = storage_path
        self.registry: Dict[str, ModelMetadata] = {}
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)

    def register_model(self, model_id: str, model_object: Any, metrics: Dict[str, float]):
        """Saves a model and its metadata."""
        file_path = os.path.join(self.storage_path, f"{model_id}.pkl")
        with open(file_path, 'wb') as f:
            pickle.dump(model_object, f)
            
        metadata = ModelMetadata(
            model_id=model_id,
            model_type=self._infer_type(model_object),
            version="1.0.0",
            training_date=pd.Timestamp.now().timestamp(),
            metrics=metrics,
            parameters={},
            feature_columns=[]
        )
        self.registry[model_id] = metadata

    def load_model(self, model_id: str) -> Optional[Any]:
        """Loads a model from disk."""
        file_path = os.path.join(self.storage_path, f"{model_id}.pkl")
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return pickle.load(f)
        return None

    def _infer_type(self, model_object: Any) -> ModelType:
        # Simple inference logic
        name = model_object.__class__.__name__.lower()
        if "demand" in name: return ModelType.DEMAND_FORECAST
        if "battery" in name: return ModelType.BATTERY_SOH
        if "maintenance" in name: return ModelType.MAINTENANCE_PREDICTION
        return ModelType.ANOMALY_DETECTION

import pandas as pd # Needed for timestamp
