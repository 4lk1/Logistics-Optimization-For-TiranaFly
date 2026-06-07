import random
from typing import List, Dict, Any
from simulation.models import DroneTwin

class BatteryFailureSimulator:
    """Models battery degradation and catastrophic failure modes."""
    
    def __init__(self, failure_config: Dict[str, Any] = None):
        self.config = failure_config or {
            "p_thermal_runaway": 0.000001,
            "p_cell_imbalance": 0.0001,
            "base_degradation_per_cycle": 0.0005
        }

    def simulate_degradation(self, drones: List[DroneTwin]):
        for drone in drones:
            # Normal aging based on usage
            if drone.status != "IDLE":
                drone.battery.state_of_health_pct -= self.config["base_degradation_per_cycle"] * random.uniform(0.8, 1.2)
            
            # Catastrophic failure (Thermal Runaway)
            if random.random() < self.config["p_thermal_runaway"]:
                drone.status = "OUT_OF_SERVICE"
                drone.health_index = 0.0
                drone.failure_count += 1
            
            # Cell imbalance / Minor fault
            if random.random() < self.config["p_cell_imbalance"]:
                drone.battery.state_of_health_pct -= 2.0  # Sudden drop
                drone.check_health()
                if drone.health_index < 0.3:
                    drone.status = "MAINTENANCE"
