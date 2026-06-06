import numpy as np
from typing import Dict, List, Optional
import datetime

class DemandForecaster:
    """
    Predicts delivery demand based on population distribution and temporal patterns.
    Baseline: 807,029 residents of Tirana.
    """
    
    TOTAL_POPULATION = 807029
    # Estimated average daily orders per 1000 residents
    BASE_ORDER_RATE = 2.5 

    def __init__(self, h3_population: Dict[str, int]):
        self.h3_population = h3_population
        self.total_h3_pop = sum(h3_population.values())
        
        # Temporal multipliers
        self.hourly_multipliers = self._init_hourly_multipliers()
        self.daily_multipliers = {
            0: 0.8,  # Monday
            1: 0.9,
            2: 1.0,
            3: 1.1,
            4: 1.4,  # Friday (Peak)
            5: 1.3,  # Saturday
            6: 0.7   # Sunday
        }

    def _init_hourly_multipliers(self) -> Dict[int, float]:
        """Defines a typical urban delivery demand curve."""
        multipliers = {}
        for h in range(24):
            if 0 <= h < 7: multipliers[h] = 0.1  # Night
            elif 7 <= h < 11: multipliers[h] = 0.8 # Morning
            elif 11 <= h < 14: multipliers[h] = 1.5 # Lunch peak
            elif 14 <= h < 18: multipliers[h] = 1.2 # Afternoon
            elif 18 <= h < 22: multipliers[h] = 2.0 # Evening peak
            else: multipliers[h] = 0.5 # Late night
        return multipliers

    def get_static_demand(self, h3_id: str) -> float:
        """Returns the expected daily orders for a specific H3 cell."""
        pop = self.h3_population.get(h3_id, 0)
        return (pop / 1000.0) * self.BASE_ORDER_RATE

    def predict_demand(self, h3_id: str, timestamp: datetime.datetime) -> float:
        """
        Predicts demand for a specific H3 cell at a specific time.
        f = baseline * hourly_m * daily_m
        """
        base = self.get_static_demand(h3_id) / 24.0 # Base hourly rate
        h_mult = self.hourly_multipliers.get(timestamp.hour, 1.0)
        d_mult = self.daily_multipliers.get(timestamp.weekday(), 1.0)
        
        return base * h_mult * d_mult

    def get_total_expected_demand(self, timestamp: datetime.datetime) -> float:
        """Predicts total network-wide demand for a given timestamp."""
        total_base = (self.total_h3_pop / 1000.0) * self.BASE_ORDER_RATE / 24.0
        h_mult = self.hourly_multipliers.get(timestamp.hour, 1.0)
        d_mult = self.daily_multipliers.get(timestamp.weekday(), 1.0)
        
        return total_base * h_mult * d_mult

    def simulate_demand_spike(self, h3_id: str, factor: float = 3.0) -> float:
        """Returns demand for a spike event (e.g., holiday or emergency)."""
        return self.get_static_demand(h3_id) * factor
