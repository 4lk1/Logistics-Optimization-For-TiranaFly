import random
from dataclasses import dataclass
from enum import Enum

class WeatherCondition(Enum):
    CLEAR = "CLEAR"
    CLOUDY = "CLOUDY"
    WINDY = "WINDY"
    RAINY = "RAINY"
    STORM = "STORM"

@dataclass
class WeatherState:
    condition: WeatherCondition
    wind_speed_mps: float
    temperature_c: float
    visibility_km: float
    precipitation_mm_hr: float

class WeatherSimulator:
    """Simulates weather conditions and their impact on drone operations."""
    
    def __init__(self):
        self.current_state = WeatherState(
            condition=WeatherCondition.CLEAR,
            wind_speed_mps=2.0,
            temperature_c=25.0,
            visibility_km=20.0,
            precipitation_mm_hr=0.0
        )

    def step(self):
        """Transition weather state based on probabilistic model."""
        # Simple Markovian transition could be implemented here
        rand = random.random()
        if rand < 0.05:
            self.current_state.condition = random.choice(list(WeatherCondition))
        
        # Add some jitter to metrics
        self.current_state.wind_speed_mps = max(0.0, self.current_state.wind_speed_mps + random.uniform(-0.5, 0.5))
        self.current_state.temperature_c += random.uniform(-0.1, 0.1)

    def get_impact_factors(self) -> dict:
        """
        Returns multipliers for energy cost and flight time.
        Energy Penalty: Wind and Temperature affect battery efficiency.
        Time Penalty: High winds or rain require slower flight speeds.
        """
        energy_penalty = 1.0
        time_penalty = 1.0
        flight_restricted = False

        # Wind impact
        if self.current_state.wind_speed_mps > 15.0:
            flight_restricted = True
        elif self.current_state.wind_speed_mps > 8.0:
            energy_penalty *= 1.3
            time_penalty *= 1.2

        # Temperature impact (Battery efficiency)
        if self.current_state.temperature_c < 0.0 or self.current_state.temperature_c > 40.0:
            energy_penalty *= 1.2

        # Rain impact
        if self.current_state.condition == WeatherCondition.RAINY:
            time_penalty *= 1.1
            energy_penalty *= 1.05
        elif self.current_state.condition == WeatherCondition.STORM:
            flight_restricted = True

        return {
            "energy_multiplier": energy_penalty,
            "time_multiplier": time_penalty,
            "is_restricted": flight_restricted
        }
