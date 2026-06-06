# filename: fleet/demand_forecaster.py
import numpy as np
from typing import List

class DemandForecasterEngine:
    @staticmethod
    def generate_stochastic_demand_matrix(base_weight: float, timesteps_hours: int = 24) -> List[float]:
        # Uses a log-normal distribution to simulate variations in consumer order patterns
        stochastic_curve = np.random.lognormal(mean=0.0, sigma=0.25, size=timesteps_hours)
        return [float(base_weight * factor) for factor in stochastic_curve]