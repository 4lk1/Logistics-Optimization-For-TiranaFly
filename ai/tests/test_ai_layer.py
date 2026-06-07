import pytest
import pandas as pd
import numpy as np
import os
import shutil
from ai.feature_store import FeatureStore
from ai.demand_forecasting import DemandForecaster
from ai.model_registry import ModelRegistry
from ai.inference_service import InferenceService

@pytest.fixture
def clean_registry():
    path = "./test_models"
    if os.path.exists(path):
        shutil.rmtree(path)
    registry = ModelRegistry(path)
    yield registry
    if os.path.exists(path):
        shutil.rmtree(path)

def test_demand_forecaster_training():
    df = pd.DataFrame({
        'h3_index': ['883901'] * 100,
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='H'),
        'demand_count': np.random.poisson(5, 100),
        'hour': np.random.randint(0, 24, 100)
    })
    
    forecaster = DemandForecaster(model_type="random_forest")
    forecaster.train(df)
    
    features = pd.DataFrame({'hour': [12]})
    pred = forecaster.predict(features, "883901")
    
    assert pred.prediction_value >= 0
    assert pred.target_id == "883901"

def test_inference_service_integration(clean_registry):
    fs = FeatureStore()
    fs.update_online_feature("h3", "883901", {"hour": 14})
    
    # Train and register a dummy model
    df = pd.DataFrame({
        'demand_count': [1, 2, 3],
        'hour': [10, 11, 12]
    })
    model = DemandForecaster()
    model.train(df)
    clean_registry.register_model("demand_random_forest", model, {"mse": 0.1})
    
    service = InferenceService(clean_registry, fs)
    pred = service.get_demand_forecast("883901")
    
    assert pred.prediction_value > 0

def test_anomaly_detection():
    from ai.anomaly_detection import AnomalyDetector
    normal_data = pd.DataFrame({'val': np.random.normal(0, 1, 100)})
    detector = AnomalyDetector()
    detector.train(normal_data)
    
    outlier = pd.DataFrame({'val': [10.0]})
    is_ano = detector.is_anomaly(outlier)
    assert is_ano[0] == -1
