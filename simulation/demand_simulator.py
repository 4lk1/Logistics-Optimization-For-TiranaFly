import random
import math
from typing import List, Dict, Any
from simulation.models import AdministrativeUnitTwin

class DemandSimulator:
    """Generates delivery requests based on population and temporal scenarios."""
    
    def __init__(self, units: List[AdministrativeUnitTwin]):
        self.units = units
        self.base_demand_rate = 0.001  # Requests per person per hour (baseline)

    def generate_step_demand(self, sim_hour: float, tick_duration_hr: float, scenario_config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Generates requests for the current simulation step.
        """
        if scenario_config is None:
            scenario_config = {}

        global_multiplier = scenario_config.get("global_multiplier", 1.0)
        is_holiday = scenario_config.get("is_holiday", False)
        is_emergency = scenario_config.get("is_emergency", False)

        if is_holiday:
            global_multiplier *= 2.5
        if is_emergency:
            global_multiplier *= 5.0

        # Temporal factor (Diurnal cycle)
        # Peak demand at 14:00 (lunch) and 19:00 (dinner)
        temporal_factor = 0.2 + 0.8 * (
            0.6 * math.exp(-0.5 * ((sim_hour - 14) / 2)**2) + 
            1.0 * math.exp(-0.5 * ((sim_hour - 19) / 2)**2)
        )

        requests = []
        for unit in self.units:
            # Adjusted demand rate for this unit
            lambda_rate = (
                unit.base.population * 
                self.base_demand_rate * 
                temporal_factor * 
                global_multiplier * 
                unit.current_demand_surge * 
                tick_duration_hr
            )
            
            # Number of requests follows a Poisson distribution
            num_requests = self._poisson_sample(lambda_rate)
            
            for _ in range(num_requests):
                requests.append({
                    "unit_id": unit.base.name,
                    "priority": self._assign_priority(is_emergency),
                    "payload_kg": random.uniform(0.5, 4.0),
                    "created_at": sim_hour
                })
                unit.active_requests += 1
                
        return requests

    def _poisson_sample(self, lam: float) -> int:
        """Simple Poisson sampler using the Knuth algorithm."""
        if lam <= 0: return 0
        L = math.exp(-lam)
        k = 0
        p = 1.0
        while p > L:
            k += 1
            p *= random.random()
        return k - 1

    def _assign_priority(self, is_emergency: bool) -> int:
        if is_emergency:
            return random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
        return random.choices([1, 2, 3], weights=[0.1, 0.3, 0.6])[0]

    def simulate_population_growth(self, years: int, annual_growth_rate: float = 0.02):
        """Applies growth to all administrative units."""
        for unit in self.units:
            unit.simulate_growth((1 + annual_growth_rate)**years - 1)
