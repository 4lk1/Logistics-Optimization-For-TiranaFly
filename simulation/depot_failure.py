import random
from typing import List, Dict, Any
from simulation.models import DepotTwin

class DepotFailureSimulator:
    """Simulates various failure modes for depots."""
    
    def __init__(self, failure_config: Dict[str, Any] = None):
        self.config = failure_config or {
            "p_grid_failure": 0.0001,
            "p_comm_failure": 0.0005,
            "p_structural_failure": 0.00001
        }

    def apply_failures(self, depots: List[DepotTwin]):
        for depot in depots:
            if not depot.is_operational:
                # Attempt recovery
                if random.random() < 0.01:
                    depot.is_operational = True
                    depot.power_grid_health = 1.0
                continue

            # Power Grid Failure
            if random.random() < self.config["p_grid_failure"]:
                depot.power_grid_health = random.uniform(0, 0.2)
                if depot.power_grid_health < 0.05:
                    depot.is_operational = False

            # Communication Outage
            if random.random() < self.config["p_comm_failure"]:
                depot.communication_latency_ms = random.uniform(500, 5000)
            else:
                depot.communication_latency_ms = max(20.0, depot.communication_latency_ms * 0.9)

            # Structural / Maintenance Issue
            if random.random() < self.config["p_structural_failure"]:
                depot.is_operational = False
