import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime

class FeatureStore:
    """
    Central repository for TiranaFly features.
    Manages historical, training, and online features for ML models.
    """
    
    def __init__(self):
        self._offline_store: Dict[str, pd.DataFrame] = {}
        self._online_cache: Dict[str, Dict[str, Any]] = {}

    def ingest_demand_features(self, df: pd.DataFrame):
        """Stores historical demand features (H3, timestamp, count, etc.)"""
        self._offline_store["demand"] = df

    def ingest_fleet_features(self, df: pd.DataFrame):
        """Stores historical fleet metrics (drone_id, battery_soh, mileage)"""
        self._offline_store["fleet"] = df

    def get_demand_training_set(self, h3_indices: List[str] = None) -> pd.DataFrame:
        """Retrieves a training set for demand forecasting."""
        df = self._offline_store.get("demand")
        if df is None: return pd.DataFrame()
        
        if h3_indices:
            df = df[df['h3_index'].isin(h3_indices)]
            
        # Feature Engineering: Lag features, Rolling averages
        df = df.sort_values(['h3_index', 'timestamp'])
        df['lag_1h'] = df.groupby('h3_index')['demand_count'].shift(1)
        df['lag_24h'] = df.groupby('h3_index')['demand_count'].shift(24)
        df['rolling_mean_6h'] = df.groupby('h3_index')['demand_count'].transform(lambda x: x.rolling(6).mean())
        
        return df.dropna()

    def get_battery_training_set(self) -> pd.DataFrame:
        """Retrieves a training set for battery SOH prediction."""
        df = self._offline_store.get("fleet")
        if df is None: return pd.DataFrame()
        
        # Features: discharge_cycles, temperature_avg, charge_rate, age
        return df

    def update_online_feature(self, entity_type: str, entity_id: str, features: Dict[str, Any]):
        """Updates low-latency cache for real-time inference."""
        if entity_type not in self._online_cache:
            self._online_cache[entity_type] = {}
        self._online_cache[entity_type][entity_id] = features

    def get_online_features(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves features for real-time inference."""
        return self._online_cache.get(entity_type, {}).get(entity_id)

    def create_spatiotemporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds time-based features (hour, day_of_week, is_weekend)."""
        if 'timestamp' not in df.columns:
            return df
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Cyclic encoding for hour
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        
        return df
