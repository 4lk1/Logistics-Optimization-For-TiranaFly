from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

class ModelType(Enum):
    DEMAND_FORECAST = "demand_forecast"
    BATTERY_SOH = "battery_soh"
    MAINTENANCE_PREDICTION = "maintenance_prediction"
    ROUTE_CONGESTION = "route_congestion"
    ANOMALY_DETECTION = "anomaly_detection"
    RL_DISPATCHER = "rl_dispatcher"

@dataclass
class ModelMetadata:
    model_id: str
    model_type: ModelType
    version: str
    training_date: float
    metrics: Dict[str, float]
    parameters: Dict[str, Any]
    feature_columns: List[str]

@dataclass
class PredictionOutput:
    model_id: str
    target_id: str  # h3_index, drone_id, depot_id, or route_id
    prediction_value: float
    confidence_interval: Optional[tuple] = None
    probability_distribution: Optional[Dict[float, float]] = None
    timestamp: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
