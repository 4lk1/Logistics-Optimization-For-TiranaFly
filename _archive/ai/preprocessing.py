import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler

class DataPreprocessor:
    """
    Handles data cleaning, normalization, and transformation for ML.
    """
    
    def __init__(self, scaling_method: str = "standard"):
        if scaling_method == "standard":
            self.scaler = StandardScaler()
        else:
            self.scaler = MinMaxScaler()

    def clean_telemetry(self, df: pd.DataFrame) -> pd.DataFrame:
        """Removes outliers and handles missing values in sensor data."""
        # Replace 0 or negative values in physical metrics where invalid
        df = df.copy()
        for col in ['battery_voltage', 'motor_rpm', 'altitude']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: np.nan if x <= 0 else x)
        
        return df.fillna(method='ffill').fillna(0)

    def transform_for_training(self, df: pd.DataFrame, target_col: str) -> tuple:
        """Scales features and returns X, y split."""
        X = df.drop(columns=[target_col], errors='ignore')
        y = df[target_col]
        
        X_scaled = self.scaler.fit_transform(X)
        return X_scaled, y

    def inverse_transform_prediction(self, pred: np.ndarray) -> np.ndarray:
        """Useful if the target variable was also scaled."""
        return pred
