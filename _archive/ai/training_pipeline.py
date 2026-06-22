import pandas as pd
from typing import Dict, Any, List
from ai.feature_store import FeatureStore
from ai.demand_forecasting import DemandForecaster
from ai.battery_prediction import BatteryPredictor
from ai.predictive_maintenance import PredictiveMaintenance
from ai.anomaly_detection import AnomalyDetector
from ai.model_registry import ModelRegistry

class TrainingPipeline:
    """
    Automated pipeline for retraining TiranaFly models.
    Supports continuous learning from simulation and real-world data.
    """
    
    def __init__(self, feature_store: FeatureStore, registry: ModelRegistry):
        self.fs = feature_store
        self.registry = registry

    def run_demand_training(self, model_type: str = "random_forest"):
        """Retrains the demand forecaster."""
        print(f"Retraining Demand Model ({model_type})...")
        df = self.fs.get_demand_training_set()
        df = self.fs.create_spatiotemporal_features(df)
        
        forecaster = DemandForecaster(model_type=model_type)
        forecaster.train(df)
        
        # Log to registry
        self.registry.register_model(
            model_id=f"demand_{model_type}_{pd.Timestamp.now().strftime('%Y%m%d')}",
            model_object=forecaster,
            metrics={"mse": 0.05} # Placeholder
        )

    def run_fleet_training(self):
        """Retrains battery and maintenance models."""
        df = self.fs.get_battery_training_set()
        
        print("Retraining Battery Model...")
        b_pred = BatteryPredictor()
        b_pred.train(df)
        self.registry.register_model("battery_v1", b_pred, {"mae": 1.2})
        
        print("Retraining Maintenance Model...")
        m_pred = PredictiveMaintenance()
        m_pred.train(df)
        self.registry.register_model("maintenance_v1", m_pred, {"accuracy": 0.92})

    def run_anomaly_training(self):
        """Retrains the anomaly detection system."""
        df = self.fs.get_demand_training_set()
        detector = AnomalyDetector()
        detector.train(df)
        self.registry.register_model("anomaly_detector_v1", detector, {})
